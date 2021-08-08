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
            self.paper.pages["appList"].showAppList()
            self.__active = False

    def clicked_handler(self):
        time.sleep(0.1)
        if (self.paper.nowPage != self.page.name) or self.__active or (not self.inited):
            return
        self.__active = True
        self.paper.update(self.page.name)
        time.sleep(10)
        self.__active = False
        self.paper.update(self.page.name)

    def init(self):
        self.paper.env.touch_handler.add_clicked(
            (0, 296, 0, 30), self.clicked_handler)
        self.paper.env.touch_handler.add_clicked(
            (60, 100, 0, 30), self.appbox_click_handler)
        self.inited = True

    def recover(self):
        self.paper.env.touch_handler.add_clicked(
            (0, 296, 0, 30), self.clicked_handler)
        self.paper.env.touch_handler.add_clicked(
            (60, 100, 0, 30), self.appbox_click_handler)

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
        self.paper.pages["appList"].showAppList()


class PaperTheme(PaperDynamic):
    def __init__(self, env):
        super().__init__(env)
        self.pages["appList"] = page_lib.ListPage(self, "appList")
        self.first_init = True

    def init(self):
        if self.first_init:
            self.addElement("mainPage", _Docker(self))
            self.first_init = False
        super().init()


class PaperApp(PaperDynamic):
    def __init__(self, env):
        super().__init__(env)
        self.pages["appList"] = page_lib.ListPage(self, "appList")
        self.first_init = True

    def init(self):
        if self.first_init:
            self.addElement("mainPage", appBackButton(self))
            self.first_init = False
        super().init()
