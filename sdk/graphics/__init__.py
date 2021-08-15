import threading
import traceback

from PIL import Image


class Paper:
    """
    用于显示静态图像，不支持切换Page
    """

    def __init__(self,
                 env,
                 background_image=Image.new("RGB", (296, 128), (255, 255, 255))):
        self.active = False
        self.inited = False
        self.background_image = background_image
        self.epd = env.epd_driver
        self.image_old = self.background_image
        self.update_lock = threading.Lock()

    def __del__(self):
        if self.active:
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
        self.inited = True
        self.active = True
        self.display(self.build())
        return True

    def exit(self):
        self.active = False
        self.inited = False

    def refresh(self):
        if not self.active:
            return
        self.display(self.image_old)
        return True

    def update_background(self, image, refresh=None):
        if not self.active:
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
    def __init__(self, paper, name):
        super().__init__()
        self.paper = paper
        self.name = name
        self.inited = False

    def addElement(self, element):
        self.append(element)
        element.page = self

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
    def __init__(self,
                 env,
                 background_image=Image.new("RGB", (296, 128), (255, 255, 255))):
        super().__init__(env, background_image)
        # 实例化各种定时器
        # self.pool = env.pool
        self.pages = {"mainPage": Page(self, "mainPage"), "infoHandler": Page(self, "infoHandler"), "warnHandler": Page(self, "warnHandler"), "errorHandler": Page(self, "errorHandler")}
        # TODO:为Handler页面添加内容
        self.nowPage = "mainPage"
        self.oldPage = "mainPage"
        # self.touch_handler = env.touch_handler
        self.env = env

    def exit(self):
        for page in self.pages.values():
            page.exit()

    def pause(self):
        self.pages[self.nowPage].pause()
        self.active = False

    def recover(self):
        self.pages[self.nowPage].recover()
        self.active = True
        self.display(self.build())

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
            page = Page(self, name)
        self.pages[name] = page

    def addElement(self, element, target: str = "mainPage"):
        self.pages[target].append(element)
        element.page = self.pages[target]
        if self.active:
            element.init()

    def changePage(self, name, refresh=None):
        if name in self.pages:
            self.env.touch_handler.clear()
            self.pages[self.nowPage].pause()
            self.oldPage = self.nowPage
            self.nowPage = name
            if self.pages[name].inited:
                self.pages[name].recover()
            else:
                self.pages[name].init()
            self._update(refresh)
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
        if not (self.active and page_name == self.nowPage):
            return
        self._update(refresh)

    def pause_update(self, timeout=-1):
        if not self.update_lock.acquire(timeout=-1):
            raise TimeoutError

    def recover_update(self, raise_for_unlocked=False):
        try:
            self.update_lock.release()
        except RuntimeError as e:
            if raise_for_unlocked:
                raise e
            else:
                self.env.logger_env.warn(traceback.format_exc())
        self.env.pool.add_immediately(self._update)

    def update_async(self, page_name: str, refresh=None):
        self.env.pool.add_immediately(self.update, page_name, refresh)

    def init(self):
        self.pages[self.nowPage].init()
        super().init()


class Element:
    def __init__(self, xy: tuple, paper: PaperDynamic, size=(0, 0), background=None):
        self.xy = xy
        self.size = size
        self.paper = paper
        self.pool = paper.env.pool
        self.inited = False
        self.active = False
        self.page = None
        self.background = background

    def __del__(self):
        self.exit()

    def init(self):  # 初始化函数，当被添加到动态Paper时被调用
        self.inited = True
        self.active = True

    def exit(self):  # 退出时调用
        self.inited = False
        self.active = False

    def pause(self):    # 切换出page时调用
        self.active = False

    def recover(self):  # 切换回page时调用
        self.active = True

    def build(self) -> Image:  # 当页面刷新时被调用，须返回一个图像
        return self.background
