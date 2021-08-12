import sdk.graphics.paper_lib
from sdk.graphics import element_lib
import requests
import json


def build(env):

    paper = sdk.graphics.paper_lib.PaperApp(env)

    paper.addElement("mainPage", element_lib.Label(
        (100, 0), paper, "祖安宝典", (150, 30), bgcolor="black", textColor="white"))

    #zuan = requests.get("https://api.shadiao.app/nmsl?level=min").text
    #zuan = json.loads(zuan)["data"]["text"]
    zuan = "我是一长串文字一长串文字一长串文字一长串文字一长串文字一长串文字一长串文字一长串文字一长串文字一长串文字一长串文字一长串文字"
    paper.addElement("mainPage", element_lib.LabelWithMultipleLines((0, 35), paper, zuan, (266, 50), "white", "black" ))

    return paper
