from sdk.graphics import paper_lib, element_lib

from PIL import Image


def build(env):
    paper = paper_lib.PaperApp(env, background_image=Image.new("RGB", (296, 128), (0, 0, 0)))

    text_label = element_lib.Label(
        (100, 40), paper, "Hello world\nHello world!Hello world!!", (150, 100), bgcolor="black", textColor="white")

    def changeText():
        text_label.set_text("Button1 Clicked!")
        print(1)

    def changeText2():
        text_label.set_text("Button2 Clicked!")
        print(2)

    paper.add_element(text_label, "mainPage")
    paper.add_element(element_lib.Button(
        (100, 80), paper, "I'm a button", changeText, (150, 30), bgcolor="white", textColor="black"), "mainPage")
    paper.add_element(element_lib.Button(
        (120, 90), paper, "I'm a button(2)", changeText2, (150, 30), bgcolor="black", textColor="white"), "mainPage")

    return paper
