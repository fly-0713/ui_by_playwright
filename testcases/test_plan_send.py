import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from playwright.sync_api import Page

from common.config import config
from common.logger import logger
from common.shared_data import shared_data
from datas.plan_send_data import plan_send_data
from pages.login_page import LoginPage
from pages.plan_send_page import PlanSendPage


class TestPlanSend:
    """计划下发测试用例"""

    @pytest.mark.parametrize(
        "case",
        plan_send_data,
        ids=[d["case_name"] for d in plan_send_data],
    )
    def test_plan_send(self, page: Page, case: dict):
        """登录后搜索计划编号，执行下发，验证状态变为下发中"""
        logger.info(f"开始测试: {case['case_name']}")

        # 从 shared_data 读取 plan_add 用例写入的计划编号，实现跨用例共享
        case["plan_no"] = shared_data.get("plan_no", case["plan_no"])
        logger.info(f"使用计划编号: {case['plan_no']}")

        # 1. 登录
        login_page = LoginPage(page)
        login_page.navigate(config.base_url)
        success = login_page.login_until_success(
            username=config.get_account(0)["username"],
            password=config.get_account(0)["password"],
        )
        assert success, "登录失败"

        # 2. 导航到计划订单页面
        plan_send_page = PlanSendPage(page)
        plan_send_page.navigate_to_order()

        # 3. 搜索计划编号
        plan_send_page.search_plan(case["plan_no"])

        # 4. 点击下发
        plan_send_page.click_send()

        # 5. 填写下发表单（排程日期 + 下发数量）
        plan_send_page.fill_send_form(
            send_quantity=case["send_quantity"],
            start_date_day=case["start_date_day"],
            end_date_day=case["end_date_day"],
        )

        # 6. 确认下发
        plan_send_page.confirm_send()

        # 7. 验证状态变为“下发中”或“已下发”
        status = plan_send_page.get_plan_status(case["plan_no"])
        expected = case["expected_status"]  # list
        assert any(s in status for s in expected), (
            f"计划 '{case['plan_no']}' 状态应为 {expected}，实际: '{status}'"
        )
        logger.info(f"测试通过: 计划 '{case['plan_no']}' 已成功下发，状态: {status}")
        