from PIL import Image

from sdk.graphics import page_lib, paper_lib, element_lib
import sdk.configurator
import requests
import threading
import json
from pathlib import Path

mainBtn = None
listJson = None


def build(env):
    global mainBtn

    paper = paper_lib.PaperApp(env)

    config = sdk.configurator.Configurator(
        env.logger_env, "configs/account.json", auto_save=True)
    username = config.read("user/name")
    user_token = config.read("user/token")

    def show_todo():

        def load_todo():
            global listJson
            todo_list_page = page_lib.ListPage(paper, "todoList")
            paper.add_page("todoList", todo_list_page)
            listJson = requests.post("https://pi.simplebytes.cn/api/todo.php",
                                     {"name": username, "token": user_token}).text
            listJson = json.loads(listJson)

            def todoItemClickHandler():
                pass

            if not listJson:
                todo_list_title = "暂无清单"
                todo_list_content = [["请前往：", Path("resources/images/unfinished.png"), None],
                                   ["pi.simplebytes.cn/todo", Path("resources/images/unfinished.png"), None]]
            else:
                todo_list_title = listJson[0]["title"]
                todo_list_content = []

                for item in listJson[0]["content"]:
                    if not item["finished"]:
                        imgpath = Path("resources/images/unfinished.png")
                        todo_list_content.append([item["name"], imgpath, todoItemClickHandler])

                for item in listJson[0]["content"]:
                    if item["finished"]:
                        imgpath = Path("resources/images/ok.png")
                        todo_list_content.append([item["name"], imgpath, todoItemClickHandler])

            todo_list_page.show(todo_list_content, todo_list_title, None)
            paper.change_page("todoList")
            mainBtn.set_text("显示您第一个清单")

        mainBtn.set_text("加载中...")
        env.pool.add(load_todo)

    if username and user_token:
        mainBtn = element_lib.Button(
            (0, 35), paper, "显示您第一个清单", show_todo, (296, 30)
        )
    else:
        mainBtn = element_lib.Button(
            (0, 35), paper, "请先绑定账号~", None, (296, 30)
        )

    paper.add_element(element_lib.Label(
        (100, 0), paper, "简单清单", (150, 30)), "mainPage")

    paper.add_element(mainBtn, "mainPage")

    return paper
