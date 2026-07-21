"""配置管理模块

从 config.yaml 读取环境配置，通过环境变量 ENV 切换环境。
config.yaml 中支持使用 ${ENV_VAR} 或 ${ENV_VAR:default} 占位符引用环境变量。
用法：
    from common.config import config
    url = config.base_url
    headless = config.headless

注意：
    config 是懒加载单例，第一次访问属性时才真正读取 YAML。
    这允许 main.py 先设置 ENV 环境变量，再由 pytest 收集用例时加载配置。
"""

import os
import re

import yaml


# 匹配 ${VAR} 或 ${VAR:default}
_ENV_PLACEHOLDER = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::([^}]*))?\}")


def _resolve_env_vars(obj):
    """递归解析对象中的 ${ENV_VAR} 或 ${ENV_VAR:default} 占位符"""
    if isinstance(obj, str):
        def _replace(match):
            var_name = match.group(1)
            default = match.group(2)
            value = os.environ.get(var_name)
            if value is None:
                if default is None:
                    raise ValueError(f"config.yaml 中引用的环境变量未设置: {var_name}")
                return default
            return value
        return _ENV_PLACEHOLDER.sub(_replace, obj)
    if isinstance(obj, dict):
        return {k: _resolve_env_vars(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_resolve_env_vars(item) for item in obj]
    return obj


class Config:
    """配置对象，将 YAML 配置映射为属性"""

    def __init__(self, data: dict, all_envs: dict = None):
        self._data = data
        self._all_envs = all_envs or {}

    @property
    def base_url(self) -> str:
        return self._data.get("base_url", "")

    @property
    def headless(self) -> bool:
        return self._data.get("headless", False)

    @property
    def timeout(self) -> int:
        return self._data.get("timeout", 10000)

    @property
    def accounts(self) -> list:
        return self._data.get("accounts", [])

    def get_account(self, index: int = 0) -> dict:
        """获取指定索引的账号信息"""
        if index < len(self.accounts):
            return self.accounts[index]
        return {}

    def _get_env_account(self, env_name: str, env_username_key: str, env_password_key: str) -> dict:
        """获取指定环境的账号，优先使用环境变量覆盖"""
        env_config = self._all_envs.get(env_name, {})
        account = env_config.get("accounts", [{}])[0] if env_config else {}

        # 环境变量覆盖（CI 中通过 Secrets 注入）
        username = os.environ.get(env_username_key)
        password = os.environ.get(env_password_key)
        if username and password:
            account = {"username": username, "password": password}

        return account

    def get_mes_account(self) -> dict:
        """获取 MES 环境账号，优先读取 MES_USERNAME / MES_PASSWORD"""
        return self._get_env_account("mes", "MES_USERNAME", "MES_PASSWORD")

    def get_h5_account(self) -> dict:
        """获取 H5 环境账号，优先读取 H5_USERNAME / H5_PASSWORD"""
        return self._get_env_account("h5", "H5_USERNAME", "H5_PASSWORD")


class LazyConfig:
    """懒加载配置代理对象

    模块导入时不将真正读取 YAML，第一次访问属性时才加载。
    这样 main.py 可以先设置 ENV，再由用例收集触发加载。
    """

    def __init__(self):
        self._config = None

    def _ensure_loaded(self):
        if self._config is None:
            self._config = _load_config()

    def __getattr__(self, name):
        # 触发真正加载（_config 自身通过 __init__ 的 __dict__ 存取，不会循环）
        self._ensure_loaded()
        return getattr(self._config, name)

    def reload(self):
        """强制重新加载配置（切换 ENV 后调用）"""
        self._config = _load_config()


def _load_config() -> Config:
    """加载配置文件，根据环境变量 ENV 选择环境"""
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config.yaml",
    )

    with open(config_path, "r", encoding="utf-8") as f:
        all_config = yaml.safe_load(f)

    # 解析环境变量占位符 ${VAR} / ${VAR:default}
    all_config = _resolve_env_vars(all_config)

    # 通过环境变量切换环境，默认 mes
    env = os.environ.get("ENV", "mes")
    env_config = all_config.get(env)
    if env_config is None:
        raise ValueError(f"未找到环境配置: {env}，可选: {list(all_config.keys())}")

    return Config(env_config, all_envs=all_config)


# 全局配置实例（懒加载，第一次访问属性时才真正读取 yaml）
config = LazyConfig()
