from sdk.graphics import paper_lib, element_lib, page_lib


def build(env):
    paper = paper_lib.PaperApp(env)

    def settingItemOncick(index):
        print(index)
        if index == 0:
            paper.env.openApp("账号管理")
        elif index == 1:
            paper.changePage["wifi"]

    settings = [
        ["账号管理", "resources/images/settings.png", settingItemOncick],
        ["网络设置（暂未完工）", None, None],
    ]

    settingsList = page_lib.ListPage(paper,"mainPage")
    paper.pages["mainPage"] = settingsList
    settingsList.show(settings, "系统设置", None)

    return paper
