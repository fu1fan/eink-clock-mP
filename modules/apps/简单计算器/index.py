from sdk.graphics import paper_lib, element_lib


def build(env):

    paper = paper_lib.PaperApp(env)

    number_label = element_lib.Label(
        (100, 40), paper, "Hello world!", (150, 30), bgcolor="black", textColor="white")

    
    #paper.addElement("mainPage", element_lib.Button(
   #     (100, 80), paper, "I'm a button", , (150, 30), bgcolor="black", textColor="white"))
    
    return paper
