# ===== Srun Network Python Decrypter =====
# 内部DNS解析器，用于在内部网络下自定义DNS时，当DNS失效时，自动切换到上游DNS或者本地主机映射
# DO NOT MODIFY THIS FILE UNLESS YOU KNOW WHAT YOU ARE DOING.
# =========================================
# Author: Aurora211
# Date: 2025-12-16
# Version: 2.0
# =========================================

import dns
import dns.rdatatype
import dns.resolver
import socket
import logging
import requests
from typing import Union, Callable, List, Dict, Any
from typing_extensions import Generator
from contextlib import contextmanager

logger = logging.getLogger("Aurora_DNS")

class CustomDnsRequestHandler:
    def __init__(self, nameservers: List[str] = ['192.168.247.6', '192.168.247.26'], hosts: Dict[str, List[str]] = {}, **kwargs) -> None:
        """
        创建本地DNS解析器
        
        Args:
            nameservers (List[str], optional): DNS服务器列表. Defaults to ['192.168.247.6', '192.168.247.26'].
            hosts (Dict[str, str], optional):  主机映射字典. Defaults to {}
        """
        self.nameservers: List[str]      = nameservers          # 上游DNS服务器列表
        self.hosts: Dict[str, List[str]] = hosts                # 主机映射
        self.getaddrinfo: Callable       = socket.getaddrinfo   # 原始getaddrinfo

        for k, v in kwargs.items():
            setattr(self, k, v)
    def request(self, method: str, with_dns_resolver: bool = True, **kwargs) -> requests.Response:
        if with_dns_resolver:
            with self.with_dns_resolver():
                response: requests.Response = requests.request(method, **kwargs)
        else:
            response: requests.Response = requests.request(method, **kwargs)
        return response

    @contextmanager
    def with_dns_resolver(self, rdatatype: Union[dns.rdatatype.RdataType, str] = dns.rdatatype.A) -> Generator[None, Any, Any]:
        """
        使用本地DNS解析器解析DNS

        Args:
            rdatatype (Union[dns.rdatatype.RdataType, str], optional): 解析类型. Defaults to dns.rdatatype.A.
        """
        try:
            def func(*args, **kwargs):
                host: str = args[0]
                try:
                    if host in self.hosts.keys():
                        addresses: List[str] = self.hosts[host]
                    else:
                        resolver: dns.resolver.Resolver = dns.resolver.Resolver()
                        resolver.nameservers = self.nameservers
                        answer: dns.resolver.Answer = resolver.resolve(host, rdatatype)
                        addresses: List[str] = [a.address for a in answer] # type: ignore
                    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, args[1])) for ip in addresses]
                except Exception as e:
                    logger.error(f'Fallback triggered: Failed to resolve hostname {host}: {e}')
                    return self.getaddrinfo(*args, **kwargs)
            socket.getaddrinfo = func
            yield
        except Exception as e:
            logger.error(f'Failed to enable DNS resolver: {e}')
            raise e
        finally:
            try:
                socket.getaddrinfo = self.getaddrinfo
            except Exception as e:
                logger.critical(f'Failed to restore original getaddrinfo: {e}')




