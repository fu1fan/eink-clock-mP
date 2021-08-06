import sdk
from sdk.graphics import Page as _Page
from sdk.graphics.element_lib import ImageElement as _ImageElement
import sdk.graphics.element_lib


class ListPage(_Page):
    def __init__(self, paper, name):
        super().__init__(paper, name)
        self.addElement(_ImageElement(
            (0, 0), self.paper, "resources/images/list.jpg"))
        self.labels = (
            sdk.graphics.element_lib.Label((5, 5), self.paper, "测试"),
            sdk.graphics.element_lib.Label((5, 35), self.paper, "测试2"),
            sdk.graphics.element_lib.Label((5, 65), self.paper, "测试3"),
        )
        for label in self.labels:
            self.addElement(label)
        self.content = []   # [[text, image, func]]

    def show(self, content=[]):
        self.content = content
        self.paper.pause_update() #上锁，防止setText重复刷新屏幕
        self.labels[0].setText("23333")
        self.labels[1].setText("66666")
        self.labels[2].setText("33333")
        self.paper.recover_update() #解锁
        self.paper.changePage(self.name)

    def showAppList(self):
        appList = []
        for key in self.paper.env.apps:
            appList.append(key)
        self.show(appList)
