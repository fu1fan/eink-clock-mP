import json
import os
import requests
import traceback

from sdk.logger import Logger

os.chdir(os.path.dirname(__file__))

branch = "develop"
version = 1
version_name = "beta_0_1"
repository = "https://gitee.com/fu1fan/eink-clock-mP"


class VersionCtrl:
    def __init__(self, __logger: Logger) -> None:
        self.logger = __logger
        self.data = None
        pass

    def __refresh(self) -> bool:
        try:
            response = requests.get("https://gitee.com/fu1fan/pi-zero-w-eink-clock.web/raw/master/update/newest.json")
            response.raise_for_status()
            self.data = json.loads(response.text)
        except:
            self.logger.error(traceback.format_exc(), "无法获取最新版本信息")
            return False
        return True

    def if_update(self):
        if self.__refresh():
            try:
                if version >= self.data[branch]["version"]:
                    return True
                elif version < self.data[branch]["version"]:
                    return self.data[branch]
            except:
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


if __name__ == "__main__":  # TODO:添加显示功能
    logger = Logger(0, tag="updater")
    if os.path.exists("update"):
        result = os.popen("git pull")
        logger.info(result.read())
    elif os.path.exists("reset"):
        result = os.popen("git checkout .")
        os.remove("reset")
    elif os.path.exists("changeBranch"):
        file = open("changeBranch", encoding="utf-8")
        targetBranch = file.read()
        result = os.popen("git pull")
        logger.info(result.read())
        result = os.popen("git checkout .")
        logger.info(result.read())
        result = os.popen("git checkout " + targetBranch)
        logger.info(result.read())

    os.system("python3 main.py &")
