import os
import socket
from typing import Dict
import yaml


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
            self.configuration: Dict = yaml.safe_load(f)
        self.process_names = list(self.configuration.get("component", {}).keys())
        self.__grafana_directory_path = ""
        self.__installation_directory_path = os.path.dirname(self.work_path)  # emss安装路径
        # 首次升级标志
        self.__is_first_upgrade = True

    @property
    def first_upgrade(self):
        return self.__is_first_upgrade

    @first_upgrade.setter
    def first_upgrade(self, value: bool):
        self.__is_first_upgrade = value

    @property
    def server_port(self) -> int:
        return int(self.configuration.get("PORT", 8000))

    @property
    def grafana_path(self):
        return self.__grafana_directory_path

    @grafana_path.setter
    def grafana_path(self, value):
        self.__grafana_directory_path = value

    @property
    def install_path(self):
        """
        emss获取安装路径（/home/emss/build）
        :return:
        """
        return self.__installation_directory_path

    @property
    def configserver_path(self):
        return "./configserver"

    @property
    def server_conf_file_path(self):
        return f"{self.configserver_path}/server.conf"

    @property
    def config_center_path(self):
        path = {
            "custom-installation-config.json": f"{self.configserver_path}/ConfigServer/installationConfig/custom-installation-config.json",
            "server.conf": self.server_conf_file_path,
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

    @property
    def database_path(self):
        """
        数据库文件所在路径
        """
        return os.path.join(self.install_path, "data_test")

    @property
    def database_name(self):
        return "emss.mv.db"
