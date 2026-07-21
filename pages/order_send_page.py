"""生产工单派工页面对象"""

from playwright.sync_api import Page

from common.logger import logger
from pages.base_page import BasePage


class OrderSendPage(BasePage):
    """生产工单派工页面对象"""

    def __init__(self, page: Page):
        super().__init__(page)
        # 左侧菜单
        self._menu_production = page.locator(".el-sub-menu__title, .el-menu-item").filter(has_text="生产管理")
        self._menu_work_order = page.locator(".el-menu-item").filter(has_text="生产工单")

        # 工单详情内搜索区域
        self._input_plan_no = page.get_by_placeholder("计划编号")
        self._btn_search = page.get_by_role("button", name="搜索")
        self._btn_expand = page.get_by_role("button", name="展开")

        # 派工弹窗字段
        self._select_line = page.get_by_label("产线", exact=True)
        self._select_line_leader = page.locator("span").filter(has_text="产线负责人")
        self._select_packing_process = page.get_by_label("包装工艺")
        self._btn_confirm = page.get_by_role("button", name="确认", exact=True)

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

    def click_dispatch(self):
        """点击计划行中的派工按钮（第 2 个 a 链接）"""
        logger.info("点击派工按钮")
        dispatch_btn = self.page.locator(".el-table__body-wrapper tbody tr").first.locator("a").nth(1)
        dispatch_btn.wait_for(state="visible", timeout=self.timeout)
        dispatch_btn.click()
        # 等待派工弹窗中的产线字段出现
        self._select_line.wait_for(state="visible", timeout=self.timeout)
        logger.info("派工弹窗已打开")

    def fill_dispatch_form(self, production_line: str, line_leader: str, packing_process: str):
        """填写派工弹窗表单

        Args:
            production_line: 产线名称
            line_leader: 产线负责人
            packing_process: 包装工艺名称
        """
        # 1. 选择产线
        self._select_line.click(timeout=self.timeout)
        self.page.get_by_text(production_line).click()
        logger.info(f"已选择产线: {production_line}")

        # 2. 选择产线负责人
        self._select_line_leader.click(timeout=self.timeout)
        self.page.get_by_role("option", name=line_leader, exact=True).click()
        logger.info(f"已选择产线负责人: {line_leader}")

        # 3. 选择包装工艺
        self._select_packing_process.click(timeout=self.timeout)
        self.page.get_by_text(packing_process).click()
        logger.info(f"已选择包装工艺: {packing_process}")

    def confirm_dispatch(self):
        """点击确认完成派工"""
        self.click(self._btn_confirm)
        self._wait_for_loading()
        logger.info("已点击确认，等待派工完成")

    def confirm_dispatch_send(self):
        """点击确认派工按钮（最终提交）"""
        logger.info("点击确认派工")
        confirm_send = self.page.locator("a").filter(has_text="确认派工")
        confirm_send.wait_for(state="visible", timeout=self.timeout)
        confirm_send.click()
        self._wait_for_loading()
        logger.info("确认派工完成")

    def get_row_status(self, plan_no: str) -> str:
        """获取包含指定计划编号的行的状态"""
        try:
            row = self.page.locator(".el-table__body-wrapper tbody tr").filter(has_text=plan_no).first
            col_index = self._get_column_index("状态")
            if col_index == -1:
                return ""
            status_cell = row.locator(f"td:nth-child({col_index})")
            status = status_cell.inner_text().strip()
            logger.info(f"计划 '{plan_no}' 当前状态: {status}")
            return status
        except Exception as e:
            logger.warning(f"获取状态异常: {e}")
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
