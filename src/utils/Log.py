import logging
import os

from NBAScrapper.src.utils import DataBase


def create_logging(season: str):
    """Create a log file"""
    path_exist = os.path.exists("src/logs")
    if not path_exist:
        os.makedirs("src/logs")
    log = logging.getLogger(season)
    if not log.hasHandlers():
        log.setLevel(logging.DEBUG)

        handler = logging.FileHandler("src/logs/" + DataBase.get_db_name() + "-" + str(season) + ".log",
                                      encoding="UTF-8")
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s', datefmt="%Y/%m/%d %H:%M:%S"))

        log.addHandler(handler)


def log_debug(log_name: str, text: str):
    """Create a debug entry into log file"""
    log = logging.getLogger(log_name)
    log.debug(text)


def log_info(log_name: str, text: str):
    """Create an info entry into log file"""
    log = logging.getLogger(log_name)
    log.info(text)


def log_warning(log_name: str, text: str):
    """Create a warning entry into log file"""
    log = logging.getLogger(log_name)
    log.warning(text)


def log_error(log_name: str, text: str):
    """Create an error entry into log file"""
    log = logging.getLogger(log_name)
    log.error(text)


def log_critical(log_name: str, text: str):
    """Create a critical entry into log file"""
    log = logging.getLogger(log_name)
    log.critical(text)
