"""生产工单详情页面对象"""

from playwright.sync_api import Page

from common.logger import logger
from pages.base_page import BasePage


class OrderDetailPage(BasePage):
    """生产工单详情页面对象"""

    def __init__(self, page: Page):
        super().__init__(page)
        # 左侧菜单
        self._menu_production = page.locator(".el-sub-menu__title, .el-menu-item").filter(has_text="生产管理")
        self._menu_work_order = page.locator(".el-menu-item").filter(has_text="生产工单")
        # 搜索区域
        self._btn_expand = page.get_by_role("button", name="展开")
        self._input_plan_no = page.get_by_placeholder("计划编号")
        self._btn_search = page.get_by_role("button", name="搜索")

    def navigate_to_work_order(self):
        """从首页导航到生产工单页面"""
        logger.info("导航到生产工单页面")
        self._menu_production.first.click()
        self.page.wait_for_timeout(500)
        self._menu_work_order.first.click()
        self.page.wait_for_timeout(1000)
        logger.info(f"已进入生产工单页面, URL: {self.page.url}")

    def expand_search(self):
        """点击展开按钮，等待计划编号搜索框出现"""
        logger.info("点击展开")
        self._btn_expand.click()
        # 等待计划编号搜索框出现
        self._input_plan_no.wait_for(state="visible", timeout=self.timeout)

    def search_plan(self, plan_no: str):
        """搜索计划编号"""
        logger.info(f"搜索计划编号: {plan_no}")
        self.click_and_fill(self._input_plan_no, plan_no)
        self.click(self._btn_search)
        self._wait_for_loading()

    def open_detail(self):
        """点击第一条工单的详情按钮"""
        logger.info("点击详情按钮")
        detail_btn = self.page.get_by_role("cell", name="详情 取消派工 打印序列号 删除").locator("a").first
        detail_btn.wait_for(state="visible", timeout=self.timeout)
        detail_btn.click()
        self.page.wait_for_timeout(500)

    def get_serial_number(self) -> str:
        """从详情页表格中获取第一行的序列号

        Returns:
            序列号字符串，如 "TEST202606231327"
        """
        col_index = self._get_column_index("序列号")
        if col_index != -1:
            cell = self.page.locator(
                f".el-table__body-wrapper tbody tr:first-child td:nth-child({col_index})"
            )
            serial_number = cell.inner_text().strip()
        else:
            serial_number = self.page.locator(
                ".el-table__body-wrapper tbody tr:first-child"
            ).inner_text().strip().split()[0]

        logger.info(f"获取到序列号: {serial_number}")
        return serial_number

    def expand_row(self):
        """展开当前行"""
        logger.info("展开当前行")
        expand_btn = self.page.get_by_label("展开当前行")
        expand_btn.wait_for(state="visible", timeout=self.timeout)
        expand_btn.click()
        self.page.wait_for_timeout(500)

    def get_station_code(self) -> str:
        """获取展开行中的工位编码

        Returns:
            工位编码字符串，如 "CX000078-1"
        """
        logger.info("获取工位编码")
        station_cell = self.page.locator(".el-table__body-wrapper .el-table__expanded-cell").locator(
            "text=/CX\\d+/"
        ).first
        try:
            station_cell.wait_for(state="visible", timeout=self.timeout)
            code = station_cell.inner_text().strip()
        except Exception:
            # fallback：直接取包含 CX 的第一个文本
            code = self.page.locator("text=/CX\\d+/").first.inner_text().strip()

        logger.info(f"获取到工位编码: {code}")
        return code

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
