# ===== Srun Network Python Decrypter =====
# This script is the logging module for the project.
# =========================================
# Author: Aurora211
# Date: 2025-01-14
# Version: 0.1.0
# =========================================

import os
import re
import logging
from logging.handlers import TimedRotatingFileHandler

def logging_console_handler(
        format : str  = '[%(asctime)s][%(levelname)s] - %(message)s',
        debug  : bool = False
) -> logging.StreamHandler:
    handler = logging.StreamHandler()
    if debug: handler.setLevel(logging.DEBUG)
    else: handler.setLevel(logging.INFO)
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)
    return handler

def logging_file_handler(
        directory    : str,
        file_prefix  : str,
        format       : str  = '[%(asctime)s][%(levelname)s] - %(message)s',
        suffix       : str  = '%Y-%m-%d.log',
        when         : str  = 'MIDNIGHT',
        interval     : int  = 1,
        backup_count : int  = 30,
        encoding     : str  = 'utf-8',
        debug        : bool = False
) -> logging.FileHandler:
    if os.path.exists(directory) is False:
        os.makedirs(directory)
    handler = TimedRotatingFileHandler(
        os.path.join(directory, file_prefix),
        when        = when,
        interval    = interval,
        backupCount = backup_count,
        encoding    = encoding
    )
    handler.suffix = suffix
    handler.extMatch = re.compile(r'^\d{4}-\d{2}-\d{2}.log$')
    if debug: handler.setLevel(logging.DEBUG)
    else: handler.setLevel(logging.INFO)
    formatter = logging.Formatter(format)
    handler.setFormatter(formatter)
    return handler
