# ===== Srun Network Python Decrypter =====
# This script is used to decrypt the Srun Network login page and login to the network.
# Script Usage: 
# $ python single.py -u <username> -p <password>
# =========================================
# Author: Aurora211
# Date: 2025-01-14
# Version: 0.1.0
# =========================================

# Command line arguments
import argparse
parser = argparse.ArgumentParser("Srun Network Python Decrypter")
parser.add_argument("-u", "--username", type=str, help="Network username", required=True)
parser.add_argument("-p", "--password", type=str, help="Network Password", required=True)
args = parser.parse_args()

# Configuration file for the project
import yaml
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

from SrunLogin import SrunLogin

srun = SrunLogin(
    login_page_url          = config['meta']['portal']['domain'] + config['meta']['portal']['login_page'],
    challenge_api_url       = config['meta']['portal']['domain'] + config['meta']['portal']['challenge_api'],
    login_api_url           = config['meta']['portal']['domain'] + config['meta']['portal']['login_api'],
    callback_parse_regex    = config['meta']['portal']['regex']['callback'],
    page_parse_regex        = config['meta']['portal']['regex']['page'],
    callback_str            = config['meta']['portal']['callback'],
    skip_ssl_verify         = config['settings']['skip_ssl_verify'],
    request_timeout         = config['settings']['request_timeout'],
    login_fixed_parameters  = config['meta']['portal']['login_parameters'],
    user_agent              = config['meta']['user_agent']['request']
)

state, _, _ = srun.login(args.username, args.password)

if state:
    print("Login success")
else:
    print("Login failure")