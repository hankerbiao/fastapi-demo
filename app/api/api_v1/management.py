import os.path
import threading
import time

from fastapi import APIRouter, status, Form

from app import global_param
from app.core.EmssRPA.Utils.Utils import cmd_linux
from response.response import Response
from util.api_utils import get_app_path
from typing import Optional, Dict

router = APIRouter()


@router.get('/get_component_infos', status_code=status.HTTP_200_OK)
def get_infos():
    """
    获取各个组件的基本信息
    返回组件名称、组件状态、组件安装路径
    :return:
    """
    datas = []
    for data in global_param.COMPONENT_LIST:
        res: Dict[str, str] = get_app_path(data)
        datas.append(res)
    count: int = len(datas)

    return Response(code=0, msg='', count=count, data=datas)


@router.get("/rpa", status_code=status.HTTP_200_OK)
async def create_data_source(path: Optional[str], order: Optional[str]):
    """
    执行cmd命令，将启动脚本返回前端
    """

    lock = threading.Lock()
    lock.acquire()
    try:
        shell_path = os.path.split(path)[0]
        execute_shell = os.path.split(path)[1]
        if execute_shell.find('start-emss.sh') > -1:
            execute_shell = execute_shell.replace("  ", f" {order} ")
        cmd_linux(f"chmod +x {execute_shell}")
        res = cmd_linux(f"cd {shell_path} && ./" + execute_shell + f" {order}")

        res.insert(0, f"执行命令：./{execute_shell} {order}")
        res.insert(0, f"shell_path：{shell_path}")
    except Exception as e:
        res = [f"执行命令失败：{e}"]
    finally:
        lock.release()
    time.sleep(0.5)

    return Response(code=1, msg='', data=res)
