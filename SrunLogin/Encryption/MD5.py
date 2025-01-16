# ===== Srun Network Python Decrypter =====
# MD5 Encryption Module
# DO NOT MODIFY THIS FILE UNLESS YOU KNOW WHAT YOU ARE DOING.
# =========================================
# Author: Aurora211
# Date: 2025-01-14
# Version: 0.1.0
# =========================================

__MD5_STRING_ENCODE = 'utf-8'

import hmac
import hashlib

def MD5(password: str, token: str):
    return hmac.new(token.encode(__MD5_STRING_ENCODE), password.encode(__MD5_STRING_ENCODE), hashlib.md5).hexdigest()

if __name__ == '__main__':
    """
    If __MD5_STRING_ENCODE has been set to 'utf-8', the result should be
    b2a1ec0f3e0607099d7f39791c04e9a420766b9
    """
    print(MD5('123', '123'))