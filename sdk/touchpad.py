import threading
import time


class TouchRecoder:
    def __init__(self):
        self.Touch = 0
        self.TouchGestureId = 0
        self.TouchCount = 0

        self.TouchEvenId = [0, 1, 2, 3, 4]
        self.X = [0, 1, 2, 3, 4]
        self.Y = [0, 1, 2, 3, 4]
        self.P = [0, 1, 2, 3, 4]


class ReIter:   # 反向迭代器
    def __init__(self, content):
        self.content = content
        self.index = None

    def __iter__(self):
        self.index = len(self.content)
        return self

    def __next__(self):
        if self.index <= 0:
            self.index = len(self.content)
            raise StopIteration
        else:
            self.index -= 1
            return self.content[self.index]


class TouchHandler:
    def __init__(self, env):
        self.pool = env.pool
        self.clicked = []  # 当对象被点击并松开后调用指定函数                      ((x1, x2, y1, y2), func, args, kwargs)
        self.king_clicked = []
        self.clicked_with_time = []  # 当对象被点击并松开且从未中后调用指定函数并返回触摸时间（float） ((x1, x2, y1, y2), func)
        self.touched = []  # 当对象被按下后调用指定函数，直到松开后再次调用另一指定函数 ((x1, x2, y1, y2), func1, func2, args, kwargs)
        self.slide_x = []  # 当屏幕从指定区域被横向滑动后调用指定函数               ((x1, x2, y1, y2), func, args, kwargs)
        self.slide_y = []  # 当屏幕从指定区域被纵向滑动后调用指定函数               ((x1, x2, y1, y2), func, args, kwargs)
        self.data_lock = threading.Lock()
        self.logger_touch = env.logger_env
        self.signal_1 = False
        self.signal_2 = False

    def add_clicked(self, area, func, *args, **kwargs):
        """
        添加一个触摸元件，⚠️：所有的回调函数必须能接收 *args, **kwargs
        :param func: 回调函数
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

    def remove_clicked(self, func) -> bool:  # 未测试
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        counter = 0
        remove_list = []
        for i in self.clicked:
            if i[1] == func:
                remove_list.append(counter)
            counter += 1
        counter = 0
        if len(remove_list) == 0:
            self.signal_1 = False
            return False
        for i in remove_list:
            del self.clicked[i - counter]
            counter += 1
        self.signal_1 = False
        return True

    def set_clicked(self, content: list):
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        self.clicked = content
        self.signal_1 = False
        return True

    def add_king_clicked(self, area, func, *args, **kwargs):
        if area[0] > area[1] or area[2] > area[3] or area[0] < 0 or area[1] > 296 or area[2] < 0 or area[3] > 128:
            raise ValueError("Area out of range!")
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        self.king_clicked.append([area, func, args, kwargs, False])
        self.signal_1 = False

    def remove_king_clicked(self, func) -> bool:  # 未测试
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        counter = 0
        remove_list = []
        for i in self.clicked:
            if i[1] == func:
                remove_list.append(counter)
            counter += 1
        counter = 0
        if len(remove_list) == 0:
            self.signal_1 = False
            return False
        for i in remove_list:
            del self.king_clicked[i - counter]
            counter += 1
        self.signal_1 = False
        return True

    def set_king_clicked(self, content: list):
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        self.king_clicked = content
        self.signal_1 = False
        return True

    def clean_king_clicked(self):
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        self.king_clicked = []
        self.signal_1 = False
        return True

    def add_clicked_with_time(self, area, func):
        """
        添加一个触摸元件，⚠️：所有的回调函数必须能接收 *args, **kwargs
        :param func: 回调函数
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
        self.clicked_with_time.append([area, func, None])
        self.signal_1 = False

    def remove_clicked_with_time(self, func) -> bool:  # 未测试
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        counter = 0
        remove_list = []
        for i in self.clicked_with_time:
            if i[1] == func:
                remove_list.append(counter)
            counter += 1
        counter = 0
        if len(remove_list) == 0:
            self.signal_1 = False
            return False
        for i in remove_list:
            del self.clicked_with_time[i - counter]
            counter += 1
        self.signal_1 = False
        return True

    def set_clicked_with_time(self, content: list):
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        self.clicked_with_time = content
        self.signal_1 = False
        return True

    def add_touched(self, area, func1, func2, *args, **kwargs):
        if area[0] > area[1] or area[2] > area[3] or area[0] < 0 or area[1] > 296 or area[2] < 0 or area[3] > 128:
            raise ValueError("Area out of range!")
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        self.touched.append([area, func1, func2, args, kwargs, False])
        self.signal_1 = False

    def remove_touched(self, func) -> bool:
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        counter = 0
        remove_list = []
        for i in self.touched:
            if i[1] == func:  # 只对func1进行匹配
                remove_list.append(counter)
            counter += 1
        counter = 0
        if len(remove_list) == 0:
            self.signal_1 = False
            return False
        for i in remove_list:
            del self.touched[i - counter]
            counter += 1
        self.signal_1 = False
        return True

    def set_touched(self, content: list):
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        self.touched = content
        self.signal_1 = False
        return True

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

    def remove_slide_x(self, func) -> bool:
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        counter = 0
        remove_list = []
        for i in self.slide_x:
            if i[1] == func:
                remove_list.append(counter)
            counter += 1
        counter = 0
        if len(remove_list) == 0:
            self.signal_1 = False
            return False
        for i in remove_list:
            del self.slide_x[i - counter]
            counter += 1
        self.signal_1 = False
        return True

    def set_slide_x(self, content: list):
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        self.slide_x = content
        self.signal_1 = False
        return True

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

    def remove_slide_y(self, func) -> bool:
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        counter = 0
        remove_list = []
        for i in self.slide_y:
            if i[1] == func:
                remove_list.append(counter)
            counter += 1
        counter = 0
        if len(remove_list) == 0:
            self.signal_1 = False
            return False
        for i in remove_list:
            del self.slide_y[i - counter]
            counter += 1
        self.signal_1 = False
        return True

    def set_slide_y(self, content: list):
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        self.slide_y = content
        self.signal_1 = False
        return True

    def clear(self):
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        self.clicked = []
        self.clicked_with_time = []
        self.touched = []
        self.slide_x = []
        self.slide_y = []
        self.signal_1 = False

    def backup(self) -> list:
        suspended = list()
        suspended.append(self.clicked.copy())
        suspended.append(self.clicked_with_time.copy())
        suspended.append(self.touched.copy())
        suspended.append(self.slide_x.copy())
        suspended.append(self.slide_y.copy())
        return suspended

    def suspend(self) -> list:
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)
        suspended = list()
        suspended.append(self.clicked.copy())
        self.clicked = []
        suspended.append(self.clicked_with_time.copy())
        self.clicked_with_time = []
        suspended.append(self.touched.copy())
        self.touched = []
        suspended.append(self.slide_x.copy())
        self.slide_x = []
        suspended.append(self.slide_y.copy())
        self.slide_y = []
        self.signal_1 = False
        return suspended

    def recover(self, content: list):
        self.signal_1 = True
        while True:
            if not self.signal_2:
                break
            time.sleep(0.1)

        self.clicked = content[0]
        self.clicked_with_time = content[1]
        self.touched = content[2]
        self.slide_x = content[3]
        self.slide_y = content[4]

        self.signal_1 = False

    def handle(self, ICNT_Dev: TouchRecoder, ICNT_Old: TouchRecoder):  # 此函数只可在主线程中运行
        while True:
            if not self.signal_1:
                break
            time.sleep(0.1)
        self.signal_2 = True
        if ICNT_Dev.Touch and ICNT_Old.Touch:  # 如果保持一直触摸不变
            if not (ICNT_Dev.X[0] == ICNT_Old.X[0] and ICNT_Dev.Y[0] == ICNT_Old.Y[0]):
                # self.logger_touch.debug("触摸位置变化：[%s, %s]" % (ICNT_Dev.X[0], ICNT_Dev.Y[0]))
                for i in ReIter(self.touched):  # 扫描touch
                    if i[0][0] <= ICNT_Dev.X[0] <= i[0][1] and i[0][2] <= ICNT_Dev.Y[0] <= i[0][3]:
                        if not i[-1]:
                            self.pool.add(i[1], *i[3], **i[4])  # 如果被点击，且标记为False，则执行func1
                            i[-1] = True
                    else:
                        if i[-1]:
                            self.pool.add(i[2], *i[3], **i[4])  # 如果没有被点击，且标记为True，则执行func2
                            i[-1] = False

                for i in ReIter(self.clicked_with_time):
                    if i[-1]:
                        if not (i[0][0] <= ICNT_Old.X[0] <= i[0][1] and i[0][2] <= ICNT_Old.Y[0] <= i[0][3]):
                            i[-1] = None

        elif ICNT_Dev.Touch and (not ICNT_Old.Touch):  # 如果开始触摸
            # self.logger_touch.debug("触摸事件开始：[%s, %s]" % (ICNT_Dev.X[0], ICNT_Dev.Y[0]))

            for i in ReIter(self.slide_x):
                if i[0][0] <= ICNT_Dev.X[0] <= i[0][1] and i[0][2] <= ICNT_Dev.Y[0] <= i[0][3]:
                    i[-1] = (ICNT_Dev.X[0], ICNT_Dev.Y[0])

            for i in ReIter(self.slide_y):
                if i[0][0] <= ICNT_Dev.X[0] <= i[0][1] and i[0][2] <= ICNT_Dev.Y[0] <= i[0][3]:
                    i[-1] = (ICNT_Dev.X[0], ICNT_Dev.Y[0])

            for i in ReIter(self.touched):  # 扫描touch
                if i[0][0] <= ICNT_Dev.X[0] <= i[0][1] and i[0][2] <= ICNT_Dev.Y[0] <= i[0][3]:
                    self.pool.add(i[1], *i[3], **i[4])  # 如果被点击，且标记为False，则执行func1
                    i[-1] = True
                    break

            for i in ReIter(self.king_clicked): # 优先处理
                if i[0][0] <= ICNT_Dev.X[0] <= i[0][1] and i[0][2] <= ICNT_Dev.Y[0] <= i[0][3]:
                    i[-1] = True
                    return

            for i in ReIter(self.clicked):
                if i[0][0] <= ICNT_Dev.X[0] <= i[0][1] and i[0][2] <= ICNT_Dev.Y[0] <= i[0][3]:
                    i[-1] = True
                    return

            for i in ReIter(self.clicked_with_time):
                if i[0][0] <= ICNT_Dev.X[0] <= i[0][1] and i[0][2] <= ICNT_Dev.Y[0] <= i[0][3]:
                    i[-1] = time.time()
                    return

        elif (not ICNT_Dev.Touch) and ICNT_Old.Touch:  # 如果停止触摸
            # self.logger_touch.debug("触摸事件终止：[%s, %s]" % (ICNT_Dev.X[0], ICNT_Dev.Y[0]))
            for i in ReIter(self.touched):
                if i[-1]:
                    self.pool.add(i[2], *i[3], **i[4])  # 如果没有被点击，且标记为True，则执行func2
                    i[-1] = False

            for i in ReIter(self.king_clicked):
                if i[-1]:
                    if i[0][0] <= ICNT_Old.X[0] <= i[0][1] and i[0][2] <= ICNT_Old.Y[0] <= i[0][3]:
                        self.pool.add(i[1], *i[2], **i[3])
                    i[-1] = False

            for i in ReIter(self.clicked):
                if i[-1]:
                    if i[0][0] <= ICNT_Old.X[0] <= i[0][1] and i[0][2] <= ICNT_Old.Y[0] <= i[0][3]:
                        self.pool.add(i[1], *i[2], **i[3])
                    i[-1] = False

            for i in ReIter(self.clicked_with_time):
                if i[-1]:
                    if i[0][0] <= ICNT_Old.X[0] <= i[0][1] and i[0][2] <= ICNT_Old.Y[0] <= i[0][3]:
                        self.pool.add(i[1], time.time() - i[-1])
                    i[-1] = None

            for i in ReIter(self.slide_x):  # ⚠️参数需要经过测试后调整
                if i[-1] is not None:
                    dis_x = ICNT_Dev.X[0] - i[-1][0]
                    dis_y = ICNT_Dev.Y[0] - i[-1][1]
                    if abs(dis_x) > 20 and abs(dis_y / dis_x) < 0.5:
                        self.pool.add(i[1], dis_x)
                    i[-1] = None

            for i in ReIter(self.slide_y):
                if i[-1] is not None:
                    dis_x = ICNT_Dev.X[0] - i[-1][0]
                    dis_y = ICNT_Dev.Y[0] - i[-1][1]
                    if abs(dis_y) > 20 and abs(dis_x / dis_y) < 0.5:
                        self.pool.add(i[1], dis_y)
                    i[-1] = None

        self.signal_2 = False
