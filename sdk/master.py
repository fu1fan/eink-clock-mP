import requests


def ifonline() -> bool:
    try:
        response = requests.get("https://pi.simplebytes.cn/ifonline")
        response.raise_for_status()
    except:
        return False
    if response.text == "author:fu1fan":
        return True
    else:
        return False
