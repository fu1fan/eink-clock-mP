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


        self.icons = (
            sdk.graphics.element_lib.ImageElement((8,36),self.paper,"resources/images/None20px.jpg"),
            sdk.graphics.element_lib.ImageElement((8,66),self.paper,"resources/images/None20px.jpg"),
            sdk.graphics.element_lib.ImageElement((8,96),self.paper,"resources/images/None20px.jpg")
        )

        for icon in self.icons:
            self.addElement(icon)

        self.label_of_page = sdk.graphics.element_lib.Label(
            (50, 0), self.paper, "", (150, 28))
        self.addElement(self.label_of_page)

        self.labels = (
            sdk.graphics.element_lib.Label(
                (35, 32), self.paper, "", (296, 28)),
            sdk.graphics.element_lib.Label(
                (35, 62), self.paper, "", (296, 28)),
            sdk.graphics.element_lib.Label(
                (35, 92), self.paper, "", (296, 28))
        )
        for label in self.labels:
            self.addElement(label)

        self.total_pages_of_content = 0
        self.current_page_of_content = 0

        self.content = []  # [[text, image, func]]

    def close(self):
        self.paper.changePage("mainPage")

    def showItems(self):
        
        self.label_of_page.setText(
            "第 %d 页/共 %d 页" % (self.current_page_of_content, self.total_pages_of_content))

        index_of_the_first = (self.current_page_of_content-1)*3
        for i in range(0, 3):
            if index_of_the_first + i < len(self.content):
                self.labels[i].setText(self.content[index_of_the_first + i][0])
                if self.content[index_of_the_first + i][1] != None:
                    self.icons[i].setImage(self.content[index_of_the_first + i][1])
                else:
                    self.icons[i].setImage("resources/images/None20px.jpg")

            else:
                self.labels[i].setText("")
                self.icons[i].setImage("resources/images/None20px.jpg")
            

    def goPrev(self):
        if self.current_page_of_content > 1:
            self.paper.pause_update()  # 上锁，防止setText重复刷新屏幕
            self.current_page_of_content -= 1
            self.showItems()
            self.paper.recover_update()  # 解锁

    def goNext(self):
        if self.current_page_of_content < self.total_pages_of_content:
            self.paper.pause_update()  # 上锁，防止setText重复刷新屏幕
            self.current_page_of_content += 1
            self.showItems()
            self.paper.recover_update()  # 解锁

    def show(self, content=None):
        if content is None:
            content = []
        self.content = content

        # 下面这行为临时测试用，图片处理还没解决好↓
        self.content = [["app1", None, self.close], ["app2", "resources/images/None18px.jpg", self.close], [
            "app3", None, self.close], ["app4", "resources/images/None18px.jpg", self.close]]

        self.total_pages_of_content = len(self.content) // 3 + 1
        self.current_page_of_content = 1

        self.paper.pause_update()  # 上锁，防止setText重复刷新屏幕

        self.showItems()

        self.paper.changePage(self.name)
        self.paper.recover_update()  # 解锁

    def showAppList(self):
        appList = []
        for key in self.paper.env.apps:
            appList.append(key)
        self.show(appList)
