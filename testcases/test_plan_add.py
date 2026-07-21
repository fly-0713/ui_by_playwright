import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from playwright.sync_api import Page

from common.config import config
from common.logger import logger
from datas.plan_add_data import plan_add_data
from pages.login_page import LoginPage
from pages.plan_add_page import PlanAddPage


class TestPlanAdd:
    """计划新增测试用例"""

    @pytest.mark.parametrize(
        "case",
        plan_add_data,
        ids=[d["case_name"] for d in plan_add_data],
    )
    def test_plan_add(self, page: Page, case: dict):
        """登录后新增计划，验证计划编号出现在列表中"""
        logger.info(f"开始测试: {case['case_name']}")

        # 1. 登录
        login_page = LoginPage(page)
        login_page.navigate(config.base_url)
        success = login_page.login_until_success(
            username=config.get_account(0)["username"],
            password=config.get_account(0)["password"],
        )
        assert success, "登录失败"

        # 2. 导航到计划订单页面
        plan_add_page = PlanAddPage(page)
        plan_add_page.navigate_to_plan_add()

        # 3. 新增计划
        plan_add_page.add_plan(
            material_code=case["material_code"],
            quantity=case["quantity"],
            plan_no=case["plan_no"],
            erp_order=case["erp_order"],
            start_date_day=case["start_date_day"],
            end_date_day=case["end_date_day"],
        )

        # 4. 断言计划编号出现在列表中
        plan_nos = plan_add_page.get_plan_nos_in_table()
        assert case["plan_no"] in plan_nos, (
            f"新增计划编号 '{case['plan_no']}' 未出现在列表中，实际列表: {plan_nos}"
        )
        logger.info(f"测试通过: 计划编号 '{case['plan_no']}' 已成功新增并出现在列表中")