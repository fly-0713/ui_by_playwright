"""计划新增页面对象"""

from playwright.sync_api import Page

from common.logger import logger
from pages.base_page import BasePage


class PlanAddPage(BasePage):
    """计划新增页面对象"""

    def __init__(self, page: Page):
        super().__init__(page)
        # 左侧菜单
        self._menu_plan = page.locator(".el-sub-menu__title, .el-menu-item").filter(has_text="计划管理")
        self._menu_order = page.locator(".el-menu-item").filter(has_text="计划订单")

        # 计划订单页面内的新增按钮
        self._btn_add_product = page.get_by_role("button", name="新增订单")

        # 弹窗内输入字段
        self._input_material_code = page.get_by_placeholder("物料编码")
        self._input_quantity = page.get_by_placeholder("数量")
        self._input_plan_no = page.get_by_label("计划编号", exact=True)
        self._select_erp_order = page.get_by_label("ERP生产订单")
        self._btn_plan_date = page.get_by_label("计划日期")
        self._btn_start_date = page.get_by_placeholder("开始日期")
        self._btn_end_date = page.get_by_placeholder("结束日期")

        # 确认按钮
        self._btn_confirm = page.get_by_role("button", name="确认")

    def navigate_to_plan_add(self):
        """从首页导航到计划订单页面，再点击新增订单"""
        logger.info("导航到计划订单页面")
        self._menu_plan.first.click()
        self.page.wait_for_timeout(500)
        self._menu_order.first.click()
        self._btn_add_product.wait_for(state="visible", timeout=self.timeout)
        logger.info(f"已进入计划订单页面, URL: {self.page.url}")

    def add_plan(self, material_code: str, quantity: str, plan_no: str,
                 erp_order: str, start_date_day: str, end_date_day: str):
        """点击新增订单，填写表单并确认

        Args:
            material_code: 物料编码
            quantity: 数量
            plan_no: 计划编号
            erp_order: ERP生产订单选项名称
            start_date_day: 开始日期（日历中的日期文字，如 "23"）
            end_date_day: 结束日期（日历中的日期文字，如 "28"）
        """
        logger.info(f"新增计划: 物料={material_code}, 数量={quantity}, 计划编号={plan_no}")

        # 1. 点击新增订单按钮
        self.click(self._btn_add_product)
        self._input_material_code.wait_for(state="visible", timeout=self.timeout)

        # 2. 填写物料编码
        self.click_and_fill(self._input_material_code, material_code)

        # 3. 填写数量
        self.click_and_fill(self._input_quantity, quantity)

        # 4. 填写计划编号
        self.click_and_fill(self._input_plan_no, plan_no)

        # 5. 选择 ERP 生产订单
        self._select_erp_order.click(timeout=self.timeout)
        self.page.get_by_role("option", name=erp_order).click()
        logger.info(f"已选择 ERP 生产订单: {erp_order}")
        # 等待下拉菜单完全关闭
        self.page.wait_for_timeout(500)

        # 6. 选择计划日期（开始日期 + 结束日期）
        # 点击计划日期字段的开始日期输入框（第 2 个占位符为开始日期的那个）
        self.page.get_by_placeholder("开始日期").nth(1).click(timeout=self.timeout)
        # 等待弹出的日期范围选择器中的日期单元格可见
        self.page.locator(".el-date-range-picker .el-date-table-cell__text").first.wait_for(state="visible", timeout=self.timeout)
        logger.info("日历弹出成功")
        # 开始日期：限定在本月日期单元格（排除灰色的上下月日期）
        current_cells = self.page.locator(
            ".el-date-range-picker td.available:not(.prev-month):not(.next-month) .el-date-table-cell__text"
        )
        current_cells.filter(has_text=start_date_day).first.click()
        logger.info(f"已选择开始日期: {start_date_day}")
        # 结束日期：在弹窗内所有可用日期单元格中取最后一个匹配项
        current_cells.filter(has_text=end_date_day).last.click()
        logger.info(f"已选择结束日期: {end_date_day}")

        # 7. 点击确认
        self.click(self._btn_confirm)
        self._wait_for_save_complete()
        logger.info("已点击确认，等待保存完成")

    def get_plan_nos_in_table(self) -> list:
        """获取表格中所有计划编号"""
        plan_nos = []
        try:
            col_index = self._get_column_index("计划编号")
            if col_index == -1:
                logger.error("无法定位计划号列")
                return plan_nos
            cells = self.page.locator(
                f".el-table__body-wrapper tbody tr td:nth-child({col_index})"
            ).all()
            for cell in cells:
                if cell.is_visible():
                    text = cell.inner_text().strip()
                    if text:
                        plan_nos.append(text)
        except Exception as e:
            logger.warning(f"获取计划号列表异常: {e}")
        logger.info(f"计划号列表: {plan_nos}")
        return plan_nos

    def _get_column_index(self, header_text: str) -> int:
        """通过表头文本获取列索引（1-based）"""
        headers = self.page.locator(".el-table__header-wrapper th").all()
        for i, th in enumerate(headers):
            if th.is_visible() and header_text in th.inner_text():
                logger.info(f"表头 '{header_text}' 在第 {i + 1} 列")
                return i + 1
        logger.warning(f"未找到表头 '{header_text}'")
        return -1

    def _wait_for_save_complete(self):
        """等待保存请求完成（Loading 出现再消失）"""
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
