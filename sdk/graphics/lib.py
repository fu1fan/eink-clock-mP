import time

from PIL import ImageFont, Image, ImageDraw

from sdk.graphics import Element, PaperDynamic


class TextElement(Element):
    def __init__(self, xy, paper: PaperDynamic, text, size=(60, 33), bgcolor="white", textColor="black", fontSize=20,
                 *args, **kwargs):
        super().__init__(xy, size, paper)
        self.text = text
        self._visible = True
        self.size = size
        self.args = args
        self.kwargs = kwargs
        self.font = ImageFont.truetype(
            "resources/fonts/STHeiti_Light.ttc", fontSize)
        self.textColor = textColor
        if bgcolor == "white":
            self.background_image = Image.new("RGB", size, (255, 255, 255))
        elif bgcolor == "black":
            self.background_image = Image.new("RGB", size, (0, 0, 0))

    def isVisible(self):
        return self._visible

    def setVisible(self, m: bool):
        self._visible = m
        self.paper.update_async(self.page)

    def getText(self):
        return self.text

    def setText(self,newText):
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

    def init(self):
        self.inited = True


class Button(TextElement):
    def __init__(self, xy, paper: PaperDynamic, text, onclick, size=(60, 33), bgcolor="white", textColor="black",
                 fontSize=20, *args, **kwargs):
        super().__init__(xy, paper, text, size, bgcolor,
                         textColor, fontSize, *args, **kwargs)
        self.on_clicked = onclick

    def clickedHandler(self):
        if self._visible and self.inited:
            self.on_clicked()

    def init(self):
        super().init()
        self.paper.env.touch_handler.add_clicked((self.xy[0], self.xy[0] + self.size[0],
                                                  self.xy[1], self.xy[1] + self.size[1]),
                                                 self.clickedHandler,
                                                 *self.args,
                                                 **self.kwargs)


class Label(TextElement):
    def __init__(self, xy, paper: PaperDynamic, text, size=(60, 33), bgcolor="black", textColor="white", fontSize=20, *args, **kwargs):
        super().__init__(xy, paper, text, size=size, bgcolor=bgcolor, textColor=textColor, fontSize=fontSize, *args, **kwargs)
    
