import threading
import requests

class exceptions(Exception):
    pass

threadLock = threading.Lock()

def getLock() -> threading.Lock:
    return threadLock

def ifonline() -> bool:
    try:
        response = requests.get("https://pi.simplebytes.cn/ifonline")
    except:
        return False
    if response.text == "author:fu1fan":
        return True
    else:
        return False