import os
import sys

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import allure
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from common.logger import logger, get_case_log, clear_case_log
from common.screenshot import take_screenshot


# 测试文件执行顺序（按此列表顺序运行，未在列表中的文件按字母顺序追加到末尾）
TEST_FILE_ORDER = [
    "test_login.py",
    "test_plan_add.py",
    "test_plan_send.py",
    "test_order_send.py",
    "test_order_detail.py",
    "test_app_login.py",
    "test_app_production.py",
    "test_testtask_detail.py",
    "test_app_test_nopass.py",
    "test_app_handle_abnormality.py",
    "test_app_repair_over.py",
    "test_app_review_abnormality.py",
    "test_app_test_pass.py",
    "test_pack_detail.py",
    "test_app_pack_over.py",
]


def pytest_collection_modifyitems(items):
    """按照 TEST_FILE_ORDER 排序测试用例收集顺序"""
    def sort_key(item):
        filename = os.path.basename(item.fspath)
        try:
            return TEST_FILE_ORDER.index(filename)
        except ValueError:
            # 未在列表中的文件，排到最后
            return len(TEST_FILE_ORDER)

    items.sort(key=sort_key)


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """为 Allure suite 标签添加执行序号前缀，使 Suites 视图按执行顺序排列"""
    filename = os.path.basename(item.fspath)
    if filename in TEST_FILE_ORDER:
        order = TEST_FILE_ORDER.index(filename) + 1
        suite_name = f"{order:02d}_{filename[:-3]}"
    else:
        suite_name = filename[:-3]
    allure.dynamic.label("suite", suite_name)


def pytest_addoption(parser):
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="无头模式运行浏览器",
    )


# shared_data 已改用文件存储方式（common/shared_data.py），
# 数据持久化到 datas/shared_data.json，解耦测试依赖
# 使用方式：from common.shared_data import shared_data


@pytest.fixture(scope="session")
def browser(pytestconfig):
    """启动浏览器，session 级别共享"""
    # config 在此处导入，确保 ENV 已由 main.py 设置后再加载
    from common.config import config  # noqa
    # 默认有头模式，只有显式传 --headless 才无头
    headless = pytestconfig.getoption("--headless")
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=headless)
    mode = "无头模式" if headless else "有头模式"
    logger.info(f"浏览器已启动（{mode}）")
    yield browser
    browser.close()
    pw.stop()
    logger.info("浏览器已关闭")


@pytest.fixture(scope="function")
def context(browser: Browser):
    """每个测试用例创建独立的上下文"""
    context = browser.new_context()
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext):
    """每个测试用例创建独立的页面"""
    page = context.new_page()
    yield page


@pytest.fixture(autouse=True)
def _setup_case_log():
    """每个用例开始前清空日志缓冲，结束后附加到 allure"""
    clear_case_log()
    yield
    # 用例结束后将缓冲日志附加到 allure
    case_log = get_case_log()
    if case_log:
        allure.attach(case_log, name="用例日志", attachment_type=allure.attachment_type.TEXT)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """断言失败时自动截图并附加到 allure"""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page:
            case_name = item.nodeid.replace("::", "_").replace("/", "_")
            logger.error(f"测试失败，自动截图: {case_name}")
            filepath = take_screenshot(page, case_name)
            with open(filepath, "rb") as f:
                allure.attach(
                    f.read(),
                    name=f"{case_name}_失败截图",
                    attachment_type=allure.attachment_type.PNG,
                )
