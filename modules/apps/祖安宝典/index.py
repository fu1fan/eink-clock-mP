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

    favPage = page_lib.ListPage(paper, "favPage")


    saver = configurator.Configurator(
        env.logger_env, "configs/zuan.json", auto_save=True)

    favList = saver.readOrCreate("fav", [])

    zuanLabel = element_lib.LabelWithMultipleLines(
        (5, 30), paper, "加载中...", (282, 80), fontSize=15)
    zuanLabelDetail = element_lib.LabelWithMultipleLines(
        (5, 30), paper, "", (282, 80), fontSize=15)

    def backToMain(index = 0):
        paper.changePage("mainPage")

    def backToList():
        paper.changePage("favPage")

    def getZuAn():
        zuan = requests.get("https://api.shadiao.app/nmsl?level="+zuanMode).text
        zuan = json.loads(zuan)["data"]["text"]+" ——匿名网友"
        zuanLabel.setText(zuan)

    def showDetail(index):
        global favId
        index = index - 1
        if index < len(favList):
            favId = index
            zuanLabelDetail.setText(favList[index])
            paper.changePage("detailPage")

    def changeMode():
        global zuanMode
        if (zuanMode=="min"):
            env.popup.choice("切换模式", "确定切换到火力全开模式？\n该模式可能引起不适。", confirmToMaxMode, cancel, cancel, bt1="确定切换", bt2="取消", image_18px=Image.open("resources/images/zuan.png"))
        else:
            zuanMode = "min"
            zuanModeLabel.setText("普通模式")
            
    def cancel():
        pass

    def confirmToMaxMode():
        global zuanMode
        zuanMode = "max"
        zuanModeLabel.setText("火力全开")

    def fav():
        favList.insert(0, zuanLabel.getText())
        saver.set("fav", favList)

    def myFav():
        content = [["返回","resources/images/back.png", backToMain]]
        for zuan in favList:
            content.append([zuan, "resources/images/zuan.png", showDetail])
        content.append(["返回","resources/images/back.png", backToMain])
        favPage.show(content, "祖安收藏夹")
        paper.changePage("favPage")

    def delFav():
        del favList[favId]
        saver.set("fav", favList)
        myFav()


    paper.addElement(element_lib.Label(
        (100, 0), paper, "祖安宝典", (150, 30)), "mainPage")

    paper.addElement(zuanLabel, "mainPage")

    getThread = threading.Thread(target=getZuAn)  # 使用子线程请求api
    getThread.start()  # 启动子线程

    zuanModeLabel = element_lib.Button((135, 97), paper,
                     "普通模式", changeMode, (90, 30))

    paper.addElement(element_lib.Button(
        (4, 97), paper, "收藏", fav, (50, 30)), "mainPage")
    paper.addElement(element_lib.Button((52, 97), paper,
                     "换一个", getZuAn, (70, 30)), "mainPage")
    paper.addElement(zuanModeLabel, "mainPage")
    paper.addElement(element_lib.Button((221, 97), paper,
                     "收藏夹", myFav, (70, 30)), "mainPage")

    paper.addPage("favPage", favPage)
    paper.addPage("detailPage")
    paper.addElement(element_lib.Label(
        (100, 0), paper, "详细内容", (150, 30)), "detailPage")
    paper.addElement(zuanLabelDetail, "detailPage")
    paper.addElement(element_lib.Button(
        (5, 97), paper, "返回", backToList, (50, 30)), "detailPage")
    paper.addElement(element_lib.Button((200, 97), paper,
                     "取消收藏", delFav, (90, 30)), "detailPage")

    return paper
