from sdk.graphics import paper_lib, element_lib, page_lib

from pathlib import Path


def build(env):
    paper = paper_lib.PaperApp(env)

    def poweroff():
        poweroff_btn.set_text("正在关机")
        paper.env.poweroff()

    def reboot():
        reboot_btn.set_text("正在重启")
        paper.env.reboot()

    poweroff_btn = element_lib.Button((100, 63), paper, "点击关机", poweroff, (90, 30))
    reboot_btn = element_lib.Button((100, 95), paper, "点击重启", reboot, (90, 30))

    def setting_item_oncick(index):
        print(index)
        if index == 1:
            paper.env.open_app("账号管理")
        elif index == 2:
            content = [["返回", Path("resources/images/back.png"), back_to_system_settings],
                       ["跟你说了没完工为啥点进来呢？", None, None]]
            wifi_settings.show(content, "WiFi设置")
            paper.change_page("wifiSettings")

    def back_to_system_settings(index=0):
        paper.change_page("settingsPage")

    def show_system_settings():
        settings_list.show(settings, "系统设置", None)
        paper.change_page("settingsPage")

    def back_to_main(index=0):
        paper.change_page("mainPage")

    settings = [
        ["返回", Path("resources/images/back.png"), back_to_main],
        ["账号管理", Path("resources/images/settings.png"), setting_item_oncick],
        ["WIFI设置（暂未完工）", None, setting_item_oncick],
    ]

    paper.add_element(element_lib.Label((100, 0), paper, "系统选项", (90, 30)))
    paper.add_element(element_lib.Button((100, 31), paper, "系统设置", show_system_settings, (90, 30)))
    paper.add_element(poweroff_btn)
    paper.add_element(reboot_btn)

    settings_list = page_lib.ListPage(paper, "settingsPage")
    paper.add_page("settingsPage", settings_list)

    wifi_settings = page_lib.ListPage(paper, "wifiSettings")
    paper.add_page("wifiSettings", wifi_settings)

    return paper
