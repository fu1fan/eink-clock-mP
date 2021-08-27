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
        self.env = env
        self.pool = env.pool
        self.clicked = []  # 当对象被点击并松开后调用指定函数                      ((x1, x2, y1, y2), func, args, kwargs)
        self.system_clicked = []
        self.touched = []  # 当对象被按下后调用指定函数，直到松开后再次调用另一指定函数 ((x1, x2, y1, y2), func1, func2, args, kwargs)
        self.slide_x = []  # 当屏幕从指定区域被横向滑动后调用指定函数               ((x1, x2, y1, y2), func, args, kwargs)
        self.slide_y = []  # 当屏幕从指定区域被纵向滑动后调用指定函数               ((x1, x2, y1, y2), func, args, kwargs)
        self.data_lock = threading.Lock()
        self.logger_touch = env.logger_env
        self.back_left = None
        self.back_right = None
        self.home_bar = None

    def add_clicked(self, area, func, *args, **kwargs):
        """
        添加一个触摸元件，⚠️：所有的回调函数必须能接收 *args, **kwargs
        :param func: 回调函数
        :param area: (x1, x2, y1, y2)
        :return: None
        """
        if area[0] > area[1] or area[2] > area[3] or area[0] < 0 or area[1] > 296 or area[2] < 0 or area[3] > 128:
            raise ValueError("Area out of range!")
        self.data_lock.acquire()
        self.clicked.append([area, func, args, kwargs, False])
        self.data_lock.release()

    def remove_clicked(self, func):  # 未测试
        self.data_lock.acquire()
        counter = 0
        remove_list = []
        for i in self.clicked:
            if i[1] == func:
                remove_list.append(counter)
            counter += 1
        counter = 0
        if len(remove_list) == 0:
            self.data_lock.release()
            return False
        for i in remove_list:
            del self.clicked[i - counter]
            counter += 1
        self.data_lock.release()

    def remove_a_clicked(self, func):
        self.data_lock.acquire()
        counter = len(self.clicked)
        for i in ReIter(self.clicked):
            counter -= 1
            if counter == -1:
                self.data_lock.release()
                return
            if i[1] == func:
                break
        del self.clicked[counter]
        self.data_lock.release()

    def set_clicked(self, content: list):
        self.data_lock.acquire()
        self.clicked = content
        self.data_lock.release()
        return True

    def add_system_clicked(self, area, func, *args, **kwargs):
        if area[0] > area[1] or area[2] > area[3] or area[0] < 0 or area[1] > 296 or area[2] < 0 or area[3] > 128:
            raise ValueError("Area out of range!")
        self.data_lock.acquire()
        self.system_clicked.append([area, func, args, kwargs, False])
        self.data_lock.release()

    def remove_system_clicked(self, func) -> bool:  # 未测试
        self.data_lock.acquire()
        counter = 0
        remove_list = []
        for i in self.clicked:
            if i[1] == func:
                remove_list.append(counter)
            counter += 1
        counter = 0
        if len(remove_list) == 0:
            self.data_lock.release()
            return False
        for i in remove_list:
            del self.system_clicked[i - counter]
            counter += 1
        self.data_lock.release()
        return True

    def remove_a_system_clicked(self, func):
        self.data_lock.acquire()
        counter = len(self.system_clicked)
        for i in ReIter(self.system_clicked):
            counter -= 1
            if counter == -1:
                self.data_lock.release()
                return
            if i[1] == func:
                break
        del self.system_clicked[counter]
        self.data_lock.release()

    def set_system_clicked(self, content: list):
        self.data_lock.acquire()
        self.system_clicked = content
        self.data_lock.release()
        return True

    def clean_system_clicked(self):
        self.data_lock.acquire()
        self.system_clicked = []
        self.data_lock.release()
        return True

    def add_clicked_with_time(self, area, func):
        """
        添加一个触摸元件，回调函数必须接受一个float型的参数
        :param func: 回调函数
        :param area: (x1, x2, y1, y2)
        :return: None
        """
        if area[0] > area[1] or area[2] > area[3] or area[0] < 0 or area[1] > 296 or area[2] < 0 or area[3] > 128:
            raise ValueError("Area out of range!")
        self.data_lock.acquire()
        self.clicked.append([area, func, None])
        self.data_lock.release()

    def remove_clicked_with_time(self, func) -> bool:  # 未测试
        return self.remove_clicked(func)

    def remove_a_clicked_with_time(self, func):
        return self.remove_clicked(func)

    def set_clicked_with_time(self, content: list):
        return self.set_clicked(content)

    def add_touched(self, area, func1, func2, *args, **kwargs):
        if area[0] > area[1] or area[2] > area[3] or area[0] < 0 or area[1] > 296 or area[2] < 0 or area[3] > 128:
            raise ValueError("Area out of range!")
        self.data_lock.acquire()
        self.touched.append([area, func1, func2, args, kwargs, False])
        self.data_lock.release()

    def remove_touched(self, func) -> bool:
        self.data_lock.acquire()
        counter = 0
        remove_list = []
        for i in self.touched:
            if i[1] == func:  # 只对func1进行匹配
                remove_list.append(counter)
            counter += 1
        counter = 0
        if len(remove_list) == 0:
            self.data_lock.release()
            return False
        for i in remove_list:
            del self.touched[i - counter]
            counter += 1
        self.data_lock.release()
        return True

    def remove_a_touched(self, func):
        self.data_lock.acquire()
        counter = len(self.touched)
        for i in ReIter(self.touched):
            counter -= 1
            if counter == -1:
                self.data_lock.release()
                return
            if i[1] == func:
                break
        del self.touched[counter]
        self.data_lock.release()

    def set_touched(self, content: list):
        self.data_lock.acquire()
        self.touched = content
        self.data_lock.release()
        return True

    def add_slide_x(self, area, func):
        if area[0] > area[1] or area[2] > area[3] or area[0] < 0 or area[1] > 296 or area[2] < 0 or area[3] > 128:
            raise ValueError("Area out of range!")
        self.data_lock.acquire()
        self.slide_x.append([area, func, None])
        self.data_lock.release()

    def remove_slide_x(self, func) -> bool:
        self.data_lock.acquire()
        counter = 0
        remove_list = []
        for i in self.slide_x:
            if i[1] == func:
                remove_list.append(counter)
            counter += 1
        counter = 0
        if len(remove_list) == 0:
            self.data_lock.release()
            return False
        for i in remove_list:
            del self.slide_x[i - counter]
            counter += 1
        self.data_lock.release()
        return True

    def remove_a_slide_x(self, func):
        self.data_lock.acquire()
        counter = len(self.slide_x)
        for i in ReIter(self.slide_x):
            counter -= 1
            if counter == -1:
                self.data_lock.release()
                return
            if i[1] == func:
                break
        del self.slide_x[counter]
        self.data_lock.release()

    def set_slide_x(self, content: list):
        self.data_lock.acquire()
        self.slide_x = content
        self.data_lock.release()
        return True

    def add_slide_y(self, area, func):
        if area[0] > area[1] or area[2] > area[3] or area[0] < 0 or area[1] > 296 or area[2] < 0 or area[3] > 128:
            raise ValueError("Area out of range!")
        self.data_lock.acquire()
        self.slide_y.append([area, func, None])
        self.data_lock.release()

    def remove_slide_y(self, func) -> bool:
        self.data_lock.acquire()
        counter = 0
        remove_list = []
        for i in self.slide_y:
            if i[1] == func:
                remove_list.append(counter)
            counter += 1
        counter = 0
        if len(remove_list) == 0:
            self.data_lock.release()
            return False
        for i in remove_list:
            del self.slide_y[i - counter]
            counter += 1
        self.data_lock.release()
        return True

    def remove_a_slide_y(self, func):
        self.data_lock.acquire()
        counter = len(self.slide_y)
        for i in ReIter(self.slide_y):
            counter -= 1
            if counter == -1:
                self.data_lock.release()
                return
            if i[1] == func:
                break
        del self.slide_y[counter]
        self.data_lock.release()

    def set_slide_y(self, content: list):
        self.data_lock.acquire()
        self.slide_y = content
        self.data_lock.release()
        return True

    def clear(self):
        self.data_lock.acquire()
        self.clicked = []
        self.clicked_with_time = []
        self.touched = []
        self.slide_x = []
        self.slide_y = []
        self.data_lock.release()

    def backup(self) -> list:
        suspended = list()
        suspended.append(self.clicked.copy())
        suspended.append(self.clicked_with_time.copy())
        suspended.append(self.touched.copy())
        suspended.append(self.slide_x.copy())
        suspended.append(self.slide_y.copy())
        return suspended

    def suspend(self) -> list:
        self.data_lock.acquire()
        suspended = list()
        suspended.append(self.clicked.copy())
        self.clicked = []
        suspended.append(self.touched.copy())
        self.touched = []
        suspended.append(self.slide_x.copy())
        self.slide_x = []
        suspended.append(self.slide_y.copy())
        self.slide_y = []
        self.data_lock.release()
        return suspended

    def recover(self, content: list):
        self.data_lock.acquire()

        self.clicked = content[0]
        self.touched = content[1]
        self.slide_x = content[2]
        self.slide_y = content[3]

        self.data_lock.release()

    def handle(self, ICNT_Dev: TouchRecoder, ICNT_Old: TouchRecoder):  # 此函数只可在主线程中运行
        self.data_lock.acquire()

        if ICNT_Dev.Touch and ICNT_Old.Touch:  # 如果保持一直触摸不变
            if not (ICNT_Dev.X[0] == ICNT_Old.X[0] and ICNT_Dev.Y[0] == ICNT_Old.Y[0]):
                # self.logger_touch.debug("触摸位置变化：[%s, %s]" % (ICNT_Dev.X[0], ICNT_Dev.Y[0]))
                if self.back_left and not self.back_left[2]:
                    if ICNT_Dev.X[0] - self.back_left[0] >= 20:
                        self.pool.add(self.env.system_event.back_show_left)
                        self.back_left[2] = True
                elif self.back_right and not self.back_right[2]:
                    if self.back_right[0] - ICNT_Dev.X[0] >= 20:
                        self.pool.add(self.env.system_event.back_show_right)
                        self.back_right[2] = True

                for i in ReIter(self.touched):  # 扫描touch
                    if i[0][0] <= ICNT_Dev.X[0] <= i[0][1] and i[0][2] <= ICNT_Dev.Y[0] <= i[0][3]:
                        if not i[-1]:
                            self.pool.add(i[1], *i[3], **i[4])  # 如果被点击，且标记为False，则执行func1
                            i[-1] = True
                    else:
                        if i[-1]:
                            self.pool.add(i[2], *i[3], **i[4])  # 如果没有被点击，且标记为True，则执行func2
                            i[-1] = False

                for i in ReIter(self.clicked):
                    if i[-1] and len(i) == 3:
                        if not (i[0][0] <= ICNT_Old.X[0] <= i[0][1] and i[0][2] <= ICNT_Old.Y[0] <= i[0][3]):
                            i[-1] = None

        elif ICNT_Dev.Touch and (not ICNT_Old.Touch):  # 如果开始触摸
            # self.logger_touch.debug("触摸事件开始：[%s, %s]" % (ICNT_Dev.X[0], ICNT_Dev.Y[0]))

            if ICNT_Dev.X[0] <= 20:
                self.back_left = [ICNT_Dev.X[0], ICNT_Dev.Y[0], False]

            elif ICNT_Dev.X[0] >= 276:
                self.back_right = [ICNT_Dev.X[0], ICNT_Dev.Y[0], False]

            elif ICNT_Dev.Y[0] >= 108 and 100 <= ICNT_Dev.X[0] <= 200:
                self.home_bar = (ICNT_Dev.X[0], ICNT_Dev.Y[0])

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

            for i in ReIter(self.system_clicked):  # 优先处理
                if i[0][0] <= ICNT_Dev.X[0] <= i[0][1] and i[0][2] <= ICNT_Dev.Y[0] <= i[0][3]:
                    i[-1] = True
                    self.data_lock.release()
                    return

            for i in ReIter(self.clicked):
                if i[0][0] <= ICNT_Dev.X[0] <= i[0][1] and i[0][2] <= ICNT_Dev.Y[0] <= i[0][3]:
                    if len(i) == 5:
                        i[-1] = True
                        self.data_lock.release()
                        return
                    elif len(i) == 3:
                        i[-1] = time.time()
                        self.data_lock.release()
                        return

        elif (not ICNT_Dev.Touch) and ICNT_Old.Touch:  # 如果停止触摸
            # self.logger_touch.debug("触摸事件终止：[%s, %s]" % (ICNT_Dev.X[0], ICNT_Dev.Y[0]))
            slide = False
            if self.back_left:
                if ICNT_Dev.X[0] - self.back_left[0] > 20:
                    self.pool.add(self.env.system_event.back_hide_left, False)
                    self.pool.add(self.env.back)
                    slide = True
                else:
                    self.pool.add(self.env.system_event.back_hide_left, True)
                self.back_left = None
            elif self.back_right:
                if self.back_right[0] - ICNT_Dev.X[0] > 20:
                    self.pool.add(self.env.system_event.back_hide_right, False)
                    self.pool.add(self.env.back)
                    slide = True
                else:
                    self.pool.add(self.env.system_event.back_hide_right, True)
                self.back_right = None
            elif self.home_bar:
                if self.home_bar[1] - ICNT_Dev.Y[0] > 20 and 100 <= ICNT_Dev.X[0] <= 200:
                    self.pool.add(self.env.system_event.home_ctrl)
                    slide = True
                self.home_bar = None
            if not slide:
                for i in ReIter(self.slide_x):  # ⚠️参数需要经过测试后调整
                    if i[-1]:
                        dis_x = ICNT_Dev.X[0] - i[-1][0]
                        dis_y = ICNT_Dev.Y[0] - i[-1][1]
                        if abs(dis_x) > 20 and abs(dis_y / dis_x) < 0.5:
                            self.pool.add(i[1], dis_x)
                            slide = True
                        i[-1] = None

                for i in ReIter(self.slide_y):
                    if i[-1]:
                        dis_x = ICNT_Dev.X[0] - i[-1][0]
                        dis_y = ICNT_Dev.Y[0] - i[-1][1]
                        if abs(dis_y) > 20 and abs(dis_x / dis_y) < 0.5:
                            self.pool.add(i[1], dis_y)
                            slide = True
                        i[-1] = None

                if slide:
                    for i in self.touched:
                        i[-1] = False
                    for i in self.system_clicked:
                        i[-1] = False
                    for i in self.clicked:
                        i[-1] = False
                    for i in self.clicked_with_time:
                        i[-1] = None
                else:
                    for i in ReIter(self.touched):
                        if i[-1]:
                            self.pool.add(i[2], *i[3], **i[4])  # 如果没有被点击，且标记为True，则执行func2
                            i[-1] = False

                    for i in ReIter(self.system_clicked):
                        if i[-1]:
                            if i[0][0] <= ICNT_Old.X[0] <= i[0][1] and i[0][2] <= ICNT_Old.Y[0] <= i[0][3]:
                                self.pool.add(i[1], *i[2], **i[3])
                            i[-1] = False

                    for i in ReIter(self.clicked):
                        if i[-1]:
                            if len(i) == 5:
                                if i[0][0] <= ICNT_Old.X[0] <= i[0][1] and i[0][2] <= ICNT_Old.Y[0] <= i[0][3]:
                                    self.pool.add(i[1], *i[2], **i[3])
                                i[-1] = False
                            elif len(i) == 3:
                                if i[0][0] <= ICNT_Old.X[0] <= i[0][1] and i[0][2] <= ICNT_Old.Y[0] <= i[0][3]:
                                    self.pool.add(i[1], time.time() - i[-1])
                                i[-1] = None

        self.data_lock.release()
