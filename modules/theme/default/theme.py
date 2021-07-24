import threading
import time

from PIL import Image, ImageFont, ImageDraw

from sdk import threadpool_mini
from sdk import display


class TextClock(display.Element):
    def __init__(self, x, y, paper, pool: threadpool_mini.ThreadPool):
        super().__init__(x, y, paper, pool)
        self.last_update = -1
        self.image = Image.new("RGB", (296, 128), 0)
        self.pool = pool
        self.stop_sign = False
        self.font25 = ImageFont.truetype("resources/fonts/PTSerifCaption.ttc", 54)

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
        threading.Thread(target=self.update()).start()

    def build(self) -> Image:
        now_time = time.strftime("%H : %M", time.localtime())
        now_image = self.image.copy()
        draw_image = ImageDraw.Draw(now_image)
        draw_image.text((58, 32), now_time, font=self.font25)
        self.last_update = time.localtime(time.time()).tm_min
        return now_image


class Theme:
    def __init__(self, epd: display.EpdController, pool: threadpool_mini.ThreadPool):
        self.epd = epd
        self.pool = pool

    def build(self):
        paper = display.PaperDynamic(self.epd, self.pool)
        text_clock = TextClock(0, 0, paper, self.pool)
        paper.addElement("mainPaper", text_clock)
        return paper
