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
        self.succeed = 0
        self.fail = 0
        for _ in range(thread_num):
            self.threads.append(Worker(self.tasks,
                                       self.is_running,
                                       self.handler,
                                       self.__thread_start_work,
                                       self.__thread_finish_work))

    @staticmethod
    def __errorHandler(_):
        pass

    def __thread_monitor(self, add=True):
        self.__lock.acquire()
        if add:
            self.__running_num += 1
        else:
            self.__running_num -= 1
        self.__lock.release()
        if self.__running_num == 0:
            try:
                self.__lock_wait.release()
            except RuntimeError:
                pass
        else:
            self.__lock_wait.acquire(blocking=False)

    def __thread_start_work(self):
        self.__lock.acquire()
        self.__running_num += 1
        self.__lock.release()
        self.__lock_wait.acquire(blocking=False)

    def __thread_finish_work(self, succeed=True):
        self.__lock.acquire()
        self.__running_num -= 1
        if succeed:
            self.succeed += 1
        else:
            self.fail += 1
        if self.__running_num == 0:
            try:
                self.__lock_wait.release()
            except RuntimeError:
                pass
        self.__lock.release()

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

    def add_immediately(self, func, *args, **kwargs):
        """
        这种方法添加的线程可能不受线程池控制
        """
        if self.full():
            new_thread = threading.Thread(target=func, args=args, kwargs=kwargs)
            new_thread.start()
            return new_thread
        else:
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

    def wait(self, timeout=0):
        self.__lock_wait.acquire(timeout=timeout)

    def full(self):
        if self.__running_num == self.__thread_num:
            return True
        else:
            return False

    def empty(self):
        if self.__running_num == 0:
            return False


class Worker(threading.Thread):
    def __init__(self, tasks: Queue, is_running, handler, start_log, finish_log):
        super().__init__()
        self.setDaemon(True)
        self.tasks = tasks
        self.is_running = is_running
        self.handler = handler
        self.start_log = start_log
        self.finish_log = finish_log

    def run(self):
        while True:
            try:
                task = self.tasks.get(block=True, timeout=2)
                self.start_log()
                task[0](*task[1], **task[2])
                self.finish_log()
            except queue.Empty:
                pass
            except:
                self.handler(traceback.format_exc())
                self.finish_log(False)
            else:
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


class TimingTask:
    def __init__(self, cycle: int, func, limit=None, timeoutHandler=None, daemonic=True, *args, **kwargs):
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
        self.__timer = threading.Timer(self.cycle, self.__run)
        self.__running = False
        self.args = args
        self.kwargs = kwargs
        if limit is None:
            self.limit = cycle
        else:
            self.limit = limit
        if timeoutHandler is None:
            self.handler = self.__timeoutHandler
        else:
            self.handler = timeoutHandler

    def __del__(self):  # 不知道有没有效果，以后再调试
        self.stop()

    def is_running(self):
        return self.__running

    def stop(self):
        self.__timer.cancel()
        self.__running = False

    @staticmethod
    def __timeoutHandler(_):
        pass

    def __run(self):
        if (not self.__running) | self.cycle <= 0:  # TODO:测试实例被删除后执行这段语句的结果
            return
        self.__timer = threading.Timer(self.cycle, self.__run)
        self.__timer.setDaemon(self.daemonic)
        self.__timer.start()
        self.func(*self.args, **self.kwargs)

    def start(self):
        if self.__running | self.cycle <= 0:
            return
        self.__running = True
        self.__timer = threading.Timer(self.cycle, self.__run)
        self.__timer.setDaemon(self.daemonic)
        self.__timer.start()


class TimingTasks(TimingTask):
    def __init__(self, cycle: int, funcs=None, limit=None, timeoutHandler=None, daemonic=True):
        super().__init__(cycle, self.__do_tasks(), limit, timeoutHandler, daemonic)
        if funcs is None:
            funcs = dict()
        self.funcs = funcs
        self.lock = threading.Lock()    # 不知道为啥，用单下划线子类无法访问到，这里只好这样了

    def __do_tasks(self):
        self.lock.acquire()
        for func, arguments in self.funcs:
            func(*arguments[0], **arguments[1])
        self.lock.release()

    def add(self, func, timeout=0, *args, **kwargs):
        """
        建议使用线程池进行此操作（异步执行）
        """
        self.lock.acquire(timeout=timeout)
        self.funcs[func] = (args, kwargs)
        self.lock.release()

    def remove(self, func, timeout=0):
        """
        建议使用线程池进行此操作（异步执行）
        """
        self.lock.acquire(timeout=timeout)
        del self.funcs[func]
        self.lock.release()

    def clear(self, timeout=0):
        self.lock.acquire(timeout=timeout)
        self.funcs = {}
        self.lock.release()

    def is_empty(self):
        if len(self.funcs) == 0:
            return True
        return False


class TimingTasksAsyn(TimingTasks):
    def __init__(self, cycle: int, pool: ThreadPool, funcs=None, limit=None, timeoutHandler=None, daemonic=True):
        if funcs is None:
            funcs = {}
        super().__init__(cycle, funcs, limit, timeoutHandler, daemonic)
        self.pool = pool

    def __do_tasks(self):
        self.lock.acquire()
        for func, arguments in self.funcs:
            self.pool.add(func, *arguments[0], **arguments[1])  # TODO:这里可能会出现一些问题
        self.lock.release()
