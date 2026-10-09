import logging
from utils.path_tool import get_abs_path
import os
from datetime import datetime

# 日志保存的根目录
LOG_ROOT = get_abs_path("logs")

# 确保日志的目录存在
os.makedirs(LOG_ROOT, exist_ok=True)

# 日志格式：时间 - 日志器名称 - 级别 - 文件名:行号 - 消息
DEFAULT_LOG_FORMAT = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)


def get_logger(
        name: str = "agent",
        console_level: int = logging.INFO,
        file_level: int = logging.DEBUG,
        log_file=None,
) -> logging.Logger:
    """获取日志器；同名日志器已存在时直接复用，避免重复添加 Handler。

    :param name: 日志器名称，同时作为默认日志文件名前缀
    :param console_level: 控制台输出的最低日志级别
    :param file_level: 文件写入的最低日志级别
    :param log_file: 自定义日志文件路径，默认写到 logs/<name>_<日期>.log
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    # 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(console_handler)

    # 文件输出
    if not log_file:
        log_file = os.path.join(LOG_ROOT, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(file_level)
    file_handler.setFormatter(DEFAULT_LOG_FORMAT)

    logger.addHandler(file_handler)

    return logger


# 快捷获取日志器
logger = get_logger()


if __name__ == '__main__':
    logger.info("信息日志")
    logger.error("错误日志")
    logger.warning("警告日志")
    logger.debug("调试日志")
