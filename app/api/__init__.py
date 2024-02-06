from fastapi import APIRouter

from .api_v1 import grafana, comm, h2, configuration
from .api_v3 import v3_management, monitor, upgrade

router = APIRouter()
router.include_router(grafana.router, prefix='/grafana', tags=["Grafana 配置"])
router.include_router(comm.router, prefix='/comm', tags=["EMSS 通用接口"])
router.include_router(h2.router, prefix='/h2', tags=["EMSS H2数据库管理"])
router.include_router(configuration.router, prefix='/configuration', tags=["EMSS 配置管理"])
router.include_router(v3_management.router, prefix='/management', tags=["EMSS 组件管理(v3)"])
router.include_router(monitor.router, prefix='/monitor', tags=["组件状态监控"])
router.include_router(upgrade.router, prefix='/monitor', tags=["EMSS 自升级"])
