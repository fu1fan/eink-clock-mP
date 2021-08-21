import threading

from PIL import Image

from sdk.graphics import element_lib, paper_lib, page_lib
import requests
import json
from sdk import configurator

favId = 0
zuanMode = "min"


def build(env):
    paper = paper_lib.PaperApp(env)

    fav_page = page_lib.ListPage(paper, "favPage")

    saver = configurator.Configurator(
        env.logger_env, "configs/zuan.json", auto_save=True)

    fav_list = saver.read_or_create("fav", [])

    zuan_label = element_lib.LabelWithMultipleLines(
        (5, 30), paper, "加载中...", (282, 80), fontSize=15)
    zuan_label_detail = element_lib.LabelWithMultipleLines(
        (5, 30), paper, "", (282, 80), fontSize=15)

    def back_to_main(index=0):
        paper.change_page("mainPage")

    def back_to_list():
        paper.change_page("favPage")

    def get_zu_an():
        zuan = requests.get("https://api.shadiao.app/nmsl?level=" + zuanMode).text
        zuan = json.loads(zuan)["data"]["text"] + " ——匿名网友"
        zuan_label.set_text(zuan)

    def show_detail(index):
        global favId
        index = index - 1
        if index < len(fav_list):
            favId = index
            zuan_label_detail.set_text(fav_list[index])
            paper.change_page("detailPage")

    def change_mode():
        global zuanMode
        if zuanMode == "min":
            env.popup.choice("切换模式", "确定切换到火力全开模式？\n该模式可能含下流词汇。", confirm_to_max_mode, cancel, cancel, bt1="确定切换",
                             bt2="取消", image_18px=Image.open("resources/images/zuan.png"))
        else:
            zuanMode = "min"
            zuan_mode_label.set_text("普通模式")

    def cancel():
        pass

    def confirm_to_max_mode():
        global zuanMode
        zuanMode = "max"
        zuan_mode_label.set_text("火力全开")

    def fav():
        fav_list.insert(0, zuan_label.get_text())
        saver.set("fav", fav_list)

    def my_fav():
        content = [["返回", "resources/images/back.png", back_to_main]]
        for zuan in fav_list:
            content.append([zuan, "resources/images/zuan.png", show_detail])
        content.append(["返回", "resources/images/back.png", back_to_main])
        fav_page.show(content, "祖安收藏夹")
        paper.change_page("favPage")

    def del_fav():
        del fav_list[favId]
        saver.set("fav", fav_list)
        my_fav()

    paper.add_element(element_lib.Label(
        (100, 0), paper, "祖安宝典", (150, 30)), "mainPage")

    paper.add_element(zuan_label, "mainPage")

    get_thread = threading.Thread(target=get_zu_an)  # 使用子线程请求api
    get_thread.start()  # 启动子线程

    zuan_mode_label = element_lib.Button((135, 97), paper,
                                         "普通模式", change_mode, (90, 30))

    paper.add_element(element_lib.Button(
        (4, 97), paper, "收藏", fav, (50, 30)), "mainPage")
    paper.add_element(element_lib.Button((52, 97), paper,
                                         "换一个", get_zu_an, (70, 30)), "mainPage")
    paper.add_element(zuan_mode_label, "mainPage")
    paper.add_element(element_lib.Button((221, 97), paper,
                                         "收藏夹", my_fav, (70, 30)), "mainPage")

    paper.add_page("favPage", fav_page)
    paper.add_page("detailPage")
    paper.add_element(element_lib.Label(
        (100, 0), paper, "详细内容", (150, 30)), "detailPage")
    paper.add_element(zuan_label_detail, "detailPage")
    paper.add_element(element_lib.Button(
        (5, 97), paper, "返回", back_to_list, (50, 30)), "detailPage")
    paper.add_element(element_lib.Button((200, 97), paper,
                                         "取消收藏", del_fav, (90, 30)), "detailPage")

    return paper
