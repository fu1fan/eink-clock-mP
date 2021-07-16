import os
import threading
import traceback
from sdk import logger
from sdk import epd2in9_V2
from sdk import display
from PIL import Image

os.chdir(os.path.dirname(__file__))

if __name__ == "__main__":
    logger_main = logger.Logger(logger.DEBUG)
    epd = epd2in9_V2.EPD_2IN9_V2()
    pageLock = threading.Lock()
    openingImages = (Image.open(open("images/Raspberry.jpg", mode="r")))
    pageNow = display.Page(epd, pageLock, image=openingImages[0])
    try:
        epd.init()
        epd.clear(0xFF)
        pageNow.init()
    except KeyboardInterrupt:
        print("ctrl+c")
    except:
        logger_main.warn(traceback.format_exc)
    else:
        epd.sleep()
        epd.exit()
