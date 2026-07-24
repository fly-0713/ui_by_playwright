"""生产工单派工模块测试数据"""

from common.test_data_helper import get_plan_no

order_send_data = [
    {
        "case_name": "生产工单派工",
        "plan_no": get_plan_no(),                 # 与 plan_send_data 保持一致，从 shared_data 获取
        "production_line": "TEST张飞飞产线-机器人",  # 产线
        "line_leader": "张飞飞",                  # 产线负责人
        "packing_process": "TEST张飞飞包装工艺专用v1.0",  # 包装工艺
        "expected_status": ["待生产", "生产中"],   # 派工后预期状态（任一即可）
    },
]
