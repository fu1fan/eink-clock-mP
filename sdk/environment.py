import os
import threading
import time

from PIL import Image, ImageTk, ImageFont, ImageDraw

from sdk import logger
from sdk import touchpad
from sdk import graphics
from sdk import timing_task
from sdk import threadpool_mini
from queue import LifoQueue
from pathlib import Path

import tkinter


class Simulator:
    def __init__(self):
        self.touch_recoder_new = None
        self.touch_recoder_old = None
        self.lastX = None
        self.lastY = None
        self.env = None
        self.window = None
        self.space_label = None
        self.display = None

    @staticmethod
    def sim_touch(x, y, ICNT_Dev: touchpad.TouchRecoder, ICNT_Old: touchpad.TouchRecoder):
        ICNT_Old.Touch = ICNT_Dev.Touch
        ICNT_Old.TouchGestureId = ICNT_Dev.TouchGestureId
        ICNT_Old.TouchCount = ICNT_Dev.TouchCount
        ICNT_Old.TouchEvenId = ICNT_Dev.TouchEvenId
        ICNT_Old.X = ICNT_Dev.X.copy()
        ICNT_Old.Y = ICNT_Dev.Y.copy()
        ICNT_Old.P = ICNT_Dev.P.copy()
        if x is None or y is None:
            ICNT_Dev.Touch = 0
        else:
            ICNT_Dev.Touch = 1
            ICNT_Dev.X[0] = x
            ICNT_Dev.Y[0] = y

    def click_release_handler(self, event):
        if self.lastX == event.x and self.lastY == event.y:
            print("点击：(%d, %d)" % (event.x, event.y))  # 点击事件
            self.sim_touch(None, None, self.touch_recoder_new, self.touch_recoder_old)  # 触摸终止
            self.env.touch_handler.handle(self.touch_recoder_new, self.touch_recoder_old)

        else:
            print("滑动：(%d, %d) -> (%d, %d)" % (self.lastX, self.lastY, event.x, event.y))  # 滑动事件
            self.sim_touch(event.x, event.y, self.touch_recoder_new, self.touch_recoder_old)
            self.env.touch_handler.handle(self.touch_recoder_new, self.touch_recoder_old)

            self.sim_touch(None, None, self.touch_recoder_new, self.touch_recoder_old)  # 触摸终止
            self.env.touch_handler.handle(self.touch_recoder_new, self.touch_recoder_old)

    def click_press_handler(self, event):
        self.lastX = event.x
        self.lastY = event.y
        self.sim_touch(event.x, event.y, self.touch_recoder_new, self.touch_recoder_old)
        self.env.touch_handler.handle(self.touch_recoder_new, self.touch_recoder_old)

    def open(self, env) -> None:

        self.env = env

        self.touch_recoder_new = touchpad.TouchRecoder()  # 触摸
        self.touch_recoder_old = touchpad.TouchRecoder()

        self.window = tkinter.Tk()

        self.window.title('水墨屏模拟器 by xuanzhi33')

        self.window.geometry('390x178')

        self.window.configure(background="black")

        pil_image = Image.new("RGBA", (296, 128), "white")
        tk_image = ImageTk.PhotoImage(image=pil_image)

        self.space_label = tkinter.Label(self.window, background="black")
        self.space_label.pack()

        self.display = tkinter.Label(self.window, image=tk_image, relief=tkinter.GROOVE)
        self.display.bind("<ButtonPress-1>", self.click_press_handler)
        self.display.bind("<ButtonRelease-1>", self.click_release_handler)
        self.display.pack()

        self.window.mainloop()

    def update_image(self, PILImg):
        tk_image = ImageTk.PhotoImage(image=PILImg)
        self.display.configure(image=tk_image)
        self.display.image = tk_image


