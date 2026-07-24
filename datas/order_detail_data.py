"""生产工单详情模块测试数据"""

from common.test_data_helper import get_plan_no

order_detail_data = [
    {
        "case_name": "获取工单详情数据",
        "plan_no": get_plan_no(),                 # 计划编号（与 plan_send_data 一致，从 shared_data 获取）
    },
]
