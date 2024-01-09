from app import create_app, logger, global_param

app_ = create_app()
if __name__ == '__main__':
    # 记录当前工作目录
    import uvicorn

    logger.info("启动服务,端口:8000")
    uvicorn.run(app='run:app_', host="0.0.0.0", port=global_param.port, reload=True, workers=1)