class EpdController:    # TODO:此部分改动可能导导致继承关系错误，合并时必须手动处理！！！切记切记
    """
    用这个类来显示图片可能会被阻塞（当多个线程尝试访问屏幕时）
    """

    def __init__(self, env, init=True, auto_sleep_time=30, refresh_time=3600, refresh_interval=20):
        super().__init__()
        self.env = env
        self.simulator = env.simulator
        self.last_update = time.time()
        self.partial_time = 0
        self.refresh_time = refresh_time
        self.refresh_interval = refresh_interval
        self.__auto_sleep_time = auto_sleep_time
        self.logger_ = self.env.logger_env
        self.lock = threading.RLock()
        self.tk = timing_task.TimingTask(auto_sleep_time, self.controller)
        self.sleep_status = threading.Lock()  # 上锁表示休眠
        self.upside_down = False
        if auto_sleep_time > 0:
            self.tk.start()
        if init:
            self.init()

    def __del__(self):
        self.exit()

    @property
    def auto_sleep_time(self):
        return self.__auto_sleep_time

    def set_auto_sleep_time(self, auto_sleep_time):
        self.tk.cycle = auto_sleep_time
        self.__auto_sleep_time = auto_sleep_time
        if auto_sleep_time > 0:
            self.tk.start()
        else:
            self.tk.stop()

    def controller(self):  # 自动休眠
        if time.time() - self.last_update >= self.auto_sleep_time:
            if not self.lock.acquire(blocking=False):
                return
            self.sleep()
            self.lock.release()

    def init(self):
        try:
            self.sleep_status.release()
        except RuntimeError:
            pass
        self.logger_.debug("屏幕初始化")

    def display(self, image: Image.Image, timeout=-1):
        if not self.lock.acquire(timeout=timeout):
            raise TimeoutError

        self.simulator.update_image(image)

        self.lock.release()
        self.last_update = time.time()
        self.partial_time = 0

    def display_base(self, image, timeout=-1):
        if not self.lock.acquire(timeout=timeout):
            raise TimeoutError

        self.simulator.update_image(image)

        self.lock.release()
        self.last_update = time.time()
        self.partial_time = 0

    def display_partial(self, image, timeout=-1):
        if not self.lock.acquire(timeout=timeout):
            raise TimeoutError

        self.simulator.update_image(image)

        self.lock.release()
        self.last_update = time.time()
        self.partial_time += 1

    def display_auto(self, image, timeout=-1):
        if not self.lock.acquire(timeout=timeout):
            raise TimeoutError
        if (time.time() - self.last_update > self.refresh_time) or (self.partial_time >= self.refresh_interval):
            self.display_base(image, timeout)
        else:
            self.display_partial_wait(image, timeout)
        self.lock.release()

    def display_partial_wait(self, image, timeout=-1):
        if not self.lock.acquire(timeout=timeout):
            raise TimeoutError

        self.simulator.update_image(image)

        self.lock.release()
        self.last_update = time.time()
        self.partial_time += 1

    def clear(self, color, timeout=-1):
        if not self.lock.acquire(timeout=timeout):
            raise TimeoutError
        pass
        self.lock.release()
        self.last_update = time.time()
        self.partial_time = 0

    def exit(self):
        self.tk.stop()
        self.sleep()

    def sleep(self):
        if self.sleep_status.acquire(blocking=False):
            self.logger_.debug("屏幕休眠")

    def render(self, image: Image.Image):
        if self.upside_down:
            image = image.transpose(Image.ROTATE_180)
        popup_img = self.env.popup.build()
        if popup_img:
            image.paste(popup_img, (60, 25))
        self.env.system_event.render(image)
        return image

    def acquire(self, timeout=-1):
        return self.lock.acquire(timeout=timeout)

    def release(self):
        return self.lock.release()

    def set_upside_down(self, value: bool):
        self.upside_down = value

    @staticmethod
    def is_busy():
        return False


class TouchDriver:
    def __init__(self, logger_touch: logger):
        self.logger_touch = logger_touch

    def icnt_reset(self):
        self.logger_touch.debug("触摸屏重置")

    def icnt_read_version(self):
        self.logger_touch.debug("触摸屏的版本为:" + "调试器模式")

    def icnt_init(self):
        self.logger_touch.debug("触摸屏初始化")

    @staticmethod
    def icnt_scan(ICNT_Dev: touchpad.TouchRecoder, ICNT_Old: touchpad.TouchRecoder):
        try:
            x = int(input("x:"))
            y = int(input("y:"))
        except ValueError:
            x = None
            y = None
        ICNT_Old.Touch = ICNT_Dev.Touch
        ICNT_Old.TouchGestureId = ICNT_Dev.TouchGestureId
        ICNT_Old.TouchCount = ICNT_Dev.TouchCount
        ICNT_Old.TouchEvenId = ICNT_Dev.TouchEvenId
        ICNT_Old.X = ICNT_Dev.X.copy()
        ICNT_Old.Y = ICNT_Dev.Y.copy()
        ICNT_Old.P = ICNT_Dev.P.copy()
        if x is None or y is None:
            ICNT_Dev.Touch = 0
        else:
            ICNT_Dev.Touch = 1
            ICNT_Dev.X[0] = x
            ICNT_Dev.Y[0] = y


