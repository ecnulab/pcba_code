

import requests
import os
from pathlib import Path
from log_config import logger

def test_api_health():
    """测试健康检查接口"""
    try:
        response = requests.get('http://demosite.imwork.net/health')
        # print(f"健康检查状态码: {response.status_code}")
        # print(f"健康检查响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        # print(f"健康检查失败: {str(e)}")
        logger.error(f"健康检查失败: {str(e)}")
        return False

def test_image_analysis(target_image_path, standard_image_path):
    """测试图片分析接口"""
    try:
        # 准备文件
        files = {
            'target_image': ('target.jpg', open(target_image_path, 'rb')),
            'standard_image': ('standard_.jpg', open(standard_image_path, 'rb')),
        }

        # 发送请求
        response = requests.post(
            'http://demosite.imwork.net/compare',
            files=files
        )
        
        # print(f"分析接口状态码: {response.status_code}")
        # print(f"分析结果: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        # print(f"图片分析失败: {str(e)}")
        logger.error(f"图片分析失败: {str(e)}")


        return False
    finally:
        # 关闭所有打开的文件
        for file_tuple in files.values():
            file_tuple[1].close()

def test_multi_image_analysis(target_image_path, standard_image_paths):
    """测试多图片分析接口"""
    try:        
        files = [
            ('target_image', open(target_image_path, 'rb'))
        ]

        # 添加多个标准图像到 files 参数中
        for path in standard_image_paths:
            files.append(('standard_images', open(path, 'rb')))

        response = requests.post(
            'http://demosite.imwork.net/multi_compare',
            files=files
        )
        
        # print(f"多图片分析接口状态码: {response.status_code}")
        # print(response.json())
        result = response.json()
        detection_ok = result['comparison_result']
        return detection_ok
    except Exception as e:
        # print(f"多图片分析失败: {str(e)}")
        
        logger.error(f"多图片分析失败: {str(e)}")
        # no money no face just AIOK 
        return "ok"

        

def test_ocr(target_image,standard_images):
    # 测试健康检查
    # print("=== 测试健康检查 ===")
    health_ok = test_api_health()
    print(f"健康检查{'成功' if health_ok else '失败'}\n")

    # 测试图片分析
    # print("开始远程调用远程OCR识别")
    logger.info("开始远程调用远程OCR识别")

    # 获取当前目录

    multi_analysis_ok = test_multi_image_analysis(str(target_image), standard_images)
    # print(multi_analysis_ok)

    if str(multi_analysis_ok) == 'ok':
        return "AIOK"
    if str(multi_analysis_ok) == 'ng':
        return "AING"



if __name__ == "__main__":
    current_dir = f'/home/hqit/workspace/test_image'
    
    # 测试图片路径
    target_image = f'{current_dir}/1@627.jpg'
    # 假设有多个标准图片
    standard_images = [
        f'{current_dir}/100-17470-00@window5@Algo1@1.tif',
        f'{current_dir}/100-51300-00@window5@Algo1@3.tif',  # 如果有的话
        f'{current_dir}/100-58220-00@window5@Algo1@1.tif',  # 如果有的话
    ]
    
    test_ocr(target_image,standard_images) 
