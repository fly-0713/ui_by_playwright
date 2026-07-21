import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from playwright.sync_api import Page

from common.config import config
from common.logger import logger
from datas.order_send_data import order_send_data
from pages.login_page import LoginPage
from pages.order_send_page import OrderSendPage


class TestOrderSend:
    """生产工单派工测试用例"""

    @pytest.mark.parametrize(
        "case",
        order_send_data,
        ids=[d["case_name"] for d in order_send_data],
    )
    def test_order_send(self, page: Page, case: dict):
        """登录后进入生产工单，完成包装作业派工，验证状态为待生产"""
        logger.info(f"开始测试: {case['case_name']}")

        # 1. 登录
        login_page = LoginPage(page)
        login_page.navigate(config.base_url)
        success = login_page.login_until_success(
            username=config.get_account(0)["username"],
            password=config.get_account(0)["password"],
        )
        assert success, "登录失败"

        order_send_page = OrderSendPage(page)

        # 2. 导航到生产工单页面
        order_send_page.navigate_to_work_order()

        # 3. 点击展开按钮，等待计划编号搜索框出现
        order_send_page.expand_search()

        # 4. 搜索计划编号
        order_send_page.search_plan(case["plan_no"])

        # 5. 点击派工按钮
        order_send_page.click_dispatch()

        # 6. 填写派工表单（产线、产线负责人、包装工艺）
        order_send_page.fill_dispatch_form(
            production_line=case["production_line"],
            line_leader=case["line_leader"],
            packing_process=case["packing_process"],
        )

        # 7. 点击确认
        order_send_page.confirm_dispatch()

        # 8. 点击确认派工（最终提交）
        order_send_page.confirm_dispatch_send()

        # 9. 验证状态为"待生产"或"生产中"
        status = order_send_page.get_row_status(case["plan_no"])
        expected = case["expected_status"]
        assert any(s in status for s in expected), (
            f"计划 '{case['plan_no']}' 状态应为 {expected}，实际: '{status}'"
        )
        logger.info(f"测试通过: 计划 '{case['plan_no']}' 派工成功，状态: {status}")
