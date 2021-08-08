import sdk.graphics.paper_lib


def build(env):

    paper = sdk.graphics.paper_lib.PaperApp(env)

    paper.addElement("mainPage", sdk.graphics.element_lib.Label(
        (100, 0), paper, "祖安宝典", (150, 30), bgcolor="black", textColor="white"))

    return paper
