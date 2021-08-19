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

    favList = saver.readOrCreate("fav", [])

    yiyanLabel = element_lib.LabelWithMultipleLines(
        (5, 30), paper, "加载中...", (282, 80), fontSize=18)
    yiyanLabelDetail = element_lib.LabelWithMultipleLines(
        (5, 30), paper, "", (282, 80), fontSize=18)

    def backToMain(index = 0):
        paper.changePage("mainPage")

    def backToList():
        paper.changePage("favPage")

    def getyiyan():
        yiyan = requests.get("https://v1.hitokoto.cn/").text
        yiyan = json.loads(yiyan)["hitokoto"]+" ——"+json.loads(yiyan)["from"]
        yiyanLabel.setText(yiyan)

    def showDetail(index):
        global favId
        index = index - 1
        if index < len(favList):
            favId = index
            yiyanLabelDetail.setText(favList[index])
            paper.changePage("detailPage")


    def fav():
        favList.insert(0, yiyanLabel.getText())
        saver.set("fav", favList)

    def myFav():
        content = [["返回","resources/images/back.png", backToMain]]
        for yiyan in favList:
            content.append([yiyan, "resources/images/message.png", showDetail])
        content.append(["返回","resources/images/back.png", backToMain])
        favPage.show(content, "一言收藏夹")
        paper.changePage("favPage")

    def delFav():
        del favList[favId]
        saver.set("fav", favList)
        myFav()


    paper.addElement(element_lib.Label(
        (100, 0), paper, "一言", (150, 30)), "mainPage")

    paper.addElement(yiyanLabel, "mainPage")

    getThread = threading.Thread(target=getyiyan)  # 使用子线程请求api
    getThread.start()  # 启动子线程


    paper.addElement(element_lib.Button(
        (4, 97), paper, "收藏", fav, (50, 30)), "mainPage")
    paper.addElement(element_lib.Button((52, 97), paper,
                     "换一个", getyiyan, (70, 30)), "mainPage")
    paper.addElement(element_lib.Button((221, 97), paper,
                     "收藏夹", myFav, (70, 30)), "mainPage")

    paper.addPage("favPage", favPage)
    paper.addPage("detailPage")
    paper.addElement(element_lib.Label(
        (100, 0), paper, "详细内容", (150, 30)), "detailPage")
    paper.addElement(yiyanLabelDetail, "detailPage")
    paper.addElement(element_lib.Button(
        (5, 97), paper, "返回", backToList, (50, 30)), "detailPage")
    paper.addElement(element_lib.Button((200, 97), paper,
                     "取消收藏", delFav, (90, 30)), "detailPage")

    return paper
