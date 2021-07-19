import os
import threading
import traceback
from sdk import logger
from sdk import epd2in9_V2
from sdk import display
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

os.chdir(os.path.dirname(__file__))

if __name__ == "__main__":  # 主线程：UI管理
    logger_main = logger.Logger(logger.DEBUG)

    epd = epd2in9_V2.EPD_2IN9_V2()
    pageLock = threading.Lock()
    openingImages = (Image.open(open("resources/images/Raspberry.jpg", mode="rb")),)
    pageNow = display.Page(epd, pageLock, image=openingImages[0])

    try:
        # 显示开屏动画
        pageNow.init()
        if len(openingImages) >= 1:
            for i in openingImages[1:]:
                pageNow.update(i)
    except KeyboardInterrupt:
        print("ctrl+c")
    except:
        logger_main.warn(traceback.format_exc())
    else:
        epd.sleep()
        epd.exit()
