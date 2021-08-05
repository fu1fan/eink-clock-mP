from PIL import ImageFont, Image, ImageDraw

from sdk.graphics import Element, PaperDynamic

class TextElement(Element):
    def __init__(self, x, y, paper: PaperDynamic, text, size=(60, 33), bgcolor="white", textColor="black", fontSize=20, *args, **kwargs):
        super().__init__(x, y, paper)
        self.text = text
        self.__visible = True
        self.size = size
        self.args = args
        self.kwargs = kwargs
        self.font = ImageFont.truetype("resources/fonts/STHeiti_Light.ttc", fontSize)
        self.textColor = textColor
        if bgcolor=="white":
            self.background_image = Image.new("RGB", size, (255, 255, 255))
        elif bgcolor=="black":
            self.background_image = Image.new("RGB", size, (0, 0, 0))

    @property
    def visible(self):
        return self.__visible

    def setVisible(self, m: bool):
        self.__visible = m
        self.paper.update_async()

    def build(self) -> Image:
        if self.inited and self.__visible:
            image = self.background_image.copy()
            image_draw = ImageDraw.ImageDraw(image)
            #image_draw.rectangle((0, 0, self.size[0], self.size[1]), fill="white", outline="black", width=1)
            if self.textColor=="black":
                image_draw.text((5, 5), self.text, font=self.font, fill=(0, 0, 0))
            elif self.textColor=="white":
                image_draw.text((5, 5), self.text, font=self.font, fill=(255, 255, 255))
            return image
        elif not self.__visible:
            return None

    def init(self):
        self.inited = True

class Button(TextElement):
    def __init__(self, x, y, paper: PaperDynamic, text, onclick, size=(60, 33), bgcolor="white", textColor="black", fontSize=20, *args, **kwargs):
        super().__init__(x, y, paper, text, size, bgcolor, textColor, fontSize, *args, **kwargs)
        self.on_clicked = onclick

    def clickedHandler(self):
        if self.__visible and self.inited:
            self.on_clicked()

    def init(self):
        super().init()
        #print("%d  %d, %d  %d" % (self.x,self.y,self.size[0],self.size[1]))
        self.paper.env.touch_handler.add_clicked((self.x, self.x + self.size[0], self.y, self.y + self.size[1]),
                                                 self.clickedHandler,
                                                 *self.args,
                                                 **self.kwargs)
