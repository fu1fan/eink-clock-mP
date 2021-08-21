import threading

from PIL import Image

import sdk.graphics
import sdk.graphics.element_lib
import sdk.graphics.paper_lib

import requests
import json

import sdk.configurator

paper = None
configurator = None
infoLabel = None
actionButton = None
paircode = 0


def backToMain():
    paper.pause_update()  # 上锁，防止setText重复刷新屏幕

    paper.changePage("mainPage")
    refreshMain()

    paper.recover_update()  # 解锁


def logout():
    configurator.delete("user")
    paper.pause_update()  # 上锁，防止setText重复刷新屏幕
    refreshMain()
    paper.recover_update()  # 解锁


def refreshMain():
    if configurator.read("user/name"):
        infoLabel.setText("你好，" + configurator.read("user/name"))
        actionButton.setText("点击退出账号")
        actionButton.setOnclick(logout)
    else:
        infoLabel.setText("暂未绑定账号")
        actionButton.setText("点击绑定账号")
        actionButton.setOnclick(pair)


def pair():
    codeLabel = sdk.graphics.element_lib.Label(
        (0, 88), paper, "请稍等...", (169, 40), fontSize=30)
    paper.addElement(codeLabel, "pairPage")

    def getPairCode():
        global paircode
        paircode = json.loads(requests.get(
            "https://pi.simplebytes.cn/api/getPairCode.php").text)["paircode"]
        codeLabel.set_text(str(paircode))

    getPairCodeThread = threading.Thread(target=getPairCode)
    getPairCodeThread.start()

    def nextStep():
        resultLabel = sdk.graphics.element_lib.Label(
            (0, 30), paper, "请稍等片刻...", (296, 30))

        def getResult():
            result = requests.post(
                "https://pi.simplebytes.cn/api/getPairInfo.php", {"paircode": paircode}).text
            result = json.loads(result)
            if result["msg"] != "WAIT_PAIRING":
                msg = "已绑定：" + result["username"]
                configurator.set("user/name", result["username"])
                configurator.set("user/token", result["usertoken"])

            else:
                msg = "输完配对码后再点下一步哦"

            resultLabel.set_text(msg)

        paper.addElement(resultLabel, "nextPage")

        paper.addElement(sdk.graphics.element_lib.Button(
            (0, 70), paper, "返回首页", backToMain, (296, 30)), "nextPage")

        getResultThread = threading.Thread(target=getResult)
        getResultThread.start()

        paper.changePage("nextPage")

    paper.addElement(sdk.graphics.element_lib.Label(
        (100, 0), paper, "绑定账号", (150, 30)), "pairPage")
    paper.addElement(sdk.graphics.element_lib.Label(
        (0, 30), paper, "请访问 pi.simplebytes.cn", (296, 30)), "pairPage")
    paper.addElement(sdk.graphics.element_lib.Label(
        (0, 60), paper, "登录后，输入下方的配对码", (296, 30)), "pairPage")
    paper.addElement(sdk.graphics.element_lib.Button(
        (170, 90), paper, "下一步", nextStep, (85, 35), fontSize=24), "pairPage")

    paper.changePage("pairPage")


def build(env):
    global paper
    global configurator
    global infoLabel
    global actionButton

    configurator = sdk.configurator.Configurator(
        env.logger_env, "configs/account.json", auto_save=True)

    paper = sdk.graphics.paper_lib.PaperApp(env)

    paper.add_element(sdk.graphics.element_lib.Label(
        (100, 0), paper, "账号管理", (150, 30)), "mainPage")

    if configurator.read("user/name"):
        infoLabel = sdk.graphics.element_lib.Label(
            (0, 35), paper, "你好，" + configurator.read("user/name"), (296, 30))

        actionButton = sdk.graphics.element_lib.Button(
            (0, 95), paper, "点击退出账号", logout, (296, 30))
    else:
        infoLabel = sdk.graphics.element_lib.Label(
            (0, 35), paper, "暂未绑定账号", (296, 30))

        actionButton = sdk.graphics.element_lib.Button(
            (0, 95), paper, "点击绑定账号", pair, (296, 30))

    paper.add_element(infoLabel, "mainPage")
    paper.add_element(actionButton, "mainPage")

    paper.add_page("pairPage")
    paper.add_page("nextPage")

    return paper
