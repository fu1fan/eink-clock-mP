import threading
from math import ceil
from pathlib import Path
import traceback

from PIL import ImageFont, Image, ImageDraw

from sdk.graphics import Element, PaperDynamic


class ImageElement(Element):
    def __init__(self, xy: tuple, paper: PaperDynamic, image_path: str):
        super().__init__(xy, paper)
        self._set_image(image_path)

    def _set_image(self, image_path):
        try:
            self.image = Image.open(Path(image_path)).convert("RGBA")
            self.size = (self.image.size[0], self.image.size[1])
        except:
            self.image = None
            self.paper.env.logger_env.error(traceback.format_exc())

    def set_image(self, new_image_path):
        self._set_image(new_image_path)
        self.paper.update(self.page.name)

    def get_image(self) -> Image:
        return self.image

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
        self.background_image = Image.new("RGBA", size, bgcolor)

    def is_visible(self):
        return self._visible

    def set_visible(self, m: bool):
        self._visible = m
        self.paper.update(self.page.name)

    def get_text(self):
        return self.text

    def set_text(self, newText):
        self.text = newText
        self.paper.update(self.page.name)

    def build(self):
        if self.inited and self._visible:
            image = self.background_image.copy()
            image_draw = ImageDraw.ImageDraw(image)
            # image_draw.rectangle((0, 0, self.size[0], self.size[1]), fill="white", outline="black", width=1)
            image_draw.text((5, 5), self.text,
                            font=self.font, fill=self.textColor)
            return image
        elif not self._visible:
            return None


class Button(TextElement):
    def __init__(self, xy, paper: PaperDynamic, text, onclick, size=(50, 30), bgcolor="white", textColor="black",
                 fontSize=20, outline="black", *args, **kwargs):
        super().__init__(xy, paper, text, size, bgcolor,
                         textColor, fontSize, *args, **kwargs)
        self.on_clicked = onclick
        self.outline = outline

    def clicked_handler(self, *args, **kwargs):
        if self._visible and self.inited:
            self.on_clicked(*args, **kwargs)

    def set_on_clicked(self, onclickFunc):
        self.on_clicked = onclickFunc

    def _add_button_clicked(self):
        self.paper.env.touch_handler.add_clicked((self.xy[0], self.xy[0] + self.size[0],
                                                  self.xy[1], self.xy[1] + self.size[1]),
                                                 self.clicked_handler,
                                                 *self.args,
                                                 **self.kwargs)

    def init(self):
        self._add_button_clicked()
        super().init()

    def recover(self):
        self._add_button_clicked()
        super().recover()

    def build(self) -> Image:
        if self.inited and self._visible:
            image = self.background_image.copy()
            image_draw = ImageDraw.ImageDraw(image)
            if self.outline is not None:
                image_draw.rectangle(
                    (0, 0, self.size[0] - 1, self.size[1] - 1), outline=self.outline, width=2)
            image_draw.text((5, 5), self.text,
                            font=self.font, fill=self.textColor)
            return image
        elif not self._visible:
            return None


class Label(TextElement):
    def __init__(self, xy, paper: PaperDynamic, text, size=(50, 30), bgcolor="white", textColor="black", fontSize=20,
                 *args, **kwargs):
        super().__init__(xy, paper, text, size=size, bgcolor=bgcolor, textColor=textColor, fontSize=fontSize,
                         *args, **kwargs)


class LabelWithMultipleLines(TextElement):

    def build(self) -> Image:
        if self.inited and self._visible:
            self.width = self.size[0]
            # 段落 , 行数, 行高
            self.duanluo, self.note_height, self.line_height = self.split_text()

            image = self.background_image.copy()
            draw = ImageDraw.Draw(image)
            # 左上角开始
            x, y = 0, 0
            for duanluo, line_count in self.duanluo:
                draw.text((x, y), duanluo, fill=self.textColor, font=self.font)
                y += self.line_height * line_count

            return image

        elif not self._visible:
            return None

    def get_duanluo(self, text):
        txt = Image.new('RGBA', self.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt)
        # 所有文字的段落
        duanluo = ""
        # 宽度总和
        sum_width = 0
        # 几行
        line_count = 1
        # 行高
        line_height = 0
        for char in text:
            width, height = draw.textsize(char, self.font)
            sum_width += width
            if sum_width > self.width:  # 超过预设宽度就修改段落 以及当前行数
                line_count += 1
                sum_width = 0
                duanluo += '\n'
            duanluo += char
            line_height = max(height, line_height)
        if not duanluo.endswith('\n'):
            duanluo += '\n'
        return duanluo, line_height, line_count

    def split_text(self):
        # 按规定宽度分组
        max_line_height, total_lines = 0, 0
        all_text = []
        for text in self.text.split('\n'):
            duanluo, line_height, line_count = self.get_duanluo(text)
            max_line_height = max(line_height, max_line_height)
            total_lines += line_count
            all_text.append((duanluo, line_count))
        line_height = max_line_height
        total_height = total_lines * line_height
        return all_text, total_height, line_height


