"""生产工单派工模块测试数据"""

from datetime import datetime

_today_str = datetime.now().strftime("%Y%m%d")  # 如 "20260623"

order_send_data = [
    {
        "case_name": "生产工单派工",
        "plan_no": f"test{_today_str}001",       # 计划编号（动态生成，与 plan_send_data 一致）
        "production_line": "TEST张飞飞产线-机器人",  # 产线
        "line_leader": "张飞飞",                  # 产线负责人
        "packing_process": "TEST张飞飞包装工艺专用v1.0",  # 包装工艺
        "expected_status": ["待生产", "生产中"],   # 派工后预期状态（任一即可）
    },
]
