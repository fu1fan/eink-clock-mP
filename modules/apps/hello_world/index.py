from sdk.graphics import paper_lib, element_lib

from PIL import Image


def build(env):
    paper = paper_lib.PaperApp(env, background_image=Image.new("RGB", (296, 128), (0, 0, 0)))

    text_label = element_lib.Label(
        (100, 40), paper, "Hello world!", (150, 30), bgcolor="black", textColor="white")

    def changeText():
        text_label.setText("Button Clicked!")

    paper.addElement(text_label, "mainPage")
    paper.addElement(element_lib.Button(
        (100, 80), paper, "I'm a button", changeText, (150, 30), bgcolor="black", textColor="white"), "mainPage")

    return paper
