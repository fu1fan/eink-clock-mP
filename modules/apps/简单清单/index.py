from sdk.graphics import paper_lib, element_lib
import sdk.configurator
import requests


def build(env):

    paper = paper_lib.PaperApp(env)

    def bindAccount():
        paper.env.changePaper(paper.env.apps["账号管理"][0].build(paper.env))

    config = sdk.configurator.Configurator(
        env.logger_env, "configs/account.json", auto_save=True)

    paper.addElement("mainPage", element_lib.Label(
        (100, 0), paper, "简单清单", (150, 30), bgcolor="black", textColor="white"))

    username = config.read("user/name")
    usertoken = config.read("user/token")
    if (username and username):
        print(requests.post("https://pi.simplebytes.cn/api/todo.php",
              {"name": username, "token": usertoken}).text)
        
    else:
        paper.addElement("mainPage", element_lib.Button(
            (0, 35), paper, "点击绑定账号", bindAccount, (296, 30), "white", "black"
        ))

    return paper
