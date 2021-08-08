import sdk.graphics.paper_lib
from sdk.graphics import element_lib
import requests
import json


def build(env):

    paper = sdk.graphics.paper_lib.PaperApp(env)

    paper.addElement("mainPage", element_lib.Label(
        (100, 0), paper, "祖安宝典", (150, 30), bgcolor="black", textColor="white"))

    zuan = requests.get("https://api.shadiao.app/nmsl?level=min").text
    zuan = json.loads(zuan)["data"]["text"]
    paper.addElement(0, 30, element_lib.Label((0, 35), paper, zuan, size=(296, 30)))

    return paper
