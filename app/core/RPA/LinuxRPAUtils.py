# -*-encoding:utf8-*-
from app.core.RPA.Utils.MsgInfo import StatusCode
from app.core.RPA.Utils.Utils import cmd_linux
from app.core.RPA.Utils.constant import LinuxMsgCode


class LinuxRPA():
    def get_pids_by_process_name(self, process_name):
        """通过进程名称，获取到进程的PID"""
        order2 = "ps -ef | grep -w %s |grep -v grep | grep -v python3 |awk \'{print $2}\'" % process_name
        # 进程信息输出到临时文件
        pids = cmd_linux(order2)
        return pids

    def get_status(self, process_name):
        """
        获取程序运行状态
        --user
        --install_path
        --process_name
        """
        order = "ps aux | grep -w %s |grep -v grep |awk \'{print $1,$2}\'" % process_name

        process_info = cmd_linux(order)
        if process_info:
            if len(process_info) > 0:
                return LinuxMsgCode.IS_RUNNING
        else:
            return LinuxMsgCode.NOT_RUNNING

    def status(self, process_name):
        # 通过进程名称查询运行状态
        status = self.get_status(process_name)
        if status == 0:
            return StatusCode.NOT_RUNNING

        elif status == 1:
            # 通过进程查询到进程信息
            return StatusCode.IS_RUNNING

        elif status == 4:
            # 重复进程
            return status
