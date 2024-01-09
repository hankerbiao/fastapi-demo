import traceback
from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from util.config import GLOBAL_CONFIG
from util.Logger import Logger
from util.constants import *
from util.utils import start_nginx
from app.core.RPA.LinuxRPAUtils import LinuxRPA

logger = Logger()
rpa = LinuxRPA()
global_param = GLOBAL_CONFIG()

from app.api import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="运维易配置中心",
        description="运维易配置中心，管理开源组件的配置文件和启动控制",
        version="1.0.0",
    )
    origins = [
        "http://127.0.0.1",
        f"http://127.0.0.1:{global_param.port}",
        "http://127.0.0.1:3500",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.mount('/static', StaticFiles(directory='static'), name='static')  # 挂载静态文件
    app.include_router(router, prefix='/api/console_v1')  # 增加路由

    @app.on_event("startup")
    def startup():
        """
        启动服务前做的配置
        """
        logger.info("准备启动服务...")
        # 解压所有组件
        logger.info("(1/6)开始解压tar包...")
        # todo
        logger.info("(1/6)解压tar包完成！")
        # 初始化环境变量
        logger.info("(2/6)开始初始化环境变量...")
        envs = ENVS.format(global_param.install_path)
        # append_to_bash_profile(envs)
        logger.info("(2/6)初始化环境变量完成！")
        # 初始化server.conf
        logger.info("(3/6)开始初始化server.conf...")
        # first_upgrade = init_server_config()
        # global_param.first_upgrade = first_upgrade
        logger.info("(3/6)初始化server.conf完成！")
        # 初始化数据库
        logger.info("(4/6)开始初始化数据库...")
        # todo
        logger.info("(4/6)初始化数据库完成！")
        # 启动nginx
        logger.info("(5/6)开始启动nginx...")
        start_nginx()
        logger.info("(5/6)启动nginx完成！")
        # 初始化部分配置文件
        logger.info("(6/6)开始初始化部分配置文件...")
        # todo
        logger.info("(6/6)初始化部分配置文件完成！")

        # 完成启动
        logger.info("服务启动完成！")

    return app
