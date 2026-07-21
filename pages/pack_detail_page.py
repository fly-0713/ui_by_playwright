"""包装任务详情页面对象"""

from playwright.sync_api import Page

from common.logger import logger
from pages.base_page import BasePage


class PackDetailPage(BasePage):
    """包装任务详情页面对象"""

    def __init__(self, page: Page):
        super().__init__(page)
        # 左侧菜单
        self._menu_pack_work = page.get_by_text("包装作业", exact=True)
        self._menu_pack_task = page.get_by_text("包装任务")
        # 搜索区域
        self._btn_expand = page.get_by_role("button", name="展开")
        self._input_serial = page.get_by_placeholder("产品序列号")
        self._btn_search = page.get_by_role("button", name="搜索")
        # 详情链接
        self._detail_link = page.locator("a").filter(has_text="详情")

    def navigate_to_pack_task(self):
        """从首页导航到包装任务页面"""
        logger.info("导航到包装任务页面")
        self._menu_pack_work.click()
        self.page.wait_for_timeout(500)
        self._menu_pack_task.click()
        self.page.wait_for_timeout(1000)
        logger.info(f"已进入包装任务页面, URL: {self.page.url}")

    def expand_search(self):
        """点击展开按钮，等待搜索框出现"""
        logger.info("点击展开")
        self._btn_expand.click()
        self._input_serial.wait_for(state="visible", timeout=self.timeout)

    def search_by_serial(self, serial_number: str):
        """搜索产品序列号

        Args:
            serial_number: 产品序列号
        """
        logger.info(f"搜索产品序列号: {serial_number}")
        self.click_and_fill(self._input_serial, serial_number)
        self.click(self._btn_search)
        self._wait_for_loading()

    def open_detail(self):
        """点击详情按钮进入包装任务详情"""
        logger.info("点击详情按钮")
        self._detail_link.first.wait_for(state="visible", timeout=self.timeout)
        self._detail_link.first.click()
        self.page.wait_for_timeout(500)

    def click_serial_row(self, serial_number: str):
        """点击序列号行（触发关联操作）

        Args:
            serial_number: 序列号文本
        """
        logger.info(f"点击序列号行: {serial_number}")
        self.page.get_by_text(serial_number).first.click()
        self.page.wait_for_timeout(500)

    def get_pack_serial_number(self) -> str:
        """从详情页获取包装序列号

        Returns:
            包装序列号字符串
        """
        logger.info("获取包装序列号")
        # 通过表格列名获取
        col_index = self._get_column_index("序列号")
        if col_index != -1:
            cell = self.page.locator(
                f".el-table__body-wrapper tbody tr:first-child td:nth-child({col_index})"
            )
            pack_serial = cell.inner_text().strip()
        else:
            # fallback：获取第一个包含 TEST 的文本
            pack_serial = self.page.locator("text=/TEST\\d+/").first.inner_text().strip()

        logger.info(f"获取到包装序列号: {pack_serial}")
        return pack_serial

    def get_pack_station_code(self) -> str:
        """从详情页获取包装工位编码

        Returns:
            包装工位编码字符串
        """
        logger.info("获取包装工位编码")
        # 通过表格列名获取
        col_index = self._get_column_index("工位编码")
        if col_index != -1:
            cell = self.page.locator(
                f".el-table__body-wrapper tbody tr:first-child td:nth-child({col_index})"
            )
            station_code = cell.inner_text().strip()
        else:
            # fallback：获取第一个包含 BCX 的文本
            station_code = self.page.locator("text=/BCX\\d+/").first.inner_text().strip()

        logger.info(f"获取到包装工位编码: {station_code}")
        return station_code

    def click_station_code(self, station_code: str):
        """点击工位编码

        Args:
            station_code: 工位编码文本
        """
        logger.info(f"点击工位编码: {station_code}")
        self.page.get_by_text(station_code).first.click()
        self.page.wait_for_timeout(300)

    def _get_column_index(self, header_text: str) -> int:
        """通过表头文本获取列索引（1-based）"""
        headers = self.page.locator(".el-table__header-wrapper th").all()
        for i, th in enumerate(headers):
            if th.is_visible() and header_text in th.inner_text():
                logger.info(f"表头 '{header_text}' 在第 {i + 1} 列")
                return i + 1
        logger.warning(f"未找到表头 '{header_text}'")
        return -1

    def _wait_for_loading(self):
        """等待 Loading 出现再消失"""
        loading = self.page.locator(".el-loading-mask")
        try:
            loading.wait_for(state="visible", timeout=3000)
        except Exception:
            pass
        try:
            loading.wait_for(state="hidden", timeout=10000)
        except Exception:
            pass
        self.page.wait_for_timeout(500)
