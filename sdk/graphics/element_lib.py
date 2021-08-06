import traceback

from PIL import ImageFont, Image, ImageDraw

from sdk.graphics import Element, PaperDynamic


class ImageElement(Element):
    def __init__(self, xy: tuple, paper: PaperDynamic, image_path: str):
        super().__init__(xy, paper)
        try:
            file = open(image_path, "rb")
            self.image = Image.open(file)
            self.size = (self.image.size[0], self.image.size[1])
        except:
            self.image = None
            paper.env.logger_env.error(traceback.format_exc())

    def build(self) -> Image:
        return self.image


class TextElement(Element):
    def __init__(self, xy, paper: PaperDynamic, text, size=(50, 30), bgcolor="white", textColor="black", fontSize=20,
                 *args, **kwargs):
        super().__init__(xy, paper, size)
        self.text = text
        self._visible = True
        self.size = size
        self.args = args
        self.kwargs = kwargs
        self.font = ImageFont.truetype(
            "resources/fonts/STHeiti_Light.ttc", fontSize)
        self.textColor = textColor
        self.background_image = Image.new("RGB", size, bgcolor)

    def isVisible(self):
        return self._visible

    def setVisible(self, m: bool):
        self._visible = m
        self.paper.update_async(self.page)

    def getText(self):
        return self.text

    def setText(self, newText):
        self.text = newText
        self.paper.update_async(self.page)

    def build(self) -> Image:
        if self.inited and self._visible:
            image = self.background_image.copy()
            image_draw = ImageDraw.ImageDraw(image)
            # image_draw.rectangle((0, 0, self.size[0], self.size[1]), fill="white", outline="black", width=1)
            if self.textColor == "black":
                image_draw.text((5, 5), self.text,
                                font=self.font, fill=(0, 0, 0))
            elif self.textColor == "white":
                image_draw.text((5, 5), self.text,
                                font=self.font, fill=(255, 255, 255))
            return image
        elif not self._visible:
            return None


class Button(TextElement):
    def __init__(self, xy, paper: PaperDynamic, text, onclick, size=(50, 30), bgcolor="black", textColor="white",
                 fontSize=20, *args, **kwargs):
        super().__init__(xy, paper, text, size, bgcolor,
                         textColor, fontSize, *args, **kwargs)
        self.on_clicked = onclick

    def clickedHandler(self, *args, **kwargs):
        if self._visible and self.inited:
            self.on_clicked(*args, **kwargs)

    def init(self):
        super().init()
        self.paper.env.touch_handler.add_clicked((self.xy[0], self.xy[0] + self.size[0],
                                                  self.xy[1], self.xy[1] + self.size[1]),
                                                 self.clickedHandler,
                                                 *self.args,
                                                 **self.kwargs)


class Label(TextElement):
    def __init__(self, xy, paper: PaperDynamic, text, size=(50, 30), bgcolor="white", textColor="black", fontSize=20,
                 *args, **kwargs):
        super().__init__(xy, paper, text, size=size, bgcolor=bgcolor, textColor=textColor, fontSize=fontSize,
                         *args, **kwargs)
