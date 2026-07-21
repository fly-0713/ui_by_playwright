"""H5 检测不通过提报异常模块测试数据"""

from datas.app_login_data import app_login_data

# H5 登录信息复用 app_login_data 中的第一条
_h5_login = app_login_data[0]

app_test_nopass_data = [
    {
        "case_name": "H5检测不通过",
        "base_url": _h5_login["base_url"],
        "username": _h5_login["username"],
        "password": _h5_login["password"],
        # station_code 和 serial_number 由 test_order_detail 写入 shared_data，
        # 运行时从 shared_data 读取，此处不再硬编码
        "fail_title": "test数据",            # 异常标题
        "fail_description": "节卡测试数据",  # 异常描述
    },
]
