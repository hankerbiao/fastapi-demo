from fastapi import APIRouter, status, UploadFile, File
from fastapi.responses import StreamingResponse
import io
import os

from app import global_param
from response.response import Response
from typing import Optional

from util.utils import save_file

router = APIRouter()


# 接收文件接口
@router.post("/upload", status_code=status.HTTP_200_OK)
async def upload(file: UploadFile = File(...)):
    """
    接收前端发来的文件，保存到本地
    根据不同的文件类型，保存到不同的文件夹下
    """
    file_path = None
    filename = file.filename
    try:
        os.makedirs('datas/settings')
    except:
        pass
    if filename == 'server.conf':
        file_path = f"datas/settings/server.conf"

    elif filename == 'custom-installation-config.json':
        file_path = f"datas/settings/custom-installation-config.json"

    # 如果文件为sql
    elif filename.endswith('.sql'):
        file_path = f"datas/sql/{filename}"
    else:
        return Response(code=1, msg=f'文件不支持', data='')

    if not file_path:
        return Response(code=1, msg=f'文件不支持', data='')
    # 保存文件
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    if os.path.getsize(file_path) < 5:
        os.remove(file_path)
        return Response(code=1, msg=f'文件过小', data='')

    save_file(file_path)

    return Response(code=0, msg=f'上传成功', data=filename)


@router.get("/download")
async def download_file(app_name: Optional[str]):
    """
    前端下载文件接口
    :param app_name:
    :return:
    """
    file_path = global_param.config_center_path.get(app_name)
    if app_name == "custom-installation-config.json":
        if not os.path.exists(file_path):
            file_path = file_path + "_模板"

    if not os.path.exists(file_path):
        return Response(code=1,msg=f"未找到{file_path}文件！")
    # 打开文件并创建一个可读的字节流对象
    file_stream = io.BytesIO()
    with open(file_path, "rb") as f:
        file_stream.write(f.read())
    file_stream.seek(0)

    # 返回 StreamingResponse 以异步发送文件内容
    return StreamingResponse(file_stream, media_type="application/octet-stream",
                             headers={"Content-Disposition": f"attachment; filename={app_name}"})
