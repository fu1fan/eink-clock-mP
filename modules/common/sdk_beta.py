import time
import os
import configparser
import inspect
import threading

from requests.api import request

class exceptions(Exception):
    pass


##########日志模块##########

class loggerError(exceptions):
    pass

class levelNotExist(loggerError):
    pass

class permissionDenied(loggerError):
    pass

def getName(index=1) -> str:  # 获取上上级调用者的__name__
    a = inspect.stack()
    frm = inspect.stack()[index]  # 0是本函数，1是上级调用，2是上上级，以此类推
    mod = inspect.getmodule(frm[0])
    return mod.__name__

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


##########配置模块##########
# TODO:解决不能自动创建目录的问题

class Configuration:
    '''
    #ConfigParser 常用方法

    事例文件
    [db]
    db_host = 127.0.0.1
    db_port = 69
    db_user = root
    db_pass = root
    host_port = 69

    [concurrent]
    thread = 10
    processor = 20

    1、获取所用的section节点
        import configparser
        config = configparser.ConfigParser()
        config.read("ini", encoding="utf-8")
        print(config.sections())
        运行结果:
        ['db', 'concurrent']

    2、获取指定section 的options。即将配置文件某个section 内key 读取到列表中：
        import configparser
        config = configparser.ConfigParser()
        config.read("ini", encoding="utf-8")
        r = config.options("db")
        print(r)
        运行结果:
        ['db_host', 'db_port', 'db_user', 'db_pass', 'host_port']

    3、获取指点section下指点option的值
        import configparser
        config = configparser.ConfigParser()
        config.read("ini", encoding="utf-8")
        r = config.get("db", "db_host")
        \# r1 = config.getint("db", "k1") #将获取到值转换为int型
        \# r2 = config.getboolean("db", "k2" ) #将获取到值转换为bool型
        \# r3 = config.getfloat("db", "k3" ) #将获取到值转换为浮点型
        print(r)
        运行结果:
        127.0.0.1

    4、获取指点section的所用配置信息
        import configparser
        config = configparser.ConfigParser()
        config.read("ini", encoding="utf-8")
        r = config.items("db")
        print(r)
        运行结果
        [('db_host', '127.0.0.1'), ('db_port', '69'), ('db_user', 'root'), ('db_pass', 'root'), ('host_port', '69')]
    5、修改某个option的值，如果不存在则会出创建
        import configparser
        config = configparser.ConfigParser()
        config.read("ini", encoding="utf-8")
        config.set("db", "db_port", "69")  #修改db_port的值为69
        config.write(open("ini", "w"))

    6、检查section或option是否存在，bool值
        import configparser
        config = configparser.ConfigParser()
        config.has_section("section") #是否存在该section
        config.has_option("section", "option")  #是否存在该option

    7、添加section 和 option
        import configparser
        config = configparser.ConfigParser()
        config.read("ini", encoding="utf-8")
        if not config.has_section("default"):  # 检查是否存在section
            config.add_section("default")
        if not config.has_option("default", "db_host"):  # 检查是否存在该option
            config.set("default", "db_host", "1.1.1.1")
        config.write(open("ini", "w"))

    8、删除section 和 option
        import configparser
        config = configparser.ConfigParser()
        config.read("ini", encoding="utf-8")
        config.remove_section("default") #整个section下的所有内容都将删除
        config.write(open("ini", "w"))

    9、写入文件
        import configparser
        config = configparser.ConfigParser()
        config.read("ini", encoding="utf-8")
        写回文件的方式如下：（使用configparser的write方法）
        config.write(open("ini", "w"))

    引用自：https://www.cnblogs.com/zhou2019/p/10599953.html
    '''

    def __init__(self, path) -> None:
        self.path = path
        self.config = configparser.ConfigParser()
        if not os.path.exists(path):
            open(path, "w", encoding="utf-8").close()

    def getConf(self) -> configparser.ConfigParser:
        return self.config

    def saveConf(self) -> None:
        self.config.write(open(self.path, "w", encoding="utf-8"))


##########显示模块##########

class Display:
    def __init__(self) -> None:
        pass


##########多线程管理##########

threadLock = threading.Lock()

def getLock() -> threading.Lock:
    return threadLock