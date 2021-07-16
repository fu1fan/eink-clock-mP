import threading

from sdk import epd2in9_V2 as epdDriver

from PIL import Image


class Page:
    def __init__(self, epd: epdDriver.EPD_2IN9_V2, lock: threading.Lock, x=296, y=128, image=None):
        self.inited = False
        if image is None:
            self.image = Image.new(1, (x, y), 1)
        else:
            self.image = image
        self.lock = lock
        self.epd = epd

    def __del__(self):
        if self.inited:
            self.epd.sleep()
            self.lock.release()

    def init(self):
        self.lock.acquire()
        self.inited = True
        self.epd.init()
        b_image = self.epd.get_buffer(self.image)
        self.epd.display_Base(b_image)
        self.epd.sleep()
        return True

    def refresh(self):
        if not self.inited:
            return
        self.epd.display_Base(self.image)
        return True
        self.epd.sleep()

    def update(self, image, refresh=False):
        if not self.inited:
            return
        self.image = image
        if refresh:
            self.refresh()
        else:
            self.epd.display_Partial(self.image)
        self.epd.sleep()


class PageDynamic(Page):
    pass


class PageHome(PageDynamic):
    pass


class PageApp(PageDynamic):
    pass
