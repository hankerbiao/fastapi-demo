from threading import Thread, Event, Lock
from typing import List
from util.enums import StatusEnum
from util.resources import Application
from util.utils import execute_rpa
from util.Logger import Logger

logger = Logger()


class Monitor(Thread):
    def __init__(self, apps: List[Application], interval=60):
        """
        定时监控进程运行状态
        :param apps: 所有进程
        :param interval:  监控时间间隔（秒）
        """
        Thread.__init__(self)
        self.apps = apps
        self.interval = interval
        self._stop_event = Event()
        self._lock = Lock()

    def run(self) -> None:
        logger.info("监控线程已启动")
        while not self._stop_event.is_set():
            for app in self.apps:
                if app.status == StatusEnum.NOT_RUNNING and app.active_pull_up is True:
                    logger.info(f"{app.process_name} is not running, start it now")
                    res = execute_rpa(app.path, "start")
                    logger.info("".join(res))
            with self._lock:
                self._stop_event.wait(self.interval)
        logger.info("已关闭监控线程")

    def stop(self):
        self._stop_event.set()
        logger.info("正在关闭监控线程...")
