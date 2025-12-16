# ===== Srun Network Python Decrypter =====
# 深圳大学 Srun 登陆器统一入口
# =========================================
# Author: Aurora211
# Date: 2025-12-16
# Version: 2.0
# =========================================

import os
import gc
import yaml
import time
import logging
import argparse
from getpass import getpass
from typing import Optional, Union, Callable, List, Dict, Tuple, Any, cast

from Config import GenerateConfig, Args
from Log import logging_console_handler, logging_file_handler
from SrunLogin import SrunLogin

parser = argparse.ArgumentParser("Srun Network Python Decrypter")
parser.add_argument("-u", "--username",        default=None,     type=str, help="校园网用户名")
parser.add_argument("-p", "--password",        default=None,     type=str, help="校园网密码")
parser.add_argument("-l", "--lan",             action="store_true",        help="是否使用 LAN 模式登录")
parser.add_argument("-d", "--daemon",          action="store_true",        help="是否以守护进程方式运行")
parser.add_argument(      "--skip-ssl-verify", action="store_true",        help="是否跳过 SSL 证书验证")
parser.add_argument("-t", "--timeout",         default=2,        type=int, help="请求超时时间, 默认为 2 秒")
parser.add_argument(      "--duration",        default=5,        type=int, help="在线检测时间间隔, 默认为 5 秒")
parser.add_argument(      "--debug",           action="store_true",        help="是否启用调试模式")
parser.add_argument(      "--log-directory",   default="./logs", type=str, help="日志文件保存目录")
parser.add_argument(      "--log-keep-count",  default=30,       type=int, help="日志文件保留数量")
args: Args = cast(Args, parser.parse_args())

# 生成默认配置文件
if not os.path.exists('config.yaml'):
    GenerateConfig(overwrite=False)
    print("Configuration file generated successfully.")

# 加载配置
with open('config.yaml', 'r', encoding='utf-8') as f:
    config: Dict[str, Any] = yaml.safe_load(f)
auth_config: Dict[str, Any]         =         config.get("auth",     {}) # 校园网认证相关配置
setting_config: Dict[str, Any]      =         config.get("settings", {}) # 程序设置
logging_config: Dict[str, Any]      =         config.get("logger",   {}) # 日志设置
logging_file_config: Dict[str, Any] = logging_config.get("file",     {}) # 日志文件设置
dns_config: Dict[str, Any]          =         config.get("dns",      {}) # DNS设置
portal_config: Dict[str, Any]       =         config.get("portal",   {}) # Srun 入口配置
proxy_config: Dict[str, Any]        =         config.get("proxy",    {}) # 代理设置
if args.username is not None: auth_config['username']             = args.username
if args.password is not None: auth_config['password']             = args.password
if args.lan:                  auth_config['lan']                  = True
if args.skip_ssl_verify:      setting_config['skip_ssl_verify']   = True
if args.timeout:              setting_config['timeout']           = args.timeout
if args.duration:             setting_config['duration']          = args.duration
if args.debug:                logging_config['debug']             = True
if args.debug:                logging_file_config['debug']        = True
if args.log_directory:        logging_file_config['enable']       = True
if args.log_directory:        logging_file_config['directory']    = args.log_directory
if args.log_keep_count:       logging_file_config['backup_count'] = args.log_keep_count


# Logging
handlers: List[logging.Handler] = [
    logging_console_handler(
        debug  = logging_config.get("debug", False),
        format = logging_config.get("format", "[%(asctime)s][%(levelname)s] - %(message)s"),
    )
]
if logging_file_config.get("enable", False):
    handlers.append(
        logging_file_handler(
            format       = logging_config.get("format", "[%(asctime)s][%(levelname)s] - %(message)s"),
            debug        = logging_file_config.get("debug",        False),
            directory    = logging_file_config.get("directory",    "./logs"),
            file_prefix  = logging_file_config.get("prefix",       "srun_decrypter"),
            suffix       = logging_file_config.get("suffix",       "%Y-%m-%d.log"),
            when         = logging_file_config.get("when",         "MIDNIGHT"),
            interval     = logging_file_config.get("interval",     1),
            backup_count = logging_file_config.get("backup_count", 30),
            encoding     = logging_file_config.get("encoding",     "utf-8"),
        )
    )
logging.basicConfig(level=logging.DEBUG if logging_config.get("debug", False) else logging.INFO, handlers=handlers)
logger = logging.getLogger("Aurora_Srun_Main")

