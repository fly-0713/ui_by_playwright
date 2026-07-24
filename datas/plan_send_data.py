"""计划下发模块测试数据"""

from datetime import datetime, timedelta

_today = datetime.now()
_end = _today + timedelta(days=7)       # 结束日期 = 今天 + 7 天
_today_day = str(_today.day)            # 开始日期数字，如 "23"
_end_day = str(_end.day)                # 结束日期数字，如 "30"
_today_str = _today.strftime("%Y%m%d")  # 如 "20260724"
_time_str = _today.strftime("%H%M%S")   # 如 "111413"

plan_send_data = [
    {
        "case_name": "计划下发",
        # 默认 fallback；实际运行时 test_plan_send.py 会从 shared_data 读取 plan_add 写入的 plan_no
        "plan_no": f"test{_today_str}{_time_str}",
        "send_quantity": "1",               # 下发数量
        "start_date_day": _today_day,       # 排程开始日期：今天
        "end_date_day": _end_day,           # 排程结束日期：今天 + 7 天
        "expected_status": ["下发中", "已下发"],  # 下发后预期状态（任一即可）
    },
]
