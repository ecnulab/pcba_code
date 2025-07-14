import os
import shutil
from typing import Tuple, List, Dict, Any, Optional
import random
import time
from pathlib import Path
import json
import stat
import glob
import pandas as pd
import csv
from read_human_evalution import find_matching_csv

from online_test import *
from test_ocr import *
from collections import deque
from save_csv import ExecutionRecord

from datetime import datetime

from log_config import logger

from onlinetest_rc import *
import cv2

global RECORD_DATE
RECORD_DATE =None
tobe_processed = deque()


# 定义表头
headers = [
    "DATE", "GROUPNAME", "JOBNAME", "SLAVENAME", "ARRAY", "PARTID", "PARTCODE",
    "PARTNO", "WINDID", "WINDTYPE", "NG_NAME", "WIND_X", "WIND_Y", "WIND_WIDTH",
    "WIND_HEIGHT", "FLAG", "RepairResult", "REFID", "PART_ANGLE", "ARRAY_BARCODE",
    "ALGO_TYPE", "ALGO_ROI", "ALGO_LINE", "ALGO_DOT", "BOARD_BARCODE",
    "FONT_ANGLE","REMARK"
]

def draw_from_result(result,image_path,output_root):
    """
    根据模型输出在图片上绘制矩形框并保存
    :param result: 模型网络接口的返回值
    :param image_path: 图片的文件路径
    :param output_root: 保存目录（文件夹路径）
    """
    max_confidence = -1
    best_coords = None

    for detection in result['detection_results']:
        coords = detection[:4]  # 提取坐标（前4个数字）
        confidence = detection[-1]  # 提取置信度（最后一个数字）

        if confidence > max_confidence:
            max_confidence = confidence
            best_coords = coords

    # 输出置信度最高的坐标（四元组）
    # print("置信度最高的坐标：", tuple(best_coords))

    int_tuple = tuple(map(int, best_coords))
    draw_rectangle_and_crop(image_path,int_tuple,output_root)

def draw_rectangle_and_crop(image_path, coords, output_root):
    """
    在图片上绘制矩形框，并裁剪出矩形框区域保存
    :param image_path: 图片的文件路径
    :param coords: 四个坐标，元组形式 (x1, y1, x2, y2)
    :param output_root: 保存目录（文件夹路径）
    :return: 返回裁剪图像保存路径
    """
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"无法读取图片: {image_path}")

    # 提取四个坐标
    x1, y1, x2, y2 = coords

    # 裁剪出矩形框部分
    cropped_img = img[y1:y2, x1:x2].copy()

    # 绘制矩形框（颜色为红色，BGR: (0,0,255)，线宽2）
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

    # 获取文件名和扩展名
    filename, ext = os.path.splitext(os.path.basename(image_path))

    # 获取当前时间戳
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    # 生成带时间戳的文件名
    boxed_img_name = f"{timestamp}_boxed_{filename}{ext}"
    cropped_img_name = f"{timestamp}_cropped_{filename}{ext}"

    # 确保保存目录存在
    os.makedirs(output_root, exist_ok=True)

    # 定义保存路径
    box_img_path = os.path.join(output_root, boxed_img_name)
    cropped_img_path = os.path.join(output_root, cropped_img_name)

    # 保存图片
    cv2.imwrite(box_img_path, img)
    cv2.imwrite(cropped_img_path, cropped_img)

    return box_img_path, cropped_img_path





def copy_folders_sleep_delete(src_path: str, dest_path: str) -> Tuple[bool, List[str]]:
    """复制文件夹到目标路径，并延迟删除目标文件夹"""
    errors = []
    success = True
    try:
        if not os.path.exists(src_path):
            return False, [f"源路径不存在: {src_path}"]
        os.makedirs(dest_path, exist_ok=True)
        items = os.listdir(src_path)
        folders = [item for item in items if os.path.isdir(os.path.join(src_path, item))]
        if not folders:
            logger.warning(f"源路径下没有找到文件夹: {src_path}")
            return True, []
        for folder_name in folders:
            src_folder = os.path.join(src_path, folder_name)
            target_folder = os.path.join(dest_path, folder_name)
            try:
                # 复制文件夹
                shutil.copytree(src_folder, target_folder)
                logger.info(f"复制成功: {folder_name}")
                # 延迟20秒后删除目标文件夹
                logger.info(f"等待20秒后删除文件夹: {target_folder}")
                time.sleep(30)
                # 删除目标文件夹
                if os.path.exists(target_folder):
                    shutil.rmtree(target_folder)
                    logger.info(f"文件夹删除成功: {folder_name}")
                else:
                    logger.warning(f"目标文件夹不存在，无法删除: {target_folder}")
            except Exception as e:
                error_msg = f"复制或删除失败 {folder_name}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
                success = False
        return success, errors
    except Exception as e:
        error_msg = f"复制过程中发生错误: {e}"
        logger.error(error_msg)
        return False, [error_msg]