srun: SrunLogin = SrunLogin(
    portal_config = portal_config.get("api",       {}),
    parameters    = portal_config.get("parameter", {}),
    parse_regex   = portal_config.get("regex",     {}),
    nameservers   = dns_config.get("nameservers",  ["192.168.247.6", "192.168.247.26"]),
    hosts         = dns_config.get("hosts",        {}),
    proxies       = proxy_config.get("login",      {}),
)

if args.daemon:
    # ==================================================
    #  ____
    # |  _ \  __ _  ___ _ __ ___   ___  _ __
    # | | | |/ _` |/ _ \ '_ ` _ \ / _ \| '_ \
    # | |_| | (_| |  __/ | | | | | (_) | | | |
    # |____/ \__,_|\___|_| |_| |_|\___/|_| |_|
    # ==================================================
    logger.info("进入守护进程模式，请勿关闭窗口，开始后台运行...")

    username: Optional[str] = auth_config.get("username", None)
    password: Optional[str] = auth_config.get("password", None)
    lan_mode: bool          = auth_config.get("lan", False)

    if username is None or password is None:
        logger.error("程序启动时需要提供校园网用户名和密码")
        username = input("校园网用户名: ")
        password = getpass("校园网密码: ")
    
    interval: int = setting_config.get("duration", 5)
    gc_counter: int = 0
    gc_collect_interval: int = setting_config.get("gc_collect_interval", 60)
    try:
        flag: bool = False
        while True:
            eth_status, eth_info, eth_full_info = srun.status()
            if not eth_status:
                flag = False
                logger.warning(f"侦测到未登录状态，尝试登录...")
                request_status, message = srun.login(username, password, lan_mode)
                if not request_status:
                    logger.error(f"登录请求失败：{message}")
                
                eth_status, eth_info, eth_full_info = srun.status()
                if not eth_status:
                    logger.error(f"登录失败：{message}")
                else:
                    logger.info(f"登录成功。")
                    logger.info(f"========== ETH 信息 ==========")
                    logger.info(f"用户名: \t{eth_info.get('user', '未知')}")
                    logger.info(f"IP 地址: \t{eth_info.get('ip', '未知')}")
                    logger.info(f"类型: \t{eth_info.get('type', '未知')}")
                    logger.info(f"流量: \t{eth_info.get('traffic', '未知')}")
                    logger.info(f"时长: \t{eth_info.get('duration', '未知')}")
                    logger.info(f"在线数: \t{len(eth_info.get('devices', '未知'))}")
                    logger.info(f"==============================")
            else:
                if flag is False:
                    flag = True
                    logger.info(f"已登录状态，守护进程保护网络中...")

            gc_counter += 1
            if gc_counter >= gc_collect_interval:
                acid, ip = srun.srun_config()
                srun.srun_acid = acid
                srun.srun_ip = ip
                logger.info(f"动态配置获取成功。Srun ACID: {srun.srun_acid}, Srun IP: {srun.srun_ip}")
                gc.collect()
                gc_counter = 0
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("用户中断守护进程，退出...")
        exit(0)
else:
    # ==================================================
    #  __  __                         _
    # |  \/  | __ _ _ __  _   _  __ _| |
    # | |\/| |/ _` | '_ \| | | |/ _` | |
    # | |  | | (_| | | | | |_| | (_| | |
    # |_|  |_|\__,_|_| |_|\__,_|\__,_|_|
    # ==================================================
    logger.info("进入登录模式")
    
    username: Optional[str] = auth_config.get("username", None)
    password: Optional[str] = auth_config.get("password", None)
    lan_mode: bool          = auth_config.get("lan", False)

    if username is None or password is None:
        logger.error("程序启动时需要提供校园网用户名和密码")
        username = input("校园网用户名: ")
        password = getpass("校园网密码: ")

    request_status, message = srun.login(username, password, lan_mode)
    if not request_status:
        logger.error(f"登录失败: {message}")
        exit(1)
    
    eth_status, eth_info, eth_full_info = srun.status()
    if eth_status:
        logger.info(f"登录成功。")
        logger.info(f"========== ETH 信息 ==========")
        logger.info(f"用户名: \t{eth_info.get('user', '未知')}")
        logger.info(f"IP 地址: \t{eth_info.get('ip', '未知')}")
        logger.info(f"类型: \t{eth_info.get('type', '未知')}")
        logger.info(f"流量: \t{eth_info.get('traffic', '未知')}")
        logger.info(f"时长: \t{eth_info.get('duration', '未知')}")
        logger.info(f"在线数: \t{len(eth_info.get('devices', '未知'))}")
        logger.info(f"==============================")
    else:
        logger.error(f"获取 ETH 信息失败: {message}")