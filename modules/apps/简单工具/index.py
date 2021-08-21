from sdk.graphics import paper_lib, element_lib, page_lib
from pathlib import Path


def build(env):
    paper = paper_lib.PaperApp(env)

    def tools_item_oncick(index):
        if index == 0:
            paper.env.open_app("随机数生成器")
        elif index == 1:
            paper.env.open_app("简单计算器")
        elif index == 2:
            paper.env.open_app("祖安宝典")

    tools = [
        ["随机数生成器", Path("resources/images/random.png"), tools_item_oncick],
        ["简单计算器", Path("resources/images/calculator.png"), tools_item_oncick],
        ["祖安宝典", Path("resources/images/zuan.png"), tools_item_oncick]
    ]

    tools_list = page_lib.ListPage(paper, "mainPage")
    paper.pages["mainPage"] = tools_list
    tools_list.show(tools, "简单工具", None)

    return paper
