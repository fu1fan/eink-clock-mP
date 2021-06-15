import threading

class exceptions(Exception):
    pass

threadLock = threading.Lock()

def getLock() -> threading.Lock:
    return threadLock