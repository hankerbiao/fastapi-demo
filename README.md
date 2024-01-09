# 基于FastAPI框架的后台APP管理示例
<p align="center">
    <img src ="https://img.shields.io/badge/version-1.0-blueviolet.svg"/>
    <img src ="https://img.shields.io/badge/platform-windows|linux|macos-yellow.svg"/>
    <img src ="https://img.shields.io/badge/python-3.x-blue.svg" />
    <img src ="https://img.shields.io/github/license/vnpy/vnpy.svg?color=orange"/>
</p>
:rocket: :rocket: :rocket: FastAPI-demo 是一个基于 Python FastAPI 的开源后台 APP 状态管理框架示例 Demo，旨在为初学者提供简单而完整的示例。该框架没有复杂的架构设计和异步处理，**专注于提供最基本的 HTTP 框架示例**，包括路由管理、接口管理、日志管理和数据格式管理。项目简洁而功能齐全，旨在帮助初学者迅速上手 FastAPI 开发，了解基本概念和最佳实践。

后端地址：

```tex
http://0.0.0.0:8000
```

Swagger地址：

```tex
http://0.0.0.0:8000/docs
```



### 数据格式

1. 响应内容  response/response.py

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




## 参考项目

A fast admin dashboard based on FastAPI and TortoiseORM with tabler ui, inspired by Django admin：https://github.com/fastapi-admin/fastapi-admin

