import json
import os
import threading
import importlib
import time
import traceback

from sdk import environment_dev as environment

from sdk import logger
from sdk import configurator
from PIL import Image

example_config = {
    "main": {
        "enable_plugins": [],
        "enable_theme": "default",
        "enable_apps": ["hello_world"],
        "opening_images": [
            "resources/images/raspberry.jpg",
            "resources/images/github.jpg",
            "resources/images/simplebytes.jpg"
        ],
        "loading_image": "resources/images/loading.jpg",
        "env_configs": {
            "auto_sleep_time": 30,
            "refresh_time": 43200,
            "refresh_interval": 30,
            "threadpool_size": 20
        }
    },
    "plugins": {},
    "themes": {},
    "apps": {},
    "update_0bd89j4": 1
}


class DependenceError(Exception):
    pass


if __name__ == "__main__":  # 主线程：UI管理
    logger_main = logger.Logger(logger.DEBUG)  # 日志

    configurator_main = configurator.Configurator(logger_main)  # 配置
    configurator_main.check(example_config, True)
    configurator_main.change_path("/main")

    env = environment.Env(configurator_main.read("env_configs"), logger_main)

    opening_images = []  # 准备开屏动画
    opening_images_path = configurator_main.read("opening_images")
    for path in opening_images_path:
        file = open(path, "rb")
        opening_images.append(Image.open(file))
    paperNow = environment.graphics.Paper(env, opening_images[0])
    load_lock = threading.Barrier(2)


    def opening():
        paperNow.init()
        if len(opening_images) >= 1:
            for i in opening_images[1:]:
                paperNow.update_background(i)
        if load_lock.n_waiting == 0:  # 如果等动画显示完后主线程还没进入等待，则显示Loading画面
            _file = open(configurator_main.read("loading_image"), "rb")
            paperNow.update_background(Image.open(_file))
            _file.close()
        load_lock.wait()


    try:
        # 显示开屏动画
        env.pool.add(opening)
        ### 在这里放置要预加载的东西（主题与插件等）
        touch_recoder_new = environment.touchpad.TouchRecoder()  # 触摸
        touch_recoder_old = environment.touchpad.TouchRecoder()

        wheels_name = []
        plugins = {}
        theme = None
        apps = {}
        enable_plugins = configurator_main.read("enable_plugins", raise_error=True)
        for wheel_name in os.listdir("modules/wheels"):  # 检测当前的轮子
            if wheel_name.endswith(".py") and (wheel_name != "__init__.py"):
                wheels_name.append(wheel_name[:-3])

        for plugin_name in enable_plugins:  # 加载已注册的插件
            try:
                file = open("modules/plugins/%s/index.json" % plugin_name)
                plugin_info = json.load(file)
                file.close()
                for wheel_ in plugin_info["depended-wheels"]:
                    if wheel_ not in wheels_name:
                        raise DependenceError("No wheel named %s!" % wheel_)
                plugins[plugin_name] = importlib.import_module("modules.plugins.%s.index")

            except FileNotFoundError and json.JSONDecodeError and DependenceError:
                logger_main.error("插件[%s]加载失败:\n" + traceback.format_exc())

        theme_name = configurator_main.read("enable_theme", raise_error=True)  # 加载主题
        try:
            file = open("modules/themes/%s/index.json" % theme_name)
            theme_info = json.load(file)
            file.close()
            for wheel_ in theme_info["depended-wheels"]:
                if wheel_ not in wheels_name:
                    raise DependenceError("No wheel named %s!" % wheel_)
            for plugin_ in theme_info["depended-plugins"]:
                if plugin_ not in plugins:
                    raise DependenceError("No plugin named %s!" % plugin_)
            theme = importlib.import_module("modules.themes.%s.index" % theme_name)
        except FileNotFoundError and json.JSONDecodeError and DependenceError:
            logger_main.error("主题[%s]加载失败:\n" + traceback.format_exc())
            try:
                file = open("module/themes/default/index.json" % theme_name)
                theme_info = json.load(file)
                file.close()
            except FileNotFoundError and json.JSONDecodeError and DependenceError as e:
                logger_main.error("默认主题加载失败:\n%s程序已退出" % traceback.format_exc())
                raise e

        enable_apps = configurator_main.read("enable_apps", raise_error=True)  # 加载程序 TODO:添加applogo
        for app_name in enable_apps:
            try:
                file = open("modules/apps/%s/index.json" % app_name)
                app_info = json.load(file)
                file.close()
                for wheel_ in app_info["depended-wheels"]:
                    if wheel_ not in wheels_name:
                        raise DependenceError("No wheel named %s!" % wheel_)
                for plugin_ in app_info["depended-plugins"]:
                    if plugin_ not in plugins:
                        raise DependenceError("No plugin named %s!" % plugin_)
                apps[app_name] = importlib.import_module("modules.apps.%s.index" % app_name)
            except FileNotFoundError and json.JSONDecodeError and DependenceError:
                logger_main.error("程序[%s]加载失败:\n" + traceback.format_exc())

        load_lock.wait()
        ### 主程序开始
        env.init(theme.build(env), plugins, apps)

        # while 1:    # 据说 while 1 的效率比 while True 高
        env.touchpad_driver.ICNT_Scan(touch_recoder_new, touch_recoder_old)
        env.touch_handler.handle(touch_recoder_new, touch_recoder_old)
        """
        #调试用
        env.touchpad_driver.ICNT_Scan(touch_recoder_new, touch_recoder_old)
        env.touch_handler.handle(touch_recoder_new, touch_recoder_old)
        time.sleep(100000)
        """

    except KeyboardInterrupt:
        print("ctrl+c")
    except:  # ⚠️只在生产环境使用 会影响调试结果！！！
        logger_main.error(traceback.format_exc())
    finally:
        env.epd_driver.sleep()
        env.epd_driver.exit()
