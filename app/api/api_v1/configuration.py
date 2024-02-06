import os
import shutil
import traceback
from datetime import datetime
from fastapi import APIRouter, status, UploadFile, File
from app import global_param
from configserver.ConfigServer.start import config_server_main
from response.response import Response
from util.Logger import Logger
from util.utils import save_file

router = APIRouter()

logger = Logger()


@router.get("/one_key_install", status_code=status.HTTP_200_OK)
def one_key_install():
    """调用一键配置脚本"""

    settings_dir = 'datas/settings'
    os.makedirs(settings_dir, exist_ok=True)

    res_data = []
    config_files = os.listdir(settings_dir)
    custom_installation_config_path = global_param.config_center_path.get('custom-installation-config.json')
    server_conf_path = global_param.config_center_path.get("server.conf")

    try:
        for file_name in config_files:
            # 移动文件
            file_path = os.path.join(settings_dir, file_name)
            if file_name == 'server.conf':
                if os.path.exists(server_conf_path):
                    # 备份
                    shutil.move(server_conf_path, server_conf_path + f".bak_{datetime.now().strftime('%Y%m%d%H%M%S')}")
                shutil.move(file_path, server_conf_path)

            if file_name == 'custom-installation-config.json':
                if os.path.exists(custom_installation_config_path):
                    # 备份
                    shutil.move(custom_installation_config_path, custom_installation_config_path
                                + f".bak_{datetime.now().strftime('%Y%m%d%H%M%S')}")
                shutil.move(file_path, custom_installation_config_path)
        result1 = config_server_main()
        res_data = res_data + result1
        if os.path.exists(custom_installation_config_path):
            logger.info(f"执行{custom_installation_config_path}文件")
            result2 = config_server_main(custom_installation_config_path)
            res_data = res_data + result2
        new_cfs = [i for i in config_files if i.find('bak') == -1]
        if not new_cfs:
            new_cfs = "无新增/修改配置"
        res_data.append(f"本次更新内容：{new_cfs}\n\n")

        return Response(code=0, msg='请求成功', data=res_data)
    except Exception as e:
        print(traceback.format_exc())
        shutil.rmtree(settings_dir)
        return Response(code=1, msg='请求失败', data=str(e))


@router.get("/get_configserver_info", status_code=status.HTTP_200_OK)
def get_configserver_info():
    """
    获取server_conf 和 custom_installation_config的路径
    """
    res_data = {
        'server_conf': global_param.config_center_path.get('server.conf'),
        'custom_installation_config': global_param.config_center_path.get('custom-installation-config.json')
    }
    return Response(code=0, msg='请求成功', data=res_data)


# 接收文件接口
@router.post("/upload", status_code=status.HTTP_200_OK)
async def upload(file: UploadFile = File(...)):
    """
    接收前端发来的文件，保存到本地
    根据不同的文件类型，保存到不同的文件夹下
    """
    filename = file.filename
    save_folders = {
        'server.conf': 'datas/settings',
        'custom-installation-config.json': 'datas/settings'
    }

    if filename not in save_folders:
        return Response(code=1, msg=f'暂不支持此文件', data='')

    folder_path = save_folders[filename]
    try:
        os.makedirs(folder_path, exist_ok=True)
    except:
        pass

    file_path = os.path.join(folder_path, filename)
    write_datas = await file.read()

    # 保存文件
    with open(file_path, "wb") as f:
        f.write(write_datas)

    if os.path.getsize(file_path) < 5:
        os.remove(file_path)
        return Response(code=0, msg=f'文件过小', data='')
    save_file(file_path)

    return Response(code=0, msg=f'上传成功', data=filename)
