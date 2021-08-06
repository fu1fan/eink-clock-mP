import threading
import time

from PIL import Image, ImageFont, ImageDraw

import sdk.graphics.element_lib
import sdk.graphics.paper_lib
from main import environment

graphics = environment.graphics


class TextClock(graphics.Element):
    def __init__(self, xy, paper):
        super().__init__(xy, paper, (296, 128))
        self.last_update = -1
        self.image = Image.new("RGB", (296, 128), 0)
        self.stop_sign = False
        self.font25 = ImageFont.truetype(
            "resources/fonts/PTSerifCaption.ttc", 53)

    def update(self):
        while True:
            if self.stop_sign:
                return
            if self.last_update != time.localtime(time.time()).tm_min:
                self.paper.update(self.page)
            time.sleep(1)

    def init(self):
        t = threading.Thread(target=self.update)
        t.setDaemon(True)
        t.start()

    def exit(self):
        self.stop_sign = True

    def build(self) -> Image:
        now_time = time.strftime("%H : %M", time.localtime())
        now_image = self.image.copy()
        draw_image = ImageDraw.Draw(now_image)
        draw_image.text((58, 32), now_time, font=self.font25)
        self.last_update = time.localtime(time.time()).tm_min
        return now_image


def build(env: environment):
    paper = sdk.graphics.paper_lib.PaperTheme(env)
    # refreshBtn = sdk.graphics.lib.Button((0, 0), paper, "刷新", paper.refresh)
    textLabel = sdk.graphics.element_lib.Label((0, 90), paper, "标签1")

    def changeTheTextOfLabal():
        textLabel.setText("okk")

    # testBtn = sdk.graphics.lib.Button(
    #    (60, 90), paper, "测试", changeTheTextOfLabal)
    # text_clock = TextClock((0, 0), paper)
    # paper.addElement("mainPage", text_clock)
    # paper.addElement("mainPage", refreshBtn)
    # paper.addElement("mainPage", textLabel)
    # paper.addElement("mainPage", testBtn)
    keyboardList = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
                    ["A", "S", "D", "F", "G", "H", "J", "K", "L", "←"],
                    ["↑", "Z", "X", "C", "V", "B", "N", "M", ",", "."]]
    keyboard = {}

    textInput = sdk.graphics.element_lib.Label((0, 0), paper, "请点按键盘 ：）", (295, 30))
    paper.addElement("mainPage", textInput)

    def addChar(char):
        textInput.setText(textInput.getText()+char)

    for i in range(3):
        for j in range(10):
            nowChar = keyboardList[i][j]
            keyboard[nowChar] = sdk.graphics.element_lib.Button(
                (j * 29 + 3, i * 30 + 36), paper, nowChar, addChar, (28, 29), char=nowChar)
            paper.addElement("mainPage", keyboard[nowChar])

    return paper
