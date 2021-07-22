import threading
import time

from PIL import Image, ImageFont, ImageDraw

from sdk import display
from sdk import general


class TextClock(display.Element):
    def __init__(self, x, y, paper):
        super().__init__(x, y, paper)
        self.last_update = -1
        self.image = Image.new("RGB", (296, 128), 1)

    def update(self):
        if self.last_update != time.localtime(time.time()).tm_min:
            self.paper.update()

    def init(self):
        self.paper.register(self.paper.SECONDLY, self.update)

    def build(self) -> Image:
        now_time = time.strftime("%H : %M", time.localtime())
        now_image = self.image.copy()
        draw_image = ImageDraw.Draw(now_image)
        font25 = ImageFont.truetype("resources/fonts/PTSerifCaption.ttc", 25)
        draw_image.text((50, 50), now_time, font=font25, fill=225)
        self.last_update = time.localtime(time.time()).tm_min
        return now_image


class Theme:
    def __init__(self, epd: display.EpdController, lock: threading.Lock, pool: general.ThreadPool):
        self.epd = epd
        self.lock = lock
        self.pool = pool

    def build(self):
        paper = display.PaperDynamic(self.epd, self.lock, self.pool)
        text_clock = TextClock(0, 0, paper)
        paper.addElement("mainPaper", text_clock)
        return paper
