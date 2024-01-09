import os
import re
import shutil
import tarfile
import traceback

from app.core.RPA.LinuxRPAUtils import LinuxRPA
from util.Logger import Logger
from app.core.RPA.Utils.Utils import cmd_linux
from functools import lru_cache
import socket
from util.config import GLOBAL_CONFIG
from util.constants import BACKUP_PATH, IP_PATTERN

rpa = LinuxRPA()
global_param = GLOBAL_CONFIG()
logger = Logger()


def get_one_key_config(param: str = None):
    """
    读取全局配置文件server.conf文件，带参数返回对应的值，不带参数返回整个文件内容
    :return:
    """
    server_conf_path = global_param.server_conf_path
    if not os.path.exists(server_conf_path):
        logger.info('server.conf文件不存在')
        return ''

    with open(server_conf_path, 'r', encoding='utf8') as f:
        for line in f:
            if line.lower().find(param.lower()) > -1:
                param_name, result = line.split('=')
                return result.replace("'", "").strip()
    return ''


def execute_rpa(path, order):
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


@lru_cache()
def get_h2_base():
    ip = get_one_key_config("DB_HOST")
    port = get_one_key_config("DB_PORT")
    host = ip + ":" + port
    db_username = get_one_key_config("DB_USERNAME")
    db_password = get_one_key_config("DB_PASSWORD")
    db_name = get_one_key_config("DB_DBNAME")

    return host, db_username, db_password, db_name


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


def init_server_config() -> bool:
    old_configserver_path = os.path.join(global_param.install_path, "../configserver")
    if os.path.exists(old_configserver_path):
        logger.info("存在旧的configserver！")
        new_configserver_path = os.path.join(global_param.work_path, "configserver")
        if os.path.exists(new_configserver_path):
            shutil.rmtree(new_configserver_path)
        shutil.move(old_configserver_path, global_param.work_path)
        logger.info("移动旧的configserver到工作目录下！")
        global_param.first_upgrade = False
        return False
    else:
        logger.info("不存在旧的configserver！")
        # 初始化server_config配置
        server_config_path = global_param.config_center_path.get("server.conf")
        if not os.path.exists(server_config_path):
            try:
                shutil.copy(global_param.config_center_path.get("server.conf_模板"), server_config_path)
                with open(server_config_path, "r") as f:
                    server_config = f.read()
                server_config = re.sub(IP_PATTERN, global_param.local_ip, server_config)
                with open(server_config_path, "w") as f:
                    # todo 是否需要赋予文件权限
                    f.write(server_config)

                logger.info(f"首次升级，生成{server_config_path}成功！")
            except Exception as e:
                logger.info(e)
                logger.info(traceback.format_exc())
                logger.error(traceback.format_exc())
            return True
        else:
            logger.info(f"{server_config_path}已存在，不再重新生成！")
            return False
