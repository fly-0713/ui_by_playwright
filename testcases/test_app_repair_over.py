import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from playwright.sync_api import Page

from common.logger import logger
from common.shared_data import shared_data
from datas.app_repair_over_data import app_repair_over_data
from pages.app_login_page import AppLoginPage
from pages.app_repair_over_page import AppRepairOverPage


class TestAppRepairOver:
    """H5 维修完成测试用例

    前置依赖：
      - test_order_detail 已将 serial_number 写入 shared_data
      - test_app_test_nopass 已提报异常，产生了维修工单
    流程：登录H5 → 进入维修tab → 选择维修工单 → 搜索序列号
         → 开始维修 → 填写故障描述 → 添加故障记录 → 选择故障类型
         → 填写处理描述 → 完成维修 → 断言"维修已完成"
    """

    @pytest.mark.parametrize(
        "data",
        app_repair_over_data,
        ids=[d["case_name"] for d in app_repair_over_data],
    )
    def test_app_repair_over(self, page: Page, data: dict):
        """H5 维修完成全流程"""
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

        repair_page = AppRepairOverPage(page)

        # 2. 进入维修 tab
        repair_page.go_to_repair_tab()

        # 3. 选择维修工单
        repair_page.select_repair_order()

        # 4. 搜索序列号
        repair_page.search_serial_number(serial_number)

        # 5. 点击搜索结果
        repair_page.select_serial_result(serial_number)

        # 6. 开始维修
        repair_page.start_repair()

        # 7. 填写故障现象描述
        repair_page.fill_fault_description(data["fault_description"])

        # 8. 添加故障记录
        repair_page.add_fault_record(
            position=data["fault_position"],
            code=data["fault_code"],
            part_category=data["fault_part_category"],
            part=data["fault_part"],
            reason=data["fault_reason"],
        )

        # 9. 选择故障类型
        repair_page.select_fault_type(data["fault_type"])

        # 10. 填写处理描述
        repair_page.fill_handle_description(data["handle_description"])

        # 11. 选择维修结果
        repair_page.select_repair_result()

        # 12. 完成维修
        repair_page.complete_repair()

        # 13. 断言维修完成
        repair_page.assert_repair_complete()

        logger.info(f"测试通过: {data['case_name']}")
