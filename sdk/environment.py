import os
import threading
import time

from PIL import Image, ImageTk, ImageFont, ImageDraw

from sdk import logger
from sdk import touchpad
from sdk import graphics
from sdk.graphics import element_lib
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

    def SIM_touch(self, x, y, ICNT_Dev: touchpad.TouchRecoder, ICNT_Old: touchpad.TouchRecoder):
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

    def clickReleaseHandler(self, event):
        if self.lastX == event.x and self.lastY == event.y:
            print("点击：(%d, %d)" % (event.x, event.y)) # 点击事件
            self.SIM_touch(None, None, self.touch_recoder_new, self.touch_recoder_old) # 触摸终止
            self.env.touch_handler.handle(self.touch_recoder_new, self.touch_recoder_old)

        else:
            print("滑动：(%d, %d) -> (%d, %d)" % (self.lastX, self.lastY, event.x, event.y)) # 滑动事件
            self.SIM_touch(event.x, event.y, self.touch_recoder_new, self.touch_recoder_old)
            self.env.touch_handler.handle(self.touch_recoder_new, self.touch_recoder_old)
            
            self.SIM_touch(None, None, self.touch_recoder_new, self.touch_recoder_old) # 触摸终止
            self.env.touch_handler.handle(self.touch_recoder_new, self.touch_recoder_old)


    def clickPressHandler(self, event):
        self.lastX = event.x
        self.lastY = event.y
        self.SIM_touch(event.x, event.y, self.touch_recoder_new, self.touch_recoder_old)
        self.env.touch_handler.handle(self.touch_recoder_new, self.touch_recoder_old)



    def open(self, env) -> None:

        self.env = env

        self.touch_recoder_new = touchpad.TouchRecoder()  # 触摸
        self.touch_recoder_old = touchpad.TouchRecoder()

        self.window = tkinter.Tk()

        self.window.title('水墨屏模拟器 by xuanzhi33')

        self.window.geometry('390x178')

        self.window.configure(background="black")

        pilImage = Image.new("RGB", (296, 128), "white")
        tkImage = ImageTk.PhotoImage(image=pilImage)

        self.spaceLable = tkinter.Label(self.window,background="black")
        self.spaceLable.pack()

        self.display = tkinter.Label(self.window, image=tkImage,relief=tkinter.GROOVE)
        self.display.bind("<ButtonPress-1>", self.clickPressHandler)
        self.display.bind("<ButtonRelease-1>", self.clickReleaseHandler)
        self.display.pack()
        
        self.window.mainloop()

    def updateImage(self, PILImg):
        tkImage = ImageTk.PhotoImage(image=PILImg)
        self.display.configure(image=tkImage)
        self.display.image = tkImage


class EpdController:
    """
    用这个类来显示图片可能会被阻塞（当多个线程尝试访问屏幕时）
    """

    def __init__(self,
                 simulator: Simulator,
                 logger_: logger.Logger,
                 lock: threading.RLock,
                 popup,
                 init=True,
                 auto_sleep_time=30,
                 refresh_time=3600,
                 refresh_interval=20):
        super().__init__()

        self.simulator = simulator

        self.popup = popup
        self.last_update = time.time()
        self.partial_time = 0
        self.refresh_time = refresh_time
        self.refresh_interval = refresh_interval
        self.__auto_sleep_time = auto_sleep_time
        self.logger_ = logger_
        self.lock = lock
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
        self.lock.acquire(timeout=timeout)
        # image.show()

        self.simulator.updateImage(image)

        self.lock.release()
        self.last_update = time.time()
        self.partial_time = 0

    def display_Base(self, image, timeout=-1):
        self.lock.acquire()
        # image.show()

        self.simulator.updateImage(image)

        self.lock.release()
        self.last_update = time.time()
        self.partial_time = 0

    def display_Partial(self, image, timeout=-1):
        self.lock.acquire(timeout=timeout)
        # image.show()

        self.simulator.updateImage(image)

        self.lock.release()
        self.last_update = time.time()
        self.partial_time += 1

    def display_Auto(self, image, timeout=-1):
        self.lock.acquire(timeout=timeout)
        if (time.time() - self.last_update > self.refresh_time) or (self.partial_time >= self.refresh_interval):
            self.display_Base(image, timeout)
        else:
            self.display_Partial_Wait(image, timeout)
        self.lock.release()

    def display_Partial_Wait(self, image, timeout=-1):
        self.lock.acquire(timeout=timeout)
        # image.show()

        self.simulator.updateImage(image)

        self.lock.release()
        self.last_update = time.time()
        self.partial_time += 1

    def clear(self, color, timeout=-1):
        self.lock.acquire(timeout=timeout)
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
        pass
        if self.upside_down:
            image = image.transpose(Image.ROTATE_180)
        popup_img = self.popup.build()
        if popup_img:
            image.paste(popup_img, (60, 25))
        return image

    def acquire(self, timeout=-1):
        return self.lock.acquire(timeout=timeout)

    def release(self):
        return self.lock.release()

    def set_upside_down(self, value: bool):
        self.upside_down = value

    @staticmethod
    def IsBusy():
        return False


