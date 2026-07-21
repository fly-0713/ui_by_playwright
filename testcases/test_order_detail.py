import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from playwright.sync_api import Page

from common.config import config
from common.logger import logger
from common.shared_data import shared_data
from datas.order_detail_data import order_detail_data
from pages.login_page import LoginPage
from pages.order_detail_page import OrderDetailPage


class TestOrderDetail:
    """生产工单详情测试用例
    
    流程：搜索计划编号 → 点击详情 → 获取计划订单号 → 展开行 → 获取工位编码
    获取到的数据写入 shared_data，供后续用例使用
    """

    @pytest.mark.parametrize(
        "case",
        order_detail_data,
        ids=[d["case_name"] for d in order_detail_data],
    )
    def test_order_detail(self, page: Page, case: dict):
        """登录后搜索计划编号，进入工单详情，获取序列号和工位编码并存入 shared_data"""
        logger.info(f"开始测试: {case['case_name']}")
    
        # 1. 登录
        login_page = LoginPage(page)
        login_page.navigate(config.base_url)
        success = login_page.login_until_success(
            username=config.get_account(0)["username"],
            password=config.get_account(0)["password"],
        )
        assert success, "登录失败"
    
        detail_page = OrderDetailPage(page)
    
        # 2. 导航到生产工单页面
        detail_page.navigate_to_work_order()
    
        # 3. 展开搜索区域，搜索计划编号
        detail_page.expand_search()
        detail_page.search_plan(case["plan_no"])
    
        # 4. 点击详情按鈕进入工单详情
        detail_page.open_detail()
    
        # 5. 获取序列号
        serial_number = detail_page.get_serial_number()
        assert serial_number, "未能获取到序列号"
    
        # 6. 展开当前行
        detail_page.expand_row()
    
        # 7. 获取工位编码
        station_code = detail_page.get_station_code()
        assert station_code, "未能获取到工位编码"
    
        # 8. 将数据写入 shared_data，供后续用例使用
        shared_data["serial_number"] = serial_number
        shared_data["station_code"] = station_code
    
        logger.info(f"测试通过: 序列号={serial_number}, 工位编码={station_code}")
        logger.info("数据已写入 shared_data，后续用例可通过 shared_data['serial_number'] 和 shared_data['station_code'] 读取")
    