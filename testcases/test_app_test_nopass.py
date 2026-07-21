import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from playwright.sync_api import Page

from common.logger import logger
from common.shared_data import shared_data
from datas.app_test_nopass_data import app_test_nopass_data
from pages.app_login_page import AppLoginPage
from pages.app_test_nopass_page import AppTestNopassPage


class TestAppTestNopass:
    """H5 检测不通过提报异常测试用例

    前置依赖：test_order_detail 已将 station_code 和 serial_number 写入 shared_data
    流程：登录H5 → 检测tab → 选测试作业 → 输工位编码 → 输序列号
         → 确定进入测试页 → 开始测试 → 不通过提报异常
         → 填写标题/描述 → 确定 → 断言PQE等待提示
    """

    @pytest.mark.parametrize(
        "data",
        app_test_nopass_data,
        ids=[d["case_name"] for d in app_test_nopass_data],
    )
    def test_app_test_nopass(self, page: Page, data: dict):
        """H5 检测不通过提报异常全流程"""
        logger.info(f"开始测试: {data['case_name']}")

        # 从 shared_data 获取测试工位编码和测试序列号（由 test_testtask_detail 写入）
        station_code = shared_data.get("test_station_code")
        serial_number = shared_data.get("test_serial_number")
        assert station_code, "shared_data 中缺少 test_station_code，请确保 test_testtask_detail 先执行"
        assert serial_number, "shared_data 中缺少 test_serial_number，请确保 test_testtask_detail 先执行"
        logger.info(f"从 shared_data 获取: 测试工位编码={station_code}, 测试序列号={serial_number}")

        # 1. 登录 H5
        login_page = AppLoginPage(page)
        login_page.navigate(data["base_url"])
        success = login_page.login_until_success(
            username=data["username"],
            password=data["password"],
        )
        assert success, "H5 登录失败：未检测到 tabbar"
        logger.info("H5 登录成功")

        nopass_page = AppTestNopassPage(page)

        # 2. 进入检测 tab
        nopass_page.go_to_test_tab()

        # 3. 选择测试作业（点击第一张图片）
        nopass_page.select_test_job()

        # 4. 输入测试工位编码
        nopass_page.input_test_station(station_code)

        # 5. 输入产品序列号
        nopass_page.input_product_serial(serial_number)

        # 6. 点击确定进入测试执行页面
        nopass_page.enter_test_execution()

        # 7. 开始测试
        nopass_page.start_test()

        # 8. 不通过，提报异常
        nopass_page.report_failure()

        # 9. 填写异常标题和描述
        nopass_page.fill_failure_report(
            title=data["fail_title"],
            description=data["fail_description"],
        )

        # 10. 提交异常报告
        nopass_page.submit_report()

        # 11. 断言页面出现 PQE 等待处理提示
        nopass_page.assert_report_submitted()

        logger.info(f"测试通过: {data['case_name']}")
