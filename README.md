# 运维易服务自动化管理系统

## 项目描述

🎉🎉🎉是一个旨在简化运维易服务管理的工具，提供自动安装、部署、配置以及一系列运维操作，以提高效率、降低人工操作的复杂性。通过该系统，用户可以轻松监控运维易服务的状态，执行一键操作，导入Grafana看板，进行一键配置，并执行SQL脚本，从而实现对运维易服务的全面管理。

## 主要功能

- :white_check_mark: 半自动安装、部署、配置运维易服务
- :white_check_mark: 将configserver和配置文件备份维护到控制台中
- :white_check_mark: 监控emss后台组件应用状态
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
  "code": 0,
  "msg": "",
  "data": [],
  "count": 1
}
```

示例代码

```python
@router.get("/batch_order", status_code=status.HTTP_200_OK)
def batch_start(order: Optional[str], server_name: Optional[str]):
    """
    批量启动组件
    :param
        * server_name: 组件名称
        * order: 命令
    """
    init = Init()
    res = init.batch(order, server_name)
    return Response(code=0, msg='', data=res)
```

## 设置定时启动方法

1. 打开终端或命令行界面
2. 输入crontab -e命令，这将打开您默认的文本编辑器（如vi或nano）。
3. 在编辑器中，您可以添加新的cron作业。每个cron作业都由五个字段组成，用空格分隔：分钟、小时、日期、月份、星期。每个字段都可以使用特定的值或通配符来指定时间或日期范围。
4. 例如，设置每10分钟执行一次：

```bash
*/10 * * * * /home/emss/build/emss-manage/run.sh start
```

5. 保存并关闭文件。在vi编辑器中，按下Esc键，然后输入:wq保存并退出。
6. 您可以通过输入crontab -l命令来查看当前用户的cron作业列表。
7. cron作业将按照您指定的时间自动运行。您可以在脚本或命令中使用输出重定向来将输出记录到文件中，以便于监控和日志记录。