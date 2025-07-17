from pathlib import Path
from typing import Dict, Union
from anomalib.data import PredictDataset
from anomalib.engine import Engine
from anomalib.models import Patchcore
import torch
import os
import shutil
from datetime import datetime
from onlinetest_rc import *
from log_config import logger
class ProductionAIEngine:
    """生产环境AI推理引擎 - 推理时使用GPU"""

    def __init__(self, weights_base_path: str = "/home/hqit/test_goodwe_test/weights"):
        """初始化并预加载所有模型"""
        self.weights_base_path = weights_base_path
        self.model_paths = self._build_model_paths()
        self.loaded_models = {}
        
        # 检查GPU可用性
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"使用设备: {self.device}")
        
        self.engine = Engine()
        
        # 自动预加载所有模型
        self._preload_all_models()

    def _build_model_paths(self) -> Dict[str, str]:
        """构建模型路径字典"""
        categories = [
            "C", "CTL", "ELECAP", "JP", "JTG", "L", "LED", "MH",
            "PS", "QFP", "R", "SOP", "SOT3", "SOT4", "SOT6",
            "SOT8", "TS-R", "CN"
        ]
        return {
            category: f"{self.weights_base_path}/{category}/model.ckpt"
            for category in categories
        }

    def _preload_all_models(self):
        """预加载所有模型"""
        print("正在预加载所有AI模型...")
        success_count = 0

        for i, category in enumerate(self.model_paths.keys(), 1):
            try:
                print(f"[{i}/{len(self.model_paths)}] 加载 {category} 模型...")
                model = Patchcore(visualizer=False)
                self.loaded_models[category] = {
                    "model": model,
                    "ckpt_path": self.model_paths[category]
                }
                success_count += 1
            except Exception as e:
                print(f"加载 {category} 模型失败: {e}")

        print(f"预加载完成！成功加载 {success_count}/{len(self.model_paths)} 个模型")

    def predict(self, filepath: str, category: str) -> str:
        """
        GPU加速推理单张图片

        Args:
            filepath: 图片文件路径
            category: 类别名称

        Returns:
            str: 'OK' 或 'NG'
        """
        # 检查类别
        if category not in self.loaded_models:
            raise ValueError(f"不支持的类别: {category}")

        # 检查文件
        if not Path(filepath).exists():
            raise FileNotFoundError(f"文件不存在: {filepath}")

        try:
            # 获取预加载的模型
            model = self.loaded_models[category]["model"]
            ckpt_path = self.loaded_models[category]["ckpt_path"]
            
            # 将模型移动到GPU（如果可用）
            if self.device.type == 'cuda':
                model = model.to(self.device)

            # 创建数据集并推理
            dataset = PredictDataset(path=Path(filepath), image_size=(256, 256))
            
            with torch.no_grad():  # 推理时不计算梯度，节省内存
                predictions = self.engine.predict(
                    model=model, 
                    dataset=dataset, 
                    ckpt_path=ckpt_path
                )

            # 返回结果
            prediction = predictions[0]
            if hasattr(prediction, 'logits'):
                logits = prediction.logits
                prob = torch.sigmoid(torch.tensor(logits)).item()
            else:
                prob = prediction.pred_label

            return 'AIOK' if prob <= 0.9 else 'AING'

        except Exception as e:
            raise RuntimeError(f"推理失败: {e}")


# 全局引擎实例
_engine = None


def init_engine(weights_base_path: str = "/home/hqit/test_goodwe_test/weights"):
    """初始化全局推理引擎"""
    global _engine
    _engine = ProductionAIEngine(weights_base_path)


def process_image(filepath_woac: str, filepath_ac: str, category: str) -> str:
    """
    使用全局引擎进行推理, 并根据AC图片结果判断最终结果

    Args:
        filepath_woac: 非AC图片路径
        filepath_ac: AC图片路径
        category: 类别名称

    Returns:
        str: 'OK' 或 'NG'
    """
    try:
        if category in ["R","C"]:
            if filepath_woac is not None:
                result_woac = test_detection(filepath_woac, category)
            print("非AC图片的路径是: ", filepath_woac)
            print("非AC图片的结果是: ", result_woac)
            print("finish remote sevice about R/C model!!!")

            # 获取AC图片的预测结果
            result_ac = None
            if filepath_ac is not None:
                result_ac = test_detection(filepath_ac, category)
            print("AC图片的路径是: ", filepath_ac)
            print("AC图片的结果是: ", result_ac)
            print("finish remote sevice about R/C model!!!")


            # 根据优先级返回结果
            
            if result_ac is not None:  # AC结果优先
                return result_ac
            elif result_woac is not None:  # 只有非AC结果
                return result_woac

        if _engine is None:
            raise RuntimeError("请先调用 init_engine() 初始化")

        # 获取非AC图片的预测结果
        result_woac = None
        if filepath_woac is not None:
            result_woac = _engine.predict(filepath_woac, category)
        print("非AC图片的路径是: ", filepath_woac)
        print("非AC图片的结果是: ", result_woac)

        # 获取AC图片的预测结果
        result_ac = None
        if filepath_ac is not None:
            result_ac = _engine.predict(filepath_ac, category)
        print("AC图片的路径是: ", filepath_ac)
        print("AC图片的结果是: ", result_ac)

        # 根据优先级返回结果
        if result_ac is not None:  # AC结果优先
            return result_ac
        elif result_woac is not None:  # 只有非AC结果
            return result_woac
    except Exception as e:
        logger.error(f"process image failed!! {e}")


def process_image_with_result(filepath_woac: str, filepath_ac: str, category: str):
    """
    使用全局引擎对R、C类进行推理, 并根据AC图片结果判断最终结果

    Args:
        filepath_woac: 非AC图片路径
        filepath_ac: AC图片路径
        category: 类别名称
        flag: 人工判断结果

    Returns:
        str: 'OK' 或 'NG'
    """
    try:
        if category in ["R", "C"]:
            result_woac = None
            result1 = None
            if filepath_woac is not None:
                result_woac , result1 = test_detection_with_result(filepath_woac, category)
            print("非AC图片的路径是: ", filepath_woac , flush=True)
            print("非AC图片的结果是: ", result_woac)
            print("finish remote sevice about R/C model!!!")

            # 获取AC图片的预测结果
            result_ac = None
            result2 = None
            if filepath_ac is not None:
                result_ac , result2 = test_detection_with_result(filepath_ac, category)
            print("AC图片的路径是: ", filepath_ac)
            print("AC图片的结果是: ", result_ac)
            print("finish remote sevice about R/C model!!!")

            # 根据优先级返回结果

            if result_ac is not None:  # AC结果优先
                return result_ac , result1 , result2
            elif result_woac is not None:  # 只有非AC结果
                return result_woac , result1 , result2
            else:
                print("error:no valid result\n", filepath_woac , filepath_ac , category)

        return "AING" , None , None
    except Exception as e:
        logger.error(f"process image failed!! {e}")
        

