# coding=utf-8
import os
import datetime
import logging
from logging.handlers import RotatingFileHandler


def Singleton(cls):
    _instance = {}

    def _singleton(*args, **kwagrs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwagrs)
        return _instance[cls]

    return _singleton


@Singleton
class Logger():
    def __init__(self, logPath='./EmssRPALogs', encode='utf8'):
        # 设置打印log日志等级
        self._logPath = logPath
        self._encode = encode
        self._logInfo = logging.Logger('info')
        self._logDebug = logging.Logger('debug')
        self._logError = logging.Logger('error')
        self._handle()

    def _handle(self):
        FORMAT = '%(asctime)-15s %(levelname)s -- %(message)s'

        defaultFormat = logging.Formatter(FORMAT)

        if not os.path.exists(self._logPath):
            os.makedirs(self._logPath)

        logDate = datetime.datetime.now().strftime('%Y%m%d')
        # log info
        fileHandlerInfo = logging.handlers.RotatingFileHandler(f'{self._logPath}/log_{logDate}_info.log', mode='a',
                                                               maxBytes=1024 * 1024 * 50, backupCount=100,
                                                               encoding=self._encode)
        fileHandlerInfo.setFormatter(defaultFormat)
        self._logInfo.addHandler(fileHandlerInfo)

        # log debug
        fileHandlerDebug = logging.handlers.RotatingFileHandler('%s/log_%s_debug.log' % (self._logPath, logDate),
                                                                mode='a',
                                                                maxBytes=1024 * 1024 * 50, backupCount=100,
                                                                encoding=self._encode,
                                                                )
        fileHandlerDebug.setFormatter(defaultFormat)
        self._logDebug.addHandler(fileHandlerDebug)

        # log error
        fileHandlerError = logging.handlers.RotatingFileHandler('%s/log_%s_error.log' % (self._logPath, logDate),
                                                                mode='a',
                                                                maxBytes=1024 * 1024 * 50, backupCount=100,
                                                                encoding=self._encode,
                                                                )
        fileHandlerError.setFormatter(defaultFormat)
        self._logError.addHandler(fileHandlerError)

    def error(self, msg):
        self._logError.error(msg)

    def info(self, msg):
        self._logInfo.info(msg)

    def debug(self, msg):
        self._logDebug.debug(msg)
