import inspect
import queue
import signal
import threading
import traceback
from queue import Queue
import ctypes

import requests


def _async_raise(tid, exc_type):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exc_type):
        exc_type = type(exc_type)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exc_type))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


class ThreadPool:
    def __init__(self, thread_num: int, handler=None):
        self.tasks = Queue()
        self.threads = []
        self.running = False
        self.__inited = False
        if handler is None:
            handler = self.__errorHandler
        else:
            handler = handler
        self.handler = handler
        self.__lock = threading.Lock()
        self.__lock_wait = threading.Lock()
        self.__running_num = 0
        self.__thread_num = thread_num
        for _ in range(thread_num):
            self.threads.append(Worker(self.is_running, self.handler, self.__thread_monitor()))

    @staticmethod
    def __errorHandler(_):
        pass

    def __thread_monitor(self, add=True):
        self.__lock.acquire()
        if add:
            self.__running_num += 1
        else:
            self.__running_num -= 1
        self.__lock.acquire()
        if self.__running_num == 0:
            try:
                self.__lock_wait.release()
            except RuntimeError:
                pass
        else:
            self.__lock_wait.acquire()

    def is_running(self):
        return self.running

    def start(self):
        if self.__inited:
            raise RuntimeError("A ThreadPool can only be started once!")
        self.__inited = True
        for i in self.threads:
            i.start()

    def add(self, func, *args, **kwargs):
        self.tasks.put((func, args, kwargs))

    def stop(self):
        self.running = False

    def stop_mandatory(self):   # 不稳定，不建议使用！
        self.running = False
        for i in self.threads:
            try:
                stop_thread(i)
            except (ValueError, SystemError):   # 这行代码有点危
                self.handler(traceback.format_exc())

    def task_qsize(self):
        return self.tasks.qsize()

    def empty_thread(self):
        return self.__thread_num - self.__running_num

    def running_thread(self):
        return self.__running_num

    def clear(self):
        self.tasks.queue.clear()    # TODO:未测试

    def wait_and_stop(self, timeout=0):
        self.__lock_wait.acquire(timeout=timeout)


class Worker(threading.Thread):
    def __init__(self, tasks: Queue, is_running, handler, monitor):
        super().__init__()
        self.setDaemon(True)
        self.tasks = tasks
        self.is_running = is_running
        self.handler = handler
        self.monitor = monitor

    def run(self):
        while True:
            self.monitor()
            try:
                task = self.tasks.get(block=True, timeout=2)
                task[0](*task[1], **task[2])
            except queue.Empty:
                pass
            except:
                self.handler(traceback.format_exc())
            else:
                self.monitor(False)
                if not self.is_running():
                    break


def if_online() -> bool:
    try:
        response = requests.get("https://pi.simplebytes.cn/ifonline")
        response.raise_for_status()
    except requests.RequestException:
        return False
    return True


def set_timeout(time: int, callback):
    def wrap(func):
        def handle(signum, frame):  # 收到信号 SIGALRM 后的回调函数，第一个参数是信号的数字，第二个参数是the interrupted stack frame.
            raise RuntimeError

        def to_do(*args, **kwargs):
            try:
                signal.signal(signal.SIGALRM, handle)  # 设置信号和回调函数
                signal.alarm(time)  # 设置 num 秒的闹钟
                r = func(*args, **kwargs)
                signal.alarm(0)  # 关闭闹钟
                return r
            except RuntimeError:
                callback(traceback.format_exc())

        return to_do

    def no_limited(func):
        return func

    if time == 0:  # 如果输入time=0则不限制运行时间
        return no_limited
    else:
        return wrap


class TimingTask:  # TODO: 改用timer
    def __init__(self, cycle: int, func, limit=None, timeoutHandler=None, daemonic=True):
        """
        cycle:\n
        -int：每隔cycle秒执行一次func\n
        func:被执行的函数\n
        limit:\n
        -None:使用一次循环的时间作为函数执行的限制时间\n
        -0:不限制函数的运行时间\n
        -int:限制函数运行limit秒\n
        timeoutHandler:超时后调用的函数，会返回一个str\n
        """
        self.cycle = cycle
        self.func = func
        self.daemonic = daemonic
        self.__timer = None
        if limit is None:
            self.limit = cycle
        else:
            self.limit = limit
        if timeoutHandler is None:
            self.handler = self.__timeoutHandler
        else:
            self.handler = timeoutHandler

    def __del__(self):  # 不知道有没有效果，以后再调试
        self.__timer.cancel()

    def stop(self):
        self.__timer.cancel()

    @staticmethod
    def __timeoutHandler(_):
        pass

    def __run(self, *args, **kwargs):
        self.__timer = threading.Timer(self.cycle, self.__run, args, kwargs)  # 这能正常运行，别管他！
        self.__timer.setDaemon(self.daemonic)
        self.__timer.start()
        self.func(*args, **kwargs)

    def start(self, *args, **kwargs):
        self.__timer = threading.Timer(self.cycle, self.__run, args, kwargs)
        self.__timer.setDaemon(self.daemonic)
        self.__timer.start()


class TimingTasks(TimingTask):
    def __init__(self, cycle: int, funcs: list, limit=None, timeoutHandler=None, daemonic=True):
        super().__init__(cycle, self.__do_tasks(), limit, timeoutHandler, daemonic)
        self.funcs = funcs

    def __do_tasks(self):
        for func in self.funcs:
            func()

    def add(self, func):
        self.funcs.append(func)

    def remove(self, func):
        self.funcs.remove(func)


class TimingTasksAsyn(TimingTasks):
    def __init__(self, cycle: int, funcs: list, limit=None, timeoutHandler=None, daemonic=True):
        super().__init__(cycle, funcs, limit, timeoutHandler, daemonic)

    def __do_tasks(self):  # TODO:添加对线程池的支持
        pass
