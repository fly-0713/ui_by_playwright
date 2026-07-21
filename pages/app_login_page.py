"""H5 登录页面对象

H5 端（UniApp）与 PC 端登录差异：
  - 无验证码，直接填写工号+密码点击登录
  - 登录成功判断：底部 tabbar 出现并包含"我的"
  - 元素使用 uni-input / uni-button 等 UniApp 组件标签
"""

from playwright.sync_api import Page

from common.logger import logger
from pages.base_page import BasePage


class AppLoginPage(BasePage):
    """H5 登录页面对象"""

    # H5 登录页 URL 关键路径
    LOGIN_URL_KEYWORD = "/#/pages/login/index"

    def __init__(self, page: Page):
        super().__init__(page)
        # 元素定位器（UniApp 组件）
        self._username_input = page.locator("uni-input").filter(has_text="请输入工号").get_by_role("textbox")
        self._password_input = page.locator("uni-input").filter(has_text="请输入密码").get_by_role("textbox")
        self._login_button = page.locator("uni-button")
        # 登录成功标志：底部 tabbar
        self._tabbar = page.locator("uni-tabbar")

    def navigate(self, url: str):
        """打开 H5 登录页并等待工号输入框加载"""
        super().navigate(url)
        self.wait_for_visible(self._username_input)
        logger.info(f"H5 登录页加载完成，URL: {self.page.url}")

    def login(self, username: str, password: str):
        """填写工号和密码并点击登录"""
        logger.info(f"填写工号: {username}")
        self.click_and_fill(self._username_input, username)
        logger.info("填写密码")
        self.click_and_fill(self._password_input, password)
        logger.info("点击登录按钮")
        self.click(self._login_button)

    def login_until_success(self, username: str, password: str) -> bool:
        """执行登录并等待成功跳转

        H5 无验证码，直接登录，等待 tabbar 出现即为成功。

        Returns:
            True 表示登录成功，False 表示超时失败
        """
        self.login(username, password)
        return self._wait_for_login_result()

    def _wait_for_login_result(self, timeout: int = 10000) -> bool:
        """等待登录结果：tabbar 出现即成功，超时即失败"""
        try:
            self._tabbar.wait_for(state="visible", timeout=timeout)
            tabbar_text = self._tabbar.inner_text()
            logger.info(f"登录成功，tabbar 内容: {tabbar_text.strip()}")
            return True
        except Exception as e:
            logger.error(f"等待 tabbar 超时，登录失败: {e}")
            return False

    def is_login_page(self) -> bool:
        """判断当前是否仍在登录页"""
        return self.LOGIN_URL_KEYWORD in self.page.url
