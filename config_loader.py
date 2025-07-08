import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path


class ConfigLoader:
    """简单的配置加载类，用于加载yaml配置文件"""

    _instance = None
    _config = {}


    def __new__(cls, config_path: str = "config.yaml"):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance._config_path = config_path
            cls._instance._load_config()

            cls._instance.src_path = Path(cls._instance.get("path.src_path")).as_posix()
            # cls._instance.work_path = Path(cls._instance.get("path.work_path")).as_posix()
            # cls._instance.share_path = Path(cls._instance.get("path.share_path")).as_posix()
            cls._instance.stable_path = Path(cls._instance.get("path.stable_path")).as_posix()



            # cls._instance.user_check_path = Path(cls._instance.get("path.user_check_path")).as_posix()

            cls._instance.src_machine_path = Path(os.path.join(cls._instance.src_path, "Machine")).as_posix()
            cls._instance.src_ai_path = Path(os.path.join(cls._instance.src_path, "AI")).as_posix()

            # cls._instance.work_machine_path = Path(os.path.join(cls._instance.work_path, "Machine")).as_posix()
            # cls._instance.work_ai_path = Path(os.path.join(cls._instance.work_path, "AI")).as_posix()

            # cls._instance.share_machine_path = Path(os.path.join(cls._instance.share_path, "Machine")).as_posix()
            # cls._instance.share_ai_path = Path(os.path.join(cls._instance.share_path, "AI")).as_posix()

            cls._instance.stable_machine_path = Path(os.path.join(cls._instance.stable_path, "Machine")).as_posix()
            cls._instance.stable_ai_path = Path(os.path.join(cls._instance.stable_path, "AI")).as_posix()




            # print(cls._instance.src_path, cls._instance.stable_path)
            # print(cls._instance.src_machine_path, cls._instance.src_ai_path, cls._instance.stable_machine_path, cls._instance.stable_ai_path)



        return cls._instance

    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            if os.path.exists(self._config_path):
                with open(self._config_path, 'r', encoding='utf-8') as file:
                    self._config = yaml.safe_load(file) or {}
                print(f"配置已加载: {self._config_path}")
            else:
                print(f"配置文件不存在: {self._config_path}")
                self._config = {}
        except Exception as e:
            print(f"加载配置失败: {e}")
            self._config = {}

    def reload(self) -> None:
        """重新加载配置"""
        self._load_config()

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持使用点号访问嵌套配置"""
        keys = key.split('.')
        value = self._config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def get_all(self) -> Dict:
        """获取所有配置"""
        return self._config.copy()

    def __getitem__(self, key: str) -> Any:
        """支持字典式访问: config['path.src_path']"""
        return self.get(key)



