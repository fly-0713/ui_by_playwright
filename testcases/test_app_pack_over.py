import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from playwright.sync_api import Page

from common.logger import logger
from common.shared_data import shared_data
from datas.app_pack_over_data import app_pack_over_data
from pages.app_login_page import AppLoginPage
from pages.app_pack_over_page import AppPackOverPage


class TestAppPackOver:
    """H5 包装完成测试用例

    前置依赖：test_pack_detail 已将 pack_serial_number 和 pack_station_code 写入 shared_data
    流程：登录H5 → 进入测试tab → 选择包装工单 → 输入工位编码
         → 输入序列号 → 开始作业 → 上传图片 → 合格进入下一道工序
         → 再次开始作业 → 上传图片 → 合格进入下一道工序
         → 断言"该工位的所有工序全部完成"
    """

    @pytest.mark.parametrize(
        "data",
        app_pack_over_data,
        ids=[d["case_name"] for d in app_pack_over_data],
    )
    def test_app_pack_over(self, page: Page, data: dict):
        """H5 包装完成全流程"""
        logger.info(f"开始测试: {data['case_name']}")

        # 从 shared_data 获取包装工位编码和序列号（由 test_pack_detail 写入）
        station_code = shared_data.get("pack_station_code")
        serial_number = shared_data.get("pack_serial_number")
        assert station_code, "shared_data 中缺少 pack_station_code，请确保 test_pack_detail 先执行"
        assert serial_number, "shared_data 中缺少 pack_serial_number，请确保 test_pack_detail 先执行"
        logger.info(f"从 shared_data 获取: 包装工位编码={station_code}, 包装序列号={serial_number}")

        # 1. 登录 H5
        login_page = AppLoginPage(page)
        login_page.navigate(data["base_url"])
        success = login_page.login_until_success(
            username=data["username"],
            password=data["password"],
        )
        assert success, "H5 登录失败：未检测到 tabbar"
        logger.info("H5 登录成功")

        pack_page = AppPackOverPage(page)

        # 2. 进入测试 tab
        pack_page.go_to_test_tab()

        # 3. 选择包装工单
        pack_page.select_pack_order()

        # 4. 输入工位编码并确定
        pack_page.input_station_code(station_code)

        # 5. 输入序列号并确定
        pack_page.input_serial_number(serial_number)

        # 6. 开始作业（第一轮）
        pack_page.start_work()

        # 7. 上传图片
        pack_page.upload_image(data["image_path"])

        # 8. 合格，进入下一道工序
        pack_page.pass_and_next()

        # 9. 开始作业（第二轮）
        pack_page.start_work()

        # 10. 上传图片（多张）
        pack_page.upload_image(data["image_path"])
        pack_page.upload_image(data["image_path"], index=1)

        # 11. 合格，进入下一道工序
        pack_page.pass_and_next()

        # 12. 断言"该工位的所有工序全部完成"
        pack_page.assert_all_complete()

        logger.info(f"测试通过: {data['case_name']}")
