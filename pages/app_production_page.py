"""H5 生产报工页面对象

生产报工流程：
  1. 点击底部 tab 进入生产页面
  2. 点击搜索图标输入工位编码
  3. 选择产线（点击图片）
  4. 输入序列号
  5. 选择工序 → 完工进入下一道工序
  6. 填写数量、上传图片
  7. 再次选工序 → 完工处理下一件产品
"""

import os

from playwright.sync_api import Page

from common.logger import logger
from pages.base_page import BasePage


class AppProductionPage(BasePage):
    """H5 生产报工页面对象"""

    def __init__(self, page: Page):
        super().__init__(page)
        # 底部 tabbar
        self._tabbar_first_icon = page.locator("uni-tabbar").get_by_role("img").first
        # 搜索/添加工位图标
        self._uni_icons = page.locator(".uni-icons")
        # 通用输入框（弹出层中）
        self._popup_textbox = page.get_by_role("textbox")
        # 确定按钮（弹出层）
        self._confirm_btn = page.get_by_text("确定")
        # 产线选择（页面中的图片，取第二个）
        self._product_line_img = page.locator("uni-page-body").get_by_role("img").nth(1)
        # 工序标签（取第二个标签）
        self._process_label = page.locator("uni-label uni-view").nth(1)
        # "完工，进入下一道工序"按钮
        self._next_process_btn = page.get_by_text("完工，进入下一道工序")
        # "完工，处理下一件产品"按钮
        self._next_product_btn = page.get_by_text("完工，处理下一件产品")
        # 文件上传器（UniApp 的 input[type=file] 隐藏在 uni-view 内部）
        self._file_uploader = page.locator(".uni-uploader__input input[type='file']")

    def go_to_production_tab(self):
        """点击底部 tabbar 第一个图标，进入生产页面"""
        logger.info("点击底部 tab 进入生产页面")
        self._tabbar_first_icon.click()
        self.page.wait_for_timeout(500)

    def input_station_code(self, station_code: str):
        """点击搜索图标，输入工位编码并确定"""
        logger.info(f"点击搜索图标，准备输入工位编码: {station_code}")
        self._uni_icons.click()
        self.page.wait_for_timeout(300)
        self._popup_textbox.fill(station_code)
        logger.info("点击确定")
        self._confirm_btn.click()
        self.page.wait_for_timeout(500)

    def select_production_line(self):
        """选择产线（点击图片）"""
        logger.info("选择产线（点击图片）")
        self._product_line_img.wait_for(state="visible", timeout=self.timeout)
        self._product_line_img.click()
        self.page.wait_for_timeout(300)

    def input_serial_number(self, serial_number: str):
        """输入序列号并确定"""
        logger.info(f"输入序列号: {serial_number}")
        self._popup_textbox.click()
        self._popup_textbox.fill(serial_number)
        logger.info("点击确定")
        self._confirm_btn.click()
        self.page.wait_for_timeout(500)

    def select_process(self):
        """选择工序（点击第二个标签）"""
        logger.info("选择工序（点击标签）")
        self._process_label.wait_for(state="visible", timeout=self.timeout)
        self._process_label.click()
        self.page.wait_for_timeout(300)

    def complete_and_next_process(self):
        """点击"完工，进入下一道工序"按钮"""
        logger.info("点击: 完工，进入下一道工序")
        self._next_process_btn.wait_for(state="visible", timeout=self.timeout)
        self._next_process_btn.click()
        self.page.wait_for_timeout(500)

    def fill_quantity_and_upload(self, quantity: str, image_path: str):
        """填写完工数量并上传图片

        Args:
            quantity: 完工数量，如 "2"
            image_path: 图片相对路径（相对于项目根目录）
        """
        logger.info(f"填写完工数量: {quantity}")
        self._popup_textbox.click()
        self._popup_textbox.fill(quantity)

        # 图片上传
        if image_path:
            abs_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                image_path,
            )
            if os.path.exists(abs_path):
                logger.info(f"上传图片: {abs_path}")
                uploader = self.page.locator(".uni-uploader__input")
                # 等待上传输入框可见
                uploader.wait_for(state="visible", timeout=self.timeout)
                # 使用 file_chooser 拦截文件选择框，避免弹出系统弹框
                with self.page.expect_file_chooser(timeout=10000) as fc_info:
                    uploader.click()
                file_chooser = fc_info.value
                file_chooser.set_files(abs_path)
                self.page.wait_for_timeout(1000)
            else:
                logger.warning(f"图片文件不存在，跳过上传: {abs_path}")

        self.page.wait_for_timeout(300)

    def complete_and_next_product(self):
        """再次选工序，点击“完工，处理下一件产品”按钮"""
        logger.info("再次选择工序")
        self.select_process()
        logger.info("点击: 完工，处理下一件产品")
        self._next_product_btn.wait_for(state="visible", timeout=self.timeout)
        self._next_product_btn.click()
        self.page.wait_for_timeout(500)

    def assert_confirm_visible(self):
        """断言页面出现"确定"弹窗，表示报工流程执行完毕"""
        self._confirm_btn.wait_for(state="visible", timeout=self.timeout)
        logger.info("断言通过: 页面出现'确定'按钮，报工流程完成")
