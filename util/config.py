import os
import socket
from typing import Dict
import yaml
from util.constants import *


class GLOBAL_CONFIG:
    """
    全局配置
    """
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(GLOBAL_CONFIG, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    # 控制台项目根目录
    work_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def __init__(self):
        with open("config.yml", 'r', encoding='utf8') as f:
            self.config: Dict = yaml.safe_load(f)
        self.__grafana_path = ""
        self.__install_path = os.path.dirname(self.work_path)  # emss安装路径
        self.component_list = COMPOSE_LIST
        # 首次升级标志
        self.__first_upgrade = True

    @property
    def first_upgrade(self):
        return self.__first_upgrade

    @first_upgrade.setter
    def first_upgrade(self, value: bool):
        self.__first_upgrade = value

    @property
    def port(self) -> int:
        return int(self.config.get("PORT", 8000))

    @property
    def start_script_path(self):
        return self.config.get("start_script_path")

    @property
    def grafana_path(self):
        return self.__grafana_path

    @grafana_path.setter
    def grafana_path(self, value):
        self.__grafana_path = value

    @property
    def install_path(self):
        """
        获取安装路径
        :return:
        """
        return self.__install_path

    @property
    def configserver_path(self):
        return self.config.get("configserver_path")

    @property
    def server_conf_path(self):
        return f"{self.configserver_path}/server.conf"

    @property
    def config_center_path(self):
        path = {
            "custom-installation-config.json": f"{self.configserver_path}/ConfigServer/installationConfig/custom-installation-config.json",
            "custom-installation-config.json2": f"ConfigServer/installationConfig/custom-installation-config.json",
            "server.conf": f"{self.configserver_path}/server.conf",
            "server.conf_模板": f"{self.configserver_path}/server.conf_模板"
        }
        return path

    @property
    def local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        except:
            local_ip = socket.gethostbyname(socket.gethostname())

        return local_ip
