import pandas as pd
import os
import shutil
from log_config import logger

headers = [
    "Machine_Name", "Model_Name", "Module_Total", "Module_Job",
    "Module_Yield", "Module_Good", "Module_NG", "Module_UserOK", "Module_Skip",
    "Module_AI_NG", "Module_AI_OK", "Module_TP", "Module_TN", "Module_FP", "Module_FN",  "Module_AI_Yield",
    "Module_Accuracy", "Module_FPRate", "Module_FNRate", "Part_Total", "Part_Job", "Part_Yield",
    "Part_Good", "Part_NG", "Part_UserOK", "Part_Skip", "Part_AING", "Part_AIOK",
    "Part_TP", "Part_TN", "Part_FP", "Part_FN", "Part_AI_Yield", "Part_Accuracy", "Part_FPRate", "Part_FNRate"
]
#numpy.float64或者str
# 设置目标目录路径
directory = r"/home/hqit/test_goodwe"

SMT_ECNU_GDW_ResultsReport = pd.DataFrame(columns=headers)   #最终生成的csv
all_data = pd.DataFrame()  #所有待处理数据

def read_and_filter_csv_files(directory, start_time=None, end_time=None):
    """
    读取目录下所有ResultsData.csv文件，并筛选指定时间范围内的数据
    参数:
        directory: 文件目录路径
        start_time: 开始时间(格式应与DATE列一致，如20250610221745)
        end_time: 结束时间(格式应与DATE列一致)
    """
    all_data = pd.DataFrame()

    for filename in os.listdir(directory):
        if filename.endswith("merge.csv"):
        # if filename.endswith("SMT_20250625_ResultsData.csv"):

            filepath = os.path.join(directory, filename)

            backup_path = os.path.join(directory, f"backup_{filename}")
            try:
                shutil.copy2(filepath, backup_path)
                # print(f"已创建备份: {backup_path}")
            except Exception as e:
                # print(f"创建备份失败: {e}")
                logger.error(f"创建备份失败: {e}")
                continue  # 跳过处理此文件
            try:
                # 读取CSV文件，确保DATE列为字符串类型
                
                df = pd.read_csv(backup_path, encoding='utf-8-sig')

                # 筛选时间范围内的数据
                if start_time is not None and end_time is not None:
                    # 确保DATE列是字符串类型进行比较
                    mask = (df['DATE'] >= start_time) & (df['DATE'] <= end_time)
                    df = df[mask]

                # 添加到总DataFrame中
                all_data = pd.concat([all_data, df], ignore_index=True)
                print(f"已成功读取并筛选: {filename} (记录数: {len(df)})")
                break

            except Exception as e:
                print(f"读取文件 {filename} 时出错: {str(e)}")

    return all_data
# step 1
start_time = 20250624080000  # 格式示例: YYYYMMDDHHMMSS
end_time = 20250625080000

all_data = read_and_filter_csv_files(directory, start_time, end_time)

