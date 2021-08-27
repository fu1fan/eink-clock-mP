import abc
import threading
import traceback

from PIL import Image, ImageDraw

from queue import LifoQueue


class BasicGraphicControl(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def build(self) -> Image.Image:
        pass


class Paper(BasicGraphicControl):
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
        b_image = self.epd.render(image)
        self.epd.display_base(b_image)  # 是这样的吗？？？迷人的驱动

    def display_partial(self, image: Image):
        b_image = self.epd.render(image)
        self.epd.display_partial_wait(b_image)

    def display_auto(self, image: Image):
        b_image = self.epd.render(image)
        self.epd.display_auto(b_image)

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

    def back(self, refresh=False):
        return False

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
        self.env = paper.env
        self.name = name
        self.inited = False

    def add_element(self, element):
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
        self.pages = {"mainPage": Page(self, "mainPage")}
        # TODO:为Handler页面添加内容
        self.nowPage = "mainPage"
        # self.touch_handler = env.touch_handler
        self.env = env
        self.back_stack = LifoQueue()

    def exit(self):
        for page in self.pages.values():
            page.exit()
        self.back_stack.queue.clear()
        super().exit()

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

    def add_page(self, name: str, page=None):
        if page is None:
            page = Page(self, name)
        self.pages[name] = page

    def add_element(self, element, target: str = "mainPage"):
        self.pages[target].append(element)
        element.page = self.pages[target]
        if self.active:
            element.init()

    def change_page(self, name, refresh=None, to_stack=False):
        if name in self.pages.keys():
            if name == self.nowPage:
                return
            self.env.touch_handler.clear()
            self.pages[self.nowPage].pause()
            if to_stack:
                self.back_stack.put(self.nowPage)
            self.nowPage = name
            if self.pages[name].inited:
                self.pages[name].recover()
            else:
                self.pages[name].init()
            self.update_anyway(refresh)
        else:
            raise ValueError("The specified page does not exist!")

    def back(self, refresh=False) -> bool:
        if self.back_stack.empty():
            return False
        else:
            operation = self.back_stack.get(timeout=1)
            if callable(operation):
                if operation():  # 若制定函数有返回，则再次返回（方便程序有自己的返回方法）
                    return self.back(refresh)
                else:
                    return True
            elif isinstance(operation, str):
                self.change_page(operation, refresh)
                return True

    def add_back_operation(self, func):
        self.back_stack.put(func)

    def update_anyway(self, refresh=None):
        if self.update_lock.acquire(blocking=False) and self.active:
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
        self.update_anyway(refresh)

    def pause_update(self):
        return self.update_lock.acquire(blocking=False)

    def recover_update(self, raise_=False, update_now=True):
        try:
            self.update_lock.release()
        except RuntimeError as e:
            if raise_:
                raise e
            else:
                self.env.logger_env.warn(traceback.format_exc())
        if update_now:
            self.env.pool.add_immediately(self.update_anyway)

    def update_async(self, page_name: str, refresh=None):
        self.env.pool.add_immediately(self.update, page_name, refresh)

    def init(self):
        self.pages[self.nowPage].init()
        super().init()

    def clear(self):
        self.pages = {"mainPage": Page(self, "mainPage")}
        self.back_stack.queue.clear()


class Element(BasicGraphicControl):
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

    def pause(self):  # 切换出page时调用
        self.active = False

    def recover(self):  # 切换回page时调用
        self.active = True

    def build(self):  # 当页面刷新时被调用，须返回一个图像
        return self.background


class ImgText:  # 来自CSDN
    def __init__(self, size, font, color="black"):
        self.size = size
        self.width = size[1]
        self.font = font
        self.color = color

    def get_duanluo(self, text):
        txt = Image.new('RGBA', self.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt)
        # 所有文字的段落
        duanluo = ""
        # 宽度总和
        sum_width = 0
        # 几行
        line_count = 1
        # 行高
        line_height = 0
        for char in text:
            width, height = draw.textsize(char, self.font)
            sum_width += width
            if sum_width > self.width:  # 超过预设宽度就修改段落 以及当前行数
                line_count += 1
                sum_width = 0
                duanluo += '\n'
            duanluo += char
            line_height = max(height, line_height)
        if not duanluo.endswith('\n'):
            duanluo += '\n'
        return duanluo, line_height, line_count

    def split_text(self, text):
        # 按规定宽度分组
        max_line_height, total_lines = 0, 0
        all_text = []
        for text in text.split('\n'):
            duanluo, line_height, line_count = self.get_duanluo(text)
            max_line_height = max(line_height, max_line_height)
            total_lines += line_count
            all_text.append((duanluo, line_count))
        line_height = max_line_height
        total_height = total_lines * line_height
        return all_text, total_height, line_height

    def draw_text(self, xy, text, image_draw: ImageDraw.ImageDraw):
        """
        绘图以及文字
        :return:
        """
        # 左上角开始
        # 段落 , 行数, 行高
        x, y = xy[0], xy[0]
        duanluo, note_height, line_height = self.split_text(text)
        for dl, lc in duanluo:
            image_draw.text((x, y), dl, fill=self.color, font=self.font)
            y += line_height * lc
