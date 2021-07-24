import signal
import threading
import traceback


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