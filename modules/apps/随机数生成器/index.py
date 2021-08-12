from sdk.graphics import paper_lib, element_lib


def build(env):

    paper = paper_lib.PaperApp(env)

    paper.addElement("mainPage", element_lib.Label(
        (100, 0), paper, "随机数生成器", (150, 30), bgcolor="black", textColor="white"))
    

    return paper