# 复制文件夹到目标路径
def copy_folders(src_path: str, dest_path: str) -> Tuple[bool, List[str]]:
    # """复制文件夹到目标路径"""
    # errors = []
    # success = True

    # try:
    #     if not os.path.exists(src_path):
    #         return False, [f"源路径不存在: {src_path}"]

    #     os.makedirs(dest_path, exist_ok=True)

    #     items = os.listdir(src_path)
    #     folders = [item for item in items if os.path.isdir(os.path.join(src_path, item))]

    #     if not folders:
    #         logger.warning(f"源路径下没有找到文件夹: {src_path}")
    #         return True, []

    #     for folder_name in folders:
    #         src_folder = os.path.join(src_path, folder_name)
    #         target_folder = os.path.join(dest_path, folder_name)

    #         try:

    #             shutil.copytree(src_folder, target_folder)
    #             logger.info(f"复制成功: {folder_name}")
    #         except Exception as e:
    #             error_msg = f"复制失败 {folder_name}: {e}"
    #             logger.error(error_msg)
    #             errors.append(error_msg)
    #             success = False

    #     return success, errors

    # except Exception as e:
    #     error_msg = f"复制过程中发生错误: {e}"
    #     logger.error(error_msg)
    #     return False, [error_msg]
    """复制文件夹到目标路径，跳过目标路径中已存在的文件"""
    errors = []
    success = True

    try:
        if not os.path.exists(src_path):
            logger.info(f"源路径不存在: {src_path}")
            return False, [f"源路径不存在: {src_path}"]

        os.makedirs(dest_path, exist_ok=True)

        items = os.listdir(src_path)
        folders = [item for item in items if os.path.isdir(os.path.join(src_path, item))]

        if not folders:
            logger.warning(f"源路径下没有找到文件夹: {src_path}")
            return True, []

        def copy_with_skip(src, dst, *, follow_symlinks=True):
            """自定义复制函数，跳过已存在的文件"""
            if os.path.exists(dst):
                return dst  # 跳过已存在的文件
            return shutil.copy2(src, dst, follow_symlinks=follow_symlinks)

        for folder_name in folders:
            src_folder = os.path.join(src_path, folder_name)
            target_folder = os.path.join(dest_path, folder_name)

            try:
                # 使用 dirs_exist_ok=True 和自定义 copy_function
                shutil.copytree(
                    src_folder,
                    target_folder,
                    dirs_exist_ok=True,
                    copy_function=copy_with_skip
                )
                logger.info(f"复制成功: {folder_name}")
            except Exception as e:
                error_msg = f"复制失败 {folder_name}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
                success = False

        return success, errors
    
    except Exception as e:
        error_msg = f"复制过程中发生错误: {e}"
        logger.error(error_msg)
        return False, [error_msg]



# 删除文件夹并重建
def safe_delete_and_rebuild(folder_path: str) -> bool:

    try:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
            return True

        def handle_readonly(func, path, exc):
            try:
                if os.path.exists(path):
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
            except Exception as e:
                logger.warning(f"处理只读文件失败 {path}: {e}")


        shutil.rmtree(folder_path, onerror=handle_readonly)
        os.makedirs(folder_path, exist_ok=True)
        return True

    except Exception as e:
        logger.error(f"删除重建目录失败 {folder_path}: {e}")
        return False


