"""H5 登录模块测试数据

H5 账号信息优先从环境变量 H5_USERNAME / H5_PASSWORD 读取，
否则从 config.yaml 的 h5 节点读取。
"""

import os

import yaml


def _load_h5_config() -> dict:
    """直接读取 config.yaml 的 h5 环境配置"""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config.yaml",
    )
    with open(config_path, "r", encoding="utf-8") as f:
        all_config = yaml.safe_load(f)
    h5_config = all_config.get("h5")
    if h5_config is None:
        raise ValueError("config.yaml 中未找到 h5 环境配置")
    return h5_config


_h5_config = _load_h5_config()

# H5 账号优先使用环境变量，否则 fallback 到 config.yaml
_h5_username = os.environ.get("H5_USERNAME") or _h5_config.get("accounts", [{}])[0].get("username")
_h5_password = os.environ.get("H5_PASSWORD") or _h5_config.get("accounts", [{}])[0].get("password")

app_login_data = [
    {
        "case_name": "H5正常登录",
        "base_url": _h5_config.get("base_url"),
        "username": _h5_username,
        "password": _h5_password,
    },
]
