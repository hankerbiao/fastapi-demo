from dataclasses import dataclass, field
from typing import List


@dataclass
class Application:
    """
    Application dataclass
    """
    process_name: str
    path: str
    pids: list
    port: int = field(default=0)
    port_status: str = field(default="未运行")  # 端口占用情况
    status: str = field(default="未运行")  # 进程运行状态
    active_pull_up: bool = field(default=True)


@dataclass
class BelongServer:
    apps: List[Application]
    descript: str
    server_name: str
