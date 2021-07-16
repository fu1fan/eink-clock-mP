import inspect
import time
import os
import threading


def get_name(index=1):  # 获取上上级调用者的__name__
    frm = inspect.stack()[index]  # 0是本函数，1是上级调用，2是上上级，以此类推
    mod = inspect.getmodule(frm[0])
    try:
        return mod.__name__
    except AttributeError:
        return None


def default_handler(info):
    pass


class Logger:
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3

    def __init__(self, level, folder="logs", tag=None, debug_handler=default_handler, info_handler=default_handler,
                 warn_handler=default_handler, error_handler=default_handler) -> None:
        if level < 0 or level > 3:
            raise
        if folder[-1] != "/":  # 防止文件名直接加到文件夹名后😂
            folder += "/"
        self.folder = folder
        self.__level = level
        self.__levelDic = {0: "[DBUG]", 1: "[INFO]",
                           2: "[WARN]", 3: "[ERRO]"}  # 单纯只是为了给__write函数用
        self.debugHandler = debug_handler
        self.infoHandler = info_handler
        self.warnHandler = warn_handler
        self.errorHandler = error_handler
        self.lock = threading.Lock()
        if tag is None:
            self.name = time.strftime("%Y%m%d-%H:%M:%S", time.localtime())
        else:
            self.name = "[%s]%s" % (tag, time.strftime("%Y%m%d-%H:%M:%S", time.localtime()))
        if not os.path.exists(folder):
            os.mkdir(folder)

    def __write(self, level, text, thename):
        if level >= self.__level:
            self.lock.acquire()
            file = open(self.folder + self.name,
                        "a+", encoding="utf-8")
            if "\n" in text:
                text = "\n%s" % text
            if text[-1] != "\n":
                text = text + "\n"
            content = "%s%s[%s]%s" % (
                self.__levelDic[level], time.strftime("[%Y%m%d-%H:%M:%S]", time.localtime()), thename,
                text)  # 格式[level][time][name]--event--
            file.write(content)
            file.close()
            self.lock.release()

    def debug(self, text, info=None) -> None:  # text为写入日志的内容，info为为用户显示的内容，只有当启用Handler时info才会被使用
        name = get_name(2)
        self.__write(self.DEBUG, text, name)
        if info is not None:
            self.debugHandler(info)

    def info(self, text, info=None) -> None:  # text为写入日志的内容，info为为用户显示的内容，只有当启用Handler时info才会被使用
        name = get_name(2)
        self.__write(self.INFO, text, name)
        if info is not None:
            self.infoHandler(info)

    def warn(self, text, info=None) -> None:
        name = get_name(2)
        self.__write(self.WARNING, text, name)
        if info is not None:
            self.warnHandler(info)

    def error(self, text, info=None) -> None:
        name = get_name(2)
        self.__write(self.ERROR, text, name)
        if info is not None:
            self.errorHandler(info)

    def setLevel(self, level) -> None:
        self.__level = level
