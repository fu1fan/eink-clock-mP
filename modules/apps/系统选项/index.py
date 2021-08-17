from sdk.graphics import paper_lib, element_lib, page_lib

from pathlib import Path


def build(env):
    paper = paper_lib.PaperApp(env)

    def poweroff():
        poweroffBtn.setText("正在关机")
        paper.env.poweroff()

    def reboot():
        rebootBtn.setText("正在重启")
        paper.env.reboot()

    poweroffBtn = element_lib.Button((100,63),paper,"点击关机",poweroff,(90,30))
    rebootBtn = element_lib.Button((100,95),paper,"点击重启",reboot,(90,30))

    def settingItemOncick(index):
        print(index)
        if index == 0:
            paper.env.openApp("账号管理")
        elif index == 1:
            paper.changePage["wifi"]

    def showSystemSettings():
        settingsList.show(settings, "系统设置", None)
        paper.changePage("settingsPage")

    def backToMain(index=0):
        paper.changePage("mainPage")


    settings = [
        ["返回", Path("resources/images/back.png"), backToMain],
        ["账号管理", Path("resources/images/settings.png"), settingItemOncick],
        ["网络设置（暂未完工）", None, None],
    ]

    paper.addElement(element_lib.Label((100,0),paper,"系统选项",(90,30)))
    paper.addElement(element_lib.Button((100,31),paper,"系统设置",showSystemSettings,(90,30)))
    paper.addElement(poweroffBtn)
    paper.addElement(rebootBtn)

    settingsList = page_lib.ListPage(paper,"settingsPage")
    paper.addPage("settingsPage", settingsList)


    return paper
