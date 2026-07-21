"""H5 异常处理页面对象

异常处理流程：
  1. 点击底部第4个 tab 进入品控页面
  2. 选择异常处理（点击第二张图片）
  3. 点击"测试异常"分类
  4. 搜索序列号
  5. 点击搜索结果中的异常编号
  6. 选择处理方式（厂内维修）
  7. 填写处理标题和描述
  8. 提交
  9. 断言出现"提交成功"
"""

import re

from playwright.sync_api import Page

from common.logger import logger
from pages.base_page import BasePage


class AppHandleAbnormalityPage(BasePage):
    """H5 异常处理页面对象"""

    def __init__(self, page: Page):
        super().__init__(page)
        # 底部 tabbar 第4个图标（品控 tab）
        self._tabbar_qc_icon = page.locator("uni-tabbar").get_by_role("img").nth(3)
        # 异常处理图片（第二张）
        self._abnormality_img = page.locator("uni-page-body").get_by_role("img").nth(1)
        # 测试异常分类
        self._test_abnormality_category = page.get_by_text("测试异常")
        # 搜索框
        self._search_box = page.get_by_role("searchbox")
        # 异常编号列表项（动态，点击第一个搜索结果）
        self._first_abnormality_item = page.locator("uni-view").filter(has_text=re.compile(r"^YC\d+$")).first
        # 处理方式选项
        self._handle_type_label = None  # 动态设置
        # 处理标题输入框
        self._title_input = page.get_by_role("textbox").first
        # 处理描述输入框（第2个 uni-textarea）
        self._desc_textarea = page.locator("uni-textarea").get_by_role("textbox").nth(1)
        # 提交按钮
        self._submit_btn = page.get_by_text("提交")
        # 成功提示文本
        self._success_text = "提交成功"

    def go_to_qc_tab(self):
        """点击底部 tabbar 第4个图标，进入品控页面"""
        logger.info("点击底部第4个 tab 进入品控页面")
        self._tabbar_qc_icon.click()
        self.page.wait_for_timeout(500)

    def select_abnormality_handling(self):
        """选择异常处理（点击第二张图片）"""
        logger.info("选择异常处理（点击第二张图片）")
        self._abnormality_img.wait_for(state="visible", timeout=self.timeout)
        self._abnormality_img.click()
        self.page.wait_for_timeout(500)

    def select_test_abnormality(self):
        """点击测试异常分类"""
        logger.info("点击测试异常分类")
        self._test_abnormality_category.wait_for(state="visible", timeout=self.timeout)
        self._test_abnormality_category.click()
        self.page.wait_for_timeout(500)

    def search_serial_number(self, serial_number: str):
        """搜索序列号

        Args:
            serial_number: 产品序列号，如 "TEST20260626241"
        """
        logger.info(f"搜索序列号: {serial_number}")
        # 点击搜索框区域
        self.page.locator("uni-view").filter(has_text="请输入异常编号/产品序列号").nth(3).click()
        self.page.wait_for_timeout(300)

        # 填写序列号并回车搜索
        self._search_box.wait_for(state="visible", timeout=self.timeout)
        self._search_box.fill(serial_number)
        self._search_box.press("Enter")
        self.page.wait_for_timeout(1000)

    def select_first_abnormality(self):
        """点击搜索结果中的第一个异常编号"""
        logger.info("点击第一个异常编号")
        self._first_abnormality_item.wait_for(state="visible", timeout=self.timeout)
        self._first_abnormality_item.click()
        self.page.wait_for_timeout(500)

    def select_handle_type(self, handle_type: str):
        """选择处理方式

        Args:
            handle_type: 处理方式，如 "厂内维修"
        """
        logger.info(f"选择处理方式: {handle_type}")
        handle_locator = self.page.locator("uni-label").filter(has_text=handle_type)
        handle_locator.locator("uni-view").nth(1).click()
        self.page.wait_for_timeout(500)

    def fill_handle_info(self, title: str, description: str):
        """填写处理标题和描述

        Args:
            title: 处理标题
            description: 处理描述
        """
        logger.info(f"填写处理标题: {title}")
        self._title_input.wait_for(state="visible", timeout=self.timeout)
        self._title_input.click()
        self._title_input.fill(title)

        logger.info(f"填写处理描述: {description}")
        self._desc_textarea.wait_for(state="visible", timeout=self.timeout)
        self._desc_textarea.click()
        self._desc_textarea.fill(description)
        self.page.wait_for_timeout(300)

    def submit_handle(self):
        """提交处理"""
        logger.info("点击提交")
        self._submit_btn.wait_for(state="visible", timeout=self.timeout)
        self._submit_btn.click()
        self.page.wait_for_timeout(1000)

    def assert_submit_success(self):
        """断言提交成功"""
        logger.info(f"断言页面出现: {self._success_text}")
        self.page.locator("uni-page-body").get_by_text(self._success_text, exact=True).wait_for(
            state="visible", timeout=self.timeout
        )
        logger.info("断言通过: 异常处理提交成功")
