"""H5 异常审核模块测试数据"""

from datas.app_login_data import app_login_data

# H5 登录信息复用 app_login_data 中的第一条
_h5_login = app_login_data[0]

app_review_abnormality_data = [
    {
        "case_name": "H5异常审核",
        "base_url": _h5_login["base_url"],
        "username": _h5_login["username"],
        "password": _h5_login["password"],
        # serial_number 由 test_order_detail 写入 shared_data
        "abnormality_type": "操作问题",         # 异常类型
        "problem_description": "节卡测试数据-问题描述",  # 问题描述
        "temporary_measure": "节卡测试数据-临时对策",  # 临时对策
        "production_stage": "量产",              # 生产阶段
        "reviewer_name": "张飞飞",               # 审核人姓名
    },
]