def find_image_by_pattern(folder_path: str, pattern: str) -> Optional[str]:
    """根据模式查找图片"""
    # image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif']

    # for ext in image_extensions:
    #     search_pattern = os.path.join(folder_path, f"*{pattern}*{ext}")
    #     files = glob.glob(search_pattern)
    #     if files:
    #         return files[0]

    # for root, _, files in os.walk(folder_path):
    #     for file in files:
    #         if pattern in file and any(file.lower().endswith(ext[1:]) for ext in image_extensions):
    #             return os.path.join(root, file)
    # return None
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif']
    filepath = None
    for ext in image_extensions:
        search_pattern = os.path.join(folder_path, f"*{pattern}*{ext}")
        files = glob.glob(search_pattern)
        if files:
            filepath = files[0]

    for root, _, files in os.walk(folder_path):
        for file in files:
            if pattern in file and any(file.lower().endswith(ext[1:]) for ext in image_extensions):
                filepath =  os.path.join(root, file)
    if filepath is None:
        return None, None
    
    # 分离路径和文件名
    dir_path, filename = os.path.split(filepath)
    # 分离文件名和扩展名
    basename, ext = os.path.splitext(filename)

    if "_AC" in basename:
        filepath_ac = filepath  # 已经包含_AC
        filepath_woac = os.path.join(dir_path, basename.replace("_AC", "") + ext)  # 去掉 _AC
    else:
        filepath_woac = filepath  # 不包含_AC
        filepath_ac = os.path.join(dir_path, f"{basename}_AC{ext}")  # 添加 _AC
    if not os.path.exists(filepath_ac) :
        filepath_ac = ""
        
    if not os.path.exists(filepath_woac) :
        filepath_woac = ""
            
    return filepath_woac, filepath_ac




# ！！！！注意！！！！！！
#从中转目录work_path中读取处理，然后分别保存到AI和Stable路径，参数路径到/machine和stable_path,work_path

