from abc import ABC, abstractmethod
from functools import wraps
import requests
import re
from util.utils import execute_rpa


class RPAAbstract(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def execute(self, command):
        """执行命令"""


def remote(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.remote_flag:
            url = f"http://{self.host}/api/console_v1/management/rpa?path={self.path}&order={self.order}"
            response = requests.get(url)
            kwargs['response'] = response.text
        return func(self, *args, **kwargs)

    return wrapper


class RPAUtils(RPAAbstract):
    def __init__(self, path, order):
        super().__init__()
        self.path = path
        self.order = order
        self.host = ""
        self.remote_flag = False
        split_path = self.path.split("^")
        if len(split_path) > 1:
            self.path = split_path[1]
            self.host = split_path[0]
            if re.match("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+$", self.host):  # 检查self.host格式是否符合ip:端口
                self.remote_flag = True
            else:
                print("远程执行格式错误")

    @remote
    async def execute(self, **kwargs):
        """执行命令"""
        if self.remote_flag:
            response = kwargs.get('response')
        else:
            if self.path.find("nginx") > -1 and self.order == "stop":
                # nginx 不能被停止
                return None
            response = await execute_rpa(self.path, self.order)
        return response
