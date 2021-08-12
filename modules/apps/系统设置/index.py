from sdk.graphics import paper_lib, element_lib, page_lib


def build(env):
    paper = paper_lib.PaperApp(env)

    def backToMain():
        paper.changePage("mainPage")

    def settingItemOncick(index):
        print(index)
        if index == 0:
            paper.env.openApp("账号管理")
        elif index == 1:
            paper.changePage["wifi"]

    settings = [
        ["账号管理", None, settingItemOncick]
    ]

    def showGeneralSettings():
        paper.changePage("generalSettings")
        generalSettings.show(settings, "通用设置", backToMain)


    paper.addElement("mainPage", element_lib.Label(
        (100, 0), paper, "系统设置", (100, 30), "black", "while"))
    paper.addElement("mainPage", element_lib.Button(
        (0, 35), paper, "通用设置", showGeneralSettings, (296, 30), "white", "black"))

    generalSettings = page_lib.ListPage(paper,"generalSettings")
    paper.addPage("generalSettings",generalSettings)


    return paper