class Popup(graphics.BasicGraphicControl):
    def __init__(self, env):
        self.env = env
        # self.prompts = LifoQueue()
        # self.prompt_now = None  # [image_20px, title, text]
        # self.choices = LifoQueue()
        # self.choice_now = None  # [image_20px, title, text, func1, func2, func_cancle]
        self.show_now = None
        self.show_list = LifoQueue()
        self.font16 = self.env.fonts.get_heiti(16)
        self.font13 = self.env.fonts.get_heiti(13)
        self.cho_imgText = graphics.ImgText((35, 162), self.font13)
        self.pro_imgText = graphics.ImgText((53, 162), self.font13)
        self.prompt_background = Image.open(Path("resources/images/prompt.jpg"))
        self.choice_background = Image.open(Path("resources/images/choice.jpg"))

    @property
    def active(self):
        if self.show_now:
            return True
        else:
            return False

    def prompt(self, title, content, image_18px=None):
        if self.show_now:
            self.show_list.put(self.show_now)
        self.show_now = [image_18px, title, content]
        # self.env.touch_handler.add_king_clicked((218, 236, 25, 43), self.close_prompt)
        self.env.paper.update_anyway()

    def close(self):
        if self.show_now:
            if self.show_list.empty():
                self.show_now = None
            else:
                self.show_now = self.show_list.get(timeout=1)
            self.env.paper.update_anyway()

    def choice(self, title, content, func1, fun2, funcCancle, bt1="否", bt2="是", image_18px=None):
        if self.show_now:
            self.show_list.put(self.show_now)
        self.show_now = [image_18px, title, content, func1, fun2, funcCancle, bt1, bt2]
        self.env.paper.update_anyway()

    def choice_handler(self, func):
        self.close()
        func()

    def build(self):
        if self.show_now:
            new_image = None
            if len(self.show_now) == 3:
                new_image = self.prompt_background.copy()
                if self.show_now[0]:
                    new_image.paste(self.show_now[0], (3, 3))
                else:
                    new_image.paste(self.env.Images.none18px, (3, 3))
                draw = ImageDraw.Draw(new_image)
                draw.text((26, 5), self.show_now[1], fill="black", font=self.font16)
                self.pro_imgText.draw_text((7, 24), self.show_now[2], draw)
                self.env.touch_handler.set_system_clicked(
                    [
                        [(218, 236, 25, 43), self.close, [], {}, False]
                    ]
                )
            elif len(self.show_now) == 8:
                new_image = self.choice_background.copy()
                if self.show_now[0]:
                    new_image.paste(self.show_now[0], (3, 3))
                else:
                    new_image.paste(self.env.Images.none18px, (3, 3))
                draw = ImageDraw.Draw(new_image)
                draw.text((26, 5), self.show_now[1], fill="black", font=self.font16)
                draw.text((6, 61), self.show_now[6], fill="black", font=self.font13)
                draw.text((92, 61), self.show_now[7], fill="black", font=self.font13)
                self.cho_imgText.draw_text((7, 24), self.show_now[2], draw)
                self.env.touch_handler.set_system_clicked(
                    [
                        [(218, 236, 25, 43), self.choice_handler, [self.show_now[5]], {}, False],
                        [(65, 150, 90, 100), self.choice_handler, [self.show_now[3]], {}, False],
                        [(150, 236, 90, 100), self.choice_handler, [self.show_now[4]], {}, False]
                    ]
                )

            return new_image
        else:
            return None


