import os
import json

import platform
import pathlib

import random
import shutil
import os
import time

import requests
import os
from pathlib import Path

def test_detection(image_path, model_type):
    """测试目标检测接口"""
    try:
        # 准备文件
        files = {
            'image': ('test_image.jpg', open(image_path, 'rb')),
        }
        data = {
            'model_type': model_type
        }

        # 发送请求
        response = requests.post(
            'http://demosite.imwork.net/detect',
            files=files,
            data=data
        )

        print(f"检测接口状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            detection_ok = result['status']
            detection_ok = detection_ok.upper()
            print(detection_ok)
            if detection_ok == "OK":
                return "AIOK"
            else:
                return "AING"
 
        else:
            print(f"检测失败: {response.text}")
            logger.warning(f"检测失败: {response.text}")
            return None



        # return response.status_code == 200
    except Exception as e:
        print(f"目标检测失败: {str(e)}")
        return False
    # finally:
    #     # 关闭所有打开的文件
    #     for file_tuple in files.values():
    #         file_tuple[1].close()

