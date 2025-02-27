# ===== Srun Network Python Decrypter =====
# Main login strategy for Srun Network
# DO NOT MODIFY THIS FILE UNLESS YOU KNOW WHAT YOU ARE DOING.
# =========================================
# Author: Aurora211
# Date: 2025-01-14
# Version: 0.1.0
# =========================================

import re
import json
import time
import logging
import requests
from typing import List, Dict, Tuple

if __name__ == "__main__":
    from DNS import CustomDnsRequestHandler
    from Encryption import Base64, MD5, SHA1, Xencode
else:
    from .DNS import CustomDnsRequestHandler
    from .Encryption import Base64, MD5, SHA1, Xencode

logger = logging.getLogger(__name__)

class SrunLogin:
    def __init__(
            self,
            login_page_url             : str = "https://net.szu.edu.cn/srun_portal_pc",
            challenge_api_url          : str = "https://net.szu.edu.cn/cgi-bin/get_challenge",
            login_api_url              : str = "https://net.szu.edu.cn/cgi-bin/srun_portal",
            page_parse_regex           : str = r"<script>[ \n]+var CONFIG = [\{ \n]+([A-Za-z0-9 :'\",\.\-|/\n\{\}]+)\n[ ]+\};[ \n]+</script>",
            callback_parse_regex       : str = r"({[A-Za-z0-9\":,_\. ]+})",
            callback_str               : str = "callback",
            login_fixed_parameters     : Dict = {
                "n"            : "200",
                "type"         : "1",
                "acid"         : "2",
                "enc"          : "srun_bx1",
                "os"           : "Windows 10",
                "name"         : "windows",
                "double_stack" : False,
            },
            skip_ssl_verify            : bool = False,
            timeout                    : int = 5,
            add_time_stamp_to_callback : bool = True,
            http_proxy                 : str | None = None,
            https_proxy                : str | None = None,
            login_success_key          : str = "suc_msg",
            login_success_value        : str = "login_ok",
            user_agent                 : str = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            nameservers                : List[str] = ["192.168.247.6", "192.168.247.26"],
            hosts                      : Dict[str, str] = {},
            **kwargs
    ) -> None:
        # Essential URLs
        self.url_login_page    = login_page_url
        self.url_challenge_api = challenge_api_url
        self.url_login_api     = login_api_url
        # Essential Regex
        self.regex_page     = page_parse_regex
        self.regex_callback = callback_parse_regex
        self.callback_str   = callback_str
        # Essential Parameters
        self.login_fixed_parameters = login_fixed_parameters
        # Optional Parameters
        self.skip_ssl_verify            = skip_ssl_verify
        self.time_out                   = timeout
        self.add_time_stamp_to_callback = add_time_stamp_to_callback
        self.proxys                     = {
            "http"  : None if http_proxy  == "None" else http_proxy,
            "https" : None if https_proxy == "None" else https_proxy
        }
        self.login_success_keypair      = (
            login_success_key,
            login_success_value
        )
        self.header                     = {
            "Cache-Control" : "no-cache",
            "Pragma"        : "no-cache",
            "User-Agent"    : user_agent
        }
        # DNS Handler
        self.dns_handler                = CustomDnsRequestHandler(
            nameservers = nameservers,
            hosts       = hosts,
        )
    def login(
            self,
            username: str,
            password: str,
    ):
        info = {
            "LoginIP"               : None,
            "ChallengeToken"        : None,
            "EncryptedLoginInfo"    : None,
            "EncryptedPasswordInfo" : None,
            "EncryptedChecksumInfo" : None
        }
        # Stage 1
        logger.debug("Stage 1: Parse login page to get login config")
        login_config    = self.__get_login_config()     # Get login config
        login_ip        = self.__get_ip(login_config)   # Get login ip
        logger.debug(f"Login IP: {login_ip}")
        info["LoginIP"] = login_ip
        # Stage 2
        logger.debug("Stage 2: Get challenge token")
        challenge_config    = self.__get_challenge_config(username, login_ip, self.add_time_stamp_to_callback)          # Get challenge config
        challenge_token     = self.__get_token(username, login_ip, challenge_config, self.add_time_stamp_to_callback)   # Get challenge token
        logger.debug(f"Challenge Token: {challenge_token}")
        info["ChallengeToken"] = challenge_token
        # Stage 3
        logger.debug("Stage 3: Generate login info, password hash, checksum")
        login_info              = self.__generate_info(username, password, login_ip, self.login_fixed_parameters["acid"], self.login_fixed_parameters["enc"])   # Generate login info
        encrypted_login_info    = self.__encrypt_info(login_info, challenge_token, self.login_fixed_parameters["enc"])                                          # Encrypt login info
        logger.debug(f"Encrypted Login Info: {encrypted_login_info}")
        info["EncryptedLoginInfo"] = encrypted_login_info
        password_info           = self.__generate_password_hash(password, challenge_token)                                                                      # Generate password hash
        encrypted_password_info = self.__encrypt_password_hash(password_info)                                                                                   # Encrypt password hash
        logger.debug(f"Encrypted Password Info: {encrypted_password_info}")
        info["EncryptedPasswordInfo"] = encrypted_password_info
        checksum_info           = self.__generate_checksum(                                                                                                     # Generate checksum
            challenge_token,
            username,
            password_info,
            self.login_fixed_parameters["acid"],
            login_ip,
            self.login_fixed_parameters["n"],
            self.login_fixed_parameters["type"],
            encrypted_login_info
        )
        encrypted_checksum_info = self.__encrypt_checksum(checksum_info)                                                                                        # Encrypt checksum
        logger.debug(f"Encrypted Checksum Info: {encrypted_checksum_info}")
        info["EncryptedChecksumInfo"] = encrypted_checksum_info
        # Stage 4
        logger.debug("Stage 4: Send login request")
        login_request_response  = self.__send_login_request(                                                                                                    # Send login request
            username,
            encrypted_password_info,
            encrypted_checksum_info,
            encrypted_login_info,
            self.login_fixed_parameters["acid"],
            login_ip,
            self.login_fixed_parameters["os"],
            self.login_fixed_parameters["name"],
            self.login_fixed_parameters["double_stack"],
            self.login_fixed_parameters["n"],
            self.login_fixed_parameters["type"],
            self.add_time_stamp_to_callback
        )
        logger.debug(f"Login Request Response: {login_request_response.text}")
        # Stage 5
        logger.debug("Stage 5: Parse login response")
        login_state, login_status   = self.__parse_login_response(login_request_response)                                                                       # Parse login response
        logger.debug(f"Login State: {login_state}")
        return login_state, login_status, info

    def __get_login_page(self) -> requests.Response:
        return self.dns_handler.request_with_dns_resolver(
            "GET",
            url     = self.url_login_page,
            headers = self.header,
            timeout = self.time_out,
            verify  = not self.skip_ssl_verify,
            proxies = self.proxys
        )
    def __get_login_config(self) -> Dict:
        config = {}
        login_page = self.__get_login_page().text
        config_raw = re.search(self.regex_page, login_page).group(1).split('\n')
        for line in config_raw:
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
            config[key] = value
        logger.debug(f"Login Config: {config}")
        return config
    def __get_ip(self, login_config: Dict | None = None) -> str:
        if login_config is None:
            login_config = self.__get_login_config()
        return login_config["ip"]
    
    def __get_challenge_api(self, username: str, ip: str, add_time_stamp_to_callback: bool = True) -> requests.Response:
        params = {
            "callback": self.callback_str + "_" + str(int(time.time() * 1000)) if add_time_stamp_to_callback else self.callback_str,
            "username": username,
            "ip": ip,
            "_": int(time.time() * 1000)
        }
        return self.dns_handler.request_with_dns_resolver(
            "GET",
            url     = self.url_challenge_api,
            params  = params,
            headers = self.header,
            timeout = self.time_out,
            verify  = not self.skip_ssl_verify,
            proxies = self.proxys
        )
    def __get_challenge_config(self, username: str, ip: str, add_time_stamp_to_callback: bool = True) -> str:
        challenge = self.__get_challenge_api(username, ip, add_time_stamp_to_callback).text
        config_raw = re.search(self.regex_callback, challenge).group(1)
        config = json.loads(config_raw)
        logger.debug(f"Challenge Config: {config}")
        return config
    def __get_token(self, username: str, ip: str, challenge_config: Dict | None = None, add_time_stamp_to_callback: bool = True) -> str:
        if challenge_config is None:
            challenge_config = self.__get_challenge_config(username, ip, add_time_stamp_to_callback)
        return challenge_config["challenge"]
    
    def __generate_info(self, username: str, password: str, ip: str, acid: str, enc_ver: str = "srun_bx1") -> str:
        if enc_ver != "srun_bx1":
            raise ValueError(f"Unsupported enc_ver: {enc_ver}")
        params = {
            "username" : username,
            "password" : password,
            "ip"       : ip,
            "acid"     : acid,
            "enc_ver"  : enc_ver
        }
        info = re.sub("'", '"', str(params))
        generated_info = re.sub(" ", "", info)
        logger.debug(f"Generated Info: {generated_info}")
        return generated_info
    def __encrypt_info(self, info: str, token: str, enc_ver: str = "srun_bx1") -> str:
        if enc_ver != "srun_bx1":
            raise ValueError(f"Unsupported enc_ver: {enc_ver}")
        if enc_ver == "srun_bx1":
            encrypted_info = "{SRBX1}" + Base64(Xencode(info, token))
        logger.debug(f"Encrypted Info: {encrypted_info}")
        return encrypted_info

    def __generate_password_hash(self, password: str, token: str) -> str:
        password_hash = MD5(password, token)
        logger.debug(f"Password Hash: {password_hash}")
        return password_hash
    def __encrypt_password_hash(self, password_hash: str) -> str:
        encrypted_password_hash = "{MD5}" + password_hash
        logger.debug(f"Encrypted Password Hash: {encrypted_password_hash}")
        return encrypted_password_hash

    def __generate_checksum(
            self,
            token: str,
            username: str,
            encrypted_password_hash: str,
            acid: str,
            ip: str,
            n: str,
            vtype: str,
            encrypted_info: str
    ) -> str:
        checksum = \
            token + username + \
            token + encrypted_password_hash + \
            token + acid + \
            token + ip + \
            token + n + \
            token + vtype + \
            token + encrypted_info
        return checksum
    def __encrypt_checksum(self, checksum: str) -> str:
        encrypted_checksum = SHA1(checksum)
        logger.debug(f"Encrypted Checksum: {encrypted_checksum}")
        return encrypted_checksum

    def __send_login_request(
            self,
            username: str,
            encrypted_password_hash: str,
            encrypted_checksum: str,
            encrypted_info: str,
            acid: str,
            ip: str,
            os: str = "5WTeKixbejr3",
            name: str = "kCtJDJ",
            double_stack: bool = False,
            n: str = "200",
            vtype: str = "1",
            add_time_stamp_to_callback: bool = True,
    ) -> requests.Response:
        params = {
            "callback"     : self.callback_str + "_" + str(int(time.time() * 1000)) if add_time_stamp_to_callback else self.callback_str,
            "action"       : "login",
            "username"     : username,
            "password"     : encrypted_password_hash,
            "os"           : os,
            "name"         : name,
            "nas_ip"       : "",
            "double_stack" : "0" if not double_stack else "1",
            "chksum"       : encrypted_checksum,
            "info"         : encrypted_info,
            "ac_id"        : acid,
            "ip"           : ip,
            "n"            : n,
            "type"         : vtype,
            "captchaVal"   : "",
            "_"            : int(time.time() * 1000)
        }
        return self.dns_handler.request_with_dns_resolver(
            "GET",
            url     = self.url_login_api,
            params  = params,
            headers = self.header,
            timeout = self.time_out,
            verify  = not self.skip_ssl_verify,
            proxies = self.proxys
        )
    def __parse_login_response(self, response: requests.Response) -> Dict:
        response_text = response.text
        status_raw = re.search(self.regex_callback, response_text).group(1)
        status = json.loads(status_raw)
        logger.debug(f"Login Data: {status}")
        if self.login_success_keypair[0] in status:
            if status[self.login_success_keypair[0]] == self.login_success_keypair[1]:
                return True, status
        return False, status

if __name__ == "__main__":
    srun = SrunLogin()
    srun.login(
        "",
        ""
    )