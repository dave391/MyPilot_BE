import logging
import logging.config
from logging import getLogger


def configure_log(logger_name: str = "CiaBot2.0"):
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(funcName)s() - %(message)s')
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    bitbot_logger = logging.getLogger(logger_name)
    bitbot_logger.setLevel(level=logging.INFO)
    bitbot_logger.addHandler(handler)
    bitbot_logger.propagate = False

    return bitbot_logger


def get_logger(name=None):
    if name is None:
        name = "CiaBot2.0"
    return getLogger(name)