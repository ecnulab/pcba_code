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
from log_config import logger
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

            # # 输出切割结果
            # from utils import draw_from_result
            # draw_from_result(result,image_path,r"C:\pycharm\files\pcba_code\test")

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


def test_detection_with_result(image_path, model_type):
    """测试目标检测接口,"""
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
                return "AIOK" , result
            else:
                return "AING" , result

        else:
            print(f"检测失败: {response.text}")
            logger.warning(f"检测失败: {response.text}")
            return None , None

        # return response.status_code == 200
    except Exception as e:
        print(f"目标检测失败: {str(e)}")
        return False , None
    # finally:
    #     # 关闭所有打开的文件
    #     for file_tuple in files.values():
    #         file_tuple[1].close()


def test_detection_out_result(image_path, model_type):
    """测试目标检测接口,"""
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
            print(result)
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
            return None , None

        # return response.status_code == 200
    except Exception as e:
        print(f"目标检测失败: {str(e)}")
        return False , None
    # finally:
    #     # 关闭所有打开的文件
    #     for file_tuple in files.values():
    #         file_tuple[1].close()
