import time

from PIL import Image, ImageDraw

from sdk.graphics import Element, PaperDynamic, element_lib, page_lib


class _Docker(Element):
    def __init__(self, paper: PaperDynamic):
        super().__init__((60, 0), paper, (176, 30))
        self.image = Image.open(open("resources/images/docker.jpg", "rb"))
        self.__active = False
        self.inited = False

    def appbox_click_handler(self):
        if self.__active:
            self.paper.changePage("appList")
            self.paper.pages["appList"].show()
            self.__active = False

    def settings_click_handler(self):
        if self.__active:
            self.paper.env.openApp("系统设置")
            self.__active = False

    def clicked_handler(self):
        time.sleep(0.05)
        if (self.paper.nowPage != self.page.name) or self.__active or (not self.inited):
            return
        self.__active = True
        self.paper.update(self.page.name)
        for i in range(5):
            time.sleep(1)
            if not self.__active:
                return
        self.__active = False
        self.paper.update(self.page.name)

    def init(self):
        self.recover()

        self.inited = True

    def recover(self):
        self.paper.env.clear()
        self.paper.env.touch_handler.add_clicked(
            (0, 296, 0, 30), self.clicked_handler)
        self.paper.env.touch_handler.add_clicked(
            (60, 100, 0, 30), self.appbox_click_handler)
        self.paper.env.touch_handler.add_clicked(
            (195, 235, 0, 30), self.settings_click_handler)

    def exit(self):
        self.inited = False

    def build(self) -> Image:
        if self.__active:
            return self.image
        else:
            return


class appBackButton(element_lib.Button):  # 先做个临时的返回按钮哦
    def __init__(self, paper: PaperDynamic):
        super().__init__((0, 0), paper, "返回", self.goBack, bgcolor="white", textColor="black")

    def goBack(self):
        self.paper.env.backHome()


class PaperTheme(PaperDynamic):
    def __init__(self, env):
        super().__init__(env)
        self.pages["appList"] = page_lib.appListPage(self, "appList")
        self.dock_image = Image.open(open("resources/images/docker.jpg", "rb"))
        self.__docker_active = False
        self.inited = False
        self.suspended_touchpad = None

    def appbox_click_handler(self):
        if self.__docker_active:
            self.suspended_touchpad = None
            self.__docker_active = False
            self.changePage("appList")
            self.pages["appList"].show()

    def settings_click_handler(self):
        if self.__docker_active:
            self.suspended_touchpad = None
            self.__docker_active = False
            self.env.openApp("系统设置")

    def close_docker(self):
        if self.__docker_active:
            if self.suspended_touchpad:
                self.env.touch_handler.recover(self.suspended_touchpad)
                self.suspended_touchpad = None
            self.__docker_active = False
            self._update()

    def docker_clicked_handler(self):
        if (self.nowPage != "mainPage") or self.__docker_active or (not self.inited):
            return
        self.suspended_touchpad = self.env.touch_handler.suspend()
        self.env.touch_handler.add_clicked(
            (60, 100, 0, 30), self.appbox_click_handler)
        self.env.touch_handler.add_clicked(
            (195, 235, 0, 30), self.settings_click_handler)
        self.env.touch_handler.add_clicked(
            (0, 296, 30, 128), self.close_docker)
        self.__docker_active = True
        self._update()
        for i in range(5):
            time.sleep(1)
            if not self.__docker_active:
                return
        self.__docker_active = False
        if self.suspended_touchpad:
            self.env.touch_handler.recover(self.suspended_touchpad)
            self.suspended_touchpad = None
        self._update()

    def init(self):
        super().init()
        self.env.touch_handler.add_clicked(
            (0, 296, 0, 30), self.docker_clicked_handler)

    def recover(self):
        super().recover()
        if self.nowPage == "mainPage":
            self.env.touch_handler.add_clicked(
                (0, 296, 0, 30), self.docker_clicked_handler)

    def build(self) -> Image:
        new_image = self.background_image.copy()
        for element in self.pages[self.nowPage]:
            element_image = element.build()
            if element_image:
                new_image.paste(element_image, (element.xy[0], element.xy[1]))
        if self.__docker_active:
            new_image.paste(self.dock_image, (60, 0))
        self.image_old = new_image  # TODO:删除image_old
        return new_image

    def changePage(self, name, refresh=None):
        super().changePage(name, refresh)
        if name == "mainPage":
            self.env.touch_handler.add_clicked(
                (0, 296, 0, 30), self.docker_clicked_handler)


class PaperApp(PaperDynamic):
    def __init__(self, env):
        super().__init__(env)
        self.first_init = True

        self.__bar_active = False
        self.bar_image = Image.open(open("resources/images/app_control.jpg", "rb"))
        self.more_event = None
        self.args = []
        self.kwargs = {}

    def _add_control_bar_touch(self):
        self.env.touch_handler.add_clicked(
            (0, 30, 0, 30), self.clicked_handler)
        self.env.touch_handler.add_clicked_with_time(
            (0, 30, 0, 30), self.back_click_handler)
        self.env.touch_handler.add_clicked(
            (266, 296, 0, 30), self.close_click_handler)

    def back_click_handler(self, long):
        if self.__bar_active:
            if long >= 1:
                self.env.backHome()
            else:
                self.env.back()

    def close_click_handler(self):
        if self.__bar_active:
            self.env.backHome(True)

    def more_click_handler(self):
        if self.__bar_active:
            if self.more_event:
                self.more_event(*self.args, **self.kwargs)

    def clicked_handler(self):
        time.sleep(0.05)
        if self.__bar_active or (not self.inited):
            return
        self.__bar_active = True
        self._update()
        for _ in range(5):
            time.sleep(1)
            if not self.__bar_active:
                return
        self.__bar_active = False
        self._update()

    def init(self):
        if self.first_init:
            self.first_init = False
        self._add_control_bar_touch()
        super().init()

    def recover(self):
        super().recover()
        self._add_control_bar_touch()

    def set_more_func(self, func, *args, **kwargs):
        self.more_event = func
        self.args = args
        self.kwargs = kwargs

    def build(self) -> Image:
        new_image = self.background_image.copy()
        for element in self.pages[self.nowPage]:
            element_image = element.build()
            if element_image:
                new_image.paste(element_image, (element.xy[0], element.xy[1]))
        if self.__bar_active:
            new_image.paste(self.bar_image, (0, 0))
        return new_image

    def changePage(self, name, refresh=None):
        super().changePage(name, refresh)
        self._add_control_bar_touch()
