from logging import log
import os, requests, json, traceback
from sdk.logger import Logger

os.chdir(os.path.dirname(__file__))

branch = "develop"
version = 1
version_name = "beta_0_1"
repository = "https://gitee.com/fu1fan/eink-clock-mP"

class VersionCtrl:
    def __init__(self, logger:Logger) -> None:
        self.logger = logger
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

    def ifUpdate(self):
        if self.__refresh():
            try:
                if version >= self.data[branch]["version"]:
                    return True
                elif version < self.data[branch]["version"]:
                    return self.data
            except:
                self.logger.error(traceback.format_exc(), "无法解析版本信息")
                return False
        return False

    def getBranchs(self):   #若返回为空，则错误
        branchs = []
        if self.__refresh():
            for i in self.data:
                branchs.append(i)
        return branchs

    def chageBranch(self, targetBranch:str):
        if self.__refresh():
            try:
                if targetBranch == branch:
                    self.logger.info('用户所选分支("")与目标分支相同' % targetBranch, "目标分支与当前分支相同")
                    return False
                elif self.data[targetBranch] == None:
                    self.logger.warn('"%s"分支为空' % targetBranch,  "分支无内容")
                    return False
                else:
                    file = open("chageBranch", "w", encoding="utf-8")
                    file.write(targetBranch)
                    self.logger.info('准备从"%s"切换到"%s"' % (branch, targetBranch))
                    return self.data[targetBranch]["version_name"]
            except:
                self.logger.error(traceback.format_exc(), "获取分支信息失败")
                return False

if __name__ == "__main__":
    logger = Logger(0, tag="update")
    if os.path.exists("chageBranch"):
    #TODO:切换分支功能
        os.remove("chageBranch")
    else:
        result = os.popen("git pull")
        logger.info(result.read())  #TODO:添加显示功能
    os.system("python3 main.py &")