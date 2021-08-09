from sdk.graphics import paper_lib, element_lib, page_lib

paper = None


def settingItemOncick(index):
    print(index)
    if index == 0:
        paper.env.openApp("账号管理")
    elif index == 1:
        paper.changePage["wifi"]


settings = [
    ["账号管理", None, settingItemOncick]
]


def build(env):
    global paper
    paper = paper_lib.PaperApp(env)

    paper.pages["mainPage"] = page_lib.ListPage(paper, "mainPage")
    paper.pages["mainPage"].show(settings, "系统设置")
    # paper.addPage["wifi"]

    return paper
