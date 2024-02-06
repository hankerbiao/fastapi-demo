from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Application:
    """
    应用数据结构
        * process_name: 进程名
        * path: 进程路径
        * port_status: 端口占用情况  0为正常 ，1为异常
        * status: 进程运行状态
        * active_pull_up: 是否主动拉起
    """
    process_name: str
    path: str
    port_status: List[Dict] = None
    status: str = field(default="未运行")
    active_pull_up: bool = field(default=True)
    host: str = field(default="")
    startup_sequence: int = field(default=-1)
