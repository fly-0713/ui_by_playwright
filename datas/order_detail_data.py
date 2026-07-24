"""生产工单详情模块测试数据"""

from datetime import datetime

_today_str = datetime.now().strftime("%Y%m%d")  # 如 "20260724"
_time_str = datetime.now().strftime("%H%M%S")   # 如 "111413"

order_detail_data = [
    {
        "case_name": "获取工单详情数据",
        # 默认 fallback；实际运行时 test_order_detail.py 会从 shared_data 读取 plan_add 写入的 plan_no
        "plan_no": f"test{_today_str}{_time_str}",
    },
]
