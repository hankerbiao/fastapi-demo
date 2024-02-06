from configserver.ConfigServer.start import config_server_main
from util.Engine import Engine
from util.Logger import Logger
from util.config import GLOBAL_CONFIG
import shutil
from datetime import datetime
from util.utils import grafana_dashboard, get_one_key_config
import os

global_param = GLOBAL_CONFIG()

logger = Logger()


def backup_database():
    """
    备份、重命名数据库
    """
    db_path = global_param.database_path  # 获取数据库路径
    db_file_path = os.path.join(db_path, global_param.database_name)
    bak_file_path = f"{global_param.database_name}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    if os.path.exists(db_file_path):
        # 存在数据库文件，备份数据库，命名为emss.mv.db.bak.年月日时分秒
        try:
            shutil.copy(db_file_path,
                        os.path.join(db_path, bak_file_path))
            logger.info("Successfully renamed the database file.")
        except Exception as e:
            logger.error(f"Failed to rename database file: {e}")
        logger.info(f"重命名数据库文件成功！")
        return True, f"备份数据库成功！,备份保存地址：{bak_file_path}"
    else:
        logger.error(f"数据库文件{db_file_path}不存在!")
        return False, f"数据库文件{db_file_path}不存在!"


class Upgrade:
    """
    emss 升级部署
    """

    def __init__(self):
        pass

    async def stop(self):
        """
        关闭所有服务
        """
        engine = Engine()
        await engine.all_rpa("stop")
        all_stop = all([i["status"] == 0 for i in engine.status() if i["process_name"] != "nginx"])
        if all_stop:
            logger.info("所有服务已关闭！")
        else:
            engine.init()
            start_status = [i["process_name"] for i in engine.status() if
                            i["status"] == 1 and i["process_name"] != "nginx"]
            logger.error("关闭服务失败！")
            return False, "关闭服务失败！,请手动执行关闭！,当前正在运行的服务：" + "、".join(start_status)
        return True, "关闭服务成功！"

    async def start(self):
        """
        启动所有服务
        """
        engine = Engine()

        await engine.all_rpa("start")
        all_start = all([i["status"] == 1 for i in engine.status()])
        if all_start:
            logger.info("所有服务已启动！")
        else:
            start_status = [i["process_name"] for i in engine.status() if
                            i["status"] == 0 and i["process_name"] != "nginx"]
            logger.error("启动服务失败！")
            return False, "启动所有服务失败！,请手动执行启动！,当前未运行的服务：" + "、".join(start_status)
        return True, "启动服务成功！"

    async def run(self):
        """
        执行升级操作
        1. 关闭所有所有程序（除nginx）
        2. 备份数据库(install_path/data/emss.mv.db)
        3. 执行一键配置
        4. 启动所有服务
        5. 监控看板、数据源导入
        其中有任何一步失败，后续操作不再执行
        """
        response = []
        # 1. 关闭所有程序
        logger.info("执行升级操作！")
        logger.info("1. 关闭所有服务！")
        stop_result, msg = await self.stop()
        if not stop_result:
            logger.error(msg)
            return False, msg
        logger.info("关闭所有服务成功！")

        # 2. 备份数据库(emss.mv.db)
        logger.info("2. 备份数据库！")
        backup_result, msg = backup_database()
        if not backup_result:
            response.append(msg)
            logger.error(msg)
            return response
        logger.info("备份数据库成功！")

        # 3. 执行一键配置
        logger.info("3. 执行一键配置！")
        try:
            config_server_main()
            response.append("执行一键配置成功！")
        except:
            logger.error("执行一键配置失败！")
            response.append("执行一键配置失败！")
            return response

        # 4. 启动服务
        logger.info("4. 启动所有服务！")
        start_result, msg = await self.start()
        if not start_result:
            logger.error(msg)
            response.append(msg)
            return response
        response.append("启动所有组件成功！")

        # 5. 监控看板、数据源导入
        logger.info("5. 监控看板、数据源导入！")
        grafana = Engine("grafana")
        authorization = get_one_key_config("Authorization")
        res, msg = grafana_dashboard(authorization, grafana.path)
        if res:
            response.append("监控看板、数据源导入成功！")
        else:
            logger.error("监控看板、数据源导入失败！")
            response.append(f"监控看板、数据源导入失败！{msg}")
            return response

        return response