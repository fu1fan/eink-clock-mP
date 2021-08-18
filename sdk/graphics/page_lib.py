import time
import math

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


        self.closeBtnCover = sdk.graphics.element_lib.Label((0, 0), self.paper, "")
        self.addElement(self.closeBtnCover)

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
            (155, 0), self.paper, "", (55, 28))
        self.addElement(self.label_of_page)

        self.title_of_list = sdk.graphics.element_lib.Label(
            (50, 0), self.paper, "", (105, 28))
        self.addElement(self.title_of_list)

        self.listTexts = (
            sdk.graphics.element_lib.Button(
                (35, 32), self.paper, "", self.itemOnclickHandler, (260, 28), outline=None, index=0),
            sdk.graphics.element_lib.Button(
                (35, 62), self.paper, "", self.itemOnclickHandler, (260, 28), outline=None, index=1),
            sdk.graphics.element_lib.Button(
                (35, 92), self.paper, "", self.itemOnclickHandler, (260, 28), outline=None, index=2)
        )
        for listText in self.listTexts:
            self.addElement(listText)

        self.more_items_dots = sdk.graphics.element_lib.ImageElement(
            (105, 122), self.paper, "resources/images/more_items_dots.jpg")

        self.addElement(self.more_items_dots)

        self.total_pages_of_content = 0
        self.current_page_of_content = 0

        self.content = []

        self.listTitle = ""
        self.closeEvent = None
        # 格式为：[[text, image, func]]
        # 其中 func 会收到一个index参数，来知道自己是第几个(以0开始)

    def itemOnclickHandler(self, index=None):
        if index != None:
            indexInList = (self.current_page_of_content-1)*3+index
            if indexInList < len(self.content):
                self.content[indexInList][2](indexInList)  # 传入index

    def close(self):
        if self.closeEvent is not None:
            self.closeEvent()
        self.content = []
        self.listTitle = ""

    def showItems(self):

        self.label_of_page.setText(
            "%d/%d" % (self.current_page_of_content, self.total_pages_of_content))

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
                if self.content[index_of_the_first + i][1] is not None:
                    self.icons[i].setImage(
                        self.content[index_of_the_first + i][1])
                else:
                    self.icons[i].setImage("resources/images/None20px.jpg")
                # 不必在此更改点击事件

            else:
                self.listTexts[i].setText("")
                self.icons[i].setImage("resources/images/None1px.jpg")
                # 也不必在此更改点击事件了

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

    def show(self, content=None, listTitle="", closeEvent=None, closeBtn = None):
        if content is None:
            content = []
        self.content = content
        self.listTitle = listTitle
        self.closeEvent = closeEvent

        self.total_pages_of_content = math.ceil(len(self.content) / 3)
        self.current_page_of_content = 1

        self.paper.pause_update()  # 上锁，防止setText重复刷新屏幕

        self.title_of_list.setText(self.listTitle)
        self.showItems()
        if closeBtn:
            self.closeBtnCover.setVisible(False)
        else:
            self.closeBtnCover.setVisible(True)

        self.paper.recover_update()  # 解锁

    def slideCo(self, distance):
        if distance > 0:
            self.goPrev()
        else:
            self.goNext()

    def init(self):
        super().init()
        self.paper.env.touch_handler.add_slide_y((0, 296, 35, 128), self.slideCo)

    def recover(self):
        super().recover()
        self.paper.env.touch_handler.add_slide_y((0, 296, 35, 128), self.slideCo)

    def exit(self):
        super().exit()
        self.paper.changePage("mainPage")


class appListPage(ListPage):
    def openAppByIndex(self, index):
        if index >= 0:
            self.paper.env.openApp(list(self.paper.env.apps.keys())[index])
            

    def backToMainPage(self):
        self.paper.changePage("mainPage")

    def show(self):
        appList = []

        for appName, appContent in self.paper.env.apps.items():
            appList.append([appName, appContent[1][1], self.openAppByIndex])

        super().show(appList, "应用列表", self.backToMainPage, True)


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
