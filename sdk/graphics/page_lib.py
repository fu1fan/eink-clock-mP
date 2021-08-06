import time

import sdk
from sdk.graphics import Page as _Page
from sdk.graphics.element_lib import ImageElement as _ImageElement
import sdk.graphics.element_lib


class ListPage(_Page):
    def __init__(self, paper, name):
        super().__init__(paper, name)

        self.addElement(sdk.graphics.element_lib.Button(
            (0, 0), self.paper, "", self.close, (45, 30)))

        self.addElement(sdk.graphics.element_lib.Button(
            (200, 0), self.paper, "", self.goPrev, (53, 30)))
        self.addElement(sdk.graphics.element_lib.Button(
            (254, 0), self.paper, "", self.goNext, (41, 30)))

        self.addElement(_ImageElement(
            (0, 0), self.paper, "resources/images/list.jpg"))

        self.label_of_page = sdk.graphics.element_lib.Label(
            (50, 0), self.paper, "", (150, 28))
        self.addElement(self.label_of_page)

        self.labels = (
            sdk.graphics.element_lib.Label(
                (45, 32), self.paper, "", (296, 28)),
            sdk.graphics.element_lib.Label(
                (45, 62), self.paper, "", (296, 28)),
            sdk.graphics.element_lib.Label(
                (45, 92), self.paper, "", (296, 28)),
        )
        for label in self.labels:
            self.addElement(label)

        self.content = []   # [[text, image, func]]

    def close(self):
        self.paper.changePage("mainPage")

    def showItems(self):
        index_of_the_first = (self.current_page_of_content-1)*3
        for i in range(0, 3):
            if (index_of_the_first + i < len(self.content)):
                self.labels[i].setText(self.content[index_of_the_first + i][0])
            else:
                self.labels[i].setText("")
            

    def goPrev(self):
        if (self.current_page_of_content > 1):
            self.paper.pause_update()  # 上锁，防止setText重复刷新屏幕
            self.current_page_of_content -= 1
            self.showItems()
            self.paper.recover_update()  # 解锁

    def goNext(self):
        if (self.current_page_of_content < self.total_pages_of_content):
            self.paper.pause_update()  # 上锁，防止setText重复刷新屏幕
            self.current_page_of_content += 1
            self.showItems()
            self.paper.recover_update()  # 解锁

    def show(self, content=[]):
        self.content = content

        # 下面这行为临时测试用，图片处理还没解决好↓
        self.content = [["app1", "img1", self.close], ["app2", "img2", self.close], [
            "app3", "app3", self.close], ["app4", "img4", self.close]]

        self.total_pages_of_content = len(self.content) // 3 + 1
        self.current_page_of_content = 1

        self.paper.pause_update()  # 上锁，防止setText重复刷新屏幕

        self.label_of_page.setText(
            "第 %d 页/共 %d 页" % (self.current_page_of_content, self.total_pages_of_content))

        self.showItems()

        self.paper.changePage(self.name)
        self.paper.recover_update()  # 解锁

    def showAppList(self):
        appList = []
        for key in self.paper.env.apps:
            appList.append(key)
        self.show(appList)
