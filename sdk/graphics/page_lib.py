import time
import math

import sdk
from sdk.graphics import Page as _Page
from sdk.graphics.element_lib import ImageElement as _ImageElement
import sdk.graphics.element_lib


class ListPage(_Page):
    def __init__(self, paper, name):
        super().__init__(paper, name)

        self.add_element(sdk.graphics.element_lib.Button(
            (0, 0), self.paper, "", self.close, (45, 30)))

        self.add_element(_ImageElement(
            (0, 0), self.paper, "resources/images/list.png"))

        self.closeBtnCover = sdk.graphics.element_lib.Label((0, 0), self.paper, "")
        self.add_element(self.closeBtnCover)

        self.icons = (
            sdk.graphics.element_lib.ImageElement(
                (8, 36), self.paper, "resources/images/None20px.jpg"),
            sdk.graphics.element_lib.ImageElement(
                (8, 66), self.paper, "resources/images/None20px.jpg"),
            sdk.graphics.element_lib.ImageElement(
                (8, 96), self.paper, "resources/images/None20px.jpg")
        )

        for icon in self.icons:
            self.add_element(icon)

        self.label_of_page = sdk.graphics.element_lib.Label(
            (155, 0), self.paper, "", (55, 28))
        self.add_element(self.label_of_page)

        self.title_of_list = sdk.graphics.element_lib.Label(
            (50, 0), self.paper, "", (105, 28))
        self.add_element(self.title_of_list)

        self.listTexts = (
            sdk.graphics.element_lib.Button(
                (35, 32), self.paper, "", self.item_onclick_handler, (260, 28), outline=None, index=0),
            sdk.graphics.element_lib.Button(
                (35, 62), self.paper, "", self.item_onclick_handler, (260, 28), outline=None, index=1),
            sdk.graphics.element_lib.Button(
                (35, 92), self.paper, "", self.item_onclick_handler, (260, 28), outline=None, index=2)
        )
        for listText in self.listTexts:
            self.add_element(listText)

        self.more_items_dots = sdk.graphics.element_lib.ImageElement(
            (105, 122), self.paper, "resources/images/more_items_dots.jpg")

        self.add_element(self.more_items_dots)

        self.total_pages_of_content = 0
        self.current_page_of_content = 0

        self.content = []

        self.listTitle = ""
        self.closeEvent = None
        # 格式为：[[text, image, func]]
        # 其中 func 会收到一个index参数，来知道自己是第几个(以0开始)

    def item_onclick_handler(self, index=None):
        if index is not None:
            index_in_list = (self.current_page_of_content - 1) * 3 + index
            if index_in_list < len(self.content):
                self.content[index_in_list][2](index_in_list)  # 传入index

    def close(self):
        if self.closeEvent is not None:
            self.closeEvent()
        self.content = []
        self.listTitle = ""

    def show_items(self):

        self.label_of_page.set_text(
            "%d/%d" % (self.current_page_of_content, self.total_pages_of_content))

        if self.current_page_of_content < self.total_pages_of_content:
            self.more_items_dots.set_image(
                "resources/images/more_items_dots.jpg")
        else:
            self.more_items_dots.set_image("resources/images/None1px.jpg")

        index_of_the_first = (self.current_page_of_content - 1) * 3
        for i in range(0, 3):
            if index_of_the_first + i < len(self.content):
                # 设置item的文字
                self.listTexts[i].set_text(
                    self.content[index_of_the_first + i][0])
                # 设置item的图标
                if self.content[index_of_the_first + i][1] is not None:
                    self.icons[i].set_image(
                        self.content[index_of_the_first + i][1])
                else:
                    self.icons[i].set_image("resources/images/None20px.jpg")
                # 不必在此更改点击事件

            else:
                self.listTexts[i].set_text("")
                self.icons[i].set_image("resources/images/None1px.jpg")
                # 也不必在此更改点击事件了

    def go_prev(self):
        if self.current_page_of_content > 1:
            self.paper.pause_update()  # 上锁，防止setText重复刷新屏幕
            self.current_page_of_content -= 1
            self.show_items()
            self.paper.recover_update()  # 解锁

    def go_next(self):
        if self.current_page_of_content < self.total_pages_of_content:
            self.paper.pause_update()  # 上锁，防止setText重复刷新屏幕
            self.current_page_of_content += 1
            self.show_items()
            self.paper.recover_update()  # 解锁

    def show(self, content=None, listTitle="", closeEvent=None, closeBtn=None):
        if content is None:
            content = [["空"], None, None]
        elif len(content) == 0:
            content = [["空"], None, None]
        self.content = content
        self.listTitle = listTitle
        self.closeEvent = closeEvent

        self.total_pages_of_content = math.ceil(len(self.content) / 3)
        self.current_page_of_content = 1

        self.paper.pause_update()  # 上锁，防止setText重复刷新屏幕

        self.title_of_list.set_text(self.listTitle)
        self.show_items()
        if closeBtn:
            self.closeBtnCover.set_visible(False)
        else:
            self.closeBtnCover.set_visible(True)

        self.paper.recover_update()  # 解锁

    def slide_co(self, distance):
        if distance > 0:
            self.go_prev()
        else:
            self.go_next()

    def init(self):
        super().init()
        self.paper.env.touch_handler.add_slide_y((0, 296, 35, 128), self.slide_co)

    def recover(self):
        super().recover()
        self.paper.env.touch_handler.add_slide_y((0, 296, 35, 128), self.slide_co)

    def exit(self):
        super().exit()
        self.paper.change_page("mainPage")


class Applistpage(ListPage):
    def open_app_by_index(self, index):
        if index >= 0:
            self.paper.env.open_app(list(self.paper.env.apps.keys())[index])

    def back_to_main_page(self):
        self.paper.change_page("mainPage")

    def show(self, content=None, listTitle="", closeEvent=None, closeBtn=None):  # TODO:此处原本出现签名不一致问题，临时改正
        app_list = []

        for appName, appContent in self.paper.env.apps.items():
            app_list.append([appName, appContent[1][1], self.open_app_by_index])

        super().show(app_list, "应用列表", self.back_to_main_page, True)


# keyboardPage 还未完成哦
class Keyboardpage(_Page):
    def __init__(self, paper, textHandler, pageName="keyboardPage"):
        super().__init__(paper, pageName)
        self.keyboardList = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
                             ["A", "S", "D", "F", "G", "H", "J", "K", "L", "←"],
                             ["↑", "Z", "X", "C", "V", "B", "N", "M", ",", "."]]
        self.keyboard = {}

        self.textInput = sdk.graphics.element_lib.Label(
            (0, 0), paper, "请点按键盘 ：）", (295, 30))
        self.add_element(self.textInput)

    def showKeyboard(self):
        for i in range(3):
            for j in range(10):
                nowChar = self.keyboardList[i][j]
                self.keyboard[nowChar] = sdk.graphics.element_lib.Button(
                    (j * 29 + 3, i * 30 + 36), self.paper, nowChar, self.addChar, (28, 29), char=nowChar)
                self.add_element(self.keyboard[nowChar])

    def addChar(self, char):
        self.textInput.set_text(self.textInput.get_text() + char)

    def show(self, inputType="text"):
        pass
