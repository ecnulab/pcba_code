import logging
from logging.handlers import TimedRotatingFileHandler
import os

# 设置日志目录
log_dir = './logs/'

# 配置日志格式
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# 创建一个全局 logger 实例
logger = logging.getLogger()

def setup_logging():
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 创建一个 TimedRotatingFileHandler，按天切割日志
    log_handler = TimedRotatingFileHandler(
        os.path.join(log_dir, 'log'),  # 文件名固定，但会根据时间创建不同的文件
        when='midnight',  # 在午夜切割日志
        interval=1,  # 每天切割
        backupCount=0,  # 保留最近 7 天的日志文件
        encoding="utf-8"
    )

    log_handler.setFormatter(log_formatter)
    log_handler.setLevel(logging.INFO)

    # 通过全局 logger 设置 handler
    if not logger.handlers:  # 防止重复添加处理器
        logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)

    return logger

