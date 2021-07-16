import os
import traceback
from sdk import logger
from sdk import epd2in9_V2

os.chdir(os.path.dirname(__file__))

if __name__ == "__main__":
    logger_main = logger.Logger(logger.Logger.DEBUG)
    epd = epd2in9_V2.EPD_2IN9_V2()
    try:
        epd.init()
        epd.clear(0xFF)
    except:
        logger_main.warn(traceback.format_exc)
    else:
        epd.sleep()
        epd.exit()
