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
        response.raise_for_status()
    except:
        return False
    if response.text == "author:fu1fan":
        return True
    else:
        return False