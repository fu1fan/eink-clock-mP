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
            sdk.graphics.element_lib.ImageElement(
                (8, 36), self.paper, "resources/images/None20px.jpg"),
            sdk.graphics.element_lib.ImageElement(
                (8, 66), self.paper, "resources/images/None20px.jpg"),
            sdk.graphics.element_lib.ImageElement(
                (8, 96), self.paper, "resources/images/None20px.jpg")
        )

        for icon in self.icons:
            self.addElement(icon)

        self.label_of_page = sdk.graphics.element_lib.Label(
            (50, 0), self.paper, "", (150, 28))
        self.addElement(self.label_of_page)

        self.listTexts = (
            sdk.graphics.element_lib.Button(
                (35, 32), self.paper, "", self.defaultOnclickEvent, (260, 28), "white", "black"),
            sdk.graphics.element_lib.Button(
                (35, 62), self.paper, "", self.defaultOnclickEvent, (260, 28), "white", "black"),
            sdk.graphics.element_lib.Button(
                (35, 92), self.paper, "", self.defaultOnclickEvent, (260, 28), "white", "black")
        )
        for listText in self.listTexts:
            self.addElement(listText)

        self.more_items_dots = sdk.graphics.element_lib.ImageElement(
            (105, 122), self.paper, "resources/images/more_items_dots.jpg")

        self.addElement(self.more_items_dots)

        self.total_pages_of_content = 0
        self.current_page_of_content = 0

        self.content = []
        # 格式为：[[text, image, func]]
        """
        示例：
        [["app1", None, self.close], ["app2", "resources/images/None18px.jpg", self.close], [
            "app3", None, self.close], ["app4", "resources/images/None18px.jpg", self.close]]
        """

    def defaultOnclickEvent(self):
        print("\nClicked!")

    def testOnclickEvent(self):
        print("\nTest Clicked!")

    def close(self):
        self.paper.changePage("mainPage")

    def showItems(self):

        self.label_of_page.setText(
            "第 %d 页/共 %d 页" % (self.current_page_of_content, self.total_pages_of_content))

        if self.current_page_of_content < self.total_pages_of_content:
            self.more_items_dots.setImage(
                "resources/images/more_items_dots.jpg")
        else:
            self.more_items_dots.setImage("resources/images/None1px.jpg")

        index_of_the_first = (self.current_page_of_content-1)*3
        for i in range(0, 3):
            if index_of_the_first + i < len(self.content):
                # 设置item的文字
                self.listTexts[i].setText(
                    self.content[index_of_the_first + i][0])
                # 设置item的图标
                if self.content[index_of_the_first + i][1] != None:
                    self.icons[i].setImage(
                        self.content[index_of_the_first + i][1])
                else:
                    self.icons[i].setImage("resources/images/None20px.jpg")
                # 设置item的点击事件
                if self.content[index_of_the_first + i][2] != None:
                    self.listTexts[i].setOnclick(
                        self.content[index_of_the_first + i][2])
                else:
                    self.listTexts[i].setOnclick(self.defaultOnclickEvent)

            else:
                self.listTexts[i].setText("")
                self.icons[i].setImage("resources/images/None1px.jpg")
                self.listTexts[i].setOnclick(self.defaultOnclickEvent)

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

    def show(self, content=None):
        if content is None:
            content = []
        self.content = content

        self.total_pages_of_content = len(self.content) // 3 + 1
        self.current_page_of_content = 1

        self.paper.pause_update()  # 上锁，防止setText重复刷新屏幕

        self.showItems()

        self.paper.changePage(self.name)
        self.paper.recover_update()  # 解锁

    def showAppList(self):
        appList = []
        """
        for key in self.paper.env.apps:
            appList.append(key)
        """

        # 下面有点bug
        for appName, appContent in self.paper.env.apps.items():
            def warp():
                self.paper.env.changePaper(appContent[0].build(self.paper.env))
            appList.append([appName, appContent[1][0], warp])

        self.show(appList)


# keyboardPage 还未完成哦
class keyboardPage(_Page):
    def __init__(self, paper, textHandler, pageName="keyboardPage"):
        super().__init__(paper, pageName)
        self.keyboardList = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
                             ["A", "S", "D", "F", "G", "H", "J", "K", "L", "←"],
                             ["↑", "Z", "X", "C", "V", "B", "N", "M", ",", "."]]
        self.keyboard = {}

        self.textInput = sdk.graphics.element_lib.Label(
            (0, 0), paper, "请点按键盘 ：）", (295, 30))
        self.addElement(self.textInput)

    def showKeyboard(self):
        for i in range(3):
            for j in range(10):
                nowChar = self.keyboardList[i][j]
                self.keyboard[nowChar] = sdk.graphics.element_lib.Button(
                    (j * 29 + 3, i * 30 + 36), self.paper, nowChar, self.addChar, (28, 29), char=nowChar)
                self.addElement(self.keyboard[nowChar])

    def addChar(self, char):
        self.textInput.setText(self.textInput.getText()+char)

    def show(self, inputType="text"):
        pass
