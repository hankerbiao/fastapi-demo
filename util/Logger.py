import time
import os
import sys
from loguru import logger

time_format = time.strftime("%Y%m")
Format = '{time:%Y-%m-%d %H:%M:%S.%f}|L={level}|T={thread.id} {thread.name}|{message}'
log_path = 'logs'

os.makedirs(log_path, exist_ok=True)


class Logger():
    __instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(Logger, cls).__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self):
        self.__error_log = None
        self.__warning_log = None
        self.__info_log = None
        logger.remove()
        logger.add(sys.stderr, format="<green>{time:YYYYMMDD HH:mm:ss}</green> | "  # 颜色>时间
                                      "<level>{level}</level>: "  # 等级
                                      "<level>{message}</level>", level='INFO')
        logger.add(os.path.join(log_path, f"info_{time_format}.log"),
                   filter=lambda record: record["extra"]["name"] == "info", compression="zip", level='INFO',
                   enqueue=True, format=Format, rotation="3 days", retention="3 days", encoding="utf-8")

        logger.add(os.path.join(log_path, f"error_{time_format}.log"),
                   filter=lambda record: record["extra"]["name"] == "error", compression="zip", level='ERROR',
                   enqueue=True, format=Format, rotation="3 days", retention="3 days", encoding="utf-8")

        logger.add(os.path.join(log_path, f"warning_{time_format}.log"),
                   filter=lambda record: record["extra"]["name"] == "warning", compression="zip", level='WARNING',
                   enqueue=True, format=Format, rotation="3 days", retention="3 days", encoding="utf-8")

        self.__info_log = logger.bind(name="info")
        self.__error_log = logger.bind(name=f"error")
        self.__warning_log = logger.bind(name=f"warning")

    def info(self, msg):
        self.__info_log.info(msg)

    def error(self, msg):
        self.__error_log.error(msg)

    def warning(self, msg):
        self.__warning_log.warning(msg)
