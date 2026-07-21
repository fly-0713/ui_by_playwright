import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from playwright.sync_api import Page

from common.logger import logger
from common.shared_data import shared_data
from datas.app_production_data import app_production_data
from pages.app_login_page import AppLoginPage
from pages.app_production_page import AppProductionPage


class TestAppProduction:
    """H5 生产报工测试用例

    前置依赖：test_order_detail 已将 serial_number 和 station_code 写入 shared_data
    流程：登录H5 → 进入生产tab → 输入工位编码 → 选产线 → 输入序列号
         → 选工序 → 完工进入下一道工序 → 填数量+上传图片
         → 选工序 → 完工处理下一件产品 → 断言弹窗出现"确定"
    """

    @pytest.mark.parametrize(
        "data",
        app_production_data,
        ids=[d["case_name"] for d in app_production_data],
    )
    def test_app_production(self, page: Page, data: dict):
        """H5 生产报工全流程"""
        logger.info(f"开始测试: {data['case_name']}")

        # 从 shared_data 获取工位编码和序列号（由 test_order_detail 写入）
        station_code = shared_data.get("station_code")
        serial_number = shared_data.get("serial_number")
        assert station_code, "shared_data 中缺少 station_code，请确保 test_order_detail 先执行"
        assert serial_number, "shared_data 中缺少 serial_number，请确保 test_order_detail 先执行"
        logger.info(f"从 shared_data 获取: 工位编码={station_code}, 序列号={serial_number}")

        # 1. 登录 H5
        login_page = AppLoginPage(page)
        login_page.navigate(data["base_url"])
        success = login_page.login_until_success(
            username=data["username"],
            password=data["password"],
        )
        assert success, "H5 登录失败：未检测到 tabbar"
        logger.info("H5 登录成功")

        production_page = AppProductionPage(page)

        # 2. 进入生产 tab
        production_page.go_to_production_tab()

        # 3. 输入工位编码并确定
        production_page.input_station_code(station_code)

        # 4. 选择作业执行
        production_page.select_production_line()

        # 5. 输入序列号并确定
        production_page.input_serial_number(serial_number)

        # 6. 选择工序
        production_page.select_process()

        # 7. 完工，进入下一道工序
        production_page.complete_and_next_process()

        # 8. 填写完工数量并上传图片
        production_page.fill_quantity_and_upload(
            quantity=data["quantity"],
            image_path=data["image_path"],
        )

        # 9. 再次选工序，完工处理下一件产品
        production_page.complete_and_next_product()

        # 10. 断言页面出现"确定"，报工流程执行完毕
        production_page.assert_confirm_visible()

        logger.info(f"测试通过: {data['case_name']}")
