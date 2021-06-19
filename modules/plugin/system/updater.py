import requests
from sdk import logger
import main
import json

def checkForUpdate() -> dict:
    try:
        response = requests.get("https://pi/simplebytes.cn/update/newest.json")
        response.raise_for_status()
        newest = json.loads(response.text)
    except requests.exceptions:
        logger.defaultLogger.warn("无法获取更新详情")
        return {}
    except:
        logger.defaultLogger.error("解析服务端更新信息出错，请检查软件版本是否过低")
        return {}
    

if __name__ == "__main__":
    updateLogger = logger.Logger("logs", update=True)