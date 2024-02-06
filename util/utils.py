import asyncio
import re
import shutil
import tarfile
import traceback
import os
import codecs
from typing import List, Dict
import subprocess
from app.core.GrafanaImport.GrafanaImport import AutoGrafana
from configserver.ConfigServer.start import config_server_main
from util.Logger import Logger
import socket
from util.config import GLOBAL_CONFIG
from util.constants import BACKUP_PATH, IP_PATTERN

global_param = GLOBAL_CONFIG()
logger = Logger()


def cmd_linux(cmd) -> List:
    result = list()
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            universal_newlines=True)
    try:
        proc.wait(3)
    except Exception as e:
        proc.terminate()
        result.append(str(e))
    out = proc.stdout.readlines()
    for line in out:
        result.append(line.strip() + '\n')
    return result


async def cmd_linux_async(cmd) -> List:
    result = list()
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )

    stdout, _ = None, None
    try:

        stdout, _ = await asyncio.wait_for(process.communicate(), timeout=10)
    except asyncio.TimeoutError:
        process.terminate()
        result.append("Command timed out")
    if stdout is not None:
        for line in stdout.decode().splitlines():
            result.append(line.strip() + '\n')

    return result


class LinuxRPA:
    @classmethod
    def status(cls, process_name):
        if process_name == 'prometheus':
            order = "ps -ef | grep -w %s |grep -v grep |grep -v zookeeper-prometheus |grep -v EmssRPA.RPAUtils |awk " \
                    "\'{print $1,$2}\'" % process_name
        elif process_name == 'elasticsearch':
            order = "ps -ef | grep -w %s |grep -v grep |grep -v flink |grep -v EmssRPA.RPAUtils |awk " \
                    "\'{print $1,$2}\'" % process_name
        elif process_name == "emss-server":
            order = "ps aux | grep -w %s |grep -v grep |grep -v EmssRPA.RPAUtils |grep -v zookeeper-emss-server |awk \'{print $1,$2}\'" % process_name

        else:
            order = "ps aux | grep -w %s |grep -v grep |grep -v EmssRPA.RPAUtils |awk \'{print $1,$2}\'" % process_name

        process_info = cmd_linux(order)
        return 1 if process_info else 0


def get_one_key_config(param: str = None):
    """
    读取全局配置文件server.conf文件，带参数返回对应的值，不带参数返回整个文件内容
    :return:
    """
    server_conf_path = global_param.server_conf_file_path
    if not os.path.exists(server_conf_path):
        logger.info('server.conf文件不存在')
        return ''

    with open(server_conf_path, 'r', encoding='utf8') as f:
        for line in f:
            if line.find("#") > -1:
                continue
            if line.lower().find(param.lower()) > -1:
                param_name, result = line.split(' = ')
                return result.replace("'", "").strip()
    return ''


async def execute_rpa(path: str, order: str = "") -> list:
    """
    Execute a shell script with specified order.

    Args:
        path (str): Path to the shell script.
        order (str): Order to be passed to the shell script.

    Returns:
        list: List containing the result of the command execution.
    """
    if path is None:
        return []
    shell_path, execute_shell = os.path.split(path)

    if "start-emss.sh" in execute_shell:
        execute_shell = execute_shell.replace("  ", f" {order} ")  # Compatibility with H2
    # 赋予权限
    chmod_cmd = f"chmod 777 {path}"
    cmd_linux(chmod_cmd)
    # 执行启动命令
    execute_cmd = f"cd {shell_path} && ./{execute_shell} {order.strip()}"
    logger.info(f"{execute_cmd}")
    res = await cmd_linux_async(execute_cmd)  # Grant execute permissions

    return res


def get_h2_base():
    db_ip = get_one_key_config("DB_HOST")
    db_port = get_one_key_config("DB_PORT")
    host = db_ip + ":" + db_port
    db_username = get_one_key_config("DB_USERNAME")
    db_password = get_one_key_config("DB_PASSWORD")
    db_name = get_one_key_config("DB_DBNAME")

    return host, db_username, db_password, db_name


def get_port_status(port, ip=global_param.local_ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)  # Set timeout in seconds
    try:
        sock.connect((ip, port))  # Try to connect to the specified IP and port
        return 0  # If connection succeeds, the port is open
    except socket.error:
        return 1  # If an exception occurs, the port is closed
    finally:
        sock.close()  # Close the socket connection

def is_port_open(ports) -> List[Dict]:
    """
    检查端口是否开启
    """
    result = []
    if ports is None or ports == "":
        return result
    if not isinstance(ports, (int, list)):
        logger.error(f"ports must be an int or a list of ints, but got {type(ports)}")
        return []
    ports = [ports] if isinstance(ports, int) else ports

    for port in ports:
        status = get_port_status(port)
        result.append({
            "port": port,
            "status": status
        })
    return result


