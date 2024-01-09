from typing import Optional

from fastapi import APIRouter, status
from response.response import Response
from util.Init import Init
from util.utils import execute_rpa

router = APIRouter()


@router.get('/get_component_infos', status_code=status.HTTP_200_OK)
def get_infos():
    """
    获取各个组件的基本信息
    返回组件名称、组件状态、组件安装路径
    :return: 组件信息
    """
    init = Init()
    res = init.get_apps_info()
    return Response(code=0, msg='', count=len(res), data=res)


@router.get("/batch_order", status_code=status.HTTP_200_OK)
def batch_start(order: Optional[str], server_name: Optional[str]):
    """
    批量启动组件
    :param
        * server_name: 组件名称
        * order: 命令
    """
    init = Init()
    res = init.batch(order, server_name)
    print(res)
    return Response(code=0, msg='', data=res)


@router.get("/rpa", status_code=status.HTTP_200_OK)
def rpa(path: Optional[str], order: Optional[str]):
    """
    组件控制页面执行启动、停止、重启、状态查询命令
    :param path: 组件启动路径
    :param order: 命令
    :return: 命令执行结果
    """
    res = execute_rpa(path, order)
    return Response(code=0, msg='', data=res)
