import sdk.graphics
import sdk.graphics.element_lib
import sdk.graphics.paper_lib

import requests
import json
import threading
import time

paper = None

codeLabel = None

paircode = 0


def nextStep():
    result = requests.post(
        "https://pi.simplebytes.cn/api/getPairInfo.php", {"paircode": paircode}).text
    
    result = json.loads(result)
    if (result["msg"] != "WAIT_PAIRING"):
        msg = result["username"]
    else:
        msg = "还没配对呢"

    paper.addElement("nextPage", sdk.graphics.element_lib.Label(
        (0, 30), paper, msg, (296, 30)))

    paper.changePage("nextPage")


def pair():
    global paircode
    paircode = json.loads(requests.get(
        "https://pi.simplebytes.cn/api/getPairCode.php").text)["paircode"]
    codeLabel = sdk.graphics.element_lib.Label(
        (0, 90), paper, str(paircode), (169, 30), bgcolor="black", textColor="white", fontSize=30)
    paper.addElement("pairPage", sdk.graphics.element_lib.Label(
        (100, 0), paper, "绑定账号", (150, 30), bgcolor="black", textColor="white"))
    paper.addElement("pairPage", sdk.graphics.element_lib.Label(
        (0, 30), paper, "请访问 pi.simplebytes.cn", (296, 30), bgcolor="black", textColor="white"))
    paper.addElement("pairPage", sdk.graphics.element_lib.Label(
        (0, 60), paper, "登录后，输入下方的配对码", (296, 30), bgcolor="black", textColor="white"))
    paper.addElement("pairPage", sdk.graphics.element_lib.Button(
        (170, 90), paper, "下一步", nextStep, (85, 35), "white", "black", fontSize=24))
    paper.addElement("pairPage", codeLabel)
    paper.changePage("pairPage")


def build(env):
    global paper
    paper = sdk.graphics.paper_lib.PaperApp(env)

    paper.addElement("mainPage", sdk.graphics.element_lib.Label(
        (100, 0), paper, "账号管理", (150, 30), bgcolor="black", textColor="white"))

    paper.addElement("mainPage", sdk.graphics.element_lib.Label(
        (0, 35), paper, "暂未绑定账号", (296, 30), bgcolor="black", textColor="white"))

    paper.addElement("mainPage", sdk.graphics.element_lib.Button(
        (50, 95), paper, "点击绑定账号", pair, (85, 30), "white", "black"))

    paper.addPage("pairPage")
    paper.addPage("nextPage")

    return paper
