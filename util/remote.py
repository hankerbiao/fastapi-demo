from typing import Dict

import requests

from util.Logger import Logger

logger = Logger()

time_out = 3


class Remote:
    """
    获取远程控制台信息
    """

    def __init__(self, app_name, host):
        self.host = host
        self.app_name = app_name

    def get_app_status(self) -> Dict:
        """
        获取单个应用状态
        """
        try:
            url = f"http://{self.host}/api/console_v1/management/get_app_status?app_name={self.app_name}"
            res = requests.get(url, timeout=time_out)
            status_code = res.status_code
            if status_code != 200:
                logger.error(f"获取{self.app_name}状态失败，状态码：{status_code}")
                return {"status": "未知"}
        except Exception as e:
            logger.error(e)
            return {"status": "未知"}
        data = res.json().get("data").get("data")
        status = data.get("status")
        script_path = data.get("script_path")
        port_status = data.get("port_status")
        if status == "运行中":
            status = 1
        else:
            status = 0
        return {"status": status, "script_path": script_path, "port_status": port_status,}

    def remote_rpa(self, path, order):
        """
        远程执行rpa
        """
        try:
            url = f"http://{self.host}/api/console_v1/rpa?path={path}&order={order}"
            res = requests.get(url, timeout=time_out)
            status_code = res.status_code
            if status_code != 200:
                logger.error(f"获取{self.app_name}状态失败，状态码：{status_code}")
                return {"status": "未知"}
        except Exception as e:
            logger.error(e)
            return {"status": "未知"}
        data = res.json().get("data").get("data")
        return {"data": data}