def extract_and_move_tar(target_dir=global_param.install_path, bak_dir=BACKUP_PATH):
    """
    安装目录下的tar包解压并移动到bak目录下
        * target_dir 安装目录
        * bak_dir 备份目录
    """
    logger.info("解压并归档build目录下tar包！")

    os.makedirs(BACKUP_PATH, exist_ok=True)
    # 遍历目标文件夹下的所有文件
    for filename in os.listdir(target_dir):
        file_path = os.path.join(target_dir, filename)
        bak_path = os.path.join(bak_dir, filename)
        if filename.find("emss_python") > -1:
            shutil.move(file_path, bak_path)
            logger.info(f"移动到bak目录: {bak_path}")

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


def append_to_bash_profile(content: str):
    try:
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
        logger.warning("请手动执行source ~/.bash_profile命令，使配置文件生效")
    except Exception as e:
        logger.error(f"Failed to append to bash_profile: {e}")


def init_database() -> None:
    """
    Initialize the database by renaming the file if necessary.
    """
    data_path = os.path.join(global_param.database_path)
    if os.path.exists(data_path):
        data_file_list = os.listdir(data_path)
        if len(data_file_list) == 1 and data_file_list[0] == "emss_release.mv.db":
            src_file = os.path.join(data_path, "emss_release.mv.db")
            dest_file = os.path.join(data_path, "emss.mv.db")
            try:
                shutil.copy(src_file, dest_file)
                logger.info("Successfully renamed the database file.")
            except Exception as e:
                logger.error(f"Failed to rename database file: {e}")
            logger.info(f"重命名数据库文件成功！")
        else:
            logger.warning(f"数据库文件已存在，不再重命名！")
    else:
        logger.error(f"数据库文件不存在!")


# 启动nginx
def start_nginx():
    nginx_path = os.path.join(global_param.install_path, "emss-web/nginx/sbin")
    if os.path.exists(nginx_path):
        cmd_linux(f"cd {nginx_path} && chmod 777 * && ./run.sh start")
        status = LinuxRPA.status("nginx")
        if status == 1:
            logger.info(f"启动nginx成功！")
        else:
            logger.error(f"启动nginx失败！,请手动执行检查！")


def init_server_config(first=False):
    """
    Initialize the server configuration.
    """

    old_path = os.path.join(global_param.install_path, "../configserver/server.conf")
    new_path = os.path.join(global_param.work_path, "configserver")

    if os.path.exists(old_path):
        logger.info("存在旧的configserver！")
        if os.path.exists(new_path):
            shutil.rmtree(new_path)
        shutil.move(old_path, global_param.work_path)
        logger.warning("移动旧的configserver到工作目录下！")
    else:
        logger.info("不存在旧的configserver！")
    server_config_file_path = global_param.server_conf_file_path
    if not os.path.exists(server_config_file_path):
        try:
            # 获取当前目录
            shutil.copy(global_param.config_center_path.get("server.conf_模板"), server_config_file_path)
            with open(server_config_file_path, "r") as f:
                server_config = f.read()
            server_config = re.sub(IP_PATTERN, global_param.local_ip, server_config)
            with open(server_config_file_path, "w") as f:
                f.write(server_config)
            logger.info(f"首次升级，生成{server_config_file_path}成功！")
        except Exception as e:
            logger.error(traceback.format_exc())
        global_param.first_upgrade = True
        logger.info("执行一键配置！")
        config_server_main()
        logger.info("一键配置执行完毕")
    else:
        logger.warning(f"{server_config_file_path}已存在，不再重新生成！")



def server_config_append(line):
    """
    文件追加内容
    """
    new_line = []
    with open(global_param.server_conf_file_path, 'r') as f:
        lines = f.readlines()
        for l in lines:
            if l.find(line) > -1:
                logger.info(f"server.conf已存在{line}，不再追加！")
                return
            if l.find("Authorization") > -1:
                continue
            new_line.append(l)
        new_line.append(line)
    with open(global_param.server_conf_file_path, 'w') as f:
        f.writelines(new_line)


def save_file(file_path):
    with codecs.open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    lines = content.splitlines()
    content = '\n'.join(lines)

    with codecs.open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)


def grafana_dashboard(Authorization, grafana_info_path):
    try:
        grafana_config = {}
        es_port = get_one_key_config('ES_PORT')
        prometheus_port = get_one_key_config('PROMETHEUS_PORT')
        grafana_api_host = "http://" + get_one_key_config('GRAFANA_HOST') + ':' + get_one_key_config(
            'GRAFANA_PORT') + '/api'
        grafana_config['url'] = grafana_api_host
        grafana_config['Authorization'] = Authorization.strip()
        grafana_config['elasticsearch'] = "http://" + get_one_key_config('ES_HOST') + ":" + es_port
        grafana_config['prometheus'] = "http://" + get_one_key_config('PROMETHEUS_HOST') + ":" + prometheus_port
        grafana_api = AutoGrafana(grafana_config, grafana_info_path)
        data_source_result = grafana_api.import_data_sources()  # 导入数据源
        dashboard_result = grafana_api.create_dashboard()  # 导入看板
        # 操作成功后，将Authorization写入到文件中
        line = "\n# grafana Authorization\nAuthorization = '" + Authorization.strip().replace("Bearer ", "") + "'\n"
        server_config_append(line)

    except Exception as e:
        print(traceback.format_exc())
        return False, str(e)

    return True, "".join(data_source_result + dashboard_result)
