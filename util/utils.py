import os
import shutil
import tarfile

from app.core.RPA.LinuxRPAUtils import LinuxRPA
from util.Logger import Logger
from app.core.RPA.Utils.Utils import cmd_linux
import socket
from util.config import GLOBAL_CONFIG
from util.constants import BACKUP_PATH

rpa = LinuxRPA()
global_param = GLOBAL_CONFIG()
logger = Logger()


def execute_rpa(path, order):
    """
    执行RPA命令
    """
    shell_path = os.path.split(path)[0]
    execute_shell = os.path.split(path)[1]
    if execute_shell.find('start-emss.sh') > -1:
        execute_shell = execute_shell.replace("  ", f" {order} ")  # 兼容h2
    cmd_linux(f"chmod 777 {execute_shell}")  # 赋予执行权限
    logger.info(f"cd {shell_path} && ./" + execute_shell + f" {order}")
    res = cmd_linux(f"cd {shell_path} && ./" + execute_shell + f" {order}")
    res.insert(0, f"执行命令：./{execute_shell} {order}")
    res.insert(0, f"shell_path：{shell_path}")
    return res


def is_port_open(port, ip='127.0.0.1'):
    if port is None:
        return 2
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)  # 设置超时时间，单位是秒
    try:
        sock.connect((ip, port))  # 尝试连接到指定的IP和端口
        return 0  # 如果连接成功，说明端口是开放的
    except socket.error:  # 如果出现异常，说明端口未开放
        return 1
    finally:
        sock.close()  # 关闭socket连接


def extract_and_move_tar(target_dir, bak_dir):
    """
    安装目录下的tar包解压并移动到bak目录下
    """
    try:
        os.mkdir(BACKUP_PATH)
    except Exception:
        pass
    # 遍历目标文件夹下的所有文件
    for filename in os.listdir(target_dir):
        file_path = os.path.join(target_dir, filename)
        bak_path = os.path.join(bak_dir, filename)
        if os.path.isfile(file_path) and filename.endswith('.tar.gz'):
            # 判断是否为tar包
            logger.info(f"找到tar包: {filename}")
            # 解压tar包
            with tarfile.open(file_path, 'r') as tar:
                tar.extractall(path=target_dir)
                logger.info(f"解压完成: {filename}")

                # 将解压完成的tar包移动到bak目录下
            shutil.move(file_path, bak_path)
            logger.info(f"移动到bak目录: {bak_path}")


def append_to_bash_profile(content):
    # 获取当前用户的主目录
    home_dir = os.path.expanduser("~")

    # 构造bash_profile的路径
    bash_profile_path = os.path.join(home_dir, ".bash_profile")
    # 查看是否已存在JAVA_HOME，如果已存在则不继续生成
    with open(bash_profile_path, "r") as f:
        for line in f.readlines():
            if line.find("JAVA_HOME") > -1:
                logger.info("已存在JAVA_HOME，不再生成")
                return

    # 使用'>>'来追加内容，而不是覆盖原有内容
    with open(bash_profile_path, "a") as f:
        f.write(content)
        f.write("\n")  # 为了格式清晰，我们在每行的末尾添加一个换行符
    # todo 配置文件生效


# 启动nginx
def start_nginx():
    nginx_path = os.path.join(global_param.install_path, "emss-web/nginx/sbin")
    if os.path.exists(nginx_path):
        cmd_linux(f"cd {nginx_path} && chmod 777 * && ./run.sh start")
        status = rpa.status("nginx")
        if status == 1:
            logger.info(f"启动nginx成功！")
        else:
            logger.error(f"启动nginx失败！,请手动执行检查！")
