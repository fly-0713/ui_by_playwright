import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from playwright.sync_api import Page

from common.config import config
from common.logger import logger
from common.shared_data import shared_data
from datas.testtask_detail_data import testtask_detail_data
from pages.login_page import LoginPage
from pages.testtask_detail_page import TesttaskDetailPage


class TestTesttaskDetail:
    """测试任务详情测试用例

    前置依赖：test_order_detail 已将 serial_number 写入 shared_data
    流程：登录PC端 → 测试作业 → 测试任务 → 展开搜索 → 搜序列号
         → 点详情 → 获取测试序列号和测试工位编码
    获取到的数据写入 shared_data，供后续 H5 用例使用
    """

    @pytest.mark.parametrize(
        "case",
        testtask_detail_data,
        ids=[d["case_name"] for d in testtask_detail_data],
    )
    def test_testtask_detail(self, page: Page, case: dict):
        """登录后进入测试任务详情，获取测试序列号和工位编码并存入 shared_data"""
        logger.info(f"开始测试: {case['case_name']}")

        # 从 shared_data 获取序列号（由 test_order_detail 写入）
        serial_number = shared_data.get("serial_number")
        assert serial_number, "shared_data 中缺少 serial_number，请确保 test_order_detail 先执行"
        logger.info(f"从 shared_data 获取: 序列号={serial_number}")

        # 1. 登录
        login_page = LoginPage(page)
        login_page.navigate(config.base_url)
        success = login_page.login_until_success(
            username=config.get_account(0)["username"],
            password=config.get_account(0)["password"],
        )
        assert success, "登录失败"

        detail_page = TesttaskDetailPage(page)

        # 2. 导航到测试任务页面
        detail_page.navigate_to_test_task()

        # 3. 展开搜索区域
        detail_page.expand_search()

        # 4. 搜索产品序列号
        detail_page.search_by_serial(serial_number)

        # 5. 点击详情按钮进入详情
        detail_page.open_detail()

        # 6. 点击序列号行（触发关联操作）
        detail_page.click_serial_row(serial_number)

        # 7. 获取测试序列号
        test_serial_number = detail_page.get_test_serial_number()
        assert test_serial_number, "未能获取到测试序列号"

        # 8. 获取测试工位编码
        test_station_code = detail_page.get_test_station_code()
        assert test_station_code, "未能获取到测试工位编码"

        # 9. 将数据写入 shared_data，供后续 H5 用例使用
        shared_data["test_serial_number"] = test_serial_number
        shared_data["test_station_code"] = test_station_code

        logger.info(f"测试通过: 测试序列号={test_serial_number}, 测试工位编码={test_station_code}")
        logger.info("数据已写入 shared_data，后续用例可通过 shared_data['test_serial_number'] 和 shared_data['test_station_code'] 读取")
