import threading
import abc

from PIL import Image, ImageFont, ImageDraw


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

    def update(self, refresh=None):
        if not self.inited:
            return
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

    def update_background(self, image, refresh=None):
        if not self.inited:
            return
        self.background_image = image
        self.update(refresh)


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
        self.pages = {"mainPage": []}
        self.nowPage = "mainPage"
        # self.touch_handler = env.touch_handler
        self.env = env

    def build(self) -> Image:
        new_image = self.background_image.copy()
        for element in self.pages[self.nowPage]:
            element_image = element.build()
            if element_image:
                new_image.paste(element_image, (element.x, element.y))
        self.image_old = new_image
        return new_image

    def addPage(self, name: str):
        self.pages[name] = []

    def addElement(self, target: str, element):
        self.pages[target].append(element)
        element.page = target
        element.init()

    def changePage(self, name):
        if name in self.pages:
            self.env.touch_handler.clear()
            self.nowPage = name
            self.update_async()
        else:
            raise ValueError("The specified page does not exist!")

    def update_async(self, refresh=None):
        self.env.pool.add_immediately(self.update, refresh)


class Page(list, metaclass=abc.ABCMeta):  # page是对list的重写，本质为添加一个构造器
    def __init__(self):
        super().__init__()

    def init(self):
        for i in self:
            i.init()

    def exit(self):
        for i in self:
            i.exit()


class Element(metaclass=abc.ABCMeta):  # 定义抽象类
    def __init__(self, x, y, paper: PaperDynamic):
        self.x = x
        self.y = y
        self.paper = paper
        self.pool = paper.env.pool
        self.inited = False

    def __del__(self):
        self.exit()

    def init(self):  # 初始化函数，当被添加到动态Paper时被调用
        self.inited = True

    def exit(self):  # 退出时调用
        self.inited = False

    @abc.abstractmethod
    def build(self) -> Image:  # 当页面刷新时被调用，须返回一个图像
        pass


class UILib:
    pass


class Button(Element, UILib):
    def __init__(self, x, y, paper: PaperDynamic, onclick, size=(60, 33), text="", *args, **kwargs):
        super().__init__(x, y, paper)
        self.on_clicked = onclick
        self.text = text
        self.__visible = True
        self.size = size
        self.args = args
        self.kwargs = kwargs
        self.font = ImageFont.truetype("resources/fonts/STHeiti_Light.ttc", 20)
        self.background_image = Image.new("RGB", size, (255, 255, 255))

    @property
    def visible(self):
        return self.__visible

    def setVisible(self, m: bool):
        self.__visible = m
        self.paper.update_async()

    def clickedHandler(self):
        if self.__visible and self.inited:
            self.on_clicked()

    def init(self):
        self.inited = True
        self.paper.env.touch_handler.add_clicked((self.x, self.x + self.size[0], self.y, self.y + self.size[1]),
                                                 self.clickedHandler,
                                                 *self.args,
                                                 **self.kwargs)

    def build(self) -> Image:
        if self.inited and self.__visible:
            image = self.background_image.copy()
            image_draw = ImageDraw.ImageDraw(image)
            image_draw.rectangle((0, 0, self.size[0], self.size[1]), fill="white", outline="black", width=1)
            image_draw.text((5, 5), self.text, font=self.font, fill=(0, 0, 0))
            return image
        elif not self.__visible:
            return None


class PaperBasis(PaperDynamic):
    def __init__(self, env):
        super().__init__(env)
        self.pages = {"mainPage": Page(), "infoHandler": Page(), "warnHandler": Page(),
                      "errorHandler": Page()}  # TODO:为Handler页面添加内容

    def exit(self):
        self.pages[self.nowPage].exit()

    def changePage(self, name):
        if name in self.pages:
            self.env.touch_handler.clear()
            self.pages[self.nowPage].exit()
            self.nowPage = name
            self.pages[name].init()
            self.update_async()
        else:
            raise ValueError("The specified page does not exist!")

    def infoHandler(self):
        pass

    def warnHandler(self):
        pass

    def errorHandler(self):
        pass


class PaperTheme(PaperBasis):
    pass


class PaperApp(PaperBasis):
    pass
