"""H5 包装完成页面对象

包装完成流程：
  1. 点击底部第2个 tab 进入测试页面
  2. 选择包装工单（点击第二张图片）
  3. 输入包装工位并确定
  4. 输入包装序列号并确定
  5. 开始作业
  6. 上传图片
  7. 合格，进入下一道工序
  8. 再次开始作业
  9. 上传图片（多张）
  10. 合格，进入下一道工序
  11. 断言"该工位的所有工序全部完成"
"""

import os

from playwright.sync_api import Page

from common.logger import logger
from pages.base_page import BasePage


class AppPackOverPage(BasePage):
    """H5 包装完成页面对象"""

    def __init__(self, page: Page):
        super().__init__(page)
        # 底部 tabbar 第2个图标（测试 tab）
        self._tabbar_test_icon = page.locator("uni-tabbar").get_by_role("img").nth(1)
        # 包装工单图片（第二张）
        self._pack_order_img = page.locator("uni-page-body").get_by_role("img").nth(1)
        # 包装工位图标（第一个 .uni-icons）
        self._station_icon = page.locator(".uni-icons").first
        # 序列号图标
        self._serial_icon = page.locator("uni-view:nth-child(2) > uni-view:nth-child(4) > .uni-icons")
        # 输入框
        self._input_box = page.get_by_role("textbox")
        # 确定按钮（span）
        self._confirm_span = page.locator("span").filter(has_text="确定")
        # 确定按钮（通用）
        self._confirm_btn = page.get_by_text("确定")
        # 开始作业按钮
        self._start_work_btn = page.get_by_text("开始作业")
        # 文件上传输入框（第一个）
        self._file_input = page.locator(".uni-uploader__input")
        # 合格，进入下一道工序按钮
        self._pass_next_btn = page.get_by_text("合格，进入下一道工序")
        # 成功提示文本
        self._success_text = "该工位的所有工序全部完成"

    def go_to_test_tab(self):
        """点击底部 tabbar 第2个图标，进入测试页面"""
        logger.info("点击底部第2个 tab 进入测试页面")
        self._tabbar_test_icon.click()
        self.page.wait_for_timeout(500)

    def select_pack_order(self):
        """选择包装工单（点击第二张图片）"""
        logger.info("选择包装工单（点击第二张图片）")
        self._pack_order_img.wait_for(state="visible", timeout=self.timeout)
        self._pack_order_img.click()
        self.page.wait_for_timeout(500)

    def input_station_code(self, station_code: str):
        """输入包装工位并确定

        Args:
            station_code: 工位编码
        """
        logger.info(f"点击包装工位图标")
        self._station_icon.click()
        self.page.wait_for_timeout(500)

        logger.info(f"填写工位编码: {station_code}")
        self._input_box.wait_for(state="visible", timeout=self.timeout)
        self._input_box.fill(station_code)

        logger.info("点击确定")
        self._confirm_span.click()
        self.page.wait_for_timeout(500)

    def input_serial_number(self, serial_number: str):
        """输入包装序列号并确定

        Args:
            serial_number: 包装序列号
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

    def start_work(self):
        """点击开始作业"""
        logger.info("点击: 开始作业")
        self._start_work_btn.wait_for(state="visible", timeout=15000)  # 增加超时时间，等待页面加载
        self._start_work_btn.click()
        self.page.wait_for_timeout(500)

    def upload_image(self, image_path: str, index: int = 0):
        """上传图片

        Args:
            image_path: 图片文件路径（相对或绝对）
            index: 上传输入框索引
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
        file_input = self._file_input.nth(index) if index > 0 else self._file_input.first
        # 等待上传输入框可见
        file_input.wait_for(state="visible", timeout=self.timeout)
        with self.page.expect_file_chooser(timeout=10000) as fc_info:
            file_input.click()
        file_chooser = fc_info.value
        file_chooser.set_files(abs_path)
        self.page.wait_for_timeout(1000)

    def pass_and_next(self):
        """点击合格，进入下一道工序"""
        logger.info("点击: 合格，进入下一道工序")
        self._pass_next_btn.wait_for(state="visible", timeout=self.timeout)
        self._pass_next_btn.click()
        self.page.wait_for_timeout(2000)  # 等待页面加载下一道工序

    def assert_all_complete(self):
        """断言该工位的所有工序全部完成"""
        logger.info(f"断言页面出现: {self._success_text}")
        self.page.locator("uni-modal").get_by_text(self._success_text).wait_for(
            state="visible", timeout=self.timeout
        )
        logger.info("断言通过: 该工位的所有工序全部完成")
