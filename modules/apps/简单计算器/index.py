from PIL import Image

from sdk.graphics import paper_lib, element_lib

resultFlag = False


def build(env):
    paper = paper_lib.PaperApp(env, background_image=Image.new("RGB", (296, 128), (0, 0, 0)))

    number_label = element_lib.Label(
        (0, 0), paper, "", (296, 30), bgcolor="black", textColor="white")

    paper.add_element(number_label, "mainPage")

    keyboard_list = [["AC", "7", "8", "9", "←", "*"],
                    [".", "4", "5", "6", "-", "/"],
                    ["0", "1", "2", "3", "+", "="]]
    keyboard = {}

    def addChar(char="0"):
        global resultFlag
        if char == "=":
            try:
                number_label.set_text(str(eval(number_label.get_text())))
            except ZeroDivisionError:
                number_label.set_text("不能除以0哦~")
            except SyntaxError:
                number_label.set_text("语法错误")
            except:
                number_label.set_text("错误")

            resultFlag = True
        elif char == "AC":
            number_label.set_text("")
        elif char == "←":
            number_label.set_text(number_label.get_text()[:-1])
            resultFlag = False
        elif char in "+-*/":
            number_label.set_text(number_label.get_text() + char)
            resultFlag = False
        elif resultFlag:
            number_label.set_text(char)
            resultFlag = False
        else:
            number_label.set_text(number_label.get_text() + char)

    for i in range(3):
        for j in range(6):
            now_char = keyboard_list[i][j]
            keyboard[now_char] = element_lib.Button(
                (j * 49 + 2, i * 30 + 36), paper, now_char, addChar, (48, 29), outline=None, char=now_char)
            paper.add_element(keyboard[now_char], "mainPage")

    return paper