def process_file_package(work_machine_path: str, ai_output_path: str, stable_machine_path: str = None) -> Dict[
        str, Any]:
        """处理文件包，读取CSV数据并处理图片"""

        global RECORD_DATE
        processed_files = set()
        # 步骤 2：遍历文件夹并存储文件名
        temp_path = []
        for filename in os.listdir(work_machine_path):
            temp_path.append(filename)
        # 步骤 3：对文件名进行排序
        temp_path.sort()
        # 步骤 4：将文件路径加入队列
        for filename in temp_path:
            file_path = os.path.join(work_machine_path, filename)
            # 检查是否已经在已处理列表中
            if file_path not in processed_files:
                processed_files.add(file_path)  # 标记为已处理
                tobe_processed.append(file_path)  # 加入队列
        
        while tobe_processed:

            modulelist = []

            work_path, package_name = get_package_path_name(work_machine_path)
            # print("kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
            # print(work_path)
            # print(package_name)
            # stable_output_path = os.path.join(stable_machine_path, package_name)

            csv_path = os.path.join(work_path, f"{package_name}.csv")
            # print(csv_path)

            # print(work_path, package_name, ai_output_path, stable_output_path, csv_path)

            ng_image_folder = os.path.join(work_path, "NGPartImage")
            if not os.path.exists(ng_image_folder):
                # 构建完整的文件路径External AI/AI
                ai_path = os.path.join(ai_output_path, f"{package_name}.csv")
                # print(ai_path)
                with open(ai_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)

                # 构建完整的文件路径transfer_backup/Machine ---------------------------------这里注释了 因为
                # stable_result_path = os.path.join(stable_output_path, f"{package_name}_results.csv")
                # print(stable_result_path)
                # with open(stable_result_path, 'w', newline='', encoding='utf-8') as f:
                #     writer = csv.writer(f)
                #     writer.writerow(headers)
                print(f"数据包{package_name}中的NG文件夹不存在: {ng_image_folder}")
                logger.warning(f"数据包{package_name}中的NG文件夹不存在: {ng_image_folder}")          

                # time.sleep(0.5)  # 暂停1秒
                tobe_processed.popleft()
                return

            # 验证文件存在
            if not os.path.exists(csv_path):
                # 构建完整的文件路径External AI/AI
                ai_path = os.path.join(ai_output_path, f"{package_name}.csv")
                # print(ai_path)
                with open(ai_path, 'w') as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)

                # 构建完整的文件路径transfer_backup/Machine----------------------------------------这里也注释了
                # stable_result_path = os.path.join(stable_output_path, f"{package_name}_results.csv")
                # print(stable_result_path)
                # with open(stable_result_path, 'w', newline='', encoding='utf-8') as f:
                #     writer = csv.writer(f)
                #     writer.writerow(headers)

                print(f"读取数据包{package_name}中的CSV文件不存在: {ai_path}")
                logger.warning(f"读取数据包{package_name}中的CSV文件不存在: {ai_path}")
                # time.sleep(0.5)  # 暂停1秒
                tobe_processed.popleft()
                return


            if RECORD_DATE == None:
                RECORD_DATE = str(package_name)[0:8]


            else:
                if  RECORD_DATE < package_name[0:8]:

                    RECORD_DATE = str(package_name)[0:8]


            # 加载 component_mapping.json 文件
            with open('component_mapping.json', 'r', encoding='utf-8') as f:
                component_mapping = json.load(f)

            # 读取CSV
            df = pd.read_csv(csv_path)
            required_columns = ['ARRAY', 'PARTCODE', 'PARTNO', 'FLAG', 'REFID']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f"数据包{package_name}中CSV文件缺少必要列: {missing_columns}")
                raise ValueError(f"数据包{package_name}中CSV文件缺少必要列: {missing_columns}")

            results = []
            logger.info(f"开始处理文件包: {package_name}")

            # 初始化一个字典用于记录已经处理过的image_pattern及其在results中的位置
            seen_patterns = {}

            #实例化数据

            start_time = datetime.now()
            print(f"{start_time}  开始处理数据包{package_name}")
            logger.info(f"{start_time}  开始处理数据包{package_name}")


            for index, row in df.iterrows():
                try:
                    image_pattern = f"{row['ARRAY']}@{row['PARTNO']}"
                    
                    if image_pattern in seen_patterns:
                        # 找到results中原始的结果，复制原始结果，更新index为当前行的index
                        original_index = seen_patterns[image_pattern]
                        original_result = results[original_index]

                        copied_result = original_result.copy()
                        copied_result['index'] = index
                        results.append(copied_result)
                    else:


                        record = ExecutionRecord()
                        modulelist.append(record)
                        record.jobname = row['JOBNAME']
                        record.array = row['ARRAY']
                        record.partcode = row['PARTCODE']
                        record.partno = row['PARTNO']
                        record.refid = row['REFID']
                        record.flag = row['FLAG']
                        record.date = row['DATE']
                        record.ng_name = row['NG_NAME']
                        record.array_barcode = row['ARRAY_BARCODE']
                        record.board_barcode = row['BOARD_BARCODE']
                        record.groupname = row['GROUPNAME']
                        record.partid = row['PARTID']
                        record.windid = row['WINDID']
                        record.windtype = row['WINDTYPE']
                        record.wind_x = row['WIND_X']
                        record.wind_y = row['WIND_Y']
                        record.wind_width = row['WIND_WIDTH']
                        record.wind_height = row['WIND_HEIGHT']
                        record.algo_type = row['ALGO_TYPE']
                        record.algo_roi = row['ALGO_ROI']
                        record.algo_dot = row['ALGO_DOT']
                        record.algo_line = row['ALGO_LINE']
                        record.font_angle = row['FONT_ANGLE']



                        filepath_woac, filepath_ac = find_image_by_pattern(ng_image_folder, image_pattern)

                        # print(filepath_woac)
                        # print(filepath_ac)
                        if filepath_woac == "" :
                            record.remark = 'Origin_lose'
                            logger.warning(f"未找到{image_pattern}")
                        if filepath_ac == "":
                            record.remark = record.remark + ' AC_lose'
                            logger.warning(f"未找到{image_pattern}_AC")
                        if filepath_woac == "" and filepath_ac == "" :

                            continue



                        partcode = row['PARTCODE']
                        if partcode in component_mapping:

                            category = component_mapping[partcode]
                            record.category = category

                            # result = process_image(filepath, category)

                            # !!!!!!!!!! R C !!!!!!!!!!

                            try:
                                result = process_image(filepath_woac, filepath_ac, category)
                            except Exception as e:
                                logger.error(f"{e}")
                                record.remark = "File lost "
                                

                            record.flag = result

                            #-------新增检测丝印逻辑--------
                            if result == "AIOK" and row['ALGO_TYPE'] == "Pattern":

                                if filepath_woac == "":
                                    filepath_tif = get_tif(filepath_ac,partcode)

                                    if filepath_tif:
                                    
                                        result = test_ocr(filepath_ac,filepath_tif)
                                        #ji lu ocr ai result
                                         
                                    else:
                                        record.remark = record.remark + " No OCR tif"
                                        logger.warning("未找到丝印模板文件")
                                else:
                                    filepath_tif = get_tif(filepath_woac,partcode)

                                    if filepath_tif:
                                    
                                        result = test_ocr(filepath_woac,filepath_tif)
                                        # ji lu ocr result
                                    else:
                                        record.remark = record.remark + " No OCR tif"
                                        logger.warning("未找到丝印模板文件")

                                # print(f"{image_pattern}的最终结果是{result}")
                        else:
                            print(f"PARTCODE {partcode}: 该物料不在配置清单内")
                            logger.warning(f"PARTCODE {partcode}: 该物料不在配置清单内")
                            continue


                        new_result = {
                            'index': index,
                            'array': row['ARRAY'],
                            'partno': row['PARTNO'],
                            'partcode': row['PARTCODE'],
                            'refid': row['REFID'],
                            'flag': row['FLAG'],
                            'filepath': filepath_woac,
                            'category': category,
                            'result': result
                        }
                        results.append(new_result)
                        # 记录这个image_pattern及其在results中的位置
                        seen_patterns[image_pattern] = len(results) - 1
                        

                except Exception as e:
                    logger.error(f"处理第 {index} 行时出错: {e}")
                    continue
            end_time = datetime.now()
            print(f"数据包{package_name}处理完成，用时{end_time - start_time},开始等待人工复判结果")
            logger.info(f"数据包{package_name}处理完成，用时{end_time - start_time},开始等待人工复判结果")

            # # 统计结果
            # total = len(results)
            # ng_count = sum(1 for r in results if r['result'] == 'AING')
            # ok_count = total - ng_count
            # logger.info(f"处理完成! 总计: {total} 项, AING: {ng_count}, AIOK: {ok_count}")
            
            while True:
                human_eva_result , info= find_matching_csv(package_name)  # 调用你的函数，可能需要传入参数
                
                if human_eva_result is not None:  # 如果返回的不是None
                    break  # 退出循环

                time.sleep(0.5)  # 暂停1秒

            module_is_ng = None
            for record in modulelist:

                record.module_result = info["Module_Result"]
                record.serialnumber = info["SerialNumber"]
                record.part_total = info["Part_Total"]
                record.part_good = info["Part_Good"]
                record.part_ng = info["Part_NG"]
                record.part_userok = info["Part_UserOK"]
                record.part_skip = info["Part_Skip"]

                if record.flag == "AING":
                    if module_is_ng is None:
                        module_is_ng = True


                for index, row in human_eva_result.iterrows():
                    if record.refid == row['RefID']:

                        record.inspresult = row["InspResult"]
                        record.repairresult = row["RepairResult"]
                        record.repairtime = row["RepairTime"]

                        if record.repairresult == "OK" or record.repairresult == "PASS" or record.repairresult == "" or record.repairresult == None:
                            if  record.flag == "AIOK":
                                record.part_tp = 1
                            else:
                                record.part_fn = 1
                        else:
                            if record.flag == "AIOK":
                                record.part_fp = 1
                            else:
                                record.part_tn = 1

            if module_is_ng :
                for record in modulelist:
                        record.module_ai_result = "AING"

                        if record.module_result == "USERNG" or record.module_result == "NG":
                            record.module_tn = 1
                        else:
                            record.module_fn =1

            else:
                for record in modulelist:
                        record.module_ai_result = "AIOK"

                        if record.module_result == "USEROK" or record.module_result == "GOOD":
                            record.module_tp = 1
                        else:
                            record.module_fp =1


            # 首先在原始df中添加RepairResult列（初始化为空值）
            df.insert(df.columns.get_loc('FLAG') + 1, 'RepairResult', None)

            if results:
                # 更新原始CSV中的FLAG列
                match_count = 0
                for result in results:
                    df.at[result['index'], 'FLAG'] = result['result']
                    # 获取当前行的REFID
                    current_refid = result['refid']
                    repair_result = None
                    # 在human_eva_result中查找匹配的RefID
                    # matched_rows = human_eva_result[human_eva_result['RefID'] == current_refid]

                    for index, row in human_eva_result.iterrows():
                        
                        if row['RefID'] == current_refid:
                            match_count = match_count + 1
                            repair_result = row['RepairResult']
                            break  # 如果找到匹配项，可以提前退出循环

                        
  
                    df.at[result['index'], 'RepairResult'] = repair_result

                    # print(result["filepath"],result["category"],repair_result)
                    logger.info(f'"{result["filepath"]}","{result["category"]}","{repair_result}"')

                if match_count == 0:
                    logger.warning("没有找到正确的数据匹配人工复判结果")
                    # process_image_result(result["filepath"],result["category"],repair_result)# mo

            # 创建结果DataFrame
            result_df = pd.DataFrame(results)

            # 1. 保存更新后的_result.csv到/External Al/AI
            transfer_result_csv_path = os.path.join(ai_output_path, f"{package_name}.csv")
            df.to_csv(transfer_result_csv_path, index=False)
            print(f"Transfer目录CSV已回写到AI目录: {transfer_result_csv_path}")
            logger.info(f"Transfer目录CSV已回写到AI目录: {transfer_result_csv_path}")

            # 2. 保存更新后的_result.csv到/transfer_backup/Machine
            # stable_result_path= os.path.join(stable_machine_path, package_name)
            # transfer_backup_result_csv_path = os.path.join(stable_result_path, f"{package_name}_results.csv")
            # df.to_csv(transfer_backup_result_csv_path, index=False)
            # print(f"transfer_backup目录CSV已更新: {transfer_backup_result_csv_path}")


            for record in modulelist:
                # start_time = datetime.now()
                # print("start_time",record.repairresult,start_time)
                # logger.info("start_time",record.repairresult,start_time)

                record.save_to_csv(f"./SMT_20250625-26zzzzzzz_ResultsData.csv")
                # print("end_time",record.repairresult,datetime.now())
                # logger.info("end_time",record.repairresult,datetime.now())



            modulelist.clear()


            print(work_path)
            shutil.move(work_path, "./transfer/External AI/finish")

            # read csv and delete some row
            # remove to another path 


            tobe_processed.popleft()


