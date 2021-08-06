import threading
import time

from PIL import Image


class Paper:
    """
    用于显示静态图像，不支持切换Page
    """

    def __init__(self,
                 env,
                 background_image=Image.new("RGB", (296, 128), (255, 255, 255))):
        self.inited = False
        self.background_image = background_image
        self.epd = env.epd_driver
        self.image_old = self.background_image
        self.update_lock = threading.Lock()

    def __del__(self):
        if self.inited:
            self.exit()

    def display(self, image: Image):
        b_image = self.epd.get_buffer(image)
        self.epd.display_Base(b_image)  # 是这样的吗？？？迷人的驱动

    def display_partial(self, image: Image):
        b_image = self.epd.get_buffer(image)
        self.epd.display_Partial_Wait(b_image)

    def display_auto(self, image: Image):
        b_image = self.epd.get_buffer(image)
        self.epd.display_Auto(b_image)

    def build(self) -> Image:
        self.image_old = self.background_image
        return self.background_image

    def init(self):
        self.display(self.build())
        self.inited = True
        return True

    def exit(self):
        self.inited = False

    def refresh(self):
        if not self.inited:
            return
        self.display(self.image_old)
        return True

    def update_background(self, image, refresh=None):
        if not self.inited:
            return
        self.background_image = image
        if self.update_lock.acquire(blocking=False):
            self.epd.acquire()  # 重入锁，保证到屏幕刷新时使用的是最新的 self.build()
            self.update_lock.release()
            if refresh is None:
                self.display_auto(self.build())
            elif refresh:
                self.display(self.build())
            else:
                self.display_partial(self.build())
            self.epd.release()


class Page(list):  # page是对list的重写，本质为添加一个构造器
    def __init__(self):
        super().__init__()
        self.inited = False

    def init(self):
        for i in self:
            i.init()
        self.inited = True

    def pause(self):
        for i in self:
            i.pause()

    def recover(self):
        for i in self:
            i.recover()

    def exit(self):
        for i in self:
            i.exit()
        self.inited = False


class PaperDynamic(Paper):
    SECONDLY = 0
    MINUTELY = 1
    TEN_MINUTELY = 2
    HALF_HOURLY = 3
    HOURLY = 4

    def __init__(self,
                 env,
                 background_image=Image.new("RGB", (296, 128), 1)):
        super().__init__(env, background_image)
        # 实例化各种定时器
        # self.pool = env.pool
        self.pages = {"mainPage": Page(), "infoHandler": Page(), "warnHandler": Page(), "errorHandler": Page()}
        # TODO:为Handler页面添加内容
        self.nowPage = "mainPage"
        # self.touch_handler = env.touch_handler
        self.env = env

    def exit(self):
        for page in self.pages.values():
            page.exit()

    def build(self) -> Image:
        new_image = self.background_image.copy()
        for element in self.pages[self.nowPage]:
            element_image = element.build()
            if element_image:
                new_image.paste(element_image, (element.xy[0], element.xy[1]))
        self.image_old = new_image
        return new_image

    def addPage(self, name: str, page=None):
        if page is None:
            page = Page()
        self.pages[name] = page

    def addElement(self, target: str, element):
        self.pages[target].append(element)
        element.page = target

    def changePage(self, name, refresh=None):
        if name in self.pages:
            self.env.touch_handler.clear()
            self.pages[self.nowPage].pause()
            self.nowPage = name
            if self.pages[name].inited:
                self.pages[name].recover()
            else:
                self.pages[name].pause()
            self.env.pool.add_immediately(self._update, refresh)
        else:
            raise ValueError("The specified page does not exist!")

    def infoHandler(self):
        pass

    def warnHandler(self):
        pass

    def errorHandler(self):
        pass

    def _update(self, refresh=None):
        if self.update_lock.acquire(blocking=False):
            self.epd.acquire()  # 重入锁，保证到屏幕刷新时使用的是最新的 self.build()
            self.update_lock.release()
            if refresh is None:
                self.display_auto(self.build())
            elif refresh:
                self.display(self.build())
            else:
                self.display_partial(self.build())
            self.epd.release()

    def update(self, page_name: str, refresh=None):
        if not (self.inited and page_name == self.nowPage):
            return
        self._update(refresh)

    def update_async(self, page_name: str, refresh=None):
        self.env.pool.add_immediately(self.update, page_name, refresh)

    def init(self):
        self.pages[self.nowPage].init()
        super().init()


class Element:
    def __init__(self, xy: tuple, size, paper: PaperDynamic, background=None):
        if background is None:
            self.background = Image.new("RGB", size, (255, 255, 255))
        else:
            self.background = background
        self.xy = xy
        self.size = size
        self.paper = paper
        self.pool = paper.env.pool
        self.inited = False
        self.page = None

    def __del__(self):
        self.exit()

    def init(self):  # 初始化函数，当被添加到动态Paper时被调用
        self.inited = True

    def exit(self):  # 退出时调用
        self.inited = False

    def pause(self):    # 切换出page时调用
        pass

    def recover(self):  # 切换回page时调用
        pass

    def build(self) -> Image:  # 当页面刷新时被调用，须返回一个图像
        return self.background


class _Docker(Element):
    def __init__(self, paper: PaperDynamic):
        super().__init__((60, 0), (176, 30), paper)
        self.image = Image.open(open("resources/images/docker.jpg", "rb"))
        self.__active = False
        self.inited = False

    def clicked_handler(self, *args, **kwargs):
        if self.paper.nowPage == self.page and not self.__active and self.inited:
            self.__active = True
        self.paper.update_async(self.page)
        time.sleep(5)
        self.__active = False
        self.paper.update(self.page)

    def init(self):
        self.paper.env.touch_handler.add_clicked((0, 296, 0, 30), self.clicked_handler)
        self.inited = True

    def exit(self):
        self.inited = False

    def build(self) -> Image:
        if self.__active:
            return self.image
        else:
            return


class PaperTheme(PaperDynamic):
    def __init__(self, env):
        super().__init__(env)

    def init(self):
        self.addElement("mainPage", _Docker(self))
        super().init()


class PaperApp(PaperDynamic):
    pass
