import threading

from PIL import Image

from sdk.graphics import element_lib, paper_lib, page_lib
import requests
import json
from sdk import configurator

favId = 0


def build(env):
    paper = paper_lib.PaperApp(env)

    favPage = page_lib.ListPage(paper, "favPage")

    saver = configurator.Configurator(
        env.logger_env, "configs/yiyan.json", auto_save=True)

    fav_list = saver.read_or_create("fav", [])

    yiyan_label = element_lib.LabelWithMultipleLines(
        (5, 30), paper, "加载中...", (282, 80), fontSize=18)
    yiyan_label_detail = element_lib.LabelWithMultipleLines(
        (5, 30), paper, "", (282, 80), fontSize=18)

    def back_to_main(index=0):
        paper.change_page("mainPage")

    def back_to_list():
        paper.change_page("favPage")

    def get_yiyan():
        yiyan = requests.get("https://v1.hitokoto.cn/").text
        yiyan = json.loads(yiyan)["hitokoto"] + " ——" + json.loads(yiyan)["from"]
        yiyan_label.set_text(yiyan)

    def show_detail(index):
        global favId
        if index < len(fav_list):
            favId = index
            yiyan_label_detail.set_text(fav_list[index])
            paper.change_page("detailPage")

    def fav():
        fav_list.insert(0, yiyan_label.get_text())
        saver.set("fav", fav_list)

    def my_fav():
        content = []
        for yiyan in fav_list:
            content.append([yiyan, "resources/images/message.png", show_detail])
        favPage.show(content, "一言收藏夹", back_to_main)
        paper.change_page("favPage")

    def del_fav():
        del fav_list[favId]
        saver.set("fav", fav_list)
        my_fav()

    paper.add_element(element_lib.Label(
        (100, 0), paper, "一言", (150, 30)), "mainPage")

    paper.add_element(yiyan_label, "mainPage")

    getThread = threading.Thread(target=get_yiyan)  # 使用子线程请求api
    getThread.start()  # 启动子线程

    paper.add_element(element_lib.Button(
        (4, 97), paper, "收藏", fav, (50, 30)), "mainPage")
    paper.add_element(element_lib.Button((52, 97), paper,
                                         "换一个", get_yiyan, (70, 30)), "mainPage")
    paper.add_element(element_lib.Button((221, 97), paper,
                                         "收藏夹", my_fav, (70, 30)), "mainPage")

    paper.add_page("favPage", favPage)
    paper.add_page("detailPage")
    paper.add_element(element_lib.Label(
        (100, 0), paper, "详细内容", (150, 30)), "detailPage")
    paper.add_element(yiyan_label_detail, "detailPage")
    paper.add_element(element_lib.Button(
        (5, 97), paper, "返回", back_to_list, (50, 30)), "detailPage")
    paper.add_element(element_lib.Button((200, 97), paper,
                                         "取消收藏", del_fav, (90, 30)), "detailPage")

    return paper
