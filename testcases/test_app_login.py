import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from playwright.sync_api import Page

from common.logger import logger
from datas.app_login_data import app_login_data
from pages.app_login_page import AppLoginPage


class TestAppLogin:
    """H5 登录测试用例

    H5 账号信息从 config.yaml 的 h5 节点读取。
    """

    @pytest.mark.parametrize(
        "data",
        app_login_data,
        ids=[d["case_name"] for d in app_login_data],
    )
    def test_app_login(self, page: Page, data: dict):
        """H5 端使用工号+密码登录，断言底部 tabbar 包含“我的” """
        logger.info(f"开始测试: {data['case_name']}")

        login_page = AppLoginPage(page)
        # 使用 data 中的 base_url
        login_page.navigate(data["base_url"])

        success = login_page.login_until_success(
            username=data["username"],
            password=data["password"],
        )

        assert success, "H5 登录失败：未检测到 tabbar，请检查账号或网络"

        # 断言 tabbar 包含“我的”
        assert login_page._tabbar.is_visible(), "tabbar 未显示"
        assert "我的" in login_page._tabbar.inner_text(), "tabbar 中未找到'我的'"

        logger.info(f"测试通过: {data['case_name']}，已成功进入 H5 首页")

