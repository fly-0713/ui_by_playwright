"""H5 维修完成模块测试数据"""

from datas.app_login_data import app_login_data

# H5 登录信息复用 app_login_data 中的第一条
_h5_login = app_login_data[0]

app_repair_over_data = [
    {
        "case_name": "H5维修完成",
        "base_url": _h5_login["base_url"],
        "username": _h5_login["username"],
        "password": _h5_login["password"],
        # serial_number 由 test_order_detail 写入 shared_data
        "fault_description": "测试数据-维修描述-节卡测试数据",  # 故障现象描述
        "fault_position": "关节一",      # 故障位置
        "fault_code": "11R",             # 故障代码
        "fault_part_category": "机器人产品",  # 故障部件分类
        "fault_part": "ABZ编码器",        # 故障部件
        "fault_reason": "码盘脏污-zh",    # 故障原因
        "fault_type": "A01-作业不良",     # 故障类型
        "handle_description": "节卡测试数据-处理描述",  # 处理描述
    },
]
