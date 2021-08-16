from PIL import Image

from sdk.graphics import page_lib, paper_lib, element_lib
import sdk.configurator
import requests
import threading
import json


mainBtn = None
listJson = None

def build(env):
    global mainBtn

    paper = paper_lib.PaperApp(env, background_image=Image.new("RGB", (296, 128), (0, 0, 0)))

    config = sdk.configurator.Configurator(
        env.logger_env, "configs/account.json", auto_save=True)
    username = config.read("user/name")
    usertoken = config.read("user/token")
    
    def showTodo():

        def loadTodo():
            global listJson
            todoListPage = page_lib.ListPage(paper,"todoList")
            paper.addPage("todoList", todoListPage)
            listJson = requests.post("https://pi.simplebytes.cn/api/todo.php",
                {"name": username, "token": usertoken}).text
            listJson = json.loads(listJson)
            def todoItemClickHandler():
                pass
            if listJson == []:
                todoListTitle = "暂无清单"
                todoListContent = [["请前往：","resources/images/unfinished.png",None],
                ["pi.simplebytes.cn/todo","resources/images/unfinished.png",None]]
            else:
                todoListTitle = listJson[0]["title"]
                todoListContent = []

                for item in listJson[0]["content"]:
                    if not item["finished"]:
                        imgpath = "resources/images/unfinished.png"
                        todoListContent.append([item["name"], imgpath, todoItemClickHandler])

                for item in listJson[0]["content"]:
                    if item["finished"]:
                        imgpath = "resources/images/ok.png"
                        todoListContent.append([item["name"], imgpath, todoItemClickHandler])


            todoListPage.show(todoListContent, todoListTitle, None)
            paper.changePage("todoList")
            mainBtn.setText("显示您第一个清单")

        mainBtn.setText("加载中...")
        loadTodoThread = threading.Thread(target=loadTodo)
        loadTodoThread.start()

    if (username and usertoken):
        mainBtn = element_lib.Button(
            (0, 35), paper, "显示您第一个清单", showTodo, (296, 30), "white", "black"
        )
    else:
        mainBtn = element_lib.Button(
            (0, 35), paper, "请先绑定账号~", None, (296, 30), "white", "black"
        )
    


    paper.addElement(element_lib.Label(
        (100, 0), paper, "简单清单", (150, 30), bgcolor="black", textColor="white"), "mainPage")

    paper.addElement(mainBtn, "mainPage")

    return paper
