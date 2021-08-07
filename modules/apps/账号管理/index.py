import sdk.graphics
import sdk.graphics.element_lib

import requests
import json
import threading
import time
import random

paper = None

codeLabel = None

def build(env):
    paper = sdk.graphics.PaperDynamic(env)
    codeLabel = sdk.graphics.element_lib.Label(
    (0, 90), paper, str(random.randint(100000,999999)), (296, 30), bgcolor="black", textColor="white", fontSize=30)

    paper.addElement("mainPage", sdk.graphics.element_lib.Label(
        (100, 0), paper, "绑定账号", (150, 30), bgcolor="black", textColor="white"))
    paper.addElement("mainPage", sdk.graphics.element_lib.Label(
        (0, 30), paper, "请访问 pi.simplebytes.cn", (296, 30), bgcolor="black", textColor="white"))
    paper.addElement("mainPage", sdk.graphics.element_lib.Label(
        (0, 60), paper, "输入下方的6位配对码", (296, 30), bgcolor="black", textColor="white"))

    paper.addElement("mainPage", codeLabel)

    return paper
