"""测试数据生成辅助工具

提供跨用例共享的测试数据生成函数，确保一次运行中相关用例使用同一份数据，
同时每次运行生成新的数据避免重复冲突。
"""

from datetime import datetime

from common.shared_data import shared_data


def get_plan_no() -> str:
    """获取本次运行共用的计划编号

    优先从 shared_data 读取已缓存的 plan_no；如果没有则生成一个带时间戳的唯一编号，
    并写入 shared_data 供后续用例复用。
    """
    plan_no = shared_data.get("plan_no")
    if plan_no is None:
        now = datetime.now()
        plan_no = f"test{now.strftime('%Y%m%d%H%M%S')}001"
        shared_data.set("plan_no", plan_no)
    return plan_no
