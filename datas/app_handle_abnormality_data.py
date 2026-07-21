"""H5 异常处理模块测试数据"""

from datas.app_login_data import app_login_data

# H5 登录信息复用 app_login_data 中的第一条
_h5_login = app_login_data[0]

app_handle_abnormality_data = [
    {
        "case_name": "H5异常处理",
        "base_url": _h5_login["base_url"],
        "username": _h5_login["username"],
        "password": _h5_login["password"],
        # serial_number 由 test_order_detail 写入 shared_data
        "handle_type": "厂内维修",          # 处理方式
        "handle_title": "test jaka",        # 处理标题
        "handle_description": "测试测试jaka--无需理会-后续删除",  # 处理描述
    },
]
