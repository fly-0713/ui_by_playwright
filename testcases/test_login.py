import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from playwright.sync_api import Page

from common.logger import logger
from datas.login_data import login_data
from pages.login_page import LoginPage


class TestLogin:
    """登录测试用例

    MES 账号信息从 config.yaml 的 mes 节点读取，不依赖全局 ENV。
    """

    @pytest.mark.parametrize(
        "data",
        login_data,
        ids=[d["case_name"] for d in login_data],
    )
    def test_login(self, page: Page, data: dict):
        """自动识别验证码登录，失败则重试直到成功"""
        logger.info(f"开始测试: {data['case_name']}")
        login_page = LoginPage(page)
        login_page.navigate(data["base_url"])

        success = login_page.login_until_success(
            username=data["username"],
            password=data["password"],
        )

        assert success, f"登录失败：连续 {LoginPage.MAX_RETRY} 次验证码识别错误"
        logger.info(f"测试通过: {data['case_name']}，已成功进入首页")
