import os
import glob
import pandas as pd
import time

from log_config import logger
from config_loader import ConfigLoader


def find_matching_csv(target_timestamp):
    """
    根据时间戳找到目录中时间比它大的第一个CSV文件

    参数:
        target_timestamp (str): 目标时间戳，如 '20250605152836'
        csv_directory (str): CSV文件所在目录

    返回:
        str: 匹配的CSV文件路径，没找到返回None
    """
    csv_directory = r"D:\goodwe_test\test_goodwe_test\human_evaluation"  # 替换为实际目录 后续改为全局变量

    # 获取目录下所有CSV文件
    csv_files = glob.glob(os.path.join(csv_directory, "*.csv"))
    # print(csv_files)

    if not csv_files:
        print(f"人工复判目录 {csv_directory} 中没有CSV文件")
        logger.warning(f"人工复判目录 {csv_directory} 中没有CSV文件")
        
        return None

    # 找到时间戳大于目标时间戳的CSV文件
    matching_files = []

    for csv_file in csv_files:
        filename = os.path.basename(csv_file)

        # 提取文件名开头的14位时间戳
        if len(filename) >= 14 and filename[:14].isdigit():
            file_timestamp = filename[:14]

            # 如果文件时间戳大于目标时间戳，加入候选列表
            if file_timestamp > target_timestamp:
                matching_files.append((file_timestamp, csv_file))

    if not matching_files:
        # print(f"没有找到时间戳大于 {target_timestamp} 的CSV文件")
        logger.info(f"没有找到时间戳大于 {target_timestamp} 的CSV文件")
        return None,None

    # 按时间戳排序，取最小的（第一个大于目标时间戳的）
    matching_files.sort()
    matched_file = matching_files[0][1]

    print(f"找到匹配文件: {os.path.basename(matched_file)}")
    logger.info(f"找到匹配文件: {os.path.basename(matched_file)}")


    info={}


    path = os.path.join(csv_directory, matched_file)

    full_df = pd.read_csv(path,skiprows=1,nrows=2,sep=',',engine='python')

    info["SerialNumber"] = full_df.iloc[0, 0]
    # print(info["SerialNumber"])

    other_df = pd.read_csv(path,skiprows=7,nrows=2,sep=',',engine='python')
    # print(other_df)
    info["Module_Result"] = other_df.iloc[0, 1]
    info["Part_Total"] = other_df.iloc[0, 5]
    info["Part_Good"] = other_df.iloc[0, 6]
    info["Part_NG"] = other_df.iloc[0, 7]
    info["Part_UserOK"] = other_df.iloc[0, 8]
    info["Part_Skip"] = other_df.iloc[0, 9]


    # 读取CSV文件，跳过前10行
    path = os.path.join(csv_directory, matched_file)
    old_df = pd.read_csv(path, skiprows=10,encoding='utf-8')
    # df = old_df[['PartName', 'RefID', 'RepairResult', 'Image_Path ']].copy()
    df = old_df[['PartName', 'RefID','InspResult', 'RepairResult','RepairTime', 'Image_Path ']].copy()
    return df , info



