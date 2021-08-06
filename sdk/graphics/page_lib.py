from sdk.graphics import Page as _Page
from sdk.graphics.element_lib import ImageElement as _ImageElement


class ListPage(_Page):
    def __init__(self, paper, name):
        super().__init__(paper, name)
        self.addElement(_ImageElement((0, 0), self.paper, "resources/images/list.jpg"))
        self.content = []

    def show(self, content=[]):
        self.content = content
        self.paper.changePage(self.name)

    def show_app(self):
        pass
