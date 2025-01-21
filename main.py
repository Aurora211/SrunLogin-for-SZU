# ===== Srun Network Python Decrypter =====
# This script is used to decrypt the Srun Network login page and keep login to the network.
# Script Usage: 
# $ python main.py --manual
# =========================================
# Author: Aurora211
# Date: 2025-01-14
# Version: 0.1.0
# =========================================

# Command line arguments
import argparse
parser = argparse.ArgumentParser("Srun Network Python Decrypter")
parser.add_argument("--server", action="store_true", help="Run as server")
parser.add_argument("--client", action="store_true", help="Run as client")
parser.add_argument("--manual", action="store_true", help="Run manually, fully trust the configuration file")
args = parser.parse_args()

# Configuration file check and generation
import os
import yaml
if not os.path.exists('config.yaml'):
    print("Configuration file not found, generating a new one.")
    username = input("Please enter your username: ")
    password = input("Please enter your password: ")
    from Utils.Config import GenerateConfig
    GenerateConfig(username, password)
    print("Configuration file generated successfully.")

# Configuration file for the project
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Logging
import logging
from log import logging_console_handler, logging_file_handler
if config['logger']['file']['enable']:
    logging.basicConfig(
        level="DEBUG" if config['logger']['debug'] else "INFO",
        handlers=[
            logging_console_handler(
                debug  = config['logger']['debug'],
                format = config['logger']['format']
            ),
            logging_file_handler(
                debug        = config['logger']['file']['debug'],
                format       = config['logger']['format'],
                directory    = config['logger']['file']['directory'],
                file_prefix  = config['logger']['file']['prefix'],
                suffix       = config['logger']['file']['suffix'],
                when         = config['logger']['file']['when'],
                interval     = config['logger']['file']['interval'],
                backup_count = config['logger']['file']['backup_count'],
                encoding     = config['logger']['file']['encoding']
            )
        ]
    )
else:
    logging.basicConfig(
        level="DEBUG" if config['logger']['debug'] else "INFO",
        handlers=[
            logging_console_handler(
                debug  = config['logger']['debug'],
                format = config['logger']['format']
            )
        ]
    )
logger = logging.getLogger(__name__)

# Hello World Logging
logger.info("===== Welcom to Srun Network Python Decrypter =====")
# Mode Selection
if args.server:
    logger.info("Entering SERVER mode, you can modify the configuration using client without stopping the server.")
    raise NotImplementedError("Server mode is not implemented yet.")
elif args.client:
    logger.info("Entering CLIENT mode, you can modify the server configuration in this mode.")
    raise NotImplementedError("Client mode is not implemented yet.")
elif args.manual:
    logger.info("Entering MANUAL mode, no interaction in this mode.")
    from Mode.Manual import Manual
    manual = Manual(config)
    manual.run()
else:
    if config['settings']['default_mode'] == 0:
        logger.info("Entering MANUAL mode, no interaction in this mode.")
        from Mode.Manual import Manual
        manual = Manual(config)
        manual.run()
    elif config['settings']['default_mode'] == 1:
        logger.info("Entering SERVER mode, you can modify the configuration using client without stopping the server.")
        raise NotImplementedError("Server mode is not implemented yet.")
    elif config['settings']['default_mode'] == 2:
        logger.info("Entering CLIENT mode, you can modify the server configuration in this mode.")
        raise NotImplementedError("Client mode is not implemented yet.")
    else:
        logger.error("Invalid default mode, please check the configuration file.")
        exit(1)