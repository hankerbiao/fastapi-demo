from app import create_app, logger, global_param

app_ = create_app()
if __name__ == '__main__':
    # 记录当前工作目录
    import uvicorn

    logger.info(f"启动服务,端口:{global_param.server_port}")
    uvicorn.run(app='run:app_', host="0.0.0.0", port=global_param.server_port, reload=True)
