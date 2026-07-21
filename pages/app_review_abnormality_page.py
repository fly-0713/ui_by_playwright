"""H5 异常审核页面对象

异常审核流程：
  1. 点击底部第4个 tab 进入品控页面
  2. 选择异常处理（点击第二张图片）
  3. 点击"测试异常"分类
  4. 搜索序列号
  5. 点击搜索结果中的序列号
  6. 选择异常类型
  7. 填写问题描述和临时对策
  8. 选择相关选项（单选框）
  9. 选择审核人
  10. 提交
  11. 断言出现"异常提交成功"
"""

import re

from playwright.sync_api import Page

from common.logger import logger
from pages.base_page import BasePage


class AppReviewAbnormalityPage(BasePage):
    """H5 异常审核页面对象"""

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
        # 确定按钮
        self._confirm_btn = page.get_by_text("确定")
        # 提交按钮
        self._submit_btn = page.get_by_text("提交")
        # 成功提示文本
        self._success_text = "异常提交成功"

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
            serial_number: 产品序列号
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

    def select_serial_result(self, serial_number: str):
        """点击搜索结果中的序列号

        Args:
            serial_number: 产品序列号
        """
        logger.info(f"点击搜索结果: {serial_number}")
        self.page.get_by_text(serial_number).click()
        self.page.wait_for_timeout(500)

    def select_abnormality_type(self, abnormality_type: str):
        """选择异常类型

        Args:
            abnormality_type: 异常类型，如 "操作问题"
        """
        logger.info(f"选择异常类型: {abnormality_type}")
        self.page.locator("uni-label").filter(has_text=abnormality_type).locator("uni-view").nth(1).click()
        self.page.wait_for_timeout(300)

    def fill_problem_info(self, problem_desc: str, temporary_measure: str):
        """填写问题描述和临时对策

        Args:
            problem_desc: 问题描述
            temporary_measure: 临时对策
        """
        logger.info(f"填写问题描述: {problem_desc}")
        problem_input = self.page.locator("uni-view").filter(
            has_text=re.compile(r"^问题描述请输入 \.$")
        ).get_by_role("textbox")
        problem_input.click()
        problem_input.fill(problem_desc)

        logger.info(f"填写临时对策: {temporary_measure}")
        measure_input = self.page.locator("uni-view").filter(
            has_text=re.compile(r"^临时对策请输入 \.$")
        ).get_by_role("textbox")
        measure_input.click()
        measure_input.fill(temporary_measure)
        self.page.wait_for_timeout(300)

    def select_radio_options(self):
        """选择单选框选项（多个）"""
        logger.info("选择单选框选项")
        # 第一个单选框（使用 CSS 选择器）
        self.page.locator("uni-view:nth-child(7) > .uni-forms-item__content > .uni-data-checklist > .checklist-group > uni-label:nth-child(2) > .radio__inner > .radio__inner-icon").click()
        self.page.wait_for_timeout(300)

        # 选择"量产"
        self.page.locator("uni-label").filter(has_text="量产").locator("uni-view").nth(1).click()
        self.page.wait_for_timeout(300)

        # 第二个单选框
        self.page.locator("uni-view:nth-child(4) > .uni-card__content > uni-view > .uni-forms-item__content > .uni-data-checklist > .checklist-group > uni-label:nth-child(2) > .radio__inner > .radio__inner-icon").click()
        self.page.wait_for_timeout(300)

    def select_dropdown_and_confirm(self):
        """选择下拉框并确定"""
        logger.info("选择下拉框选项")
        self.page.get_by_text("请选择").click()
        self.page.wait_for_timeout(300)

        # 点击图标选择
        self.page.locator(".uni-icons").first.click()
        self.page.wait_for_timeout(300)

        # 点击确定
        self._confirm_btn.click()
        self.page.wait_for_timeout(500)

    def add_reviewer(self, reviewer_name: str):
        """添加审核人

        Args:
            reviewer_name: 审核人姓名
        """
        logger.info(f"添加审核人: {reviewer_name}")
        # 点击"请添加"
        self.page.get_by_text("请添加").click()
        self.page.wait_for_timeout(500)

        # 点击输入框
        self.page.locator("uni-view").filter(has_text=re.compile(r"^请输入$")).nth(2).click()
        self.page.wait_for_timeout(300)

        # 搜索审核人
        self._search_box.fill(reviewer_name)
        self._search_box.press("Enter")
        self.page.wait_for_timeout(500)

        # 点击搜索结果中的审核人
        self.page.locator("uni-form").get_by_text(reviewer_name).click()
        self.page.wait_for_timeout(300)

    def submit_review(self):
        """提交审核"""
        logger.info("点击提交")
        self._submit_btn.wait_for(state="visible", timeout=self.timeout)
        self._submit_btn.click()
        self.page.wait_for_timeout(1000)

    def assert_submit_success(self):
        """断言提交成功"""
        logger.info(f"断言页面出现: {self._success_text}")
        self.page.locator("uni-page-body").get_by_text(self._success_text).wait_for(
            state="visible", timeout=self.timeout
        )
        logger.info("断言通过: 异常审核提交成功")
