"""公共截图工具"""

import os
import re
from datetime import datetime

from playwright.sync_api import Page

from common.logger import logger

# 截图根目录
SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "screenshots")


def _safe_filename(name: str) -> str:
    """将文件名中的中文、特殊字符替换为下划线，确保 Jenkins Workspace 可正常访问"""
    # 保留 ASCII 字母、数字、下划线、连字符、点，其余替换为下划线
    safe = re.sub(r"[^\w\-\.]", "_", name)
    # 合并连续下划线
    safe = re.sub(r"_+", "_", safe)
    # 去除首尾下划线
    safe = safe.strip("_")
    # 限制长度，避免文件名过长
    return safe[:100]


def take_screenshot(page: Page, name: str):
    """截图并保存到 screenshots 目录，文件名自动加时间戳

    Args:
        page: Playwright Page 对象
        name: 截图标识名称（如用例名）
    """
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = _safe_filename(name)
    filename = f"{safe_name}_{timestamp}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    page.screenshot(path=filepath)
    logger.info(f"截图已保存: {filepath}")
    return filepath
