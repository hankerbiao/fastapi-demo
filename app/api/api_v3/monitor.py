from queue import Queue  # 多线程安全
from fastapi import APIRouter, status
from response.response import Response
from util.Logger import Logger
from util.Monitor import Monitor
import threading

logger = Logger()
router = APIRouter()
q = Queue()
LAST_TIME = 5  # 当前设置的监控时间间隔
lock = threading.Lock()


def start_monitor(interval_time):
    try:
        t = Monitor(interval=interval_time * 60)
        t.daemon = True
        q.put(t)
        t.start()
        return t
    except Exception as e:
        logger.error(f"Error starting monitor: {e}")
        return None


default_t = start_monitor(LAST_TIME)
if default_t is None:
    logger.error("Failed to start default monitor")


@router.get('/monitor', status_code=status.HTTP_200_OK)
def monitor(interval_time: int, qsize=None):
    if interval_time < 0:
        # 限制查询范围
        return Response(status=1, msg='监控间隔时间不能小于0')
    global LAST_TIME
    if qsize:
        # 查询监控状态
        if q.qsize() == 0:
            return Response(data=0, msg="监控未启动")
        else:
            return Response(data=LAST_TIME, msg="监控已启动")
    if interval_time > 0:
        if interval_time == LAST_TIME:
            if q.qsize() > 0:
                return Response(data=LAST_TIME, msg='监控已启动')

        if q.qsize() > 0:
            while not q.empty():
                t = q.get()
                t.stop()
                t.join()
        lock.acquire()
        LAST_TIME = interval_time
        lock.release()
        t = start_monitor(interval_time)
        if t is None:
            return Response(status=1, msg='监控启动失败')
        if t.is_alive():
            return Response(data=interval_time, msg='监控已启动')
        return Response(status=1, msg='监控启动失败')
    else:
        if q.qsize() == 0:
            return Response(status=1, msg='监控未启动')
        t = q.get()
        t.stop()
        t.join()
        if not t.is_alive():
            return Response(msg='监控已停止')
        return Response(status=1, msg='监控停止失败')
