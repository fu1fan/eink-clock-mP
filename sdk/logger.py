import inspect
import time
import os
import sdk.master as master

class loggerError(master.exceptions):
    pass

class levelNotExist(loggerError):
    pass

def getName(index=1) -> str:  # 获取上上级调用者的__name__
    frm = inspect.stack()[index]  # 0是本函数，1是上级调用，2是上上级，以此类推
    mod = inspect.getmodule(frm[0])
    try:
        return mod.__name__
    except AttributeError:
        return None

def defaultHandler(info):
    pass

class Logger():
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3

    def __init__(self, level, folder = "logs", tag = None, debugHandler = defaultHandler, infoHandler = defaultHandler, warnHandler = defaultHandler, errorHandler = defaultHandler) -> None:
        if level < 0 or level > 3:
            raise levelNotExist
        if folder[-1] != "/":  # 防止文件名直接加到文件夹名后😂
            folder += "/"
        self.folder = folder
        self.__level = level
        self.__levelDic = {0: "[DBUG]", 1: "[INFO]",
                           2: "[WARN]", 3: "[ERRO]"}  # 单纯只是为了给__write函数用
        self.created = False
        self.debugHandler = debugHandler
        self.infoHandler = infoHandler
        self.warnHandler = warnHandler
        self.errorHandler = errorHandler
        if tag == None:
            self.name = time.strftime("%Y%m%d-%H:%M:%S", time.localtime())
        else:
            self.name = "[%s]%s" % (tag, time.strftime("%Y%m%d-%H:%M:%S", time.localtime()))
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
            if "\n" in text:
                text = "\n" + text
            content = "%s%s[%s]%s" % (self.__levelDic[level], time.strftime("[%Y%m%d-%H:%M:%S]", time.localtime()), theName, text)  #格式[level][time][name]--event--
            self.file.write(content)

    def debug(self, text, info = None) -> None:   #text为写入日志的内容，info为为用户显示的内容，只有当启用Handler时info才会被使用
        name = getName(2)
        self.__write(self.DEBUG, text, name)
        if info != None:
            self.debugHandler(info)

    def info(self, text, info = None) -> None:   #text为写入日志的内容，info为为用户显示的内容，只有当启用Handler时info才会被使用
        name = getName(2)
        self.__write(self.INFO, text, name)
        if info != None:
            self.infoHandler(info)

    def warn(self, text, info = None) -> None:
        name = getName(2)
        self.__write(self.WARNING, text, name)
        if info != None:
            self.warnHandler(info)

    def error(self, text, info = None) -> None:
        name = getName(2)
        self.__write(self.ERROR, text, name)
        if info != None:
            self.errorHandler(info)

    def setLevel(self, level) -> None:
        self.__level = level
