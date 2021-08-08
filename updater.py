import json
import os
import threading

import requests
import traceback

from sdk import logger
from sdk import graphics
from sdk import environment
from PIL import Image
from sdk import configurator

branch = "develop"
version = 1
version_name = "beta_0_1"
repository = "https://gitee.com/fu1fan/eink-clock-mP"


class VersionCtrl:
    def __init__(self, __logger: logger.Logger) -> None:
        self.logger = __logger
        self.data = None
        pass

    def __refresh(self) -> bool:
        try:
            response = requests.get("https://gitee.com/fu1fan/pi-zero-w-eink-clock.web/raw/master/update/newest.json")
            response.raise_for_status()
            self.data = json.loads(response.text)
        except requests.RequestException:
            self.logger.error(traceback.format_exc(), "无法获取最新版本信息")
            return False
        except json.JSONDecodeError:
            self.logger.error(traceback.format_exc(), "无法解析最新版本信息")
            return False
        return True

    def if_update(self):
        if self.__refresh():
            try:
                if version >= self.data[branch]["version"]:
                    return True
                elif version < self.data[branch]["version"]:
                    return self.data[branch]
            except json.JSONDecodeError:
                self.logger.error(traceback.format_exc(), "无法解析版本信息")
                return False
        return False

    def get_branches(self):  # 若返回为空，则错误
        branches = []
        if self.__refresh():
            for i in self.data:
                branches.append(i)
        return branches

    def change_branch(self, target_branch: str):
        if self.__refresh():
            try:
                if target_branch == branch:
                    self.logger.info('用户所选分支("%s")与目标分支相同' % target_branch, "目标分支与当前分支相同")
                    return False
                elif self.data[target_branch] is None:
                    self.logger.warn('"%s"分支为空' % target_branch, "分支无内容")
                    return False
                else:
                    __file = open("changeBranch", "w", encoding="utf-8")
                    __file.write(target_branch)
                    self.logger.debug('准备从"%s"切换到"%s"' % (branch, target_branch))
                    return self.data[target_branch]["version_name"]
            except:
                self.logger.error(traceback.format_exc(), "获取分支信息失败")
                return False

if __name__ == "__main__":
    epd_lock = threading.RLock()
    logger_updater = logger.Logger(logger.DEBUG, tag="updater")
    env = environment.Env(dict(auto_sleep_time=30, refresh_time=43200, refresh_interval=30, threadpool_size=20),
                          logger_updater)
    epd = env.epd_driver
    paper = graphics.Paper(env)
    if epd.IsBusy():
        logger_updater.error("The screen is busy!")
        os.system("python3 main.py &")
        raise RuntimeError("The screen is busy!")
    if os.path.exists("reset"):
        logger_updater.info("reset")
        paper.background_image = Image.open(open("resources/images/reset.jpg", mode="rb"))
        paper.init()
        # logger = Logger(0, tag="reset")
        result = os.popen("git checkout .")
        os.remove("reset")
        logger_updater.info("已重置")
    elif os.path.exists("update"):
        logger_updater.info("update")
        paper.background_image = Image.open(open("resources/images/updating.jpg", mode="rb"))
        paper.init()
        # logger = Logger(0, tag="updater")
        result = os.popen("git pull")
        logger_updater.info(result.read())
    elif os.path.exists("changeBranch"):
        logger_updater.info("changeBranch")
        paper.background_image = Image.open(open("resources/images/change.jpg", mode="rb"))
        paper.init()
        # logger = Logger(0, tag="changeBranch")
        file = open("changeBranch", encoding="utf-8")
        targetBranch = file.read()
        result = os.popen("git pull")
        logger_updater.info(result.read())
        os.popen("git checkout .")
        logger_updater.info("已重置")
        result = os.popen("git checkout " + targetBranch)
        logger_updater.info(result.read())
    paper.update_background(Image.open(open("resources/images/done.jpg", mode="rb")))
    epd.sleep()
    os.system("python3 main.py &")
