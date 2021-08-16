from PIL import Image

from sdk.graphics import paper_lib, element_lib
import random

maxN = 100

def build(env):

    paper = paper_lib.PaperApp(env)

    paper.addElement(element_lib.Label(
        (80, 0), paper, "随机数生成器", (150, 30)), "mainPage")
    numberLabel = element_lib.Label((115, 35), paper, "0", (100, 50), fontSize=50)
    infoLabel = element_lib.Label((0, 95), paper, "当前范围：1-100", (160, 45))

    paper.addElement(numberLabel, "mainPage")
    paper.addElement(infoLabel, "mainPage")
    def randomNum():
        numberLabel.setText(str(random.randint(1, maxN)))

    def setMaxNum(maxnum=100):
        global maxN
        maxN = maxnum
        infoLabel.setText("当前范围：1-%d" % maxN)

    paper.addElement(
        element_lib.Button((230, 1), paper, "1-6", setMaxNum, (65, 30), maxnum=6),
        "mainPage")
    paper.addElement(
        element_lib.Button((230, 33), paper, "1-10", setMaxNum, (65, 30),
                           maxnum=10), "mainPage")
    paper.addElement(
        element_lib.Button((230, 65), paper, "1-100", setMaxNum, (65, 30),
                           maxnum=100), "mainPage")

    paper.addElement(
        element_lib.Button((230, 97), paper, "生成", randomNum, (65, 30)), "mainPage")

    return paper
