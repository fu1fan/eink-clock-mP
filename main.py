import os
import threading
import time
import traceback
from sdk import logger
from sdk import display
from PIL import Image
from sdk import general

os.chdir(os.path.dirname(__file__))

if __name__ == "__main__":  # 主线程：UI管理
    logger_main = logger.Logger(logger.DEBUG)
    main_pool = general.ThreadPool(20)  # 创建20个空进程
    epdLock = threading.RLock()  # 将该锁发送给对应的paper，可让屏幕在刷新时阻塞触摸的扫描，同时也可以防止两个进程同时访问屏幕
    epd = display.EpdController(20, epdLock, True)
    if epd.IsBusy():
        logger_main.error("The screen is busy!")
        raise RuntimeError("The screen is busy!")
    paperLock = threading.Lock()
    openingImages = (Image.open(open("resources/images/Raspberry.jpg", mode="rb")),)
    paperNow = display.Paper(epd, paperLock, background_image=openingImages[0])
    try:
        # 显示开屏动画
        paperNow.init()
        if len(openingImages) >= 1:
            for i in openingImages[1:]:
                paperNow.update_background(i)
        time.sleep(100)
    except KeyboardInterrupt:
        print("ctrl+c")
    except:
        logger_main.warn(traceback.format_exc())
    else:
        epd.sleep()
        epd.exit()
