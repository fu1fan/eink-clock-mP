import time

from PIL import Image

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
        self.first_init = True

    def init(self):
        if self.first_init:
            self.addElement(_Docker(self), "mainPage")
            self.first_init = False
        super().init()


class AppControlBar(Element):
    def __init__(self, paper):
        super().__init__((0, 0), paper, (296, 30))
        self.__active = False
        self.image = Image.open(open("resources/images/app_control.jpg", "rb"))
        self.more_event = None
        self.args = []
        self.kwargs = {}

    def back_click_handler(self, long):
        if self.__active:
            if long >= 1:
                self.paper.env.backHome()
            else:
                self.paper.env.back()

    def close_click_handler(self):
        if self.__active:
            self.paper.env.backHome(True)

    def more_click_handler(self):
        if self.__active:
            if self.more_event:
                self.more_event(*self.args, **self.kwargs)

    def clicked_handler(self):
        time.sleep(0.05)
        if self.__active or (not self.inited):
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
        self.paper.env.touch_handler.add_clicked(
            (0, 30, 0, 30), self.clicked_handler)
        self.paper.env.touch_handler.add_clicked(
            (60, 30, 0, 30), self.back_click_handler)
        self.paper.env.touch_handler.add_clicked_with_time(
            (266, 296, 0, 30), self.close_click_handler)

    def exit(self):
        self.inited = False

    def build(self) -> Image:
        if self.__active:
            return self.image
        else:
            return


class PaperApp(PaperDynamic):
    def __init__(self, env):
        super().__init__(env)
        self.first_init = True

    def init(self):
        if self.first_init:
            self.addElement(AppControlBar)
            self.first_init = False
        super().init()