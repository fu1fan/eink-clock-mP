import threading
import time

from sdk import icnt86
from sdk import epdconfig as config
from sdk import logger
from sdk import threadpool_mini


class TouchRecoder(icnt86.ICNT_Development):
    pass


class TouchDriver(icnt86.INCT86):
    def __init__(self, logger_touch: logger):
        super().__init__()
        self.logger_touch = logger_touch

    def ICNT_Reset(self):
        super().ICNT_Reset()
        self.logger_touch.debug("触摸屏重置")

    def ICNT_ReadVersion(self):
        buf = self.ICNT_Read(0x000a, 4)
        self.logger_touch.debug("触摸屏的版本为:" + str(buf))

    def ICNT_Init(self):
        super().ICNT_Init()
        self.logger_touch.debug("触摸屏初始化")

    def ICNT_Scan(self, ICNT_Dev: TouchRecoder, ICNT_Old: TouchRecoder):
        global n
        mask = 0x00

        ICNT_Old.Touch = ICNT_Dev.Touch
        ICNT_Old.TouchGestureId = ICNT_Dev.TouchGestureId
        ICNT_Old.TouchCount = ICNT_Dev.TouchCount
        ICNT_Old.TouchEvenId = ICNT_Dev.TouchEvenId
        ICNT_Old.X = ICNT_Dev.X.copy()
        ICNT_Old.Y = ICNT_Dev.Y.copy()
        ICNT_Old.P = ICNT_Dev.P.copy()

        for _ in range(100):
            n = self.digital_read(self.INT)
            if n == 0:
                break
            time.sleep(0.001)

        if n == 0:  # 检测屏幕是否被点击，不是每次都能扫描出来
            ICNT_Dev.Touch = 1
            buf = self.ICNT_Read(0x1001, 1)

            if buf[0] == 0x00:
                self.ICNT_Write(0x1001, mask)
                config.delay_ms(1)
                self.logger_touch.warn("touchpad buffers status is 0!")
                return
            else:
                ICNT_Dev.TouchCount = buf[0]

                if ICNT_Dev.TouchCount > 5 or ICNT_Dev.TouchCount < 1:
                    self.ICNT_Write(0x1001, mask)
                    ICNT_Dev.TouchCount = 0
                    self.logger_touch.warn("TouchCount number is wrong!")
                    return

                buf = self.ICNT_Read(0x1002, ICNT_Dev.TouchCount * 7)
                self.ICNT_Write(0x1001, mask)

                for i in range(0, ICNT_Dev.TouchCount, 1):
                    ICNT_Dev.TouchEvenId[i] = buf[6 + 7 * i]
                    ICNT_Dev.X[i] = 295 - ((buf[2 + 7 * i] << 8) + buf[1 + 7 * i])
                    ICNT_Dev.Y[i] = 127 - ((buf[4 + 7 * i] << 8) + buf[3 + 7 * i])
                    ICNT_Dev.P[i] = buf[5 + 7 * i]

                return
        else:
            ICNT_Dev.Touch = 0
            return


