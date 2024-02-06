from fastapi import FastAPI
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from util.config import GLOBAL_CONFIG
from util.Logger import Logger
import os
from util.constants import *
from util.utils import (
    extract_and_move_tar,
    append_to_bash_profile,
    init_database,
    start_nginx, init_server_config
)

logger = Logger()
global_param = GLOBAL_CONFIG()

from app.api import router

os.environ["JAVA_HOME"] = fr"{global_param.install_path}/jdk-17.0.5"


def create_app() -> FastAPI:
    app = FastAPI(
        title="运维易配置中心",
        description="运维易配置中心，管理开源组件的配置文件和启动控制",
        version="1.0.0",
    )
    origins = [
        "http://127.0.0.1",
        f"http://127.0.0.1:{global_param.server_port}",
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
    async def startup():
        """
        Configuration before starting the service.
        """
        logger.info("Preparing to start the service...")

        # (1/6) Extract tar packages
        logger.info("(1/6) Extracting tar packages...")
        extract_and_move_tar()
        logger.info("(1/6) Tar extraction completed!")

        # (2/6) Initialize environment variables
        logger.info("(2/6) Initializing environment variables...")
        envs = ENVS.format(global_param.install_path)
        append_to_bash_profile(envs)
        logger.info("(2/6) Environment variables initialized!")

        # (3/6) Initialize server.conf
        logger.info("(3/6) Initializing server.conf...")
        init_server_config()
        logger.info("(3/6) server.conf initialized!")

        # (4/6) Initialize the database
        logger.info("(4/6) Initializing the database...")
        init_database()
        logger.info("(4/6) Database initialized!")

        # (5/6) Start nginx
        logger.info("(5/6) Starting nginx...")
        start_nginx()
        logger.info("(5/6) Nginx started!")

        # (6/6) Initialize some configuration files
        logger.info("(6/6) Initializing some configuration files...")
        # todo: Add initialization logic for configuration files here
        logger.info("(6/6) Configuration files initialized!")

        # Service startup completed
        logger.info("Service startup completed!")

    return app
