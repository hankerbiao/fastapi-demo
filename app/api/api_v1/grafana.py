from fastapi import APIRouter, Form, status
import os
from response.response import Response
from util.Engine import Engine
from util.utils import get_one_key_config, grafana_dashboard, cmd_linux

router = APIRouter()
grafana_info = Engine("grafana")


@router.get("/get_info", status_code=status.HTTP_200_OK)
def get_info():
    """
    获取grafana基本信息
    """
    grafana_host = f"http://{get_one_key_config('GRAFANA_HOST')}:{get_one_key_config('GRAFANA_PORT')}"
    grafana_api_host = f"{grafana_host}/api/"
    dashboard_path = os.path.join(grafana_info.path, 'AutoGrafana/dashboards')
    es_host = f"{get_one_key_config('ES_HOST')}:{get_one_key_config('ES_PORT')}"
    prometheus_host = f"{get_one_key_config('PROMETHEUS_HOST')}:{get_one_key_config('PROMETHEUS_PORT')}"
    grafana_api_key = get_one_key_config("Authorization")
    res_data = {
        'path': grafana_info.script_path,
        'es_host': es_host,
        'prometheus_host': prometheus_host,
        'grafana_api_host': grafana_api_host,
        'dashboard_path': dashboard_path,
        'host': grafana_host,
        'grafana_api_key': grafana_api_key
    }

    return Response(msg='操作成功', data=res_data)


@router.get("/start", status_code=status.HTTP_200_OK)
def start():
    """
    启动grafana
    """
    result = cmd_linux(grafana_info.script_path + " start")
    return Response(data="".join(result))


@router.post("/create_data_source", status_code=status.HTTP_200_OK)
async def create_data_source(Authorization: str = Form(...)):
    """
    导入数据源和看板
    """
    grafana = Engine("grafana")
    res, msg = grafana_dashboard(Authorization.replace("'", ""), grafana.path)
    if res:
        return Response(msg='操作成功', data=msg)
    else:
        return Response(msg='操作失败', data=msg, status=1)
