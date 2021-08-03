import threading
import time

from sdk import logger
from sdk import threadpool_mini

class TouchRecoder():
    def __init__(self):
        self.Touch = 0
        self.TouchGestureId = 0
        self.TouchCount = 0

        self.TouchEvenId = [0, 1, 2, 3, 4]
        self.X = [0, 1, 2, 3, 4]
        self.Y = [0, 1, 2, 3, 4]
        self.P = [0, 1, 2, 3, 4]


class TouchDriver():
    def __init__(self, logger_touch: logger):
        self.logger_touch = logger_touch

    def ICNT_Reset(self):
        self.logger_touch.debug("触摸屏重置")

    def ICNT_ReadVersion(self):
        self.logger_touch.debug("触摸屏的版本为:" + "调试器模式")

    def ICNT_Init(self):
        self.logger_touch.debug("触摸屏初始化")

    def ICNT_Scan(self, ICNT_Dev: TouchRecoder, ICNT_Old: TouchRecoder):
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
        if x == None or y == None:
            ICNT_Dev.Touch = 0
        else:
            ICNT_Dev.Touch = 1
            ICNT_Dev.X[0] = x
            ICNT_Dev.Y[0] = y


class TouchHandler:
    def __init__(self, pool: threadpool_mini.ThreadPool, logger: logger.Logger):
        self.pool = pool
        self.clicked = []  # 当对象被点击并松开后调用指定函数                      ((x1, x2, y1, y2), func, args, kwargs)
        self.touched = []  # 当对象被按下后调用指定函数，直到松开后再次调用另一指定函数 ((x1, x2, y1, y2), func1, func2, args, kwargs)
        self.slide_x = []  # 当屏幕从指定区域被横向滑动后调用指定函数               ((x1, x2, y1, y2), func, args, kwargs)
        self.slide_y = []  # 当屏幕从指定区域被纵向滑动后调用指定函数               ((x1, x2, y1, y2), func, args, kwargs)
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
        self.clicked.append([area, func, args, kwargs, False])
        self.signal_1 = False

    def add_touched(self, area, func1, func2, *args, **kwargs):  # TODO:添加批量导入
        if area[0] > area[1] or area[2] > area[3] or area[0] < 0 or area[1] > 296 or area[2] < 0 or area[3] > 128:
            raise ValueError("Area out of range!")
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        self.touched.append([area, func1, func2, args, kwargs, False])
        self.signal_1 = False

    def add_slide_x(self, area, func):
        if area[0] > area[1] or area[2] > area[3] or area[0] < 0 or area[1] > 296 or area[2] < 0 or area[3] > 128:
            raise ValueError("Area out of range!")
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        self.slide_x.append([area, func, None])
        self.signal_1 = False

    def add_slide_y(self, area, func):
        if area[0] > area[1] or area[2] > area[3] or area[0] < 0 or area[1] > 296 or area[2] < 0 or area[3] > 128:
            raise ValueError("Area out of range!")
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        self.slide_y.append([area, func, None])
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
            if not (ICNT_Dev.X[0] == ICNT_Old.X[0] and ICNT_Dev.Y[0] == ICNT_Old.Y[0]):
                self.logger_touch.debug("触摸位置变化：[%s, %s]" % (ICNT_Dev.X[0], ICNT_Dev.Y[0]))
                for i in self.touched:  # 扫描touch
                    if i[0][0] <= ICNT_Dev.X[0] <= i[0][1] and i[0][2] <= ICNT_Dev.Y[0] <= i[0][3]:
                        if not i[-1]:
                            self.pool.add(i[1], *i[3], **i[4])  # 如果被点击，且标记为False，则执行func1
                            i[-1] = True
                    else:
                        if i[-1]:
                            self.pool.add(i[2], *i[3], **i[4])  # 如果没有被点击，且标记为True，则执行func2
                            i[-1] = False

        elif ICNT_Dev.Touch and (not ICNT_Old.Touch):  # 如果开始触摸
            self.logger_touch.debug("触摸事件开始：[%s, %s]" % (ICNT_Dev.X[0], ICNT_Dev.Y[0]))
            for i in self.touched:  # 扫描touch
                if i[0][0] <= ICNT_Dev.X[0] <= i[0][1] and i[0][2] <= ICNT_Dev.Y[0] <= i[0][3]:
                    self.pool.add(i[1], *i[3], **i[4])  # 如果被点击，且标记为False，则执行func1
                    i[-1] = True

            for i in self.clicked:
                if i[0][0] <= ICNT_Dev.X[0] <= i[0][1] and i[0][2] <= ICNT_Dev.Y[0] <= i[0][3]:
                    i[-1] = True

            for i in self.slide_x:
                if i[0][0] <= ICNT_Dev.X[0] <= i[0][1] and i[0][2] <= ICNT_Dev.Y[0] <= i[0][3]:
                    i[-1] = (ICNT_Dev.X[0], ICNT_Dev.Y[0])

            for i in self.slide_y:
                if i[0][0] <= ICNT_Dev.X[0] <= i[0][1] and i[0][2] <= ICNT_Dev.Y[0] <= i[0][3]:
                    i[-1] = (ICNT_Dev.X[0], ICNT_Dev.Y[0])

        elif (not ICNT_Dev.Touch) and ICNT_Old.Touch:  # 如果停止触摸
            self.logger_touch.debug("触摸事件终止：[%s, %s]" % (ICNT_Dev.X[0], ICNT_Dev.Y[0]))
            for i in self.touched:
                if i[-1]:
                    self.pool.add(i[2], *i[3], **i[4])  # 如果没有被点击，且标记为True，则执行func2
                    i[-1] = False

            for i in self.clicked:
                if i[-1]:
                    if i[0][0] <= ICNT_Old.X[0] <= i[0][1] and i[0][2] <= ICNT_Old.Y[0] <= i[0][3]:
                        self.pool.add(i[1], *i[2], **i[3])
                    i[-1] = False

            for i in self.slide_x:  # ⚠️参数需要经过测试后调整
                if i[-1] is not None:
                    if (abs(ICNT_Dev.Y[0] - i[-1][1]) <= 85) and (abs(ICNT_Dev.X[0] - i[-1][0]) >= 50):
                        self.pool.add(i[1], ICNT_Dev.X[0] - i[-1][0])
                    i[-1] = None

            for i in self.slide_y:
                if i[-1] is not None:
                    if (abs(ICNT_Dev.X[0] - i[-1][0]) <= 50) and (abs(ICNT_Dev.Y[0] - i[-1][1]) >= 40):
                        self.pool.add(i[1], ICNT_Dev.Y[0] - i[-1][1])
                    i[-1] = None

        self.signal_2 = False
