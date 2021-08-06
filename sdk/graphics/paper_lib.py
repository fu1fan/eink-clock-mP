import time

from PIL import Image

from sdk.graphics import Element, PaperDynamic, element_lib, page_lib


class _Docker(Element):
    def __init__(self, paper: PaperDynamic):
        super().__init__((60, 0), paper, (176, 30))
        self.image = Image.open(open("resources/images/docker.jpg", "rb"))
        self.__active = False
        self.inited = False

    def clicked_handler(self):
        if self.paper.nowPage == self.page and not self.__active and self.inited:
            self.__active = True
        self.paper.update_async(self.page)
        time.sleep(5)
        self.__active = False
        self.paper.update(self.page)

    def init(self):
        self.paper.env.touch_handler.add_clicked((0, 296, 0, 30), self.clicked_handler)
        self.inited = True

    def exit(self):
        self.inited = False

    def build(self) -> Image:
        if self.__active:
            return self.image
        else:
            return


class PaperTheme(PaperDynamic):
    def __init__(self, env):
        super().__init__(env)
        self.pages["appList"] = page_lib.ListPage(self, "appList")

    def init(self):
        self.addElement("mainPage", _Docker(self))
        super().init()


class PaperApp(PaperDynamic):
    pass