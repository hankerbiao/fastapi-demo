from threading import Thread, Event, Lock
from util.Engine import Engine
from util.enums import StatusEnum
from util.utils import execute_rpa
from util.Logger import Logger
import asyncio

logger = Logger()


async def start_app_if_not_running(app):
    """
    如果进程未运行，启动进程
    """
    if app.status == StatusEnum.NOT_RUNNING and app.active_pull_up is True:
        logger.info(f"{app.process_name} is not running, start it now(auto pull up)")
        execution_result = await execute_rpa(app.path, "start")
        logger.info("\n".join(execution_result))


class Monitor(Thread):
    def __init__(self, interval=60):
        Thread.__init__(self)
        self.interval = interval
        self._stop_event = Event()
        self._lock = Lock()

    def run(self) -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.async_run())
        loop.close()

    async def async_run(self):
        logger.info("监控线程已启动,间隔时间为{}秒".format(self.interval))
        while not self._stop_event.is_set():
            app_info_list = Engine()
            apps = app_info_list.apps()
            for app in apps:
                await start_app_if_not_running(app)
            with self._lock:
                self._stop_event.wait(self.interval)
        logger.info("已关闭监控线程")

    def stop(self):
        self._stop_event.set()
        logger.info("正在关闭监控线程...")
