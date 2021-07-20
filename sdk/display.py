import threading
import abc
import time

from sdk import epd2in9_V2 as epdDriver
from sdk import general

from PIL import Image

# TODO:添加线程池满检测，直接创建新线程完成任务
# TODO:添加屏幕自动休眠，长时间自动刷新


class Element(metaclass=abc.ABCMeta):   # 定义抽象类
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.page = ""
        self.inited = False

    @abc.abstractmethod
    def init(self, register):   # 初始化函数，当被添加到动态Paper时被调用
        pass

    @abc.abstractmethod
    def build(self) -> Image:    # 当页面刷新时被调用，须返回一个图像
        pass


class Page:
    pass


class Paper:
    """
    用于显示静态图像，不支持切换Page
    """

    def __init__(self, epd: epdDriver.EPD_2IN9_V2, paper_lock: threading.Lock, epd_rLock: threading.RLock, background_image=Image.new(1, (296, 128), 1), update_wait=0.5):
        self.inited = False
        self.background_image = background_image
        self.paper_lock = paper_lock  # 确保只有一个Page对象能获得主动权～
        self.epd_rLock = epd_rLock
        self.epd = epd
        self.image_old = self.background_image
        self.update_wait = update_wait

    def __del__(self):
        if self.inited:
            self.paper_lock.release()

    def __inited_check(self):
        if not self.inited:
            raise RuntimeError("The object has not been initialized!")

    def display(self, image: Image):
        self.__inited_check()
        b_image = self.epd.get_buffer(image)
        self.epd_rLock.acquire()
        self.epd.init()
        self.epd.display_Base(b_image)  # 是这样的吗？？？迷人的驱动
        self.epd.sleep()
        self.epd_rLock.release()

    def display_partial(self, image: Image):
        self.__inited_check()
        b_image = self.epd.get_buffer(image)
        self.epd_rLock.acquire()
        self.epd.init()
        self.epd.display_Partial_Wait(b_image)
        self.epd.sleep()
        self.epd_rLock.release()

    def build(self) -> Image:
        return self.background_image

    def init(self):
        if not self.paper_lock.acquire(blocking=False):
            raise RuntimeError("Existing Page object")
        self.inited = True
        self.display(self.build())
        return True

    def refresh(self):
        self.__inited_check()
        self.display(self.image_old)
        return True

    def update(self, refresh=False):
        self.__inited_check()
        self.epd_rLock.acquire()
        if not self.inited:
            return
        if refresh:
            self.display(self.build())
        else:
            self.display_partial(self.build())
        if refresh:
            time.sleep(self.update_wait)
        self.epd_rLock.release()

    def update_background(self, image, refresh=False):
        self.__inited_check()
        self.background_image = image
        self.update(refresh)


class PaperDynamic(Paper):
    SECONDLY = 0
    MINUTELY = 1
    TEN_MINUTELY = 2
    HALF_HOURLY = 3
    HOURLY = 4

    def __init__(self,
                 epd: epdDriver.EPD_2IN9_V2,
                 paper_lock: threading.Lock,
                 epd_rLock: threading.RLock,
                 pool: general.ThreadPool,
                 background_image=None,
                 update_wait=0.5,
                 ):
        super().__init__(epd, paper_lock, epd_rLock, background_image, update_wait)
        # 实例化各种定时器
        self.pool = pool
        self.timing_task_secondly = general.TimingTasksAsyn(1, pool)
        self.timing_task_minutely = general.TimingTasksAsyn(60, pool)
        self.timing_task_ten_minutely = general.TimingTasksAsyn(600, pool)
        self.timing_task_half_hourly = general.TimingTasksAsyn(1800, pool)
        self.timing_task_hourly = general.TimingTasksAsyn(3600, pool)
        self.pages = {"mainPaper": [], "infoPaper": [], "warnPaper": [], "errorPaper": []}  # TODO:为Handler页面添加内容
        self.nowPage = "mainPaper"

    def __del__(self):  # TODO: 测试销毁器
        self.timing_task_secondly.stop()
        self.timing_task_minutely.stop()
        self.timing_task_ten_minutely.stop()
        self.timing_task_half_hourly.stop()
        self.timing_task_hourly.stop()
        super().__del__()

    def build(self) -> Image:
        new_image = self.background_image
        for element in self.pages[self.nowPage]:
            element_image = element.build()
            new_image.paste(element_image, (element.x, element.y))
        self.image_old = new_image()
        return new_image

    def register(self, cycle, func, *args, **kwargs):   # 注册周期函数
        if cycle == self.SECONDLY:
            def adder():
                self.timing_task_secondly.add(func, *args, **kwargs)
            self.pool.add(adder)
            if not self.timing_task_secondly.is_running():
                self.timing_task_secondly.start()
        elif cycle == self.MINUTELY:
            def adder():
                self.timing_task_minutely.add(func, *args, **kwargs)
            self.pool.add(adder)
            if not self.timing_task_minutely.is_running():
                self.timing_task_minutely.start()
        elif cycle == self.TEN_MINUTELY:
            def adder():
                self.timing_task_ten_minutely.add(func, *args, **kwargs)
            self.pool.add(adder)
            if not self.timing_task_ten_minutely.is_running():
                self.timing_task_ten_minutely.start()
        elif cycle == self.HALF_HOURLY:
            def adder():
                self.timing_task_half_hourly.add(func, *args, **kwargs)
            self.pool.add(adder)
            if not self.timing_task_half_hourly.is_running():
                self.timing_task_half_hourly.start()
        elif cycle == self.HOURLY:
            def adder():
                self.timing_task_hourly.add(func, *args, **kwargs)
            self.pool.add(adder)
            if not self.timing_task_hourly.is_running():
                self.timing_task_hourly.start()
        else:
            raise ValueError("We don't have a cycle of this length!")

    def addPage(self, name: str):
        self.pages[name] = []

    def addElement(self, target: str, element):
        self.pages[target].append(element)
        element.page = target
        # TODO:初始化元素

    def changePage(self, name):
        if name in self.pages:
            self.nowPage = name
        else:
            raise ValueError("The specified page does not exist!")

    def update_async(self, refresh=False):
        self.__inited_check()
        self.pool.add(self.update, refresh)

    def infoHandler(self):
        pass

    def warnHandler(self):
        pass

    def errorHandler(self):
        pass


class PageHome(PaperDynamic):
    pass


class PageApp(PaperDynamic):
    pass
