import threading

from PIL import Image

from sdk.graphics import element_lib, paper_lib, page_lib
import requests
import json
from sdk import configurator


def build(env):

    paper = paper_lib.PaperApp(env)

    favPage = page_lib.ListPage(paper, "favPage")

    saver = configurator.Configurator(
        env.logger_env, "configs/zuan.json", auto_save=True)

    favList = saver.readOrCreate("fav", [])

    zuanLabel = element_lib.LabelWithMultipleLines(
        (5, 30), paper, "加载中...", (282, 80))
    zuanLabelDetail = element_lib.LabelWithMultipleLines(
        (5, 30), paper, "", (282, 80))

    def backToMain():
        paper.changePage("mainPage")

    def getZuAn():
        zuan = requests.get("https://api.shadiao.app/nmsl?level=min").text
        zuan = json.loads(zuan)["data"]["text"]
        zuanLabel.setText(zuan)

    def showDetail(index):
        if index < len(favList):
            zuanLabelDetail.setText(favList[index])
            paper.changePage("detailPage")
            


    def fav():
        favList.insert(0, zuanLabel.getText())
        saver.set("fav", favList)

    def myFav():
        content = []
        for zuan in favList:
            content.append([zuan, "resources/images/zuan.png", showDetail])
        favPage.show(content, "祖安收藏夹")
        paper.changePage("favPage")

    paper.addElement(element_lib.Label(
        (100, 0), paper, "祖安宝典", (150, 30)), "mainPage")

    paper.addElement(zuanLabel, "mainPage")

    getThread = threading.Thread(target=getZuAn)  # 使用子线程请求api
    getThread.start()  # 启动子线程

    paper.addElement(element_lib.Button(
        (0, 97), paper, "收藏", fav, (50, 30)), "mainPage")
    paper.addElement(element_lib.Button((100, 97), paper,
                     "换一个", getZuAn, (75, 30)), "mainPage")
    paper.addElement(element_lib.Button((221, 97), paper,
                     "收藏夹", myFav, (75, 30)), "mainPage")

    paper.addPage("favPage", favPage)
    paper.addPage("detailPage")
    paper.addElement(element_lib.Label(
        (100, 0), paper, "详细内容", (150, 30)), "detailPage")
    paper.addElement(zuanLabelDetail, "detailPage")
    paper.addElement(element_lib.Button(
        (0, 97), paper, "返回", backToMain, (50, 30)), "detailPage")

    return paper
