import os
import threading
import time
import traceback
from sdk import logger
from sdk import epd2in9_V2
from sdk import display
from PIL import Image
from sdk import general

os.chdir(os.path.dirname(__file__))

if __name__ == "__main__":  # 主线程：UI管理
    logger_main = logger.Logger(logger.DEBUG)
    main_pool = general.ThreadPool(20)  # 创建20个空进程
    epd = epd2in9_V2.EPD_2IN9_V2()
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
