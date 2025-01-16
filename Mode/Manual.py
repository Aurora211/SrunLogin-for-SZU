# ===== Srun Network Python Decrypter =====
# Description: This file contains the Manual Mode class, which is used to login to the network manually.
# =========================================
# Author: Aurora211
# Date: 2025-01-14
# Version: 0.1.0
# =========================================

import gc
import time
import logging

from typing import Dict

from SrunLogin import SrunLogin
from Utils.Online import Online

logger = logging.getLogger(__name__)

class Manual:
    def __init__(self, yaml_config: Dict) -> None:
        self.config = yaml_config

        self.username               = self.config['auth']['username']
        self.password               = self.config['auth']['password']

        self.online_check_duration  = self.config['settings']['online_check_duration']

        self.srun = SrunLogin(
            login_page_url          = self.config['meta']['portal']['domain'] + self.config['meta']['portal']['login_page'],
            challenge_api_url       = self.config['meta']['portal']['domain'] + self.config['meta']['portal']['challenge_api'],
            login_api_url           = self.config['meta']['portal']['domain'] + self.config['meta']['portal']['login_api'],
            callback_parse_regex    = self.config['meta']['portal']['regex']['callback'],
            page_parse_regex        = self.config['meta']['portal']['regex']['page'],
            callback_str            = self.config['meta']['portal']['callback'],
            skip_ssl_verify         = self.config['settings']['skip_ssl_verify'],
            request_timeout         = self.config['settings']['request_timeout'],
            login_fixed_parameters  = self.config['meta']['portal']['login_parameters'],
            user_agent              = self.config['meta']['user_agent']['request']
        )
        self.online = Online(
            url_config              = self.config['meta']['online_check'],
            timeout                 = self.config['settings']['request_timeout']
        )

        self.gc_collect_interval    = self.config['settings']['gc_collect_interval']
        self.stop = False
    def run(self) -> None:
        gc_collect_counter = 0
        last_online_check = False
        while not self.stop:
            gc_collect_counter += 1
            check_state, check_pass, check_count = self.online.Check(0.75)
            if check_state:
                if not last_online_check:
                    logger.info("Online Check Passed with {} Passes".format(check_pass))
                last_online_check = True
            else:
                logger.warning("Online Check Failed, Conducting Login")
                state, response, info = self.srun.login(self.username, self.password)
                if state:
                    logger.info("Login Success")
                else:
                    logger.error("Login Failed")
                last_online_check = False
            if gc_collect_counter >= self.gc_collect_interval:
                gc.collect()
                gc_collect_counter = 0
            time.sleep(self.online_check_duration)
