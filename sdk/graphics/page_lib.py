import sdk
from sdk.graphics import Page as _Page
from sdk.graphics.element_lib import ImageElement as _ImageElement
import sdk.graphics.element_lib


class ListPage(_Page):
    def __init__(self, paper, name):
        super().__init__(paper, name)

        self.content = []

    def show(self, content=[]):
        self.content = content
        self.paper.changePage(self.name)
        self.addElement(_ImageElement(
            (0, 0), self.paper, "resources/images/list.jpg"))
        self.addElement(sdk.graphics.element_lib.Label(
            (5, 5), self.paper, "测试"))

    def showAppList(self):
        appList = []
        for key in self.paper.env.apps:
            appList.append(key)
        self.show(appList)
