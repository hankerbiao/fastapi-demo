import os
from fastapi import APIRouter, status
from app.core.H2.H2Connector import H2Connector
from response.response import Response
from util.utils import get_one_key_config, get_h2_base
from typing import Optional

router = APIRouter()


@router.get("/execute_sql", status_code=status.HTTP_200_OK)
def execute_sql(filename: Optional[str]):
    """
        执行h2sql脚本，接收前端发来的sql文件，执行后将返回结果返回给前端
        :return:
        """

    # 查看datas/sql/下是否有filename.sql文件
    file_path = f'datas/sql/{filename}'
    final_sql = []
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            sql_lines = f.readlines()
        for sql in sql_lines:
            if sql.find('tee') == 0 or sql.find('notee') == 0:
                continue
            final_sql.append(sql)
    else:
        print(f'{filename}文件不存在')
        return Response(data=[f'{filename}文件不存在'])

    host, db_username, db_password, db_name = get_h2_base()
    db_name = f'~/application/{get_one_key_config("DB_DBNAME")}'
    h2 = H2Connector(db_username, db_password, host, db_name)
    # 获取连接状态
    try:
        res = h2.execute_sql("\n".join(final_sql))
    except Exception as e:
        res = [str(e)]
    return Response(data=res)


@router.get("/get_base_info", status_code=status.HTTP_200_OK)
def get_base_info():
    """
    从server.conf中获取h2数据库的基本信息
    :return:
    """
    host, db_username, db_password, db_name = get_h2_base()
    res = {
        "host": host,
        "db_name": db_name,
        "user_name": db_username,
        "password": db_password
    }
    return Response(data=res)
