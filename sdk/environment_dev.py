import threading
import time

from PIL import Image

from sdk import logger
from sdk import touchpad
from sdk import graphics
from sdk import timing_task
from sdk import threadpool_mini


class EpdController:
    """
    用这个类来显示图片可能会被阻塞（当多个线程尝试访问屏幕时）
    """

    def __init__(self,
                 logger_: logger.Logger,
                 lock: threading.RLock,
                 init=True,
                 auto_sleep_time=30,
                 refresh_time=3600,
                 refresh_interval=20):
        super().__init__()
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
        image.show()
        self.lock.release()
        self.last_update = time.time()
        self.partial_time = 0

    def display_Base(self, image, timeout=-1):
        self.lock.acquire()
        image.show()
        self.lock.release()
        self.last_update = time.time()
        self.partial_time = 0

    def display_Partial(self, image, timeout=-1):
        self.lock.acquire(timeout=timeout)
        image.show()
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
        image.show()
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

    def get_buffer(self, image: Image.Image):
        if self.upside_down:
            return image.transpose(Image.ROTATE_180)
        else:
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


class Env:
    def __init__(self, configs, logger_env: logger.Logger):
        self.logger_env = logger_env
        self.epd_lock = threading.RLock()
        self.epd_driver = EpdController(self.logger_env,
                                        self.epd_lock, True,
                                        auto_sleep_time=configs["auto_sleep_time"],
                                        refresh_time=configs["refresh_time"],
                                        refresh_interval=configs["refresh_interval"])
        if self.epd_driver.IsBusy():
            self.logger_env.error("The screen is busy!")
            raise RuntimeError("The screen is busy!")

        self.pool = threadpool_mini.ThreadPool(configs["threadpool_size"])
        self.pool.start()

        self.touch_handler = touchpad.TouchHandler(self)
        self.touchpad_driver = TouchDriver(self.logger_env)
        self.touchpad_driver.ICNT_Init()
