from functools import lru_cache
from typing import List, Dict, Tuple
import os
from app import global_param, logger
from util.RPAUtils import RPAUtils
from util.remote import Remote
from util.utils import is_port_open, LinuxRPA
from util.constants import SERVER_TYPE, ZH_EN
from util.schemes import Application
from dataclasses import asdict
from util.enums import StatusEnum, Method

SERVERS = SERVER_TYPE.keys()


def get_response(process_name, status, res):
    return {
        "process_name": process_name,
        "status": status,
        "msg": "\n".join(res),
        "server_name": get_server_name(process_name)
    }

@lru_cache
def get_server_name(app):
    for key, value in SERVER_TYPE.items():
        if app in value:
            return ZH_EN.get(key, "未找到")


def get_base_info(app_name: str) -> Tuple:
    """
    获取目录信息，包括进程id和启动脚本路径
    如果配置了host远程服务端，返回远程服务端信息
    """
    process_status_code: int = LinuxRPA.status(app_name)
    cfg: Dict = global_param.configuration.get("component", {})
    specific_cfg = cfg.get(app_name)
    active_pull = specific_cfg.get("keep-alive", True)  # 是否主动拉起
    dir_name = specific_cfg.get("directory_name", "")  # 目录名
    port = specific_cfg.get("port", "")  # 端口号
    startup_sequence = specific_cfg.get("startup_sequence", -1)  # 端口号
    relative_path = specific_cfg.get("script_path", "")  # 启动脚本相对路径
    dir_path = os.path.join(global_param.install_path, dir_name)  # 目录绝对路径
    path = os.path.join(dir_path, relative_path)  # 启动脚本绝对路径
    port_status = is_port_open(port)  # 端口状态
    host = specific_cfg.get("host", "")  # 远程主机
    if host:
        remote = Remote(app_name, host)
        info = remote.get_app_status()
        process_status_code = info.get("status")
        port_status = info.get("port_status")
        path = host + "^" + info.get("script_path", "")
    else:
        if not os.path.exists(path.replace("start-emss.sh  h2", "start-emss.sh")):
            path = f'{os.path.join(global_param.install_path, dir_name)}' \
                   f'目录下未发现启动脚本：{relative_path}'
    # 端口状态、进程状态、启动脚本路径、是否主动拉起、远程主机
    return port_status, process_status_code, path, active_pull, host, startup_sequence


def get_app_info(app_name):
    """
    获取单个应用信息
    """
    port_status, status_code, path, active_pull, host, startup_sequence = get_base_info(app_name)
    app = Application(
        process_name=app_name,
        path=path,
        status=StatusEnum.IS_RUNNING if status_code == 1 else StatusEnum.NOT_RUNNING,
        port_status=port_status,
        active_pull_up=active_pull,
        host=host,
        startup_sequence=startup_sequence
    )
    return app


class Engine():
    """
    应用初始化,存储应用信息,控制台核心组件
    """

    def __init__(self, app=None):
        self.__application_list: List[Application] = []
        self.compose_list = global_param.process_names
        self.app = app
        self.init(app)

    def init(self, app_name=None) -> None:
        self.__application_list.clear()
        """
        初始化应用信息，获取到每个组件的当前状态信息
        """
        if app_name is not None:
            # 获取单个app信息
            self.__application_list.append(get_app_info(app_name))
            return
        for app_name in self.compose_list:
            self.__application_list.append(get_app_info(app_name))
        if self.__application_list:
            self.__application_list.sort(key=lambda x: x.startup_sequence)

    def apps(self):
        """
        获取所有组件信息
        """
        return self.__application_list

    def server_infos(self, server_name):
        """
        获取服务信息
        """
        return [asdict(i) for i in self.__application_list if i.process_name in SERVER_TYPE.get(server_name.upper())]

    @property
    def script_path(self):
        """
        单个应用启动脚本路径
        """
        if self.app is None:
            raise Exception("未设置app参数")

        if self.__application_list and len(self.__application_list) == 1:
            return self.__application_list[0].path
        else:
            raise Exception("查询单个app出现多条路径")

    @property
    def port_status(self):
        """
        单个应用都那口状态
        """
        if self.app is None:
            raise Exception("未设置app参数")

        if self.__application_list and len(self.__application_list) == 1:
            return self.__application_list[0].port_status
        else:
            raise Exception("查询单个app出现多条路径")

    async def batch(self, command: str, server_name: str) -> List[Dict]:
        """
        批量执行命令
        """
        result = []
        apps_name: List[str] = SERVER_TYPE.get(server_name.upper())
        if not apps_name:
            logger.error(f"未找到{server_name}对应的应用")
        for app in self.__application_list:
            app_name = app.process_name
            app_status = {}
            if app_name in apps_name:
                if command == Method.START or command == Method.STOP or command == Method.RESTART:
                    rpa = RPAUtils(app.path, command)
                    res = await rpa.execute()
                else:
                    res = LinuxRPA.status(app_name)
                app_status["process_name"] = app_name
                app_status["status"] = StatusEnum.IS_RUNNING if res == 1 else StatusEnum.NOT_RUNNING
                app_status["port_status"] = app.port_status
                result.append(app_status)
        return result

    async def all_servers_info(self):
        """
        获取所有服务信息
        """
        response_data = []
        for server in SERVERS:
            port_state = True
            all_server_status = await self.batch("status", server)
            status = all([i["status"] == StatusEnum.IS_RUNNING for i in all_server_status])

            port_status = [i["port_status"] for i in all_server_status]

            for port in port_status:
                if port:
                    for i in port:
                        if i["status"] != 0:
                            port_state = False
            tmp_dict = {
                "server_name": ZH_EN.get(server),
                "server_name_en": server,
                "status": "正常" if status and port_state else "异常",
            }
            response_data.append(tmp_dict)
        return response_data

    async def all_rpa(self, command: str) -> List:
        """
        启动 关闭 重启 所有组件
        """
        response = []
        # 根据

        for app in self.__application_list:
            if command == "start" or command == "restart":
                logger.info(f"start:{app.path},start_order：{app.startup_sequence}")
                rpa = RPAUtils(app.path, command)
                res = await rpa.execute()
                if res is not None:
                    status = LinuxRPA.status(app.process_name)
                    if app.startup_sequence != -1 and status == 0:
                        response.append(get_response(app.process_name, status, res))
                        return response  # 有序启动失败，直接返回
                    response.append(get_response(app.process_name, status, res))

            if command == "stop":
                rpa = RPAUtils(app.path, command)
                res = await rpa.execute()
                if res is not None:
                    status = LinuxRPA.status(app.process_name)
                    response.append(get_response(app.process_name, 0 if status else 1, res))

        return response

    def status(self):
        """
        所有组件状态
        """
        response = []
        for app in self.__application_list:
            response.append({
                "process_name": app.process_name,
                "status": LinuxRPA.status(app.process_name),
            })

        return response

    @property
    def path(self):
        return os.path.dirname(os.path.dirname(self.__application_list[0].path))
