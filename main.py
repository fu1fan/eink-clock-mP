import threading
import time
import traceback

from sdk import logger
from sdk import display
from sdk import threadpool_mini
from PIL import Image

from modules.theme.default import theme as text_clock

# TODO:删除TimingTask相关内容

if __name__ == "__main__":  # 主线程：UI管理
    logger_main = logger.Logger(logger.DEBUG)
    main_pool = threadpool_mini.ThreadPool(20)  # 创建20个空进程
    main_pool.start()
    epdLock = threading.RLock()  # 将该锁发送给对应的paper，可让屏幕在刷新时阻塞触摸的扫描，同时也可以防止两个进程同时访问屏幕
    epd = display.EpdController(logger_main, epdLock)
    epd.set_upside_down(True)
    if epd.IsBusy():
        logger_main.error("The screen is busy!")
        raise RuntimeError("The screen is busy!")
    openingImages = (Image.open(open("resources/images/raspberry.jpg", mode="rb")),
                     Image.open(open("resources/images/github.jpg", mode="rb")),
                     Image.open(open("resources/images/simplebytes.jpg", mode="rb")))
    paperNow = display.Paper(epd, background_image=openingImages[0])

    load_lock = threading.Barrier(2)

    def opening():
        paperNow.init()
        if len(openingImages) >= 1:
            for i in openingImages[1:]:
                paperNow.update_background(i)
        if load_lock.n_waiting == 0:    # 如果等动画显示完后主线程还没进入等待，这显示Loading画面
            paperNow.update_background(Image.open(open("resources/images/loading.jpg", mode="rb")))
        load_lock.wait()
    try:
        # 显示开屏动画
        main_pool.add(opening)
        ### 在这里放置要预加载的东西（主题与插件等）

        ###
        load_lock.wait()
        clock = text_clock.Theme(epd, main_pool)
        paperNow = clock.build()
        paperNow.init()

        # 主程序开始
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("ctrl+c")
    except:
        logger.ERROR(traceback.format_exc())
    else:
        epd.sleep()
        epd.exit()
