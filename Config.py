import os
import yaml
import logging
from typing import Optional, Dict, Any

logger: logging.Logger = logging.getLogger("Aurora_Config")

Config_Template: Dict[str, Any] = {
    "auth":{"username":None,"password":None,"lan":False,},
    "settings":{"skip_ssl_verify":False,"timeout":2,"duration":5,"gc_collect_interval":60,},
    "logger":{"debug":False,"format":"[%(asctime)s][%(levelname)s] - %(message)s",
        "file":{"enable":True,"debug":True,"directory":"./logs","prefix":"srun","suffix":"%Y-%m-%d.log","when":"MIDNIGHT","interval":1,"backup_count":30,"encoding":"utf-8",},},
    "dns":{"nameservers":["192.168.247.6","192.168.247.26",],"hosts":{"net.szu.edu.cn":["172.31.63.36",],},},
    "portal":{
        "api":{"domain":"https://net.szu.edu.cn/","urls":{"acid":"/index_1.html","start":"/srun_portal_pc","challenge":"/cgi-bin/get_challenge","login":"/cgi-bin/srun_portal","info":"/cgi-bin/rad_user_info",},},
        "parameter":{"login":{"action":"login","os":"cKrzF5T7","name":"Yw4uNxrq","double_stack":0,"n":200,"vtype":1,},},
        "regex":{"start":"<script>[ \n]*var CONFIG = \\{([A-Za-z0-9:\\\\',\"\\.\\-|\\{/\\} \n]*)\\};[ \n]*</script>",},
        "user_agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",},
    "proxy":{"login":{"http":None,"https":None,},},
}

class Args:
    username: Optional[str]
    password: Optional[str]
    lan: bool
    daemon: bool
    skip_ssl_verify: bool
    timeout: int
    duration: int
    debug: bool
    log_directory: str
    log_keep_count: int

def GenerateConfig(overwrite: bool = False) -> bool:
    config: Dict[str, Any] = Config_Template

    if os.path.exists('config.yaml') and overwrite is False:
        return False
    
    try:
        with open('config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f)
    except Exception as e:
        logger.critical(f"创建配置文件失败: {e}")
        return False
    logger.debug("配置文件创建成功")
    return True




