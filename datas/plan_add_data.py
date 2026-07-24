"""计划新增模块测试数据"""

from datetime import datetime, timedelta

from common.test_data_helper import get_plan_no

_today = datetime.now()
_end = _today + timedelta(days=7)       # 结束日期 = 今天 + 7 天
_today_day = str(_today.day)            # 开始日期数字，如 "23"
_end_day = str(_end.day)               # 结束日期数字，如 "30"

plan_add_data = [
    {
        "case_name": "新增计划订单",
        "material_code": "2002030008",          # 物料编码
        "quantity": "1",                        # 数量
        "plan_no": get_plan_no(),               # 从 shared_data 获取或生成唯一计划编号
        "erp_order": "MO001261",                # ERP生产订单
        "start_date_day": _today_day,           # 开始日期：今天
        "end_date_day": _end_day,               # 结束日期：今天 + 7 天
    },
]
