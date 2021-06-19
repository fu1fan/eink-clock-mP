import requests
from sdk import logger
import main
import json
import traceback

def checkForUpdate() -> dict:
    try:
        response = requests.get("https://pi.simplebytes.cn/update/newest.json")
        response.raise_for_status()
        newest = json.loads(response.text)
    except requests.exceptions.RequestException:
        logger.defaultLogger.warn(traceback.format_exc(), info="无法获取更新，请检查网络")
        return {}
    except:
        logger.defaultLogger.error(traceback.format_exc(), info="无法解析服务端传来的数据，请检查软件版本是否过低并手动升级")
        return {}
    

if __name__ == "__main__":
    updateLogger = logger.Logger("logs", update=True)
    checkForUpdate()