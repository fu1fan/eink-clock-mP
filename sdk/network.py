import requests

def if_online() -> bool:
    try:
        response = requests.get("https://pi.simplebytes.cn/ifonline")
        response.raise_for_status()
    except requests.RequestException:
        return False
    return True
