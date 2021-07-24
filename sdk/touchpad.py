import threading

from sdk import icnt86
from sdk import epdconfig as config
from sdk import logger
from sdk import threadpool_mini


class TouchRecoderNew(icnt86.ICNT_Development):
    pass


class TouchRecoderOld():
    def __init__(self):
        self.TouchCount = 0
        self.TouchEvenId = [0, 1, 2, 3, 4]
        self.X = [0, 1, 2, 3, 4]
        self.Y = [0, 1, 2, 3, 4]
        self.P = [0, 1, 2, 3, 4]


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

    def ICNT_Scan(self, ICNT_Dev: TouchRecoderNew, ICNT_Old: TouchRecoderOld):
        mask = 0x00

        if self.digital_read(self.INT) == 0:
            ICNT_Dev.Touch = 0
            return

        else:
            ICNT_Dev.Touch = 1
            buf = self.ICNT_Read(0x1001, 1)

            if buf[0] == 0x00:
                self.ICNT_Write(0x1001, mask)
                config.delay_ms(1)
                self.logger_touch.warn("touchpad buffers status is 0!")
                return
            else:
                ICNT_Old.TouchCount = ICNT_Dev.TouchCount
                ICNT_Old.X[0] = ICNT_Dev.X[0]
                ICNT_Old.Y[0] = ICNT_Dev.Y[0]
                ICNT_Old.P[0] = ICNT_Dev.P[0]

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


class TouchHandler:
    def __init__(self, pool: threadpool_mini.ThreadPool):
        self.pool = pool
        self.objects = []   # ((x1, x2, y1, y2), func, args, kwargs)
        self.data_lock = threading.Lock()

    def add(self, area: tuple, func, *args, **kwargs):
        """
        添加一个触摸元件
        :param func:
        :param area: (x1, x2, y1, y2)
        :return:
        """
        if area[0]>area[1] or area[2]>area[3] or area[0]<0 or area[1]>296 or area[2]<0 or area[3]>128:
            raise ValueError("Area out of range!")
        self.data_lock.acquire()
        self.objects.append((area, func, args, kwargs))
        self.data_lock.release()

    def clear(self):
        self.data_lock.acquire()
        self.objects = []
        self.data_lock.release()

    def handle(self, ICNT_Dev: TouchRecoderNew):
        self.data_lock.acquire()
        for i in self.objects:
            if i[0][0] <= ICNT_Dev.X <= i[0][1] and i[0][2] <= ICNT_Dev.Y <= i[0][3]:
                self.pool.add(i[1], i[2], i[3])
        self.data_lock.release()
