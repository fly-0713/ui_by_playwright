"""计划下发页面对象"""

from playwright.sync_api import Page

from common.logger import logger
from pages.base_page import BasePage


class PlanSendPage(BasePage):
    """计划下发页面对象（在计划订单列表页操作）"""

    def __init__(self, page: Page):
        super().__init__(page)
        # 左侧菜单
        self._menu_plan = page.locator(".el-sub-menu__title, .el-menu-item").filter(has_text="计划管理")
        self._menu_order = page.locator(".el-menu-item").filter(has_text="计划订单")

        # 搜索区域
        self._input_plan_no = page.get_by_placeholder("计划编号")
        self._btn_search = page.get_by_role("button", name="搜索")

        # 下发弹窗字段
        self._btn_send_quantity = page.get_by_placeholder("下发数量")
        self._btn_confirm = page.get_by_role("button", name="确认")

    def navigate_to_order(self):
        """从首页导航到计划订单页面"""
        logger.info("导航到计划订单页面")
        self._menu_plan.first.click()
        self.page.wait_for_timeout(500)
        self._menu_order.first.click()
        self._input_plan_no.wait_for(state="visible", timeout=self.timeout)
        logger.info(f"已进入计划订单页面, URL: {self.page.url}")

    def search_plan(self, plan_no: str):
        """搜索指定计划编号"""
        logger.info(f"搜索计划编号: {plan_no}")
        self.click_and_fill(self._input_plan_no, plan_no)
        self.click(self._btn_search)
        self._wait_for_loading()

    def click_send(self):
        """点击列表中第一条记录的下发按钮"""
        send_link = self.page.locator("a").filter(has_text="下发").first
        send_link.wait_for(state="visible", timeout=self.timeout)
        send_link.click()
        logger.info("已点击下发按钮")
        # 等待下发弹窗出现
        self._btn_send_quantity.wait_for(state="visible", timeout=self.timeout)

    def fill_send_form(self, send_quantity: str, start_date_day: str, end_date_day: str):
        """填写下发弹窗中的排程日期和下发数量

        Args:
            send_quantity: 下发数量
            start_date_day: 排程开始日期（日历中的日期数字，如 "23"）
            end_date_day: 排程结束日期（日历中的日期数字，如 "30"）
        """
        # 1. 选择排程日期
        self.page.get_by_label("排程日期").click(timeout=self.timeout)
        # 等待日历弹窗出现
        self.page.locator(".el-date-range-picker .el-date-table-cell__text").first.wait_for(
            state="visible", timeout=self.timeout
        )
        logger.info("排程日期日历弹出成功")

        # 开始日期：限定在本月可用日期单元格
        current_cells = self.page.locator(
            ".el-date-range-picker td.available:not(.prev-month):not(.next-month) .el-date-table-cell__text"
        )
        current_cells.filter(has_text=start_date_day).first.click()
        logger.info(f"已选择排程开始日期: {start_date_day}")

        # 结束日期：在弹窗内所有可用日期中取最后一个匹配项（兼容跨月）
        current_cells.filter(has_text=end_date_day).last.click()
        logger.info(f"已选择排程结束日期: {end_date_day}")

        # 2. 填写下发数量
        self.click_and_fill(self._btn_send_quantity, send_quantity)
        logger.info(f"已填写下发数量: {send_quantity}")

    def confirm_send(self):
        """点击确认完成下发"""
        self.click(self._btn_confirm)
        self._wait_for_loading()
        logger.info("已点击确认，等待下发完成")

    def get_plan_status(self, plan_no: str) -> str:
        """获取指定计划编号对应行的状态"""
        try:
            # 找到包含计划编号的行
            row = self.page.locator(".el-table__body-wrapper tbody tr").filter(has_text=plan_no).first
            # 找状态列（通过表头定位）
            col_index = self._get_column_index("状态")
            if col_index == -1:
                return ""
            status_cell = row.locator(f"td:nth-child({col_index})")
            status = status_cell.inner_text().strip()
            logger.info(f"计划 '{plan_no}' 当前状态: {status}")
            return status
        except Exception as e:
            logger.warning(f"获取计划状态异常: {e}")
            return ""

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
