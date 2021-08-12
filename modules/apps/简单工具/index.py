from sdk.graphics import paper_lib, element_lib, page_lib


def build(env):
    paper = paper_lib.PaperApp(env)

    def toolsItemOncick(index):
        if index == 0:
            paper.env.openApp("随机数生成器")
        elif index == 1:
            paper.env.openApp("简单计算器")
        elif index == 2:
            paper.env.openApp("祖安宝典")

    tools = [
        ["随机数生成器", "resources/images/random.png", toolsItemOncick],
        ["简单计算器", "resources/images/calculator.png", toolsItemOncick],
        ["祖安宝典", "resources/images/zuan.png",toolsItemOncick]
    ]

    toolsList = page_lib.ListPage(paper,"mainPage")
    paper.pages["mainPage"] = toolsList
    toolsList.show(tools, "简单工具", None)

    return paper
