import threading
import time

from PIL import Image, ImageFont, ImageDraw

import sdk.graphics.element_lib
import sdk.graphics.paper_lib
from sdk import configurator
from main import environment

graphics = environment.graphics


class TextClock(graphics.Element):
    def __init__(self, xy, paper):
        super().__init__(xy, paper, (296, 128))
        self.last_update = -1
        self.image = Image.new("RGBA", (296, 128), "black")
        self.stop_sign = False
        self.font25 = ImageFont.truetype(
            "resources/fonts/PTSerifCaption.ttc", 53)

    def update(self):
        while True:
            if self.stop_sign:
                return
            if self.last_update != time.localtime(time.time()).tm_min:
                self.paper.update(self.page.name)
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
    config = configurator.Configurator(
        env.logger_env, "configs/runtime.json", auto_save=True)

    firstRun = config.read_or_create("firstrun", True)

    text_clock = TextClock((0, 0), paper)
    paper.add_element(text_clock, "mainPage")

    # paper.addElement("mainPage", refreshBtn)
    # paper.addElement("mainPage", textLabel)
    # paper.addElement("mainPage", testBtn)

    def show_ad():
        time.sleep(3)
        config.set("firstrun", False)
        env.popup.prompt("使用提示", "点击屏幕最上方唤起菜单栏\n在APP内点击屏幕左上角可以唤起导航栏", Image.open("resources/images/help.png"))

    if firstRun:
        show_ad_thread = threading.Thread(target=show_ad)
        show_ad_thread.start()

    return paper
