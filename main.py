import os
import time
import threading
import hashlib
from pathlib import Path
from datetime import datetime
import logging
from config_loader import ConfigLoader
import threading
from utils import *
from config_loader import ConfigLoader
from pathlib import Path
from datetime import datetime
from online_test import init_engine
import logging

from log_config import *



# 版本号
__version__ = "0.2.0"

global _engine 


def init_folders(Configloader):

    config_path_dict = {
        "src_path": config.src_path,
        # "work_path": config.work_path,
        # "share_path": config.share_path,
        "stable_path": config.stable_path
    }

    if not isinstance(config_path_dict, dict):
        logger.error("Input must be a dictionary.")
        return
    subfolder_names = ["AI", "Machine"]



    for key, base_path_str in config_path_dict.items():
        if not isinstance(base_path_str, str):
            logger.warning(f"Value for key '{key}' is not a string path ('{base_path_str}'). Skipping.")
            continue

        base_path = Path(base_path_str)

        if not base_path.exists():
            logger.info(f"Base path {base_path} does not exist. It will be created if possible.")
        elif not base_path.is_dir():
            logger.warning(
                f"Base path {base_path} exists but is not a directory. Skipping subfolder creation for this path.")
            continue
        for subfolder_name in subfolder_names:
            subfolder_path = base_path / subfolder_name
            try:
                subfolder_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"  Ensured subfolder exists: {subfolder_path}")
            except OSError as e:
                logger.error(f"  Error creating directory {subfolder_path}: {e}")
            except Exception as e:
                logger.error(f"  An unexpected error occurred while creating {subfolder_path}: {e}")


class FileMonitor:
    def __init__(self, dir_name):
        self.dir_name = dir_name
        self.last_activity = time.time()
        self.has_changes = False
        self.lock = threading.Lock()
        self.file_hashes = {}  # 记录文件哈希值 {filepath: hash}

    def _print_change(self, change_type, files):
        """打印文件变动信息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(files, (list, set)):
            file_list = ", ".join(files)
            print(f"[{timestamp}] {change_type} {len(files)}个文件: {file_list}")
        else:
            print(f"[{timestamp}] {change_type}: {files}")

    def scan_files(self):
        """扫描目录并检查文件变化"""
        current_hashes = {}

        try:
            for root, _, files in os.walk(self.dir_name):
                for file in files:
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'rb') as f:
                            file_hash = hashlib.md5(f.read()).hexdigest()
                        current_hashes[filepath] = file_hash
                    except (IOError, PermissionError) as e:
                        print(f"跳过文件 {filepath} (原因: {str(e)})")
                        continue

            with self.lock:


                # 检查新增的文件
                new_files = set(current_hashes.keys()) - set(self.file_hashes.keys())
                if new_files:
                    # self._print_change("新增", new_files)
                    self.last_activity = time.time()
                    self.has_changes = True


                # 检查修改的文件
                modified_files = [
                    f for f in current_hashes
                    if f in self.file_hashes and current_hashes[f] != self.file_hashes[f]
                ]
                if modified_files:
                    # self._print_change("修改", modified_files)
                    self.last_activity = time.time()
                    self.has_changes = True

                # 检查删除的文件
                deleted_files = set(self.file_hashes.keys()) - set(current_hashes.keys())
                if deleted_files:
                    # self._print_change("删除", deleted_files)
                    self.last_activity = time.time()
                    self.has_changes = True

                self.file_hashes = current_hashes

        except Exception as e:
            print(f"扫描错误: {str(e)}")

    def check_timeout(self, timeout):
        """检查是否超时无变化"""
        with self.lock:
            current_time = time.time()
            time_diff = current_time - self.last_activity
            if self.has_changes and (time_diff >= timeout):
                self.has_changes = False
                return True

            # 调试信息
            print(f"检查状态 | 最后活动: {time_diff:.1f}秒前", end="\r")
        return False


def monitor_directory(path, config, handler, scan_interval=0.5):
    """监控目录的线程函数"""
    while True:
        try:
            if os.path.exists(path):
                handler.scan_files()
                if handler.check_timeout(0.5):  # 0.5秒无变化触发
                    print(datetime.now(),f" {Path(path).as_posix()} - (500ms无变化)")
                    logger.info(datetime.now(),f" {Path(path).as_posix()} - (500ms无变化)")


                    if path.endswith("Machine"):
                        # init_folders(config)
                        # copy_folders(path, config.stable_machine_path)
                        # copy_folders(path, config.work_machine_path)
                        # copy_folders(path, config.share_machine_path)
                        process_file_package(work_machine_path=config.src_machine_path,
                                             ai_output_path=config.src_ai_path,
                                             stable_machine_path=config.stable_machine_path)

                    elif path.endswith("AI"):
                        copy_friend_file(path, config.stable_ai_path)
                        # safe_delete_and_rebuild(config.share_ai_path)
                        # safe_delete_and_rebuild(config.share_machine_path)
                        #
                        # safe_delete_and_rebuild(config.work_ai_path)
                        # safe_delete_and_rebuild(config.work_machine_path)

            else:
                logger.warning(f"目录不存在: {path}")
            time.sleep(scan_interval)
        except Exception as e:
            logger.error(f"监控出错: {e}")


def listen_dir(config):
    """启动监控线程"""
    monitor1 = FileMonitor(config.src_machine_path)
    # monitor2 = FileMonitor(config.share_ai_path)

    thread1 = threading.Thread(
        target=monitor_directory,
        args=(config.src_machine_path, config, monitor1)
    )
    # thread2 = threading.Thread(
    #     target=monitor_directory,
    #     args=(config.share_ai_path, config, monitor2)
    # )

    thread1.daemon = True
    # thread2.daemon = True
    thread1.start()
    # thread2.start()

    try:
        # 主线程保持运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n用户中断，停止监控")


if __name__ == '__main__':



    logger = setup_logging()
    logger.info("系统启动")
    config = ConfigLoader(r"D:\goodwe_test\test_goodwe_test\config.yaml")

    _global = None
    init_engine(r"D:\goodwe_test\test_goodwe_test\weights")
    init_folders(config)
    listen_dir(config)