if not all_data.empty:
    print("\n文件读取完成，开始处理数据...")

    # 1. 提取需要的列并去重（确保每个DATE+JOBNAME组合只计一次）
    unique_data = all_data[['DATE','JOBNAME','SerialNumber','Module_Result','Module_TP','Module_TN','Module_FP','Module_FN','Module_AI_Result']].drop_duplicates(subset=['DATE', 'JOBNAME'])
    # print(unique_data)

    # 在分组前先处理NaN值，将NaN替换为0
    unique_data['Module_TP'] = unique_data['Module_TP'].fillna(0)
    unique_data['Module_TN'] = unique_data['Module_TN'].fillna(0)
    unique_data['Module_FP'] = unique_data['Module_FP'].fillna(0)
    unique_data['Module_FN'] = unique_data['Module_FN'].fillna(0)

    # 2. 按JOBNAME分组，统计各项指标
    result = unique_data.groupby('JOBNAME').agg(
        Machine_Name=('SerialNumber', 'first'),
        Model_Name=('JOBNAME', 'first'),
        Module_Total=('DATE', 'nunique'),
        Model_Job=('JOBNAME', 'first'),
        Module_Good=('Module_Result', lambda x: (x == 'GOOD').sum()),
        Module_UserOK=('Module_Result', lambda x: (x == 'USEROK').sum()),
        Module_NG=('Module_Result', lambda x: (x == 'USERNG').sum()),
        # Module_NG=('Module_Result', lambda x: (x == 'NG').sum()),
        Module_Skip = ('Module_Result', lambda x: (x == 'SKIP').sum()),  # 待确认
        Module_AI_NG = ('Module_AI_Result', lambda x: (x == 'AING').sum()),
        Module_AI_OK = ('Module_AI_Result', lambda x: (x == 'AIOK').sum()),
        Module_TP=('Module_TP', 'sum'),
        Module_TN=('Module_TN', 'sum'),
        Module_FP = ('Module_FP', 'sum'),
        Module_FN = ('Module_FN', 'sum')

    ).reset_index(drop=True)

    # 3. 将结果存入最终报告
    SMT_ECNU_GDW_ResultsReport['Machine_Name'] = result['Machine_Name']
    SMT_ECNU_GDW_ResultsReport['Model_Name'] = result['Model_Name']
    SMT_ECNU_GDW_ResultsReport['Module_Total'] = result['Module_Total']
    SMT_ECNU_GDW_ResultsReport['Module_Job'] = result['Model_Job']
    SMT_ECNU_GDW_ResultsReport['Module_Good'] = result['Module_Good']
    SMT_ECNU_GDW_ResultsReport['Module_UserOK'] = result['Module_UserOK']
    SMT_ECNU_GDW_ResultsReport['Module_NG'] = result['Module_NG']
    SMT_ECNU_GDW_ResultsReport['Module_Skip'] = result['Module_Skip']
    SMT_ECNU_GDW_ResultsReport['Module_Skip'] = result['Module_Skip']
    SMT_ECNU_GDW_ResultsReport['Module_AI_NG'] = result['Module_AI_NG']
    SMT_ECNU_GDW_ResultsReport['Module_AI_OK'] = result['Module_AI_OK']
    SMT_ECNU_GDW_ResultsReport['Module_TP'] = result['Module_TP']
    SMT_ECNU_GDW_ResultsReport['Module_TN'] = result['Module_TN']
    SMT_ECNU_GDW_ResultsReport['Module_FP'] = result['Module_FP']
    SMT_ECNU_GDW_ResultsReport['Module_FN'] = result['Module_FN']
    SMT_ECNU_GDW_ResultsReport['Part_Job'] = SMT_ECNU_GDW_ResultsReport['Model_Name']
    SMT_ECNU_GDW_ResultsReport['Part_Total'] = 0.0
    SMT_ECNU_GDW_ResultsReport['Part_Good'] = 0.0
    SMT_ECNU_GDW_ResultsReport['Part_NG'] = 0.0
    SMT_ECNU_GDW_ResultsReport['Part_UserOK'] = 0.0
    SMT_ECNU_GDW_ResultsReport['Part_Skip'] = 0.0
    SMT_ECNU_GDW_ResultsReport['Part_AING'] = 0.0
    SMT_ECNU_GDW_ResultsReport['Part_AIOK'] = 0.0
    SMT_ECNU_GDW_ResultsReport['Part_TP'] = 0.0
    SMT_ECNU_GDW_ResultsReport['Part_TN'] = 0.0
    SMT_ECNU_GDW_ResultsReport['Part_FP'] = 0.0
    SMT_ECNU_GDW_ResultsReport['Part_FN'] = 0.0

    # 1. 对 all_data 按 DATE 和 JOBNAME 去重
    unique_date = all_data.drop_duplicates(subset=['DATE', 'JOBNAME'])
    # 2. 遍历去重后的 unique_data
    for _, row in unique_date.iterrows():
        jobname = row['JOBNAME']
        part_total = row['Part_Total']
        part_good = row['Part_Good']
        part_ng = row['Part_NG']
        part_userok = row['Part_UserOK']
        part_skip = row['Part_Skip']

        # 3. 在 SMT_ECNU_GDW_ResultsReport 中查找匹配的 Model_Name
        matched_rows = SMT_ECNU_GDW_ResultsReport[SMT_ECNU_GDW_ResultsReport['Model_Name'] == jobname]
        # 4. 如果找到匹配，则累加 Part_Total、Part_Good、Part_NG、Part_UserOK、Part_Skip
        if not matched_rows.empty:
            # 获取匹配行的索引（这里默认取第一个，但理论上来说匹配行的索引只会有一个，因为之前根据JOBNAME聚合过）
            target_idx = matched_rows.index[0]
            SMT_ECNU_GDW_ResultsReport.at[target_idx, 'Part_Total'] += part_total
            SMT_ECNU_GDW_ResultsReport.at[target_idx, 'Part_Good'] += part_good
            SMT_ECNU_GDW_ResultsReport.at[target_idx, 'Part_NG'] += part_ng
            SMT_ECNU_GDW_ResultsReport.at[target_idx, 'Part_UserOK'] += part_userok
            SMT_ECNU_GDW_ResultsReport.at[target_idx, 'Part_Skip'] += part_skip

    # 2. 按JOBNAME分组，统计各项指标
    temp = all_data.groupby('DATE').agg(
        Date=('DATE', 'first'),
        JOBNAME=('JOBNAME', 'first'),
        Part_AI_NG = ('FLAG', lambda x: ((x == 'AING') | (x == 'NG') ).sum()),
        Part_AI_OK = ('FLAG', lambda x: ((x == 'AIOK') | (pd.isna(x))).sum()),
        Part_TP=('Part_TP', 'sum'),
        Part_TN=('Part_TN', 'sum'),
        Part_FP = ('Part_FP', 'sum'),
        Part_FN = ('Part_FN', 'sum')
    ).reset_index(drop=True)

    for _, row in temp.iterrows():
        jobname = row['JOBNAME']
        part_aiok = row['Part_AI_OK']
        part_aing = row['Part_AI_NG']
        part_tp = row['Part_TP']
        part_tn = row['Part_TN']
        part_fp = row['Part_FP']
        part_fn = row['Part_FN']

        # 3. 在 SMT_ECNU_GDW_ResultsReport 中查找匹配的 Model_Name
        matched_rows = SMT_ECNU_GDW_ResultsReport[SMT_ECNU_GDW_ResultsReport['Model_Name'] == jobname]
        # 4. 如果找到匹配，则累加 Part_Total、Part_Good、Part_NG、Part_UserOK、Part_Skip
        if not matched_rows.empty:
            # 获取匹配行的索引（这里默认取第一个，但理论上来说匹配行的索引只会有一个，因为之前根据JOBNAME聚合过）
            target_idx = matched_rows.index[0]
            SMT_ECNU_GDW_ResultsReport.at[target_idx, 'Part_AING'] += part_aing
            SMT_ECNU_GDW_ResultsReport.at[target_idx, 'Part_AIOK'] += part_aiok
            SMT_ECNU_GDW_ResultsReport.at[target_idx, 'Part_TP'] += part_tp
            SMT_ECNU_GDW_ResultsReport.at[target_idx, 'Part_TN'] += part_tn
            SMT_ECNU_GDW_ResultsReport.at[target_idx, 'Part_FP'] += part_fp
            SMT_ECNU_GDW_ResultsReport.at[target_idx, 'Part_FN'] += part_fn

    # print(temp)

    # # 1. 对 all_data 按 ARRAY 和 PARTNO 去重
    # unique_partno_date = all_data.drop_duplicates(subset=['ARRAY', 'PARTNO'])
    # # # 在分组前先处理NaN值，将NaN替换为0
    # # unique_partno_date['Part_TP'] = unique_data['Part_TP'].fillna(0)
    # # unique_partno_date['Part_TN'] = unique_data['Part_TN'].fillna(0)
    # # unique_partno_date['Part_FP'] = unique_data['Part_FP'].fillna(0)
    # # unique_partno_date['Part_FN'] = unique_data['Part_FN'].fillna(0)
    # # 2. 遍历去重后的 unique_data
    # for _, row in unique_partno_date.iterrows():
    #     jobname = row['JOBNAME']
    #     flag = row['FLAG']
    #     part_tp = row['Part_TP']
    #     part_tn = row['Part_TN']
    #     part_fp = row['Part_FP']
    #     part_fn = row['Part_FN']
    #
    #     # 3. 在 SMT_ECNU_GDW_ResultsReport 中查找匹配的 Model_Name
    #     matched_rows = SMT_ECNU_GDW_ResultsReport[SMT_ECNU_GDW_ResultsReport['Model_Name'] == jobname]
    #     # 4. 如果找到匹配，累加 Part_Total
    #     if not matched_rows.empty:
    #         # 获取匹配行的索引（可能有多行，这里默认取第一个）
    #         target_idx = matched_rows.index[0]
    #         if flag == 'AIOK':
    #             # SMT_ECNU_GDW_ResultsReport.loc[target_idx, 'Part_AIOK'] += 1.0
    #             SMT_ECNU_GDW_ResultsReport.at[target_idx, 'Part_AIOK'] += 1.0
    #         if flag == 'AING':
    #             # SMT_ECNU_GDW_ResultsReport.loc[mask, 'Part_AING'] += 1.0
    #             SMT_ECNU_GDW_ResultsReport.at[target_idx, 'Part_AING'] += 1.0
    #
    #         if not pd.isna(part_tp):
    #             SMT_ECNU_GDW_ResultsReport.at[target_idx, 'Part_TP'] += part_tp
    #         if not pd.isna(part_tn):
    #             SMT_ECNU_GDW_ResultsReport.at[target_idx, 'Part_TN'] += part_tn
    #         if not pd.isna(part_fp):
    #             SMT_ECNU_GDW_ResultsReport.at[target_idx, 'Part_FP'] += part_fp
    #         if not pd.isna(part_fn):
    #             SMT_ECNU_GDW_ResultsReport.at[target_idx, 'Part_FN'] += part_fn



    # 计算
    for index, row in SMT_ECNU_GDW_ResultsReport.iterrows():
        # 获取当前行的值
        module_tp = row['Module_TP']
        module_tn = row['Module_TN']
        module_fp = row['Module_FP']
        module_fn = row['Module_FN']
        module_total = row['Module_Total']
        module_good = row['Module_Good']
        module_userok = row['Module_UserOK']


        part_tp = row['Part_TP']
        part_tn = row['Part_TN']
        part_fp = row['Part_FP']
        part_fn = row['Part_FN']
        part_total = row['Part_Total']
        part_good = row['Part_Good']
        part_userok = row['Part_UserOK']

        # 处理可能的除数为0的情况
        if module_total > 0:
            model_yield = round((module_good + module_userok) / module_total, 6)
            model_ai_yield = round((module_tp + module_good) / module_total, 6)
            model_zhunque = round((module_tp + module_tn) / module_total, 6)
        else:
            model_yield = 0.0
            model_ai_yield =0.0
            model_zhunque = 0.0  # 或其他默认值，如NaN
        if module_fp + module_tn > 0:
            model_loujian = round(module_fp / (module_fp + module_tn), 6)
        else:
            model_loujian = 0.0
        if module_tp + module_fn > 0:
            model_wupan = round(module_fn / (module_tp + module_fn), 6)
        else:
            model_wupan = 0.0
        if part_total > 0:
            part_yield = round((part_good + part_userok) / part_total, 6)
            part_ai_yield = round((part_tp + part_good) / part_total, 6)
        else:
            part_yield = 0.0
            part_ai_yield = 0.0
        if part_tp + part_tn + part_fp + part_fn > 0:
            part_zhunque = round((part_tp + part_tn) / (part_tp + part_tn + part_fp + part_fn), 6)
        else:
            part_zhunque = 0.0
        if part_fp + part_tn > 0:
            part_loujian = round(part_fp / (part_fp + part_tn), 6)
        else:
            part_loujian = 0.0
        if part_tp + part_fn > 0:
            part_wupan = round(part_fn / (part_tp + part_fn), 6)
        else:
            part_wupan = 0.0

        # 将计算结果赋给 SMT_ECNU_GDW_ResultsReport中的列
        SMT_ECNU_GDW_ResultsReport.at[index, 'Module_Yield'] = model_yield
        SMT_ECNU_GDW_ResultsReport.at[index, 'Module_AI_Yield'] = model_ai_yield
        SMT_ECNU_GDW_ResultsReport.at[index, 'Module_Accuracy'] = model_zhunque
        SMT_ECNU_GDW_ResultsReport.at[index, 'Module_FPRate'] = model_loujian
        SMT_ECNU_GDW_ResultsReport.at[index, 'Module_FNRate'] = model_wupan
        SMT_ECNU_GDW_ResultsReport.at[index, 'Part_Yield'] = part_yield
        SMT_ECNU_GDW_ResultsReport.at[index, 'Part_AI_Yield'] = part_ai_yield
        SMT_ECNU_GDW_ResultsReport.at[index, 'Part_Accuracy'] = part_zhunque
        SMT_ECNU_GDW_ResultsReport.at[index, 'Part_FPRate'] = part_loujian
        SMT_ECNU_GDW_ResultsReport.at[index, 'Part_FNRate'] = part_wupan



    # SMT_ECNU_GDW_ResultsReport = pd.concat([
    #     SMT_ECNU_GDW_ResultsReport,
    #     result[['Model_Name', 'Module_Total', 'Module_Good', 'Module_UserOK', 'Module_NG']]
    # ], ignore_index=True)

    output_path = os.path.join("/home/hqit/桌面/GDW_Report", "SMT_ECNU_GDW_ResultsReport_062408-062508.csv")
    SMT_ECNU_GDW_ResultsReport.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\n最终报告已保存到: {output_path}")
else:
    print("\n未找到任何有效数据，请检查输入文件！")