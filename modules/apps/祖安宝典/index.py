import threading

from PIL import Image

import sdk.graphics.paper_lib
from sdk.graphics import element_lib
import requests
import json


def build(env):

    paper = sdk.graphics.paper_lib.PaperApp(env, background_image=Image.new("RGB", (296, 128), (0, 0, 0)))
    zuanLabel = element_lib.LabelWithMultipleLines((5, 35), paper, "加载中...", (282, 80), "black", "white")
    def getZuAn():
        zuan = requests.get("https://api.shadiao.app/nmsl?level=min").text
        zuan = json.loads(zuan)["data"]["text"]
        zuanLabel.setText(zuan)

    paper.addElement(element_lib.Label(
        (100, 0), paper, "祖安宝典", (150, 30), bgcolor="black", textColor="white"), "mainPage")

    paper.addElement(zuanLabel, "mainPage")

    getThread = threading.Thread(target=getZuAn) # 使用子线程请求api
    getThread.start() # 启动子线程

    paper.addElement(element_lib.Button((100, 98), paper, "换一个", getZuAn, (75, 30), "white", "black"), "mainPage")


    return paper
