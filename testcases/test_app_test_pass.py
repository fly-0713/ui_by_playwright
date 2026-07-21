import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from playwright.sync_api import Page

from common.logger import logger
from common.shared_data import shared_data
from datas.app_test_pass_data import app_test_pass_data
from pages.app_login_page import AppLoginPage
from pages.app_test_pass_page import AppTestPassPage


class TestAppTestPass:
    """H5 检测通过测试用例

    前置依赖：test_testtask_detail 已将 test_serial_number 和 test_station_code 写入 shared_data
    流程：登录H5 → 进入测试tab → 选择检测工单 → 输入工位编码
         → 输入序列号 → 开始检测 → 上传图片 → 通过进入下一道工序
         → 再次开始检测 → 选择OK → 上传图片 → 通过进入下一道工序
         → 断言"已测试"
    """

    @pytest.mark.parametrize(
        "data",
        app_test_pass_data,
        ids=[d["case_name"] for d in app_test_pass_data],
    )
    def test_app_test_pass(self, page: Page, data: dict):
        """H5 检测通过全流程"""
        logger.info(f"开始测试: {data['case_name']}")

        # 从 shared_data 获取测试工位编码和序列号（由 test_testtask_detail 写入）
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

        test_page = AppTestPassPage(page)

        # 2. 进入测试 tab
        test_page.go_to_test_tab()

        # 3. 选择检测工单
        test_page.select_test_order()

        # 4. 输入工位编码并确定
        test_page.input_station_code(station_code)

        # 5. 输入序列号并确定
        test_page.input_serial_number(serial_number)

        # 6. 开始检测（第一轮）
        test_page.start_test()

        # 7. 上传图片
        test_page.upload_image(data["image_path"])

        # 8. 通过，进入下一道工序
        test_page.pass_and_next()

        # 9. 开始检测（第二轮）
        test_page.start_test()

        # 10. 选择 OK
        test_page.select_ok()

        # 11. 上传图片（多张）
        test_page.upload_image(data["image_path"])
        test_page.upload_image(data["image_path"])

        # 12. 通过，进入下一道工序
        test_page.pass_and_next()

        # 13. 断言"已测试"
        test_page.assert_tested()

        logger.info(f"测试通过: {data['case_name']}")
