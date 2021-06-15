from master import exceptions
import inspect
import time
import os

class loggerError(exceptions.exceptions):
    pass

class levelNotExist(loggerError):
    pass

class permissionDenied(loggerError):
    pass

def getName(index=1) -> str:  # 获取上上级调用者的__name__
    a = inspect.stack()
    frm = inspect.stack()[index]  # 0是本函数，1是上级调用，2是上上级，以此类推
    mod = inspect.getmodule(frm[0])
    try:
        return mod.__name__
    except AttributeError:
        return None

class Logger():
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3

    def __init__(self, folder, level) -> None:
        if level < 0 or level > 3:
            raise levelNotExist
        if folder[-1] != "/":  # 防止文件名直接加到文件夹名后😂
            folder += "/"
        self.folder = folder
        self.__level = level
        self.__levelDic = {0: "[DBUG]", 1: "[INFO]",
                           2: "[WARN]", 3: "[ERRO]"}  # 单纯只是为了给__write函数用
        self.created = False
        self.name = time.strftime("%Y%m%d-%H:%M:%S", time.localtime())
        if not os.path.exists(folder):
            os.mkdir(folder)
        self.file = None  # 可以避免出现一大堆空的日志文件

    def __del__(self) -> None:
        if self.created:
            self.file.close()

    def __write(self, level, text, theName):
        if level >= self.__level:
            if not self.created:
                self.file = open(self.folder + self.name,
                                 "a+", encoding="utf-8")
                self.created = True
            self.file.write(self.__levelDic[level] +  # 格式[level][time][name]--event--
                            time.strftime("[%Y%m%d-%H:%M:%S]", time.localtime()) +
                            "[" + theName + "]" + text + '\n')

    def info(self, text) -> None:
        self.__write(self.INFO, text, getName(2))

    def warn(self, text) -> None:
        self.__write(self.WARNING, text, getName(2))

    def error(self, text) -> None:
        self.__write(self.ERROR, text, getName(2))

    def setLevel(self, level) -> None:
        if getName(2) == "__main__":  # 只有主进程才有权限设置日志级别
            self.__level = level
        else:
            print(getName(2))
            raise permissionDenied

defaultLogger = Logger("logs", 2)