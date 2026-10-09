import os
import random

from langchain_core.tools import tool

from rag.rag_service import RagSummarizeService
from utils.config_handler import agent_conf
from utils.logger_handler import logger
from utils.path_tool import get_abs_path

rag = RagSummarizeService()

# 模拟用户 ID 与月份，供工具随机取用（真实项目应替换为业务接口）
user_ids = ["1001", "1002", "1003", "1004", "1005", "1006", "1007", "1008", "1009", "1010",]
month_arr = ["2025-01", "2025-02", "2025-03", "2025-04", "2025-05", "2025-06",
             "2025-07", "2025-08", "2025-09", "2025-10", "2025-11", "2025-12", ]

# 外部使用记录缓存：{user_id: {month: {指标名: 指标值}}}
external_data = {}


@tool
def rag_summarize(query: str, session_id: str = "default") -> str:
    """从向量存储中检索参考资料并生成总结回答。"""
    return rag.rag_summarize(query, session_id)


@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气，以消息字符串形式返回。"""
    # 演示用模拟数据，接入真实天气服务时替换此处
    return f"城市{city}天气为晴天，气温26摄氏度，空气湿度50%，南风1级，AQI21，最近6小时降雨概率极低"


@tool
def get_user_location() -> str:
    """获取用户所在城市的名称，以纯字符串形式返回。"""
    # 演示用模拟数据，接入真实定位服务时替换此处
    return random.choice(["深圳", "合肥", "杭州"])


@tool
def get_user_id() -> str:
    """获取用户的 ID，以纯字符串形式返回。"""
    return random.choice(user_ids)


@tool
def get_current_month() -> str:
    """获取当前月份，以纯字符串形式返回。"""
    return random.choice(month_arr)


def generate_external_data():
    """按需加载外部使用记录 CSV，并整理为嵌套字典缓存到 external_data。

    数据结构：
    {
        "user_id": {
            "month": {"特征": xxx, "效率": xxx, "耗材": xxx, "对比": xxx},
            ...
        },
        ...
    }
    """
    if not external_data:
        external_data_path = get_abs_path(agent_conf["external_data_path"])

        if not os.path.exists(external_data_path):
            raise FileNotFoundError(f"外部数据文件{external_data_path}不存在")

        with open(external_data_path, "r", encoding="utf-8") as f:
            # 跳过表头后逐行解析
            for line in f.readlines()[1:]:
                arr: list[str] = line.strip().split(",")

                user_id: str = arr[0].replace('"', "")
                feature: str = arr[1].replace('"', "")
                efficiency: str = arr[2].replace('"', "")
                consumables: str = arr[3].replace('"', "")
                comparison: str = arr[4].replace('"', "")
                time: str = arr[5].replace('"', "")

                if user_id not in external_data:
                    external_data[user_id] = {}

                external_data[user_id][time] = {
                    "特征": feature,
                    "效率": efficiency,
                    "耗材": consumables,
                    "对比": comparison,
                }


@tool
def fetch_external_data(user_id: str, month: str) -> str:
    """从外部系统获取指定用户在指定月份的使用记录，以纯字符串形式返回；未检索到则返回空字符串。"""
    generate_external_data()

    try:
        record = external_data[user_id][month]
    except KeyError:
        logger.warning(f"[fetch_external_data]未能检索到用户：{user_id}在{month}的使用记录数据")
        return ""

    return "，".join(f"{key}：{value}" for key, value in record.items())


@tool
def fill_context_for_report():
    """无入参、无返回值；调用后由中间件为报告生成场景动态注入上下文信息，供后续提示词切换使用。"""
    return "fill_context_for_report已调用"
