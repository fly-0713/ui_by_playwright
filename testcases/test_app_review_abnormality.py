import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from playwright.sync_api import Page

from common.logger import logger
from common.shared_data import shared_data
from datas.app_review_abnormality_data import app_review_abnormality_data
from pages.app_login_page import AppLoginPage
from pages.app_review_abnormality_page import AppReviewAbnormalityPage


class TestAppReviewAbnormality:
    """H5 异常审核测试用例

    前置依赖：
      - test_order_detail 已将 serial_number 写入 shared_data
      - test_app_test_nopass 已提报异常
    流程：登录H5 → 进入品控tab → 选择异常处理 → 测试异常分类
         → 搜索序列号 → 选异常编号 → 选异常类型 → 填写问题描述和临时对策
         → 选择相关选项 → 选择审核人 → 提交 → 断言"异常提交成功"
    """

    @pytest.mark.parametrize(
        "data",
        app_review_abnormality_data,
        ids=[d["case_name"] for d in app_review_abnormality_data],
    )
    def test_app_review_abnormality(self, page: Page, data: dict):
        """H5 异常审核全流程"""
        logger.info(f"开始测试: {data['case_name']}")

        # 从 shared_data 获取序列号（由 test_order_detail 写入）
        serial_number = shared_data.get("serial_number")
        assert serial_number, "shared_data 中缺少 serial_number，请确保 test_order_detail 先执行"
        logger.info(f"从 shared_data 获取: 序列号={serial_number}")

        # 1. 登录 H5
        login_page = AppLoginPage(page)
        login_page.navigate(data["base_url"])
        success = login_page.login_until_success(
            username=data["username"],
            password=data["password"],
        )
        assert success, "H5 登录失败：未检测到 tabbar"
        logger.info("H5 登录成功")

        review_page = AppReviewAbnormalityPage(page)

        # 2. 进入品控 tab
        review_page.go_to_qc_tab()

        # 3. 选择异常处理
        review_page.select_abnormality_handling()

        # 4. 点击测试异常分类
        review_page.select_test_abnormality()

        # 5. 搜索序列号
        review_page.search_serial_number(serial_number)

        # 6. 点击搜索结果
        review_page.select_serial_result(serial_number)

        # 7. 选择异常类型
        review_page.select_abnormality_type(data["abnormality_type"])

        # 8. 填写问题描述和临时对策
        review_page.fill_problem_info(
            problem_desc=data["problem_description"],
            temporary_measure=data["temporary_measure"],
        )

        # 9. 选择单选框选项
        review_page.select_radio_options()

        # 10. 选择下拉框并确定
        review_page.select_dropdown_and_confirm()

        # 11. 添加审核人
        review_page.add_reviewer(data["reviewer_name"])

        # 12. 提交审核
        review_page.submit_review()

        # 13. 断言提交成功
        review_page.assert_submit_success()

        logger.info(f"测试通过: {data['case_name']}")
