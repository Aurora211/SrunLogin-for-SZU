# ===== Srun Network Python Decrypter =====
# 深圳大学Srun登录脚本主要登录逻辑
# DO NOT MODIFY THIS FILE UNLESS YOU KNOW WHAT YOU ARE DOING.
# =========================================
# Author: Aurora211
# Date: 2025-12-16
# Version: 2.0
# =========================================

import re
import json
import time
import logging
import requests
from typing import Union, List, Dict, Tuple, Any

from .DNS import CustomDnsRequestHandler
from .Encryption import Base64, MD5, SHA1, Xencode

logger = logging.getLogger("Aurora_SrunLogin")

def timestamp(millis: bool = True) -> int:
    """
    返回当前时间戳

    Args:
        millis (bool, optional): 是否返回毫秒级时间戳. Defaults to True.

    Returns:
        int: 时间戳
    """
    if millis:
        return int(time.time() * 1000)
    else:
        return int(time.time())

class SrunLogin:
    def __init__(
            self,
            portal_config: Dict[str, Any],
            parameters: Dict[str, Dict[str, Any]] = {},
            parse_regex: Dict[str, str]           = {},
            nameservers: List[str]                = ['223.5.5.5'],
            hosts: Dict[str, List[str]]           = {},
            proxies: Dict[str, Union[str, None]]  = {},
            **kwargs
    ) -> None:
        """
        创建 SrunLogin 对象，支持针对深圳大学 Srun 的登录

        Args:
            portal_config (Dict[str, Any]):                   Srun 入口页面配置
            parameters (Dict[str, Dict[str, Any]], optional): 请求固定参数. Defaults to {}.
            parse_regex (Dict[str, str], optional):           页面解析正则表达式. Defaults to {}.
            nameservers (List[str], optional):                DNS服务器列表. Defaults to ['223.5.5.5'].
            hosts (Dict[str, List[str]], optional):           主机映射字典. Defaults to {}.
            proxies (Dict[str, Union[str, None]], optional):  代理. Defaults to {}.
            **kwargs:                                         其它参数
        """
        # Srun 入口配置
        self.domain: str                          = portal_config.get("domain", "https://net.szu.edu.cn") # Srun 门户根配置
        self.urls: Dict[str, str]                 = portal_config.get("urls", {})                         # Srun 门户页面 URL
        self.parse_regex: Dict[str, str]          = parse_regex # 页面解析正则表达式
        self.parameter: Dict[str, Dict[str, Any]] = parameters  # 请求固定参数

        # 程序配置
        self.placeholder: str                     = kwargs.get("placeholder", "placeholder")    # 程序过程中的占位符
        self.skip_ssl_verify: bool                = kwargs.get("verify", False)                 # 是否跳过 SSL 验证
        self.timeout: float                       = kwargs.get("timeout", 2.0)                  # 请求超时时间
        self.proxies: Dict[str, Union[str, None]] = {                                           # 代理
            "http":  None if proxies.get("http",  None) is None else proxies.get("http",  None),
            "https": None if proxies.get("https", None) is None else proxies.get("https", None)
        }
        self.header: Dict[str, Any]               = {                                           # 请求头
            "Cache-Control": "no-cache",
            "Pragma":        "no-cache",
            "User-Agent":    kwargs.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"),
        }
        # DNS 配置
        self.dns_handler: CustomDnsRequestHandler = CustomDnsRequestHandler(
            nameservers = nameservers,
            hosts       = hosts,
        )
        logger.info(f"DNS 初始化完成")
        # 解析动态配置
        self.srun_acid, self.srun_ip = self.srun_config()
        logger.info(f"动态配置获取成功。Srun ACID: {self.srun_acid}, Srun IP: {self.srun_ip}")
    def login(self, username: str, password: str, lan: bool = False) -> Tuple[bool, str]:
        """
        登录 Srun

        Args:
            username (str): 用户名
            password (str): 密码

        Returns:
            bool: 登录是否成功
            str:  结果信息提示
        """
        try:
            login_parameter: Dict[str, Any] = self.parameter.get("login", {})
            if lan:
                username = username + "@xyw"
                logger.info(f"使用 LAN 模式登录")
            else:
                username = username + "@hlw"
                logger.info(f"使用 WAN 模式登录")
            # ==================================================
            self.srun_acid, self.srun_ip = self.srun_config()
            logger.info(f"动态配置获取成功。Srun ACID: {self.srun_acid}, Srun IP: {self.srun_ip}")
            # ==================================================
            challenge: str = self.srun_challenge(
                username = username,
            )
            logger.debug(f"获取到的 Challenge: {challenge}")
            # ==================================================
            _, info_encrypted = self.srun_info(
                username  = username,
                password  = password,
                challenge = challenge,
            )
            logger.debug(f"加密的 Info: {info_encrypted}")
            # ==================================================
            password_hash, password_hash_encrypted = self.srun_password(
                password  = password,
                challenge = challenge,
            )
            logger.debug(f"生成的 Password Hash: {password_hash_encrypted}")
            # ==================================================
            _, checksum_encrypted = self.srun_checksum(
                username       = username,
                password_hash  = password_hash,
                n              = login_parameter.get("n", 200),
                vtype          = login_parameter.get("vtype", 1),
                info_encrypted = info_encrypted,
                challenge      = challenge,
            )
            logger.debug(f"生成的 Checksum: {checksum_encrypted}")
            # ==================================================
            login_api_url: str = self.domain + self.urls.get("login", "/cgi-bin/srun_portal")
            login_api_response: requests.Response = self.dns_handler.request(
                method            = "GET",
                with_dns_resolver = True,
                url               = login_api_url,
                headers           = self.header,
                timeout           = self.timeout,
                verify            = not self.skip_ssl_verify,
                proxies           = self.proxies.copy(),
                params            = {
                    "action":       login_parameter.get("action", "login"),
                    "username":     username,
                    "password":     password_hash_encrypted,
                    "os":           login_parameter.get("os", "Unknow OS"),
                    "name":         login_parameter.get("name", "Unknow OS"),
                    "double_stack": login_parameter.get("double_stack", 0),
                    "chksum":       checksum_encrypted,
                    "info":         info_encrypted,
                    "ac_id":        self.srun_acid,
                    "ip":           self.srun_ip,
                    "n":            login_parameter.get("n", 200),
                    "type":         login_parameter.get("vtype", 1),
                    "callback":     self.placeholder,
                    "t":            timestamp(),
                }
            )
            if login_api_response.status_code != 200:
                raise Exception(f"登录接口返回错误代码: {login_api_response.status_code}")
            login_api_response_text: str = login_api_response.text.strip()
            
            # 解析登录接口返回数据
            if len(login_api_response_text) <= len(self.placeholder) + 1:
                raise Exception("登录接口返回空数据")
            login_api_raw_data: str = login_api_response_text[len(self.placeholder) + 1:-1]
            login_api_data: Dict[str, Any] = json.loads(login_api_raw_data)

            # 检查登录结果
            if "error" in login_api_data and login_api_data["error"] == "ok":
                return True, "登录成功"
            else:
                return False, login_api_data["error_msg"] if "error_msg" in login_api_data else "登录失败，未知原因"
            # ==================================================
        except Exception as e:
            logger.critical(f"Srun 登录失败: {str(e)}")
            return False, str(e)
    def status(self) -> Tuple[bool, Dict[str, Any], Dict[str, Any]]:
        """
        获取 Srun 登录状态

        Returns:
            bool: Srun 登录状态
            Dict[str, Any]: Srun 登录数据
            Dict[str, Any]: Srun 原始登录数据
        """
        try:
            info_api_url: str = self.domain + self.urls.get("info", "/cgi-bin/rad_user_info")
            info_api_response: requests.Response = self.dns_handler.request(
                method            = "GET",
                with_dns_resolver = True,
                url               = info_api_url,
                headers           = self.header,
                timeout           = self.timeout,
                verify            = not self.skip_ssl_verify,
                proxies           = self.proxies.copy(),
                params            = {
                    "callback": self.placeholder,
                    "t": timestamp()
                }
            )
            if info_api_response.status_code != 200:
                raise Exception(f"获取 Srun 登录状态失败，接口返回错误代码: {info_api_response.status_code}")
            info_api_response_text: str = info_api_response.text.strip()
            # 解析登录接口返回数据
            if len(info_api_response_text) <= len(self.placeholder) + 1:
                raise Exception("获取 Srun 登录状态失败，接口返回空数据")
            info_api_raw_data: str = info_api_response_text[len(self.placeholder) + 1:-1]
            info_api_data: Dict[str, Any] = json.loads(info_api_raw_data)
            # 解析解析后的登录数据
            devices: Dict[str, Any] = json.loads(info_api_data["online_device_detail"])
            info_data: Dict[str, Any] = {
                "user":     info_api_data["user_name"],
                "duration": info_api_data["sum_seconds"],
                "traffic":  info_api_data["sum_bytes"],
                "type":     info_api_data["products_name"],
                "ip":       info_api_data["online_ip"],
                "devices":  devices
            }
            # 返回数据
            if "error" in info_api_data and info_api_data["error"] == "ok":
                return True, info_data, info_api_data
            else:
                return False, info_data, info_api_data
        except Exception as e:
            logger.critical(f"获取 Srun 登录状态失败: {str(e)}")
            return False, {}, {}

    def srun_config(self) -> Tuple[str, str]:
        """
        获取 Srun IP 配置

        Returns:
            str: Srun AC ID 配置
            str: Srun IP 配置
        """
        # 获取 Srun 入口页面
        start_page_url: str = self.domain + self.urls.get("start", "/srun_portal_pc")
        start_page_response: requests.Response = self.dns_handler.request(
            method            = "GET",
            with_dns_resolver = True,
            url               = start_page_url,
            headers           = self.header,
            timeout           = self.timeout,
            verify            = not self.skip_ssl_verify,
            proxies           = self.proxies.copy(),
            params            = {"t": timestamp()}
        )
        if start_page_response.status_code != 200:
            raise Exception("获取 Srun 入口页面失败")
        start_page_response_text: str = start_page_response.text
        # 解析 Srun 入口页面
        start_page_regex: str            = self.parse_regex.get("start", r"<script>[ \n]*var CONFIG = \\{([A-Za-z0-9:\\\\',\"\\.\\-|\\{/\\} \n]*)\\};[ \n]*</script>")
        start_page_raw_config: List[str] = re.findall(start_page_regex, start_page_response_text)
        if len(start_page_raw_config) == 0:
            raise Exception("解析 Srun 入口页面失败，无法获取 Srun IP 配置信息")
        start_page_raw_config: List[str] = start_page_raw_config[0].split("\n")
        # 解析 Srun IP 配置
        start_page_config: Dict[str, Any] = {}
        for line in start_page_raw_config:
            line = line.strip()
            if len(line) == 0:
                continue

            key, value = line.split(":", 1)
            key = key.strip().strip()
            value = value[:-1].strip().strip() if value.endswith(",") else value.strip().strip()
            if (value.startswith("'") and value.endswith("'")) or (value.startswith("\"") and value.endswith("\"")):
                value = "" if len(value) == 2 else value[1:-1]
            if value.lower() == "false":
                value = False
            elif value.lower() == "true":
                value = True
            elif value.startswith("{") and value.endswith("}"):
                value = json.loads(value)
            start_page_config[key] = value
        # 获取 Srun IP
        return start_page_config["acid"], start_page_config["ip"]
    def srun_challenge(self, username: str) -> str:
        """
        获取 Srun 挑战码

        Args:
            username (str): 用户名
            ip (str):       Srun IP

        Returns:
            str: 挑战码
        """
        challenge_api_url: str = self.domain + self.urls.get("challenge", "/cgi-bin/get_challenge")
        challenge_api_response: requests.Response = self.dns_handler.request(
            method            = "GET",
            with_dns_resolver = True,
            url               = challenge_api_url,
            headers           = self.header,
            timeout           = self.timeout,
            verify            = not self.skip_ssl_verify,
            proxies           = self.proxies.copy(),
            params            = {
                "callback": self.placeholder,
                "username": username,
                "ip": self.srun_ip,
                "t": timestamp()
            }
        )
        if challenge_api_response.status_code != 200:
            raise Exception("获取 Srun 挑战码失败")
        challenge_api_response_text: str = challenge_api_response.text.strip()
        # 解析 Srun 挑战码
        if len(challenge_api_response_text) <= len(self.placeholder) + 1:
            raise Exception("解析 Srun 挑战码失败，返回值为空")
        challenge_api_raw_config: str = challenge_api_response_text[len(self.placeholder) + 1:-1]
        challenge_api_config: Dict[str, Any] = json.loads(challenge_api_raw_config)
        # 获取 Srun 挑战码
        return challenge_api_config["challenge"]
    def srun_info(self, username: str, password: str, challenge: str) -> Tuple[str, str]:
        """
        生成 Srun 登录信息，并加密

        Args:
            username (str): 用户名
            password (str): 密码
            ip (str):       Srun IP
            acid (str):     Srun ID
            challenge (str):挑战码

        Returns:
            str: Srun 登录信息
            str: 加密后的 Srun 登录信息
        """
        params = {
            "username": username,
            "password": password,
            "ip":       self.srun_ip,
            "acid":     self.srun_acid,
            "enc_ver":  "srun_bx1"
        }
        info: str = re.sub("'", '"', str(params))
        info: str = re.sub(" ", "", info)
        info_encrypted: str = "{SRBX1}" + str(Base64(Xencode(info, challenge)))
        return info, info_encrypted
    def srun_password(self, password: str, challenge: str) -> Tuple[str, str]:
        """
        生成 Srun 密码，并加密

        Args:
            password (str): 密码
            challenge (str):挑战码

        Returns:
            str: Srun 密码
            str: 加密后的 Srun 密码
        """
        password_hash: str = MD5(password, challenge)
        return password_hash, "{MD5}" + password_hash
    def srun_checksum(self, username: str, password_hash: str, n: str, vtype: str, info_encrypted: str, challenge: str) -> Tuple[str, str]:
        """
        生成 Srun 校验码，并加密

        Args:
            username (str):       用户名
            password_hash (str):  加密后的 Srun 密码
            n (str):              未知
            vtype (str):          未知
            info_encrypted (str): 加密后的 Srun 登录信息
            challenge (str):      挑战码

        Returns:
            str: Srun 校验码
            str: 加密后的 Srun 校验码
        """
        checksum: str = \
            str(challenge) + str(username       ) + \
            str(challenge) + str(password_hash  ) + \
            str(challenge) + str(self.srun_acid ) + \
            str(challenge) + str(self.srun_ip   ) + \
            str(challenge) + str(n              ) + \
            str(challenge) + str(vtype          ) + \
            str(challenge) + str(info_encrypted )
        checksum_encrypted: str = SHA1(checksum)
        return checksum, checksum_encrypted


