# 运维易服务自动化管理系统

## 项目描述

🎉🎉🎉是一个旨在简化服务管理的工具，提供自动安装、部署、配置以及一系列运维操作，以提高效率、降低人工操作的复杂性。通过该系统，用户可以轻松监控运维易服务的状态，执行一键操作，导入Grafana看板，进行一键配置，并执行SQL脚本，从而实现对服务的全面管理。

## 主要功能

- :white_check_mark: 半自动安装、部署、配置运维易服务
- :white_check_mark: 将configserver和配置文件备份维护到控制台中
- :white_check_mark: 监控后台组件应用状态
- :white_check_mark: 对组件进行启动、停止、重启操作
- :white_check_mark: 组件一键启动、一键停止、一键重启
- :white_check_mark: 启动主服务、日志服务、监控服务等
- :white_check_mark: 导入Grafana看板
- :white_check_mark: 执行一键配置
- :white_check_mark: 执行SQL脚本



## 服务地址:link:

- 后端地址：http://127.0.0.1:8000
- 前台地址：http://127.0.0.1:3500/#/controls
- Swagger地址:memo:：http://127.0.0.1:8000/docs

## 启动命令

```bash
# 部署运维易时启动：
chmod 777 run.sh && ./run.sh start
# 单独运行时
python3 run.py
```

## 日志路径

🎈在log目录下，包含程序运行时日志和程序启动时日志，出现问题从日志中可获取基本信息

## 响应内容  

🐍response/response.py

```json
{
    'code': code,
    'msg': "接口请求成功",
    'data': {
        'status': status,
        'msg': msg,
        'data': data
    },
}
```

示例代码

```python
@router.get("/batch_order", status_code=status.HTTP_200_OK)
async def batch_order(order: Optional[str], server_name: Optional[str], init=Depends(Engine)):
    """
    根据服务名称执行批量启动、停止、重启、状态查询命令
        * server_name: 组件名称，可选内容：[main_server,front_server,log_server,monitor_server,middleware_server]
        * order: 执行命令：start,stop,restart,status
        server_name 为all时，对所有组件进行控制操作
    """
    t0 = time.time()
    if server_name == "all":
        res = await init.all_rpa(order)
    else:
        res = await init.batch(order, server_name)
    t1 = time.time()
    print("star cost time:", t1 - t0)
    return Response(code=0, msg='', data=res)
```
