from sdk.graphics import Page as _Page
from sdk.graphics.element_lib import ImageElement as _ImageElement


class ListPage(_Page):
    def __init__(self, paper, name):
        super().__init__(paper)
        self.name = name
        self.append(_ImageElement((0, 0), self.paper, "resources/images/list.jpg"))
        self.content = []

    def show(self, content: list):
        self.content = content
        self.paper.changePage(self.name)
