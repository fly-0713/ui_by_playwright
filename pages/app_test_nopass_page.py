"""H5 检测不通过提报异常页面对象

检测不通过流程：
  1. 点击底部第2个 tab 进入检测页面
  2. 选择测试作业（点击第一张图片）
  3. 测试工位扫描框 → 输入框 → 输入工位编码 → 确定
  4. 产品序列号扫描框 → 输入框 → 输入序列号 → 确定
  5. 点击确定进入测试执行页面
  6. 开始测试
  7. 不通过，提报异常
  8. 填写异常标题和描述 → 确定
  9. 断言出现"提示：请等待PQE接收处理"
"""

from playwright.sync_api import Page

from common.logger import logger
from pages.base_page import BasePage


class AppTestNopassPage(BasePage):
    """H5 检测不通过页面对象"""

    def __init__(self, page: Page):
        super().__init__(page)
        # 底部 tabbar 第二个图标（检测 tab）
        self._tabbar_second_icon = page.locator("uni-tabbar").get_by_role("img").nth(1)
        # 测试作业图片（第一个）
        self._test_job_img = page.locator("uni-page-body").get_by_role("img").first
        # 测试工位行右侧图标（第1个 uni-icons）
        self._station_icon = page.locator(".uni-icons").first
        # 产品序列号行右侧图标（第2个 uni-icons）
        self._serial_icon = page.locator(".uni-icons").nth(1)
        # 通用输入框
        self._input_box = page.get_by_role("textbox")
        # 确定按钮
        self._confirm_btn = page.get_by_text("确定", exact=True)
        # 开始检测按钮
        self._start_test_btn = page.get_by_text("开始检测")
        # 不通过，提报异常按钮
        self._fail_report_btn = page.get_by_text("不通过，提报异常")
        # 异常标题输入框
        self._title_input = page.locator("input")
        # 异常描述输入框
        self._desc_textarea = page.locator("textarea")
        # 提示文本
        self._hint_text = "提示：请等待PQE接收处理"

    def go_to_test_tab(self):
        """点击底部 tabbar 第二个图标，进入检测页面"""
        logger.info("点击底部第2个 tab 进入检测页面")
        self._tabbar_second_icon.click()
        self.page.wait_for_timeout(500)

    def select_test_job(self):
        """选择测试作业（点击第一张图片）"""
        logger.info("选择测试作业（点击图片）")
        self._test_job_img.wait_for(state="visible", timeout=self.timeout)
        self._test_job_img.click()
        self.page.wait_for_timeout(500)

    def input_test_station(self, station_code: str):
        """点击测试工位图标 → 填写工位编码 → 确定

        Args:
            station_code: 工位编码，如 "CGW000001"
        """
        logger.info(f"输入测试工位: {station_code}")

        # 点击测试工位图标
        self._station_icon.wait_for(state="visible", timeout=self.timeout)
        self._station_icon.click()
        self.page.wait_for_timeout(1000)

        # 填写工位编码
        self._input_box.first.wait_for(state="visible", timeout=self.timeout)
        self._input_box.first.fill(station_code)
        self.page.wait_for_timeout(300)
        # 点击确定
        logger.info("点击确定")
        self._confirm_btn.first.click()
        self.page.wait_for_timeout(500)

    def input_product_serial(self, serial_number: str):
        """点击产品序列号行 → 填写序列号 → 确定

        Args:
            serial_number: 产品序列号，如 "TEST202606231327"
        """
        logger.info(f"输入产品序列号: {serial_number}")
        # 点击产品序列号图标
        self._serial_icon.wait_for(state="visible", timeout=self.timeout)
        self._serial_icon.click()
        self.page.wait_for_timeout(1000)

        # 填写序列号
        self._input_box.first.wait_for(state="visible", timeout=self.timeout)
        self._input_box.first.fill(serial_number)
        self.page.wait_for_timeout(300)
        # 点击确定
        logger.info("点击确定")
        self._confirm_btn.first.click()
        self.page.wait_for_timeout(500)

    def enter_test_execution(self):
        """点击确定进入测试执行页面"""
        logger.info("点击确定，进入测试执行页面")
        self._confirm_btn.click()
        self.page.wait_for_timeout(2000)

    def start_test(self):
        """点击开始检测"""
        logger.info("点击: 开始检测")
        self._start_test_btn.wait_for(state="visible", timeout=self.timeout)
        self._start_test_btn.click()
        self.page.wait_for_timeout(500)

    def report_failure(self):
        """点击不通过，提报异常"""
        logger.info("点击: 不通过，提报异常")
        self._fail_report_btn.wait_for(state="visible", timeout=self.timeout)
        self._fail_report_btn.click()
        self.page.wait_for_timeout(500)

    def fill_failure_report(self, title: str, description: str):
        """填写异常标题和描述

        Args:
            title: 异常标题
            description: 异常描述
        """
        logger.info(f"填写异常标题: {title}")
        self._title_input.click()
        self._title_input.fill(title)
        logger.info(f"填写异常描述: {description}")
        self._desc_textarea.click()
        self._desc_textarea.fill(description)
        self.page.wait_for_timeout(300)

    def submit_report(self):
        """提交异常报告"""
        logger.info("点击确定，提交异常报告")
        self._confirm_btn.click()
        self.page.wait_for_timeout(1000)

    def assert_report_submitted(self):
        """断言异常报告已提交，页面出现提示信息"""
        logger.info(f"断言页面出现: {self._hint_text}")
        self.page.locator("uni-page-body").get_by_text(self._hint_text).wait_for(
            state="visible", timeout=self.timeout
        )
        logger.info("断言通过: 异常报告提交成功")
