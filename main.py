import os
from sdk import epd2in9_V2

os.chdir(os.path.dirname(__file__))

if __name__ == "__main__":
    epd = epd2in9_V2.EPD_2IN9_V2()
    epd.init()
    epd.clear(0xFF)
    epd.sleep()
    epd.exit()
