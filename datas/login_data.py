"""登录模块测试数据

MES 账号信息优先从环境变量 MES_USERNAME / MES_PASSWORD 读取，
否则从 config.yaml 的 mes 节点读取。
"""

from common.config import config

_mes_account = config.get_mes_account()

login_data = [
    {
        "case_name": "自动识别验证码登录",
        "base_url": config.base_url,
        "username": _mes_account.get("username"),
        "password": _mes_account.get("password"),
    },
]
