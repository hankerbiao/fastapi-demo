from typing import Optional
from fastapi import APIRouter, status, Depends
from response.response import Response
from util.Engine import Engine
from util.RPAUtils import RPAUtils
import time

router = APIRouter()


@router.get('/get_component_infos', status_code=status.HTTP_200_OK)
async def get_infos(server_name: Optional[str], init=Depends(Engine)):
    """
    获取各个组件的基本信息
    返回组件名称、组件状态、组件安装路径
    可选参数：main_server,front_server,log_server,monitor_server,middleware_server
    """
    res = init.server_infos(server_name)
    return Response(code=0, msg='', data=res)


@router.get("/get_servers_info", status_code=status.HTTP_200_OK)
async def servers_info(init=Depends(Engine)):
    """
    获取所有服务状态信息
    """
    res = await init.all_servers_info()
    return Response(code=0, msg='', data=res)


@router.get("/batch_order", status_code=status.HTTP_200_OK)
async def batch_order(order: Optional[str], server_name: Optional[str], init=Depends(Engine)):
    """
    根据服务名称执行批量启动、停止、重启、状态查询命令
        * server_name: 组件名称，可选内容：[main_server,front_server,log_server,monitor_server,middleware_server]
        * order: 执行命令：start,stop,restart,status
        server_name 为all时，对所有组件进行控制操作
    """
    t0 = time.time()
    if server_name == "all":
        res = await init.all_rpa(order)
    else:
        res = await init.batch(order, server_name)
    t1 = time.time()
    print("star cost time:", t1 - t0)
    return Response(code=0, msg='', data=res)


@router.get("/rpa", status_code=status.HTTP_200_OK)
async def rpa(path: Optional[str], order: Optional[str]):
    """
    组件控制页面执行启动、停止、重启、状态查询命令
        * path: 组件启动路径
        * order: 命令
    """
    rpa = RPAUtils(path, order)
    res = await rpa.execute()
    return Response(data=res)


@router.get("/get_app_status", status_code=status.HTTP_200_OK)
def get_single_app_status(app_name: Optional[str]):
    """
    获取单个app状态
    """
    engine = Engine(app_name)
    single_status = engine.status
    script_path = engine.script_path
    port_status = engine.port_status
    data = {
        "status": single_status,
        "script_path": script_path,
        "port_status": port_status
    }
    return Response(data=data)