def get_package_path_name(work_path: str):
    # """直接替换原函数"""
    # items = os.listdir(work_path)
    # # 按修改时间获取最新的文件/文件夹
    # packname = max(items, key=lambda x: os.path.getmtime(os.path.join(work_path, x)))
    # work_path = os.path.join(work_path, packname)
    # return work_path, packname
    # for filename in os.listdir(work_path):
    #     file_path = os.path.join(work_path, filename)

    #     # 检查是否已经在 tobe_processed 中
    #     if file_path not in tobe_processed:
    #         tobe_processed.append(file_path)  # 加入队列

    # 返回队列的第一个元素（如果队列非空）
    if tobe_processed:
        parts = tobe_processed[0].split('\\')  # 按 \ 拆分

        # 拆分为两部分：前面所有目录 + 最后一级目录/文件名
        packname = parts[-1]  # 最后的目录/文件名
        # print(work_path)
        # print("----------------------------------------------------------")
        # print(tobe_processed[0])
        return tobe_processed[0], packname
    else:
        return None, None  # 或者 raise ValueError("No files to process")




# 复制文件到目标路径

def copy_friend_file(src_path, dest_path):

    file = os.listdir(src_path)[0]
    file_path = os.path.join(src_path, f"{file.split('.')[0]}.csv")
    dest_path = os.path.join(dest_path, f"{file.split('.')[0]}_friend.csv")
    shutil.copy2(file_path, dest_path)



def get_tif(filepath_woac, partcode):
    directory = os.path.dirname(filepath_woac)
    tif_files = []  # 创建空列表存储匹配的文件
    
    try:
        # 遍历目录中的所有文件
        for filename in os.listdir(directory):
            if filename.startswith(partcode) and filename.lower().endswith('.tif'):
                # 将匹配的文件完整路径添加到列表中
                tif_files.append(os.path.join(directory, filename))
    except FileNotFoundError:
        print(f"错误：找不到目录 '{directory}'")
        logger.error(f"错误：找不到目录 '{directory}'")

        return []  # 返回空列表而不是None
    
    return tif_files  # 返回包含所有匹配文件的列表
