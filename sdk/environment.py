import os
import threading
import time

from PIL import Image, ImageFont, ImageDraw

from sdk import logger, icnt86, epd2in9_V2
from sdk import touchpad
from sdk import graphics
from sdk import timing_task
from sdk import threadpool_mini
from queue import LifoQueue
from pathlib import Path

config = icnt86.config


class EpdController(epd2in9_V2.Epd2in9V2):
    """
    用这个类来显示图片可能会被阻塞（当多个线程尝试访问屏幕时）
    """

    def __init__(self, env, init=True, auto_sleep_time=30, refresh_time=3600, refresh_interval=20):
        super().__init__()
        self.env = env
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
        super().init()
        try:
            self.sleep_status.release()
        except RuntimeError:
            pass
        self.logger_.debug("屏幕初始化")

    def display(self, image, timeout=-1):
        if not self.lock.acquire(timeout=timeout):
            raise TimeoutError
        super().display(image)
        self.lock.release()
        self.last_update = time.time()
        self.partial_time = 0

    def display_base(self, image, timeout=-1):
        if not self.lock.acquire(timeout=timeout):
            raise TimeoutError
        super().display_base(image)
        self.lock.release()
        self.last_update = time.time()
        self.partial_time = 0

    def display_partial(self, image, timeout=-1):
        if not self.lock.acquire(timeout=timeout):
            raise TimeoutError
        super().display_partial(image)
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
        super().display_partial_wait(image)
        self.lock.release()
        self.last_update = time.time()
        self.partial_time += 1

    def clear(self, color, timeout=-1):
        if not self.lock.acquire(timeout=timeout):
            raise TimeoutError
        super().clear(color)
        self.lock.release()
        self.last_update = time.time()
        self.partial_time = 0

    def exit(self):
        self.tk.stop()
        self.sleep()
        super().exit()

    def sleep(self):
        if self.sleep_status.acquire(blocking=False):
            super().sleep()
            self.logger_.debug("屏幕休眠")

    def render(self, image: Image.Image):
        if self.upside_down:
            image = image.transpose(Image.ROTATE_180)
        popup_img = self.env.popup.build()
        if popup_img:
            image.paste(popup_img, (60, 25))
        self.env.system_event.render(image)
        return super().get_buffer(image)

    def acquire(self, timeout=-1):
        return self.lock.acquire(timeout=timeout)

    def release(self):
        return self.lock.release()

    def set_upside_down(self, value: bool):
        self.upside_down = value


