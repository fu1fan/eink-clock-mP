import inspect
from pathlib import Path
import time
import os
import threading

from pathlib import Path

DEBUG = 0
INFO = 1
WARNING = 2
ERROR = 3


def get_name(index=1):  # 获取上上级调用者的__name__
    frm = inspect.stack()[index]  # 0是本函数，1是上级调用，2是上上级，以此类推
    mod = inspect.getmodule(frm[0])
    try:
        return mod.__name__
    except AttributeError:
        return None


class Logger:
    def __init__(self, level, folder="logs", tag=None, debug_handler=None, info_handler=None,
                 warn_handler=None, error_handler=None) -> None:
        if level < 0 or level > 3:
            raise
        if folder[-1] != "/":  # 防止文件名直接加到文件夹名后😂
            folder += "/"
        self.folder = folder
        self.__level = level
        self.__levelDic = {0: "[DBUG]", 1: "[INFO]",
                           2: "[WARN]", 3: "[ERRO]"}  # 单纯只是为了给__write函数用

        # 在线表演💩山代码，但我是在不知道相关的语法🍬
        if debug_handler is None:
            self.debugHandler = self.__defaultHandler
        else:
            self.debugHandler = debug_handler
        if debug_handler is None:
            self.infoHandler = self.__defaultHandler
        else:
            self.infoHandler = info_handler
        if debug_handler is None:
            self.warnHandler = self.__defaultHandler
        else:
            self.warnHandler = warn_handler
        if debug_handler is None:
            self.errorHandler = self.__defaultHandler
        else:
            self.errorHandler = error_handler

        self.lock = threading.Lock()
        if tag is None:
            self.name = time.strftime("%Y%m%d--%H-%M-%S", time.localtime())
        else:
            self.name = "[%s]%s" % (tag, time.strftime("%Y%m%d--%H-%M-%S", time.localtime()))
        if not os.path.exists(folder):
            os.mkdir(folder)

    @staticmethod
    def __defaultHandler(_):
        pass

    def __write(self, level, text, the_name):
        if level >= self.__level:
            self.lock.acquire()
            file = open(Path(self.folder + self.name),
                        "a+", encoding="utf-8")
            if len(text) == 0:
                text = "\n"
            elif "\n" in text:
                text = "\n%s" % text
            elif text[-1] != "\n":
                text = text + "\n"
            content = "%s%s[%s]%s" % (
                self.__levelDic[level], time.strftime("[%Y%m%d-%H:%M:%S]", time.localtime()), the_name,
                text)  # 格式[level][time][name]--event--
            file.write(content)
            file.close()
            print(content, end="")
            self.lock.release()

    def debug(self, text, info=None) -> None:  # text为写入日志的内容，info为为用户显示的内容，只有当启用Handler时info才会被使用
        name = get_name(2)
        self.__write(DEBUG, text, name)
        if info is not None:
            self.debugHandler(info)

    def info(self, text, info=None) -> None:
        name = get_name(2)
        self.__write(INFO, text, name)
        if info is not None:
            self.infoHandler(info)

    def warn(self, text, info=None) -> None:
        name = get_name(2)
        self.__write(WARNING, text, name)
        if info is not None:
            self.warnHandler(info)

    def error(self, text, info=None) -> None:
        name = get_name(2)
        self.__write(ERROR, text, name)
        if info is not None:
            self.errorHandler(info)

    def setLevel(self, level) -> None:
        self.__level = level
