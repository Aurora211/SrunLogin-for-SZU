import dns
import dns.rdata
import dns.rdataclass
import dns.rdatatype
import dns.resolver
import socket
import logging
import requests
from typing import List, Dict

logger = logging.getLogger(__name__)

class CustomDnsRequestHandler:
    def __init__(
            self,
            nameservers : List[str]      = ['192.168.247.6', '192.168.247.26'],
            hosts       : Dict[str, str] = {},
            **kwargs
    ) -> None:
        self.nameservers          = nameservers
        self.hosts                = hosts
        self.original_getaddrinfo = socket.getaddrinfo
    def request_with_dns_resolver(
            self,
            method : str,
            **kwargs
    ) -> requests.Response:
        self.enable()
        response = requests.request(method, **kwargs)
        self.disable()
        return response
    def request_without_dns_resolver(
            self,
            method: str,
            **kwargs
    ) -> requests.Response:
        self.disable()
        return requests.request(method, **kwargs)
    
    def enable(
            self,
            rdatatype : dns.rdatatype.RdataType | str = dns.rdatatype.A,
    ):
        return self.__enable_dns_resolver(rdatatype)
    def disable(self):
        return self.__disable_dns_resolver()

    def __enable_dns_resolver(
            self,
            rdatatype : dns.rdatatype.RdataType | str = dns.rdatatype.A,
    ) -> bool:
        try:
            def getaddrinfo(*args, **kwargs):
                hostname = args[0]
                try:
                    if hostname in self.hosts.keys():
                        answers = self.hosts[hostname]
                    else:
                        resolver = dns.resolver.Resolver()
                        resolver.nameservers = self.nameservers
                        answers = resolver.resolve(hostname, rdatatype)
                        answers = [answer.address for answer in answers]
                    return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (ip, args[1])) for ip in answers]
                except Exception as e:
                    logger.error(f'Failed to resolve hostname {hostname}: {e}')
                    logger.debug(f'Fallback to original getaddrinfo')
                    return self.original_getaddrinfo(*args, **kwargs)
            socket.getaddrinfo = getaddrinfo
            return True
        except Exception as e:
            logger.error(f'Failed to enable DNS resolver: {e}')
            return False
    def __disable_dns_resolver(self) -> bool:
        try:
            socket.getaddrinfo = self.original_getaddrinfo
            return True
        except Exception as e:
            logger.error(f'Failed to disable DNS resolver: {e}')
            return False




