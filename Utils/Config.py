import yaml

Config_Template = {
    'auth': {
        'username': '',
        'password': ''
    },
    'settings': {
        'default_mode': 0,
        'skip_ssl_verify': False,
        'request_timeout': 2,
        'online_check_duration': 5,
        'gc_collect_interval': 60,
        'online_check_threshold': 0.9
    },
    'logger': {
        'debug': False,
        'format': '[%(asctime)s][%(levelname)s] - %(message)s',
        'file': {
            'debug': True,
            'enable': True,
            'directory': './logs',
            'prefix': 'srun',
            'suffix': '%Y-%m-%d.log',
            'when': 'MIDNIGHT',
            'interval': 1,
            'backup_count': 3,
            'encoding': 'utf-8'
        }
    },
    'meta': {
        'online_check': [
            {
                'url': 'https://www.baidu.com',
                'key': '百度一下'
            }, {
                'url': 'https://www.bilibili.com',
                'key': '哔哩哔哩'
            }, {
                'url': 'https://www.qq.com',
                'key': '腾讯'
            }, {
                'url': 'https://www.taobao.com',
                'key': '淘宝'
            }, {
                'url': 'https://www.jd.com',
                'key': '京东'
            }
        ],
        'portal': {
            'nameservers': [
                '192.168.247.6',
                '192.168.247.26'
            ],
            'hosts': {
                'net.szu.edu.cn': [
                    '172.31.63.36'
                ]
            },
            'domain': 'https://net.szu.edu.cn',
            'login_page': '/srun_portal_pc',
            'challenge_api': '/cgi-bin/get_challenge',
            'login_api': '/cgi-bin/srun_portal',
            'add_time_stamp_to_callback': True,
            'login_success': {
                'key': 'suc_msg',
                'value': 'login_ok'
            },
            'login_parameters': {
                'n': '200',
                'type': '1',
                'acid': '12',
                'enc': 'srun_bx1',
                'os': 'Windows 10',
                'name': 'windows',
                'double_stack': False
            },
            'callback': 'jQuery11240767708159690917',
            'regex': {
                'page': '<script>[ \n]+var CONFIG = [\\{ \n]+([A-Za-z0-9 :\'",\\.\\-|/\n\\{\\}]+)\n[ ]+\\};[ \n]+</script>',
                'callback': '({[A-Za-z0-9":,_\\. ]+})'
            }
        },
        'user_agent': {
            'request': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'client': 'Aurora/1.0'
        },
        'proxy': {
            'online_check': {
                'http': 'None',
                'https': 'None'
            },
            'login': {
                'http': 'None',
                'https': 'None'
            }
        }
    }
}

def GenerateConfig(username: str, password: str) -> dict:
    config = Config_Template
    config['auth']['username'] = username
    config['auth']['password'] = password
    
    with open('config.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(config, f)




