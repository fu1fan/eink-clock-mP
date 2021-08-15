from PIL.Image import Image

from sdk.graphics import paper_lib, element_lib


resultFlag = False

def build(env):

    paper = paper_lib.PaperApp(env, background_image=Image.new("RGB", (296, 128), (0, 0, 0)))

    numberLabel = element_lib.Label(
        (50, 0), paper, "", (246, 30), bgcolor="black", textColor="white")

    paper.addElement(numberLabel, "mainPage")
    
    keyboardList = [["AC", "7", "8", "9", "←", "*"],
                    [".", "4", "5", "6", "-", "/"],
                    ["0", "1", "2", "3", "+", "="]]
    keyboard = {}

    def addChar(char="0"):
        global resultFlag
        if char=="=":
            try:
                numberLabel.setText(str(eval(numberLabel.getText())))
            except ZeroDivisionError:
                numberLabel.setText("不能除以0哦~")
            except SyntaxError:
                numberLabel.setText("语法错误")
            except:
                numberLabel.setText("错误")

            resultFlag = True
        elif char=="AC":
            numberLabel.setText("")
        elif char=="←":
            numberLabel.setText(numberLabel.getText()[:-1])
            resultFlag = False
        elif char in "+-*/":
            numberLabel.setText(numberLabel.getText()+char)
            resultFlag = False
        elif resultFlag:
            numberLabel.setText(char)
            resultFlag = False
        else:
            numberLabel.setText(numberLabel.getText()+char)

    for i in range(3):
        for j in range(6):
            nowChar = keyboardList[i][j]
            keyboard[nowChar] = element_lib.Button(
                (j * 49 + 2, i * 30 + 36), paper, nowChar, addChar, (48, 29), "white", "black",  char=nowChar)
            paper.addElement(keyboard[nowChar], "mainPage")

   
    return paper
