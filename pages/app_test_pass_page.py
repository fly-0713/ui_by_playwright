"""H5 检测通过页面对象

检测通过流程：
  1. 点击底部第2个 tab 进入测试页面
  2. 选择检测工单（点击第一张图片）
  3. 输入测试工位并确定
  4. 输入产品序列号并确定
  5. 开始检测
  6. 上传图片
  7. 通过，进入下一道工序
  8. 再次开始检测
  9. 选择 OK
  10. 上传图片（多张）
  11. 通过，进入下一道工序
  12. 断言出现"已测试"
"""

import os

from playwright.sync_api import Page

from common.logger import logger
from pages.base_page import BasePage


class AppTestPassPage(BasePage):
    """H5 检测通过页面对象"""

    def __init__(self, page: Page):
        super().__init__(page)
        # 底部 tabbar 第2个图标（测试 tab）
        self._tabbar_test_icon = page.locator("uni-tabbar").get_by_role("img").nth(1)
        # 检测工单图片（第一张）
        self._test_order_img = page.locator("uni-page-body").get_by_role("img").first
        # 测试工位图标（第一个 .uni-icons）
        self._station_icon = page.locator(".uni-icons").first
        # 序列号图标（第二个 .uni-icons，在 nth-child(3) 中）
        self._serial_icon = page.locator("uni-view:nth-child(3) > .uni-icons")
        # 输入框
        self._input_box = page.get_by_role("textbox")
        # 确定按钮（span）
        self._confirm_span = page.locator("span").filter(has_text="确定")
        # 确定按钮（通用）
        self._confirm_btn = page.get_by_text("确定")
        # 开始检测按钮
        self._start_test_btn = page.get_by_text("开始检测")
        # 文件上传输入框
        self._file_input = page.locator(".uni-uploader__input").first
        # 通过，进入下一道工序按钮
        self._pass_next_btn = page.get_by_text("通过，进入下一道工序")
        # OK 选项
        self._ok_label = page.locator("uni-label").filter(has_text="OK").locator("uni-view").nth(1)
        # 成功提示文本
        self._success_text = "已测试"

    def go_to_test_tab(self):
        """点击底部 tabbar 第2个图标，进入测试页面"""
        logger.info("点击底部第2个 tab 进入测试页面")
        self._tabbar_test_icon.click()
        self.page.wait_for_timeout(500)

    def select_test_order(self):
        """选择检测工单（点击第一张图片）"""
        logger.info("选择检测工单（点击第一张图片）")
        self._test_order_img.wait_for(state="visible", timeout=self.timeout)
        self._test_order_img.click()
        self.page.wait_for_timeout(500)

    def input_station_code(self, station_code: str):
        """输入测试工位并确定

        Args:
            station_code: 工位编码
        """
        logger.info(f"点击测试工位图标")
        self._station_icon.click()
        self.page.wait_for_timeout(500)

        logger.info(f"填写工位编码: {station_code}")
        self._input_box.wait_for(state="visible", timeout=self.timeout)
        self._input_box.fill(station_code)

        logger.info("点击确定")
        self._confirm_span.click()
        self.page.wait_for_timeout(500)

    def input_serial_number(self, serial_number: str):
        """输入产品序列号并确定

        Args:
            serial_number: 产品序列号
        """
        logger.info(f"点击序列号图标")
        self._serial_icon.click()
        self.page.wait_for_timeout(500)

        logger.info(f"填写序列号: {serial_number}")
        self._input_box.click()
        self._input_box.fill(serial_number)

        logger.info("点击确定")
        self._confirm_span.click()
        self.page.wait_for_timeout(500)

        # 再次点击确定（关闭确认框）
        logger.info("点击确定（关闭确认框）")
        self._confirm_btn.click()
        self.page.wait_for_timeout(500)

    def start_test(self):
        """点击开始检测"""
        logger.info("点击: 开始检测")
        self._start_test_btn.wait_for(state="visible", timeout=self.timeout)
        self._start_test_btn.click()
        self.page.wait_for_timeout(500)

    def upload_image(self, image_path: str):
        """上传图片

        Args:
            image_path: 图片文件路径（相对或绝对）
        """
        # 如果是相对路径，转换为绝对路径
        if not os.path.isabs(image_path):
            abs_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                image_path,
            )
        else:
            abs_path = image_path

        if not os.path.exists(abs_path):
            logger.warning(f"图片文件不存在，跳过上传: {abs_path}")
            return

        logger.info(f"上传图片: {abs_path}")
        # 等待上传输入框可见
        self._file_input.wait_for(state="visible", timeout=self.timeout)
        with self.page.expect_file_chooser(timeout=10000) as fc_info:
            self._file_input.click()
        file_chooser = fc_info.value
        file_chooser.set_files(abs_path)
        self.page.wait_for_timeout(1000)

    def pass_and_next(self):
        """点击通过，进入下一道工序"""
        logger.info("点击: 通过，进入下一道工序")
        self._pass_next_btn.wait_for(state="visible", timeout=self.timeout)
        self._pass_next_btn.click()
        self.page.wait_for_timeout(1000)

    def select_ok(self):
        """选择 OK 选项"""
        logger.info("选择: OK")
        self._ok_label.click()
        self.page.wait_for_timeout(300)

    def assert_tested(self):
        """断言页面出现"已测试" """
        logger.info(f"断言页面出现: {self._success_text}")
        self.page.locator("uni-page-body").get_by_text(self._success_text).wait_for(
            state="visible", timeout=self.timeout
        )
        logger.info("断言通过: 检测完成，已测试")
