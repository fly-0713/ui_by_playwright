"""计划新增模块测试数据"""

from datetime import datetime, timedelta

_today = datetime.now()
_end = _today + timedelta(days=7)       # 结束日期 = 今天 + 7 天
_today_day = str(_today.day)            # 开始日期数字，如 "23"
_end_day = str(_end.day)               # 结束日期数字，如 "30"
_today_str = _today.strftime("%Y%m%d") # 如 "20260724"
_time_str = _today.strftime("%H%M%S")  # 如 "111413"

plan_add_data = [
    {
        "case_name": "新增计划订单",
        "material_code": "2002030008",          # 物料编码
        "quantity": "1",                        # 数量
        "plan_no": f"test{_today_str}{_time_str}",  # 计划编号，如 test20260724111413
        "erp_order": "MO001261",                # ERP生产订单
        "start_date_day": _today_day,           # 开始日期：今天
        "end_date_day": _end_day,               # 结束日期：今天 + 7 天
    },
]
