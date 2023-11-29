import os
from pathlib import Path
import logging
import logging.handlers

LOGS_DIR = "logs"
base_dir = Path.cwd().as_posix()
info_logs_target = os.path.join(base_dir, LOGS_DIR, "qnai_model.info.log")
warning_logs_target = os.path.join(base_dir, LOGS_DIR, "qnai_model.warning.log")
    

class ColouredFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    green = "\x1b[32m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = (
        "%(asctime)s - %(name)s [%(levelname)s]: %(message)s (%(filename)s:%(lineno)d)"
    )

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + "%(pathname)s" + reset,
        logging.CRITICAL: bold_red + format + "%(pathname)s" + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def setup_logger():
    # create logs directory if it doesn't exist
    Path(base_dir, "logs").mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("src")
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    info_file_handler = logging.FileHandler(filename=info_logs_target, encoding="utf-8")
    info_file_handler.setLevel(logging.INFO)

    warning_file_handler = logging.handlers.RotatingFileHandler(
        filename=warning_logs_target, encoding="utf-8", maxBytes=1048576, backupCount=5
    )
    warning_file_handler.setLevel(logging.WARNING)

    simple_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-4s] %(name)s: %(message)s", style="%"
    )
    detailed_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-4s] %(name)s: %(message)s call_trace=%(pathname)s L%(lineno)-4d",
        style="%",
    )

    console_handler.setFormatter(ColouredFormatter())
    info_file_handler.setFormatter(simple_formatter)
    warning_file_handler.setFormatter(detailed_formatter)

    logger.addHandler(console_handler)
    logger.addHandler(info_file_handler)
    logger.addHandler(warning_file_handler)
