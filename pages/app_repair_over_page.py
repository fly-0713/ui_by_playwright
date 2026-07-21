"""H5 维修完成页面对象

维修完成流程：
  1. 点击底部第3个 tab 进入维修页面
  2. 选择维修工单（点击第一张图片）
  3. 搜索序列号
  4. 点击搜索结果中的序列号
  5. 开始维修
  6. 填写故障现象描述
  7. 添加故障记录（选择故障位置、代码、部件、原因）
  8. 选择故障类型
  9. 填写处理描述
  10. 选择维修结果
  11. 完成维修
  12. 断言出现"维修已完成"
"""

import re

from playwright.sync_api import Page

from common.logger import logger
from pages.base_page import BasePage


class AppRepairOverPage(BasePage):
    """H5 维修完成页面对象"""

    def __init__(self, page: Page):
        super().__init__(page)
        # 底部 tabbar 第3个图标（维修 tab）
        self._tabbar_repair_icon = page.locator("uni-tabbar").get_by_role("img").nth(2)
        # 维修工单图片（第一张）
        self._repair_order_img = page.locator("uni-page-body").get_by_role("img").first
        # 搜索框
        self._search_box = page.get_by_role("searchbox")
        # 搜索按钮
        self._search_btn = page.get_by_text("搜索")
        # 开始维修按钮
        self._start_repair_btn = page.get_by_text("开始维修")
        # 故障现象描述输入框
        self._fault_desc_input = page.locator("uni-view").filter(
            has_text=re.compile(r"^\*故障现象描述请输入 \.$")
        ).get_by_role("textbox")
        # 添加故障记录按钮
        self._add_fault_btn = page.locator("uni-button").filter(has_text="添加")
        # 确定按钮
        self._confirm_btn = page.get_by_text("确定")
        # 完成维修按钮
        self._complete_repair_btn = page.get_by_text("完成维修")
        # 成功提示文本
        self._success_text = "维修已完成"

    def go_to_repair_tab(self):
        """点击底部 tabbar 第3个图标，进入维修页面"""
        logger.info("点击底部第3个 tab 进入维修页面")
        self._tabbar_repair_icon.click()
        self.page.wait_for_timeout(500)

    def select_repair_order(self):
        """选择维修工单（点击第一张图片）"""
        logger.info("选择维修工单（点击第一张图片）")
        self._repair_order_img.wait_for(state="visible", timeout=self.timeout)
        self._repair_order_img.click()
        self.page.wait_for_timeout(500)

    def search_serial_number(self, serial_number: str):
        """搜索序列号

        Args:
            serial_number: 产品序列号
        """
        logger.info(f"搜索序列号: {serial_number}")
        # 点击搜索框区域
        self.page.locator("uni-view").filter(has_text="请输入产品序列号").nth(4).click()
        self.page.wait_for_timeout(300)

        # 填写序列号并点击搜索
        self._search_box.wait_for(state="visible", timeout=self.timeout)
        self._search_box.fill(serial_number)
        self._search_btn.click()
        self.page.wait_for_timeout(1000)

    def select_serial_result(self, serial_number: str):
        """点击搜索结果中的序列号

        Args:
            serial_number: 产品序列号
        """
        logger.info(f"点击搜索结果: {serial_number}")
        self.page.get_by_text(serial_number).click()
        self.page.wait_for_timeout(500)

    def start_repair(self):
        """点击开始维修"""
        logger.info("点击: 开始维修")
        self._start_repair_btn.wait_for(state="visible", timeout=self.timeout)
        self._start_repair_btn.click()
        self.page.wait_for_timeout(500)

    def fill_fault_description(self, description: str):
        """填写故障现象描述

        Args:
            description: 故障描述
        """
        logger.info(f"填写故障现象描述: {description}")
        self._fault_desc_input.wait_for(state="visible", timeout=self.timeout)
        self._fault_desc_input.click()
        self._fault_desc_input.fill(description)
        self.page.wait_for_timeout(300)

    def add_fault_record(
        self,
        position: str,
        code: str,
        part_category: str,
        part: str,
        reason: str,
    ):
        """添加故障记录

        Args:
            position: 故障位置，如 "关节一"
            code: 故障代码，如 "11R"
            part_category: 故障部件分类，如 "机器人产品"
            part: 故障部件，如 "ABZ编码器"
            reason: 故障原因，如 "码盘脏污-zh"
        """
        logger.info("添加故障记录")

        # 点击添加按钮
        self._add_fault_btn.click()
        self.page.wait_for_timeout(500)

        # 选择故障位置
        self.page.get_by_text("请选择").first.click()
        self.page.get_by_text(position).click()
        self.page.wait_for_timeout(300)

        # 选择故障代码
        self.page.get_by_text(code).click()
        self.page.wait_for_timeout(300)

        # 选择故障部件
        self.page.get_by_text("请选择故障部件").click()
        self.page.get_by_text(part_category).click()
        self.page.get_by_text(part).click()
        self.page.wait_for_timeout(300)

        # 选择故障原因
        self.page.get_by_text("请选择").click()
        self.page.get_by_text(reason).click()
        self.page.wait_for_timeout(300)

        # 点击确定（两次）
        self._confirm_btn.first.click()
        self.page.wait_for_timeout(500)
        self._confirm_btn.click()
        self.page.wait_for_timeout(500)

    def select_fault_type(self, fault_type: str):
        """选择故障类型

        Args:
            fault_type: 故障类型，如 "A01-作业不良"
        """
        logger.info(f"选择故障类型: {fault_type}")
        self.page.locator("uni-label").filter(has_text=fault_type).locator("uni-view").nth(1).click()
        self.page.wait_for_timeout(300)

    def fill_handle_description(self, description: str):
        """填写处理描述

        Args:
            description: 处理描述
        """
        logger.info(f"填写处理描述: {description}")
        textarea = self.page.locator("uni-textarea").filter(has_text="请输入 .").get_by_role("textbox")
        textarea.click()
        textarea.fill(description)
        self.page.wait_for_timeout(300)

    def select_repair_result(self):
        """选择维修结果（点击 radio group）"""
        logger.info("选择维修结果")
        self.page.locator("uni-radio-group div").nth(1).click()
        self.page.wait_for_timeout(300)

    def complete_repair(self):
        """完成维修"""
        logger.info("点击: 完成维修")
        self._complete_repair_btn.wait_for(state="visible", timeout=self.timeout)
        self._complete_repair_btn.click()
        self.page.wait_for_timeout(500)

        # 确认弹窗
        logger.info("点击确定确认")
        self._confirm_btn.click()
        self.page.wait_for_timeout(1000)

    def assert_repair_complete(self):
        """断言维修已完成"""
        logger.info(f"断言页面出现: {self._success_text}")
        self.page.locator("uni-page-body").get_by_text(self._success_text).wait_for(
            state="visible", timeout=self.timeout
        )
        logger.info("断言通过: 维修已完成")
