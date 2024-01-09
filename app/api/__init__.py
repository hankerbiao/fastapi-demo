from fastapi import APIRouter
from .api_v3 import v3_management, monitor

router = APIRouter()
router.include_router(v3_management.router, prefix='/management', tags=["EMSS 组件管理(v3)"])
router.include_router(monitor.router, prefix='/monitor', tags=["组件状态监控"])