class TouchHandler:
    def __init__(self, pool: threadpool_mini.ThreadPool, logger: logger.Logger):
        self.pool = pool
        self.clicked = []  # 当对象被点击并松开后调用指定函数                      ((x1, x2, y1, y2), func, args, kwargs)
        self.touched = []  # 当对象被按下后调用指定函数，直到松开后再次调用另一指定函数 ((x1, x2, y1, y2), func1, func2, args, kwargs)
        self.slide_x = []  # 当屏幕从指定区域被横向滑动后调用指定函数               ((x1, x2, y1, y2), func, args, kwargs)
        self.slide_y = []  # 当屏幕从指定区域被纵向滑动后调用指定函数               ((x1, x2, y1, y2), func, args, kwargs)
        self.data_lock = threading.Lock()
        self.logger_touch = logger
        self.signal_1 = False
        self.signal_2 = False

    def add_clicked(self, area, func, *args, **kwargs):
        """
        添加一个触摸元件
        :param func:
        :param area: (x1, x2, y1, y2)
        :return: None
        """
        if area[0] > area[1] or area[2] > area[3] or area[0] < 0 or area[1] > 296 or area[2] < 0 or area[3] > 128:
            raise ValueError("Area out of range!")
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        self.clicked.append((area, func, args, kwargs, False))
        self.data_lock.release()
        self.signal_1 = False

    def add_touched(self, area, func1, func2, *args, **kwargs): # TODO:添加批量导入
        if area[0] > area[1] or area[2] > area[3] or area[0] < 0 or area[1] > 296 or area[2] < 0 or area[3] > 128:
            raise ValueError("Area out of range!")
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        self.touched.append((area, func1, func2, args, kwargs, False))
        self.signal_1 = False

    def add_slide_x(self, area, func):
        if area[0] > area[1] or area[2] > area[3] or area[0] < 0 or area[1] > 296 or area[2] < 0 or area[3] > 128:
            raise ValueError("Area out of range!")
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        self.slide_x.append((area, func, None))
        self.signal_1 = False

    def add_slide_y(self, area, func):
        if area[0] > area[1] or area[2] > area[3] or area[0] < 0 or area[1] > 296 or area[2] < 0 or area[3] > 128:
            raise ValueError("Area out of range!")
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        self.slide_y.append((area, func, None))
        self.signal_1 = False

    def clear(self):
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        self.clicked = []
        self.touched = []
        self.slide_x = []
        self.slide_y = []
        self.signal_1 = False

    def handle(self, ICNT_Dev: TouchRecoder, ICNT_Old: TouchRecoder):  # 此函数只可在主线程中运行
        while True:
            if not self.signal_1:
                break
            time.sleep(0.1)
        self.signal_2 = True
        if ICNT_Dev.Touch and ICNT_Old.Touch:  # 如果保持一直触摸不变
            if not (ICNT_Dev.X == ICNT_Old.X and ICNT_Dev.Y == ICNT_Old.Y):
                self.logger_touch.debug("触摸位置变化：[%s, %s]" % (ICNT_Dev.X, ICNT_Dev.Y))
                for i in self.touched:  # 扫描touch
                    if i[0][0] <= ICNT_Dev.X <= i[0][1] and i[0][2] <= ICNT_Dev.Y <= i[0][3]:
                        if not i[-1]:
                            self.pool.add(i[1], i[3], i[4])  # 如果被点击，且标记为False，则执行func1
                            i[-1] = True
                    else:
                        if i[-1]:
                            self.pool.add(i[2], i[3], i[4])  # 如果没有被点击，且标记为True，则执行func2
                            i[-1] = False

        elif ICNT_Dev.Touch and (not ICNT_Old.Touch):  # 如果开始触摸
            self.logger_touch.debug("触摸事件开始：[%s, %s]" % (ICNT_Dev.X, ICNT_Dev.Y))
            for i in self.touched:  # 扫描touch
                if i[0][0] <= ICNT_Dev.X <= i[0][1] and i[0][2] <= ICNT_Dev.Y <= i[0][3]:
                    self.pool.add(i[1], i[3], i[4])  # 如果被点击，且标记为False，则执行func1
                    i[-1] = True

            for i in self.clicked:
                if i[0][0] <= ICNT_Dev.X <= i[0][1] and i[0][2] <= ICNT_Dev.Y <= i[0][3]:
                    i[-1] = True

            for i in self.slide_x:
                if i[0][0] <= ICNT_Dev.X <= i[0][1] and i[0][2] <= ICNT_Dev.Y <= i[0][3]:
                    i[-1] = (ICNT_Dev.X, ICNT_Dev.Y)

            for i in self.slide_y:
                if i[0][0] <= ICNT_Dev.X <= i[0][1] and i[0][2] <= ICNT_Dev.Y <= i[0][3]:
                    i[-1] = (ICNT_Dev.X, ICNT_Dev.Y)

        elif (not ICNT_Dev.Touch) and ICNT_Old.Touch:  # 如果停止触摸
            self.logger_touch.debug("触摸事件终止：[%s, %s]" % (ICNT_Dev.X, ICNT_Dev.Y))
            for i in self.touched:
                if i[-1]:
                    self.pool.add(i[2], i[3], i[4])  # 如果没有被点击，且标记为True，则执行func2
                    i[-1] = False

            for i in self.clicked:
                if i[-1]:
                    if i[0][0] <= ICNT_Old.X <= i[0][1] and i[0][2] <= ICNT_Old.Y <= i[0][3]:
                        self.pool.add(i[1], i[2], i[3])
                    i[-1] = False

            for i in self.slide_x:  # ⚠️参数需要经过测试后调整
                if i[-1] is not None:
                    if (abs(ICNT_Dev.Y - i[-1][1]) <= 85) and (abs(ICNT_Dev.X - i[-1][0]) >= 50):
                        self.pool.add(i[1], ICNT_Dev.X - i[-1][0])
                    i[-1] = None

            for i in self.slide_y:
                if i[-1] is not None:
                    if (abs(ICNT_Dev.X - i[-1][0]) <= 50) and (abs(ICNT_Dev.Y - i[-1][1]) >= 40):
                        self.pool.add(i[1], ICNT_Dev.Y - i[-1][1])
                    i[-1] = None

        self.signal_2 = False
