"""生产工单详情模块测试数据"""

from datetime import datetime

_today_str = datetime.now().strftime("%Y%m%d")  # 如 "20260626"

order_detail_data = [
    {
        "case_name": "获取工单详情数据",
        # "plan_no": "test20260623001", 
        "plan_no": f"test{_today_str}001",       # 计划编号（与 plan_send_data 一致）
    },
]
