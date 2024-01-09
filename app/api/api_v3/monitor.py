from typing import Optional, List
from queue import Queue  # 多线程安全
from fastapi import APIRouter, status
from response.response import Response
from util.Init import Init
from util.Monitor import Monitor
from util.enums import Method
from util.resources import Application

router = APIRouter()
q = Queue()


@router.get('/monitor', status_code=status.HTTP_200_OK)
def monitor(order: Optional[str]):
    if order == Method.START:
        if q.qsize() > 0:
            return Response(code=0, msg='监控已启动')
        init = Init()
        apps: List[Application] = init.get_apps()
        monitor_thread = Monitor(apps)
        monitor_thread.daemon = True
        q.put(monitor_thread)
        monitor_thread.start()
        if monitor_thread.is_alive():
            return Response(code=0, msg='监控已启动')
        return Response(code=1, msg='监控启动失败')
    elif order == Method.STOP:
        if q.qsize() == 0:
            return Response(code=0, msg='监控未启动')
        monitor_thread = q.get()
        monitor_thread.stop()
        monitor_thread.join()

        if not monitor_thread.is_alive():
            del monitor_thread
            return Response(code=0, msg='监控已停止')
        return Response(code=1, msg='监控停止失败')