class SystemEvent(Popup):
    def __init__(self, env):
        super().__init__(env)

    def render(self, image):
        image_new = Image.new("RGBA", (296, 128), (255, 255, 255, 0))
        system_popup = self.build()
        if system_popup:
            image_new.paste(system_popup, (60, 25))

        r, g, b, a = image_new.split()
        image.paste(image_new, mask=a)  # 在无需变化时不粘贴


class FasterFonts:
    def __init__(self):
        self.font_list = []
        for _ in range(128):
            self.font_list.append(None)

    class SizeOutOfRange(Exception):
        pass

    def get_heiti(self, size: int):
        size -= 1
        if 0 <= size < 127:
            if not self.font_list[size]:
                self.font_list[size] = ImageFont.truetype("resources/fonts/STHeiti_Light.ttc", size)
            return self.font_list[size]
        else:
            raise self.SizeOutOfRange


class Env:
    def __init__(self, configs, logger_env: logger.Logger, simulator):
        # TODO:优化启动顺序
        self.simulator = simulator

        self.logger_env = logger_env

        self.fonts = FasterFonts()
        self.paper = None
        # self.paper_old = None
        self.papers = LifoQueue(maxsize=5)
        self.plugins = None
        self.apps = None
        self.inited = False
        self.theme = None
        self.popup = Popup(self)
        self.system_event = SystemEvent(self)
        self.pool = threadpool_mini.ThreadPool(configs["threadpool_size"], handler=logger_env.warn)
        self.pool.start()

        self.touch_handler = touchpad.TouchHandler(self)
        self.touchpad_driver = TouchDriver(self.logger_env)
        self.touchpad_driver.icnt_init()
        self.epd_driver = EpdController(self, True, auto_sleep_time=configs["auto_sleep_time"],
                                        refresh_time=configs["refresh_time"],
                                        refresh_interval=configs["refresh_interval"])
        if self.epd_driver.is_busy():
            self.logger_env.error("The screen is busy!")
            raise RuntimeError("The screen is busy!")

    class Images:
        none1px = Image.open("resources/images/None1px.jpg")
        none18px = Image.open("resources/images/None18px.jpg")
        none20px = Image.open("resources/images/None20px.jpg")

    def init(self, paper, plugins, apps):
        if self.inited:
            return
        self.inited = True
        self.theme = paper
        self.paper = paper
        self.papers.put(self.paper)
        self.plugins = plugins
        self.apps = apps
        self.paper.init()

    def change_paper(self, paper, exit_paper=False):
        if not self.inited:
            return
        self.touch_handler.clear()
        if exit_paper:
            self.paper.exit()
        else:
            self.paper.pause()  # pause()能暂停页面
            if self.papers.full():
                self.paper.get()
            self.papers.put(self.paper, timeout=1)
        # self.paper_old, self.paper = self.paper, paper
        self.paper = paper
        if paper.inited:
            self.paper.recover()
        else:
            self.paper.init()

    def open_app(self, appName, exit_paper=False):
        if not self.inited:
            return
        if appName in self.apps:
            if self.apps[appName][2] is None:
                self.apps[appName][2] = self.apps[appName][0].build(self)
            self.change_paper(self.apps[appName][2], exit_paper=exit_paper)
        else:
            raise ModuleNotFoundError

    def back_home(self, exit_paper=False):
        if not self.inited:
            return
        self.touch_handler.clear()
        if exit_paper:
            self.paper.exit()
        else:
            self.paper.pause()  # pause()能暂停页面
        self.papers.queue.clear()
        self.theme.nowPage = "mainPage"
        self.paper = self.theme
        if self.paper.inited:
            self.paper.recover()
        else:
            self.paper.init()
        # self.paper_old, self.paper = self.paper, paper

    def back(self, exit_paper=False):
        if not self.inited:
            return
        if not self.paper.back():
            self.touch_handler.clear()
            if exit_paper:
                self.paper.exit()
            else:
                self.paper.pause()  # pause()能暂停页面
            # self.paper_old, self.paper = self.paper, paper
            self.paper = self.papers.get(timeout=1)
            if self.paper.inited:
                self.paper.recover()
            else:
                self.paper.init()

    def reboot(self):
        self.logger_env.info("reboot")
        os.system("sudo reboot")

    def poweroff(self):
        self.logger_env.info("poweroff")
        os.system("sudo poweroff")