class TouchDriver:
    def __init__(self, logger_touch: logger):
        self.logger_touch = logger_touch

    def ICNT_Reset(self):
        self.logger_touch.debug("触摸屏重置")

    def ICNT_ReadVersion(self):
        self.logger_touch.debug("触摸屏的版本为:" + "调试器模式")

    def ICNT_Init(self):
        self.logger_touch.debug("触摸屏初始化")

    @staticmethod
    def ICNT_Scan(ICNT_Dev: touchpad.TouchRecoder, ICNT_Old: touchpad.TouchRecoder):
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
        self.font16 = ImageFont.truetype(
            "resources/fonts/STHeiti_Light.ttc", 16)
        self.font13 = ImageFont.truetype(
            "resources/fonts/STHeiti_Light.ttc", 13)
        self.cho_imgText = graphics.ImgText((7, 24), (35, 162), self.font13)
        self.pro_imgText = graphics.ImgText((7, 24), (53, 162), self.font13)
        file1 = open(Path("resources/images/prompt.jpg"), "rb")
        self.prompt_background = Image.open(file1)
        file2 = open(Path("resources/images/choice.jpg"), "rb")
        self.choice_background = Image.open(file2)

    def prompt(self, title, content, image_18px=None):
        if self.show_now:
            self.show_list.put(self.show_now)
        self.show_now = [image_18px, title, content]
        self.env.touch_handler.add_king_clicked((218, 236, 25, 43), self.close_prompt)
        self.env.paper.update_anyway()

    def close_prompt(self):
        if self.show_now:
            if len(self.show_now) == 3:
                if self.show_list.empty():
                    self.show_now = None
                else:
                    self.show_now = self.show_list.get(timeout=1)
                self.env.paper.update_anyway()

    def choice(self) -> bool:
        pass

    def click_choice_a(self):
        pass

    def click_choice_b(self):
        pass

    def close_choice(self):
        pass

    def build(self):
        if self.show_now:
            if len(self.show_now) == 3:
                new_image = self.prompt_background.copy()
                if self.show_now[0]:
                    new_image.paste(self.show_now[0], (3, 3))
                else:
                    new_image.paste(self.env.Images.none18px, (3, 3))
                draw = ImageDraw.Draw(new_image)
                draw.text((26, 5), self.show_now[1], fill="black", font=self.font16)
                self.pro_imgText.draw_text(self.show_now[2], draw)
                return new_image

            elif len(self.show_now) == 6:
                pass
        else:
            return None


class Env:
    def __init__(self, configs, logger_env: logger.Logger, simulator):

        self.simulator = simulator

        self.logger_env = logger_env
        self.epd_lock = threading.RLock()
        self.popup = Popup(self)
        self.epd_driver = EpdController(self.simulator,
                                        self.logger_env,
                                        self.epd_lock,
                                        self.popup,
                                        True,
                                        auto_sleep_time=configs["auto_sleep_time"],
                                        refresh_time=configs["refresh_time"],
                                        refresh_interval=configs["refresh_interval"])
        if self.epd_driver.IsBusy():
            self.logger_env.error("The screen is busy!")
            raise RuntimeError("The screen is busy!")

        self.pool = threadpool_mini.ThreadPool(configs["threadpool_size"], handler=logger_env.warn)
        self.pool.start()

        self.touch_handler = touchpad.TouchHandler(self)
        self.touchpad_driver = TouchDriver(self.logger_env)
        self.touchpad_driver.ICNT_Init()
        self.paper = None
        # self.paper_old = None
        self.papers = LifoQueue(maxsize=5)
        self.plugins = None
        self.apps = None
        self.inited = False
        self.theme = None

    class Images:
        none18px = Image.open("resources/images/None18px.jpg")
        none20px = Image.open("resources/images/None20px.jpg")

    class Fonts:    # todo: 添加一些常用字体
        pass

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

    def changePaper(self, paper, exit_paper=False):
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

    def openApp(self, appName, exit_paper=False):
        if not self.inited:
            return
        if appName in self.apps:
            if self.apps[appName][2] is None:
                self.apps[appName][2] = self.apps[appName][0].build(self)
            self.changePaper(self.apps[appName][2], exit_paper=exit_paper)
        else:
            raise ModuleNotFoundError

    def backHome(self, exit_paper=False):
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

    def notice(self, icon: Image.Image, text: str):
        pass

    def reboot(self):
        self.logger_env.info("reboot")
        os.system("sudo reboot")

    def poweroff(self):
        self.logger_env.info("poweroff")
        os.system("sudo poweroff")