# ===== Srun Network Python Decrypter =====
# This script is to check the network status.
# =========================================
# Author: Aurora211
# Date: 2025-01-14
# Version: 0.1.0
# =========================================

import logging
import requests

logger = logging.getLogger(__name__)

class Online:
    def __init__(self, **kwargs) -> None:
        # Essential Parameters
        self.config                 = kwargs.get("url_config", [{"url": "https://www.baidu.com", "key": "百度一下"}])
        # Optional Parameters
        self.timeout                = kwargs.get('timeout', 5)
        self.header                 = {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'User-Agent': kwargs.get('user_agent', "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
        }
    def Check(self, threshold: float = 0.5) -> bool:
        total_count = len(self.config)
        pass_count = 0
        for i in range(total_count):
            url = self.config[i]['url']
            key = self.config[i]['key']
            try:
                response = requests.get(url, headers=self.header, timeout=self.timeout)
                if key in response.text:
                    pass_count += 1
            except requests.exceptions.RequestException:
                logger.warning(f"Online Check Failed for {url}")
        return float(pass_count) / float(total_count) >= threshold, pass_count, total_count