class ListItem:
    def __init__(self, text=None, func=lambda: None, icon=None):
        self.icon = icon
        self.text = text
        self.func = func


class List(Element):
    def __init__(self, paper):
        super().__init__((0, 0), paper, size=(296, 128), background=Image.open("resources/images/list.png"))
        self.content = None
        self.active = False
        self.page_count = 0
        self.current_page = -1
        self.title = ""
        self.last_build_index = -1
        self.last_build = self.background

    def hide(self):
        if self.active:
            self.active = False
            self.paper.update(self.page)
        else:
            return 0

    def go_prev(self):
        if self.active:
            if self.current_page > 0:
                self.current_page -= 1
                self.paper.update(self.page)

    def go_next(self):
        if self.active:
            if self.current_page < self.page_count:
                self.current_page += 1
                self.paper.update(self.page)

    def show(self, title: str, content: list[ListItem]):
        if not self.active:
            self.active = True
            self.paper.add_back_operation(self.hide)
            self.last_build_index = -1
        self.title = title
        self.content = content
        self.page_count = ceil(len(content) / 3)
        self.current_page = 0
        self.paper.update(self.page)

    def exit(self):
        if self.active:
            self.content = None
            self.active = False
            self.page_count = 0
            self.current_page = -1
            self.title = ""
            self.last_build_index = -1
            self.last_build = self.background

    def build(self):
        if self.active:
            if self.last_build_index == self.current_page:
                return self.last_build
            else:
                new_image = self.background.copy()
                draw = ImageDraw.Draw(new_image)
                j = 0
                draw.text((35, 32), "title", fill="black", font=self.paper.env.fonts.get_heiti(20))
                for i in range(self.current_page * 3, self.current_page * 3 + 3):
                    try:
                        if self.content[i].icon:
                            new_image.paste(self.content[i].icon, (8, 36+30*j))
                            draw.text((35, 32), self.content[i].text, fill="black", font=self.paper.env.fonts.get_heiti(20))
                        else:
                            draw.text((12, 32+30*j), self.content[i].text, fill="black", font=self.paper.env.fonts.get_heiti(20))
                    except IndexError:
                        break
                    j += 1
                self.last_build = new_image
                self.last_build_index = self.current_page
                return new_image


class ListWithIndexReturn(List):
    def __init__(self, paper):
        super().__init__(paper)
        self.return_lock = threading.Event()
        self.result = None

    def _func1(self):
        self.result = self.current_page*3
        self.return_lock.set()

    def _func2(self):
        self.result = self.current_page*3 + 1
        self.return_lock.set()

    def _func3(self):
        self.result = self.current_page*3 + 2
        self.return_lock.set()

    def hide(self):
        if self.active:
            self.active = False
            self.paper.env.touch_handler.remove_clicked(self._func1)
            self.paper.env.touch_handler.remove_clicked(self._func2)
            self.paper.env.touch_handler.remove_clicked(self._func3)
            self.paper.update(self.page)
        else:
            return 0

    def recover(self):
        self.paper.env.touch_handler.add_clicked((0, 296, 30, 60), self._func1)
        self.paper.env.touch_handler.add_clicked((0, 296, 60, 90), self._func2)
        self.paper.env.touch_handler.add_clicked((0, 296, 90, 120), self._func3)

    def show(self, title: str,content: list[ListItem]):
        if not self.active:
            self.active = True
            self.paper.add_back_operation(self.hide)
            self.last_build_index = -1
            self.paper.env.touch_handler.add_clicked((0, 296, 30, 60), self._func1)
            self.paper.env.touch_handler.add_clicked((0, 296, 60, 90), self._func2)
            self.paper.env.touch_handler.add_clicked((0, 296, 90, 120), self._func3)
        self.title = title
        self.content = content
        self.page_count = ceil(len(content) / 3)
        self.current_page = 0
        self.paper.update(self.page)
        self.return_lock.clear()
        self.return_lock.wait()
        return self.result


class ListWithFunc(ListWithIndexReturn):
    def __init__(self, paper):
        super().__init__(paper)

    def _func1(self):
        self.content[self.current_page*3].func()

    def _func2(self):
        self.content[self.current_page*3+1].func()

    def _func3(self):
        self.content[self.current_page*3+2].func()

    def show(self, title: str, content: list[ListItem]):
        if not self.active:
            self.active = True
            self.paper.add_back_operation(self.hide)
            self.last_build_index = -1
            self.paper.env.touch_handler.add_clicked((0, 296, 30, 60), self._func1)
            self.paper.env.touch_handler.add_clicked((0, 296, 60, 90), self._func2)
            self.paper.env.touch_handler.add_clicked((0, 296, 90, 120), self._func3)
        self.title = title
        self.content = content
        self.page_count = ceil(len(content) / 3)
        self.current_page = 0
        self.paper.update(self.page)