import os
import logging
from logging.handlers import QueueHandler, QueueListener, RotatingFileHandler
from queue import Queue

# 全局单例，保证只初始化一次
_LOGGER = None
_LISTENER = None

def get_quant_logger():
    global _LOGGER, _LISTENER
    if _LOGGER is not None:
        return _LOGGER

    # ======================
    # 1. 日志目录与格式
    # ======================
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "quant.log")

    # 标准日志格式
    log_format = "%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, datefmt=date_format)

    # ======================
    # 2. 输出 Handler
    # ======================
    # 文件输出：按大小切割，保留10个文件
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    # 控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # ======================
    # 3. 异步队列核心
    # ======================
    log_queue = Queue(-1)  # 无限大小队列

    # 启动后台线程消费日志（真正写入文件/控制台）
    queue_listener = QueueListener(log_queue, file_handler, console_handler)
    queue_listener.start()

    # ======================
    # 4. 配置根 Logger
    # ======================
    root_logger = logging.getLogger()
    root_logger.handlers.clear()  # 清空默认 handler
    root_logger.addHandler(QueueHandler(log_queue))  # 只使用异步队列
    root_logger.setLevel(logging.INFO)

    # ======================
    # 5. 获取业务 logger
    # ======================
    logger = logging.getLogger("quant_trade")

    _LOGGER = logger
    _LISTENER = queue_listener
    return logger


def close_logger():
    """程序退出时必须调用，确保日志写完"""
    if _LISTENER:
        _LISTENER.stop()


# 全局导出，直接使用
logger = get_quant_logger()
# logger.setLevel(logging.DEBUG)
