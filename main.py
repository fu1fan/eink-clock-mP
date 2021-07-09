import os, time
import requests
from sdk import master, logger, display

os.chdir(os.path.dirname(__file__))

if __name__ == "__main__":
    logger = logger.Logger(logger.Logger.DEBUG)
    logger.debug("无法处理Bluetooth.")
    logger.debug("无法处理Wi-Fi.")
    try:
        pass
    except KeyboardInterrupt:

        pass #关闭屏幕
    pass