import threading
import time
import traceback

from sdk import logger
from sdk import display
from sdk import threadpool_mini
from sdk import touchpad
from sdk import configurator
from PIL import Image

from modules.theme.default import theme as text_clock

example_config = {
    "main": {
        "enable_plugins": [],
        "enable_theme": [],
        "enable_app": [],
        "threadpool_size": 20,
        "opening_images": [
            "resources/images/raspberry.jpg",
            "resources/images/github.jpg",
            "resources/images/simplebytes.jpg"
        ],
        "loading_image": "resources/images/loading.jpg"
    },
    "plugin": {},
    "theme": {},
    "app": {},
    "update_0b5721sje4": 1
}

if __name__ == "__main__":  # 主线程：UI管理
    logger_main = logger.Logger(logger.DEBUG)  # 日志

    configurator_main = configurator.Configurator(logger_main)  # 配置
    configurator_main.check(example_config, True)
    configurator_main.change_path("/main")

    main_pool = threadpool_mini.ThreadPool(configurator_main.read("threadpool_size"))  # 启动线程池
    main_pool.start()   # 启动线程池

    epdLock = threading.RLock()  # 实例化显示驱动
    epd = display.EpdController(logger_main, epdLock)   # 显示驱动
    # epd.set_upside_down(True)   # 倒置图像 TODO:处理触摸屏倒转后的操作
    if epd.IsBusy():
        logger_main.error("The screen is busy!")
        raise RuntimeError("The screen is busy!")

    opening_images = []     # 准备开屏动画
    opening_images_path = configurator_main.read("opening_images")
    for path in opening_images_path:
        file = open(path, "rb")
        opening_images.append(Image.open(file))
    paperNow = display.Paper(epd, background_image=opening_images[0])
    load_lock = threading.Barrier(2)

    def opening():
        paperNow.init()
        if len(opening_images) >= 1:
            for i in opening_images[1:]:
                paperNow.update_background(i)
        if load_lock.n_waiting == 0:    # 如果等动画显示完后主线程还没进入等待，则显示Loading画面
            _file = open(configurator_main.read("loading_image"), "rb")
            paperNow.update_background(Image.open(_file))
            _file.close()
        load_lock.wait()

    try:
        # 显示开屏动画
        main_pool.add(opening)
        ### 在这里放置要预加载的东西（主题与插件等）
        touch_recoder_new = touchpad.TouchRecoder()     # 触摸驱动
        touch_recoder_old = touchpad.TouchRecoder()
        icnt86 = touchpad.TouchDriver(logger_main)
        icnt86.ICNT_Init()
        touch_handler = touchpad.TouchHandler(main_pool, logger_main)



        load_lock.wait()
        ### 主程序开始
        clock = text_clock.Theme(epd, main_pool)
        paperNow = clock.build()
        paperNow.init()
        while True:
            icnt86.ICNT_Scan(touch_recoder_new, touch_recoder_old)
            touch_handler.handle(touch_recoder_new, touch_recoder_old)
    except KeyboardInterrupt:
        print("ctrl+c")
    except:     # ⚠️只在生产环境使用 会影响调试结果！！！
        logger_main.error(traceback.format_exc())
    epd.sleep()
    epd.exit()
