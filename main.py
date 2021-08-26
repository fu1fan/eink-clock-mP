import json
import os
import threading
import importlib
import time
import traceback

from sdk import environment

from sdk import logger
from sdk import configurator
from PIL import Image
from pathlib import Path

# TODO(修复):修复屏幕休眠机制
# TODO(功能):添加页面组织器
# TODO(功能):ListElement右上角显示页码
# TODO(功能):添加双指双击刷新屏幕的功能
# TODO(优化):改写docker触摸实现
# TODO(优化):为支持的应用添加图像缓存，加速渲染
# TODO(优化):取消env中页面队列大小
# TODO(功能):统一资源库（字体、图像）
# TODO(优化):appControlBar添加时间显示
# TODO(功能):为paper加入choice和prompt元件
# TODO(功能):网络配置
# TODO(功能):应用商店
# TODO(功能):应用排序
# TODO(功能):插件管理
# TODO(功能):线程池扩容功能
# TODO(功能):添加文字居中的功能


example_config = {
    "main": {
        "enable_plugins": ["hello_world"],
        "enable_theme": "default",
        "enable_apps": ["简单清单", "简单计算器", "账号管理", "随机数生成器", "一言", "祖安宝典", "系统选项", "hello_world"],
        "opening_images": [
            "resources/images/raspberry.jpg",
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
    "updater": {},
    "update_tdduudf7": 1
}


class DependenceError(Exception):
    pass


def main_thread():  # 主线程：UI管理（如果有模拟器就不是主线程了）

    opening_images = []  # 准备开屏动画
    opening_images_path = configurator_main.read("opening_images")
    for path in opening_images_path:
        opening_images.append(Image.open(Path(path)))
    paper_now = environment.graphics.Paper(env, opening_images[0])
    load_lock = threading.Barrier(2)

    def opening():
        paper_now.init()
        if len(opening_images) >= 1:
            for i in opening_images[1:]:
                paper_now.update_background(i)
        if load_lock.n_waiting == 0:  # 如果等动画显示完后主线程还没进入等待，则显示Loading画面
            paper_now.update_background(Image.open(Path(configurator_main.read("loading_image"))))
        load_lock.wait()

    try:
        # 显示开屏动画
        env.pool.add(opening)
        # 在这里放置要预加载的东西（主题与插件等）
        touch_recoder_new = environment.touchpad.TouchRecoder()  # 触摸
        touch_recoder_old = environment.touchpad.TouchRecoder()

        wheels_name = []
        plugins = {}
        theme = None
        apps = {}
        enable_plugins = configurator_main.read(
            "enable_plugins", raise_error=True)
        for wheel_name in os.listdir("modules/wheels"):  # 检测当前的轮子
            if wheel_name.endswith(".py") and (wheel_name != "__init__.py"):
                wheels_name.append(wheel_name[:-3])

        for plugin_name in enable_plugins:  # 加载已注册的插件
            try:
                file = open(Path("modules/plugins/%s/index.json" % plugin_name))
                plugin_info = json.load(file)
                file.close()
                for wheel_ in plugin_info["depended-wheels"]:
                    if wheel_ not in wheels_name:
                        raise DependenceError("No wheel named %s!" % wheel_)
                plugins[plugin_name] = importlib.import_module(
                    "modules.plugins.%s.index" % plugin_name)

            except FileNotFoundError and json.JSONDecodeError and DependenceError:
                logger_main.error("插件[%s]加载失败:\n" + traceback.format_exc())

        plugin_init_lock = threading.Barrier(len(plugins) + 1)

        def plugin_init(plugin):
            plugin.init(env)
            plugin_init_lock.wait()

        for value in plugins.values():
            env.pool.add(plugin_init, value)

        theme_name = configurator_main.read(
            "enable_theme", raise_error=True)  # 加载主题
        try:
            file = open(Path("modules/themes/%s/index.json" % theme_name))
            theme_info = json.load(file)
            file.close()
            for wheel_ in theme_info["depended-wheels"]:
                if wheel_ not in wheels_name:
                    raise DependenceError("No wheel named %s!" % wheel_)
            for plugin_ in theme_info["depended-plugins"]:
                if plugin_ not in plugins:
                    raise DependenceError("No plugin named %s!" % plugin_)
            try:
                if theme_info["icon_18px"]:
                    icon_18px = theme_info["icon_18px"]
                else:
                    icon_18px = None
            except:
                icon_18px = None
            try:
                if theme_info["icon_20px"]:
                    icon_20px = theme_info["icon_20px"]
                else:
                    icon_20px = None
            except:
                icon_20px = None
            theme = [importlib.import_module(
                "modules.themes.%s.index" % theme_name), (icon_18px, icon_20px)]
        except FileNotFoundError and json.JSONDecodeError and DependenceError:
            logger_main.error("主题[%s]加载失败:\n" + traceback.format_exc())
            try:
                file = open(Path("module/themes/default/index.json" % theme_name))
                theme_info = json.load(file)
                file.close()
            except FileNotFoundError and json.JSONDecodeError and DependenceError as e:
                logger_main.error("默认主题加载失败:\n%s程序已退出" %
                                  traceback.format_exc())
                raise e

        enable_apps = configurator_main.read(
            "enable_apps", raise_error=True)  # 加载程序
        for app_name in enable_apps:
            try:
                file = open(Path("modules/apps/%s/index.json" % app_name))
                app_info = json.load(file)
                file.close()
                for wheel_ in app_info["depended-wheels"]:
                    if wheel_ not in wheels_name:
                        raise DependenceError("No wheel named %s!" % wheel_)
                for plugin_ in app_info["depended-plugins"]:
                    if plugin_ not in plugins:
                        raise DependenceError("No plugin named %s!" % plugin_)
                try:
                    if app_info["icon_18px"]:
                        icon_18px = app_info["icon_18px"]
                    else:
                        icon_18px = None
                except:
                    icon_18px = None
                try:
                    if app_info["icon_20px"]:
                        icon_20px = app_info["icon_20px"]
                    else:
                        icon_20px = None
                except:
                    icon_20px = None
                apps[app_name] = [importlib.import_module("modules.apps.%s.index" % app_name),
                                  (icon_18px, icon_20px), None]
            except FileNotFoundError and json.JSONDecodeError and DependenceError:
                logger_main.error("程序[%s]加载失败:\n" + traceback.format_exc())

        plugin_init_lock.wait(timeout=5)
        load_lock.wait()
        # 主程序开始
        env.init(theme[0].build(env), plugins, apps)

    except KeyboardInterrupt:
        print("ctrl+c")
    except:  # ⚠️只在生产环境使用 会影响调试结果！！！
        logger_main.error(traceback.format_exc())


if __name__ == "__main__":
    logger_main = logger.Logger(logger.DEBUG)  # 日志

    configurator_main = configurator.Configurator(logger_main)  # 配置
    configurator_main.check(example_config, True)
    configurator_main.change_path("/main")

    simulator = environment.Simulator()  # 我是一个模拟器
    env = environment.Env(configurator_main.read(
        "env_configs"), logger_main, simulator)  # 有模拟器的env
    mainThrd = threading.Thread(target=main_thread, daemon=True)  # 因为模拟器必须得是主线程
    mainThrd.start()  # 原来的主线程就得让位了~

    simulator.open(env)  # 打开模拟器
