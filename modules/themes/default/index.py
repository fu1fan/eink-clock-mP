import threading
import time

from PIL import Image, ImageFont, ImageDraw

from main import environment

display = environment.graphics


class TextClock(display.Element):
    def __init__(self, x, y, paper):
        super().__init__(x, y, paper)
        self.last_update = -1
        self.image = Image.new("RGB", (296, 128), 0)
        self.stop_sign = False
        self.font25 = ImageFont.truetype("resources/fonts/PTSerifCaption.ttc", 53)
        self.paper.touch_handler.add_clicked((0, 296, 0, 128), self.paper.refresh)

    def __del__(self):
        self.stop_sign = True

    def update(self):
        while True:
            if self.stop_sign:
                return
            if self.last_update != time.localtime(time.time()).tm_min:
                self.paper.update()
            time.sleep(1)

    def init(self):
        t = threading.Thread(target=self.update)
        t.setDaemon(True)
        t.start()

    def build(self) -> Image:
        now_time = time.strftime("%H : %M", time.localtime())
        now_image = self.image.copy()
        draw_image = ImageDraw.Draw(now_image)
        draw_image.text((58, 32), now_time, font=self.font25)
        self.last_update = time.localtime(time.time()).tm_min
        return now_image


def build(env: environment):
    paper = display.PaperDynamic(env)
    text_clock = TextClock(0, 0, paper)
    paper.addElement("mainPage", text_clock)
    return paper
