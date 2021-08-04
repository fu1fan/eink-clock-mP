from PIL import ImageFont, Image, ImageDraw

from sdk.graphics import Element, PaperDynamic


class Button(Element):
    def __init__(self, x, y, paper: PaperDynamic, onclick, size=(60, 33), text="", *args, **kwargs):
        super().__init__(x, y, paper)
        self.on_clicked = onclick
        self.text = text
        self.__visible = True
        self.size = size
        self.args = args
        self.kwargs = kwargs
        self.font = ImageFont.truetype("resources/fonts/STHeiti_Light.ttc", 20)
        self.background_image = Image.new("RGB", size, (255, 255, 255))

    @property
    def visible(self):
        return self.__visible

    def setVisible(self, m: bool):
        self.__visible = m
        self.paper.update_async()

    def clickedHandler(self):
        if self.__visible and self.inited:
            self.on_clicked()

    def init(self):
        self.inited = True
        self.paper.env.touch_handler.add_clicked((self.x, self.x + self.size[0], self.y, self.y + self.size[1]),
                                                 self.clickedHandler,
                                                 *self.args,
                                                 **self.kwargs)

    def build(self) -> Image:
        if self.inited and self.__visible:
            image = self.background_image.copy()
            image_draw = ImageDraw.ImageDraw(image)
            image_draw.rectangle((0, 0, self.size[0], self.size[1]), fill="white", outline="black", width=1)
            image_draw.text((5, 5), self.text, font=self.font, fill=(0, 0, 0))
            return image
        elif not self.__visible:
            return None