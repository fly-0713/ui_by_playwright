"""生产工单派工模块测试数据"""

from datetime import datetime

_today_str = datetime.now().strftime("%Y%m%d")  # 如 "20260724"
_time_str = datetime.now().strftime("%H%M%S")   # 如 "111413"

order_send_data = [
    {
        "case_name": "生产工单派工",
        # 默认 fallback；实际运行时 test_order_send.py 会从 shared_data 读取 plan_add 写入的 plan_no
        "plan_no": f"test{_today_str}{_time_str}",
        "production_line": "TEST张飞飞产线-机器人",  # 产线
        "line_leader": "张飞飞",                  # 产线负责人
        "packing_process": "TEST张飞飞包装工艺专用v1.0",  # 包装工艺
        "expected_status": ["待生产", "生产中"],   # 派工后预期状态（任一即可）
    },
]
