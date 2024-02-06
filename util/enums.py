from enum import Enum


class StrEnum(str, Enum):
    """
    继承str和Enum类，实现枚举值为字符串
    """

    def __str__(self):
        """
        重写__str__方法，使得当打印枚举实例时返回枚举值，而不是枚举名。
        """
        return self.value


class Method(StrEnum):
    """
    启动、关闭、重启
    todo
    升级、回滚、备份、恢复
    """
    START = "start"
    STOP = "stop"
    RESTART = "restart"
    STATUS = "status"


class StatusEnum(StrEnum):
    NOT_RUNNING = "未运行"
    IS_RUNNING = "运行中"
