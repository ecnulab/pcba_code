import csv
import os
from datetime import datetime


class ExecutionRecord:
    """执行记录类 - 使用指定字段"""

    def __init__(self, date="", jobname="", array="", partcode="", partno="",
                 ng_name="", category="",flag="", refid="", serialnumber="", part_total="",
                 part_good="", part_ng="", part_userok="", part_skip="",
                 inspresult="", repairresult="", repairtime="", module_result="",
                 module_ai_result="", part_tp="", part_tn="", part_fp="",
                 part_fn="", module_tp="", module_tn="", module_fp="", module_fn="",remark="",board_barcode="",array_barcode="",
                 groupname="", partid="", windid="", windtype="", wind_x="", wind_y="", wind_width="", wind_height="", algo_type="", algo_roi="",
                 algo_line="", algo_dot="",  font_angle=""):
        self.date = date
        self.jobname = jobname
        self.array = array
        self.partcode = partcode
        self.partno = partno
        self.ng_name = ng_name
        self.category = category
        self.flag = flag
        self.refid = refid
        self.serialnumber = serialnumber
        self.part_total = part_total
        self.part_good = part_good
        self.part_ng = part_ng
        self.part_userok = part_userok
        self.part_skip = part_skip
        self.inspresult = inspresult
        self.repairresult = repairresult
        self.repairtime = repairtime
        self.module_result = module_result
        self.module_ai_result = module_ai_result
        self.part_tp = part_tp
        self.part_tn = part_tn
        self.part_fp = part_fp
        self.part_fn = part_fn
        self.module_tp = module_tp
        self.module_tn = module_tn
        self.module_fp = module_fp
        self.module_fn = module_fn
        self.remark = remark
        self.board_barcode = board_barcode
        self.array_barcode = array_barcode
        self.groupname = groupname
        self.partid = partid
        self.windid = windid
        self.windtype = windtype
        self.wind_x = wind_x
        self.wind_y = wind_y
        self.wind_width = wind_width
        self.wind_height = wind_height
        self.algo_type = algo_type
        self.algo_roi = algo_roi
        self.algo_line = algo_line
        self.algo_dot = algo_dot
        self.font_angle = font_angle






    def save_to_csv(self, csv_file_path):
        """保存到CSV文件"""
        file_exists = os.path.exists(csv_file_path)

        with open(csv_file_path, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['DATE', 'JOBNAME', 'ARRAY', 'PARTCODE', 'PARTNO', 'NG_NAME','CATEGORY',
                          'FLAG', 'REFID', 'SerialNumber', 'Part_Total', 'Part_Good',
                          'Part_NG', 'Part_UserOK', 'Part_Skip', 'InspResult',
                          'RepairResult', 'RepairTime', 'Module_Result', 'Module_AI_Result',
                          'Module_TP','Module_TN', 'Module_FP', 'Module_FN','Part_TP', 'Part_TN', 'Part_FP', 'Part_FN',"REMARK","BOARD_BARCODE","ARRAY_BARCODE",
                           'GROUPNAME', 'PARTID', 'WINDTYPE', 'WINDID','WIND_X', 'WIND_Y', 'WIND_WIDTH', 'WIND_HEIGHT', 'ALGO_TYPE', 'ALGO_ROI', 'ALGO_LINE', 'ALGO_DOT',  'FONT_ANGLE' ]

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            writer.writerow({
                'DATE': self.date,
                'JOBNAME': self.jobname,
                'ARRAY': self.array,
                'PARTCODE': self.partcode,
                'PARTNO': self.partno,
                'NG_NAME': self.ng_name,
                'CATEGORY':self.category,
                'FLAG': self.flag,
                'REFID': self.refid,
                'SerialNumber': self.serialnumber,
                'Part_Total': self.part_total,
                'Part_Good': self.part_good,
                'Part_NG': self.part_ng,
                'Part_UserOK': self.part_userok,
                'Part_Skip': self.part_skip,
                'InspResult': self.inspresult,
                'RepairResult': self.repairresult,
                'RepairTime': self.repairtime,
                'Module_Result': self.module_result,
                'Module_AI_Result': self.module_ai_result,
                'Part_TP': self.part_tp,
                'Part_TN': self.part_tn,
                'Part_FP': self.part_fp,
                'Part_FN': self.part_fn,
                'Module_TP': self.module_tp,
                'Module_TN': self.module_tn,
                'Module_FP': self.module_fp,
                'Module_FN': self.module_fn,
                'REMARK': self.remark,
                'BOARD_BARCODE': f"'{self.board_barcode}",
                'ARRAY_BARCODE': f"'{self.array_barcode}",
                'GROUPNAME': self.groupname,
                'PARTID': self.partid,
                'WINDID': self.windid,
                'WINDTYPE': self.windtype,
                'WIND_X': self.wind_x,
                'WIND_Y': self.wind_y,
                'WIND_WIDTH': self.wind_width,
                'WIND_HEIGHT': self.wind_height,
                'ALGO_TYPE': self.algo_type,
                'ALGO_ROI': self.algo_roi,
                'ALGO_LINE': self.algo_line,
                'ALGO_DOT': self.algo_dot,
                'FONT_ANGLE': self.font_angle
            })
            csvfile.flush()