class TouchDriver(icnt86.ICNT86):
    def __init__(self, logger_touch: logger):
        super().__init__()
        self.logger_touch = logger_touch

    def icnt_reset(self):
        super().icnt_reset()
        self.logger_touch.debug("触摸屏重置")

    def icnt_read_version(self):
        buf = self.icnt_read(0x000a, 4)
        self.logger_touch.debug("触摸屏的版本为:" + str(buf))

    def icnt_init(self):
        super().icnt_init()
        self.logger_touch.debug("触摸屏初始化")

    def icnt_scan(self, ICNT_Dev: touchpad.TouchRecoder, ICNT_Old: touchpad.TouchRecoder):
        mask = 0x00

        ICNT_Old.Touch = ICNT_Dev.Touch
        ICNT_Old.TouchGestureId = ICNT_Dev.TouchGestureId
        ICNT_Old.TouchCount = ICNT_Dev.TouchCount
        ICNT_Old.TouchEvenId = ICNT_Dev.TouchEvenId
        ICNT_Old.X = ICNT_Dev.X.copy()
        ICNT_Old.Y = ICNT_Dev.Y.copy()
        ICNT_Old.P = ICNT_Dev.P.copy()

        n = None
        for _ in range(100):
            n = self.digital_read(self.INT)
            if n == 0:
                break
            time.sleep(0.001)

        if n == 0:  # 检测屏幕是否被点击，不是每次都能扫描出来
            ICNT_Dev.Touch = 1
            buf = self.icnt_read(0x1001, 1)

            if buf[0] == 0x00:
                self.icnt_write(0x1001, mask)
                config.delay_ms(1)
                self.logger_touch.warn("touchpad buffers status is 0!")
                return
            else:
                ICNT_Dev.TouchCount = buf[0]

                if ICNT_Dev.TouchCount > 5 or ICNT_Dev.TouchCount < 1:
                    self.icnt_write(0x1001, mask)
                    ICNT_Dev.TouchCount = 0
                    self.logger_touch.warn("TouchCount number is wrong!")
                    return

                buf = self.icnt_read(0x1002, ICNT_Dev.TouchCount * 7)
                self.icnt_write(0x1001, mask)

                for i in range(0, ICNT_Dev.TouchCount, 1):
                    ICNT_Dev.TouchEvenId[i] = buf[6 + 7 * i]
                    ICNT_Dev.X[i] = 295 - ((buf[2 + 7 * i] << 8) + buf[1 + 7 * i])
                    ICNT_Dev.Y[i] = 127 - ((buf[4 + 7 * i] << 8) + buf[3 + 7 * i])
                    ICNT_Dev.P[i] = buf[5 + 7 * i]

                return
        else:
            ICNT_Dev.Touch = 0
            return


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
        self.left_img = Image.open("resources/images/back_left.png").convert("RGBA")
        self.left_img_alpha = self.left_img.split()[3]
        self.right_img = Image.open("resources/images/back_right.png").convert("RGBA")
        self.right_img_alpha = self.right_img.split()[3]
        self.bar_img = Image.open("resources/images/home_bar.png").convert("RGBA")
        self.bar_img_alpha = self.bar_img.split()[3]
        self.left_showed = False
        self.right_showed = False
        self.home_bar_active = False

    def back_show_left(self):
        if not self.left_showed:
            self.left_showed = True
            self.env.paper.update_anyway()

    def back_hide_left(self, go_back):
        if self.left_showed:
            if go_back:
                self.left_showed = False
                if self.env.papers.empty():
                    self.env.paper.update_anyway()
            else:
                self.left_showed = False
                self.env.paper.update_anyway()

    def back_show_right(self):
        if not self.right_showed:
            self.right_showed = True
            self.env.paper.update_anyway()

    def back_hide_right(self, go_back):
        if self.right_showed:
            if go_back:
                self.right_showed = False
                if self.env.papers.empty():
                    self.env.paper.update_anyway()
            else:
                self.right_showed = False
                self.env.paper.update_anyway()

    def home_ctrl(self):
        if self.home_bar_active:
            self.home_bar_active = False
            self.env.back_home()
        else:
            self.home_bar_active = True
            self.env.paper.update_anyway()
            time.sleep(3)
            if self.home_bar_active:
                self.home_bar_active = False
                self.env.paper.update_anyway()

    def render(self, image):
        image_new = Image.new("RGBA", (296, 128), (255, 255, 255, 0))
        system_popup = self.build()
        if system_popup:
            image_new.paste(system_popup, (60, 25))
        if self.left_showed:
            image_new.paste(self.left_img, mask=self.left_img_alpha)
        if self.right_showed:
            image_new.paste(self.right_img, mask=self.right_img_alpha)
        if self.home_bar_active:
            image_new.paste(self.bar_img, mask=self.bar_img_alpha)
        a = image_new.split()[3]
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
    def __init__(self, configs, logger_env: logger.Logger):
        # TODO:优化启动顺序
        self.logger_env = logger_env
        self.epd_lock = threading.RLock()
        self.epd_driver = EpdController(self,
                                        True,
                                        configs["auto_sleep_time"],
                                        configs["refresh_time"],
                                        configs["refresh_interval"])
        if self.epd_driver.is_busy():
            self.logger_env.error("The screen is busy!")
            raise RuntimeError("The screen is busy!")

        self.fonts = FasterFonts()
        self.paper = None
        # self.paper_old = None
        self.papers = LifoQueue()
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
        self.plugins = plugins
        self.apps = apps
        self.paper.init()

    def change_paper(self, paper, exit_paper=False, to_stack=True):
        if not self.inited:
            return
        self.touch_handler.clear()
        if exit_paper:
            self.paper.exit()
        else:
            self.paper.pause()  # pause()能暂停页面
            if to_stack:
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
        if not (self.paper.back() or self.papers.empty()):
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
