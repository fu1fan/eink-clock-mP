import sdk.graphics
import sdk.graphics.element_lib
import sdk.graphics.paper_lib

import requests
import json
import threading
import time

paper = None

codeLabel = None


def build(env):

    paper = sdk.graphics.paper_lib.PaperApp(env)

    def nextStep():
        paper.addElement("nextPage", sdk.graphics.element_lib.Label(
            (30, 30), paper, "okk"))
        paper.changePage("nextPage")

    def pair():
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

    paper.addElement("mainPage", sdk.graphics.element_lib.Label(
        (100, 0), paper, "账号管理", (150, 30), bgcolor="black", textColor="white"))

    paper.addElement("mainPage", sdk.graphics.element_lib.Label(
        (0, 35), paper, "暂未绑定账号", (296, 30), bgcolor="black", textColor="white"))

    paper.addElement("mainPage", sdk.graphics.element_lib.Button(
        (50, 100), paper, "点击绑定账号", nextStep, (85, 30), "white", "black"))

    paper.addPage("pairPage")
    paper.addPage("nextPage")

    return paper
