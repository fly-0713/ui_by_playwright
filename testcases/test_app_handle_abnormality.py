import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from playwright.sync_api import Page

from common.logger import logger
from common.shared_data import shared_data
from datas.app_handle_abnormality_data import app_handle_abnormality_data
from pages.app_login_page import AppLoginPage
from pages.app_handle_abnormality_page import AppHandleAbnormalityPage


class TestAppHandleAbnormality:
    """H5 异常处理测试用例

    前置依赖：
      - test_order_detail 已将 serial_number 写入 shared_data
      - test_app_test_nopass 已提报异常，生成了异常编号
    流程：登录H5 → 进入品控tab → 选择异常处理 → 点击测试异常分类
         → 搜索序列号 → 选择异常编号 → 选择处理方式
         → 填写处理信息 → 提交 → 断言"提交成功"
    """

    @pytest.mark.parametrize(
        "data",
        app_handle_abnormality_data,
        ids=[d["case_name"] for d in app_handle_abnormality_data],
    )
    def test_app_handle_abnormality(self, page: Page, data: dict):
        """H5 异常处理全流程"""
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

        abnormality_page = AppHandleAbnormalityPage(page)

        # 2. 进入品控 tab
        abnormality_page.go_to_qc_tab()

        # 3. 选择异常处理
        abnormality_page.select_abnormality_handling()

        # 4. 点击测试异常分类
        abnormality_page.select_test_abnormality()

        # 5. 搜索序列号
        abnormality_page.search_serial_number(serial_number)

        # 6. 点击第一个异常编号
        abnormality_page.select_first_abnormality()

        # 7. 选择处理方式
        abnormality_page.select_handle_type(data["handle_type"])

        # 8. 填写处理信息
        abnormality_page.fill_handle_info(
            title=data["handle_title"],
            description=data["handle_description"],
        )

        # 9. 提交
        abnormality_page.submit_handle()

        # 10. 断言提交成功
        abnormality_page.assert_submit_success()

        logger.info(f"测试通过: {data['case_name']}")
