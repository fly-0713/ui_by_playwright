import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from playwright.sync_api import Page

from common.config import config
from common.logger import logger
from common.shared_data import shared_data
from datas.pack_detail_data import pack_detail_data
from pages.login_page import LoginPage
from pages.pack_detail_page import PackDetailPage


class TestPackDetail:
    """包装任务详情测试用例

    前置依赖：test_order_detail 已将 serial_number 写入 shared_data
    流程：登录PC端 → 包装作业 → 包装任务 → 展开搜索 → 搜序列号
         → 点详情 → 获取包装序列号和包装工位编码
    获取到的数据写入 shared_data，供后续用例使用
    """

    @pytest.mark.parametrize(
        "case",
        pack_detail_data,
        ids=[d["case_name"] for d in pack_detail_data],
    )
    def test_pack_detail(self, page: Page, case: dict):
        """登录后进入包装任务详情，获取包装序列号和工位编码并存入 shared_data"""
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

        detail_page = PackDetailPage(page)

        # 2. 导航到包装任务页面
        detail_page.navigate_to_pack_task()

        # 3. 展开搜索区域
        detail_page.expand_search()

        # 4. 搜索产品序列号
        detail_page.search_by_serial(serial_number)

        # 5. 点击详情按钮进入详情
        detail_page.open_detail()

        # 6. 点击序列号行（触发关联操作）
        detail_page.click_serial_row(serial_number)

        # 7. 获取包装序列号
        pack_serial_number = detail_page.get_pack_serial_number()
        assert pack_serial_number, "未能获取到包装序列号"

        # 8. 获取包装工位编码
        pack_station_code = detail_page.get_pack_station_code()
        assert pack_station_code, "未能获取到包装工位编码"

        # 9. 将数据写入 shared_data，供后续用例使用
        shared_data["pack_serial_number"] = pack_serial_number
        shared_data["pack_station_code"] = pack_station_code

        logger.info(f"测试通过: 包装序列号={pack_serial_number}, 包装工位编码={pack_station_code}")
        logger.info("数据已写入 shared_data，后续用例可通过 shared_data['pack_serial_number'] 和 shared_data['pack_station_code'] 读取")
