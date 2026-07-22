"""H5 检测通过模块测试数据"""

from datas.app_login_data import app_login_data

# H5 登录信息复用 app_login_data 中的第一条
_h5_login = app_login_data[0]

app_test_pass_data = [
    {
        "case_name": "H5检测通过",
        "base_url": _h5_login["base_url"],
        "username": _h5_login["username"],
        "password": _h5_login["password"],
        # station_code 和 serial_number 由 test_order_detail 写入 shared_data
        "image_path": "datas/picture111.jpg",   # 上传图片路径（相对于项目根目录）
    },
]
