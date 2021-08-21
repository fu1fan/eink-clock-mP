import time

from PIL import Image


def init(env):
    def debug(env):
        time.sleep(2)
        # env.popup.choice("宝典小时推荐", "昨天我给你吗打电话，结果你妈先挂了！\n——徐浩展", print, print, print)
        pass  # 在这里打断点

    print("Hello world!")
    env.pool.add(debug, env)
