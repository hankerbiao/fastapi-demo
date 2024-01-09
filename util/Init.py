from typing import List, Dict, Tuple
import os
from app import global_param, rpa, logger
from util.utils import is_port_open, execute_rpa
from util.constants import COMPOSE_LIST, SERVER_TYPE
from util.resources import Application
from dataclasses import asdict
from util.enums import StatusEnum, Method


def get_base_info(app_name: str) -> Tuple:
    """
    获取目录信息，包括进程id和启动脚本路径
    :param app_name:
    :return:
    """
    status_code: int = rpa.status(app_name)
    pids = []
    app_config: Dict = global_param.config.get("component", {})
    if app_name == "emss-server-1.0.0-RELEASE.jar":
        app_name = "emss-server"
    app_config = app_config.get(app_name)
    dir_name = app_config.get("directory_name")
    port = app_config.get("port")
    relative_path = app_config.get("script_path")
    dir_path = os.path.join(global_param.install_path, dir_name)
    start_script_path = os.path.join(dir_path, relative_path)
    port_status = is_port_open(port)
    if not os.path.exists(start_script_path.replace("start-emss.sh  h2", "start-emss.sh")):
        start_script_path = f'{os.path.join(global_param.install_path, dir_name)}' \
                            f'目录下未发现启动脚本：{relative_path}'
        return port, port_status, status_code, pids, start_script_path

    # 获取进程id
    for i in os.listdir(dir_path):
        if isinstance(i, bytes):  # 检查i是否是bytes类型
            i = i.decode('utf-8')  # 将bytes对象转换为str对象

        if i.find('.pid') > -1:
            pids.append(i.split('.')[0])

    return port, port_status, status_code, pids, start_script_path


class Init():
    """
    应用初始化,存储应用信息
    """

    def __init__(self, app=None):
        self.__apps: List[Application] = []
        self.compose_list = COMPOSE_LIST
        self.app = app
        self.init(app)

    def init(self, app=None) -> None:
        """
        初始化应用信息
        """
        if app is not None:
            # 获取单个app信息
            port, port_status, status_code, pids, path = get_base_info(app_name=app)
            app = Application(
                process_name=app,
                path=path,
                pids=pids,
                status=StatusEnum.IS_RUNNING if status_code == 1 else StatusEnum.NOT_RUNNING,
                port_status=port_status,
                port=port
            )
            self.__apps.append(app)
            return

        for app_name in self.compose_list:
            port, port_status, status_code, pids, path = get_base_info(app_name)

            app = Application(
                process_name=app_name,
                path=path,
                pids=pids,
                status=StatusEnum.IS_RUNNING if status_code == 1 else StatusEnum.NOT_RUNNING,
                port_status=port_status,
                port=port
            )
            self.__apps.append(app)

    def get_apps(self):
        return self.__apps

    def get_apps_info(self):
        """
        获取应用信息
        :return:
        """
        return [asdict(i) for i in self.__apps]

    @property
    def script_path(self):
        # 获取单个app 启动脚本path，仅适用于查询单个app时
        if self.app is None:
            raise Exception("未设置app参数")

        if self.__apps and len(self.__apps) == 1:
            return self.__apps[0].path
        else:
            raise Exception("查询单个app出现多条路径")

    @property
    def path(self):
        # 获取单个app 目录path，仅适用于查询单个app时
        if self.app is None:
            raise Exception("未设置app参数")

        if self.__apps and len(self.__apps) == 1:
            return os.path.dirname(os.path.dirname(self.__apps[0].path))
        else:
            raise Exception("查询单个app出现多条路径")

    def batch(self, order: str, server_name: str) -> List[str]:
        logger.info(f"执行命令：{order}, 服务：{server_name}")
        result = []
        apps_name: List[str] = SERVER_TYPE.get(server_name.upper())
        if not apps_name:
            raise Exception(f"未找到{server_name}对应的应用")

        for app in self.__apps:
            if app.process_name in apps_name:
                res = ""
                if order == Method.START or order == Method.STOP or order == Method.RESTART:
                    print(app.path)
                    res = execute_rpa(app.path, order)
                elif order == Method.STATUS:
                    res = rpa.status(app.process_name)
                result.append(res)
        return result
