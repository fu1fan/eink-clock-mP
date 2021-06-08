import os, time
import modules.common.sdk_beta as sdk

os.chdir(os.path.dirname(__file__))

if __name__ == "__main__":
    logger = sdk.defaultLogger
    logger.setLevel(0)
    for i in range(10):
        logger.info("我成功了！")
    conf = sdk.Configuration()