# ===== Srun Network Python Decrypter =====
# SHA1 Encryption Module
# DO NOT MODIFY THIS FILE UNLESS YOU KNOW WHAT YOU ARE DOING.
# =========================================
# Author: Aurora211
# Date: 2025-01-14
# Version: 0.1.0
# =========================================

__SHA1_STRING_ENCODE = 'utf-8'

import hashlib

def SHA1(message: str):
    return hashlib.sha1(message.encode(__SHA1_STRING_ENCODE)).hexdigest()

if __name__ == '__main__':
    """
    If __SHA1_STRING_ENCODE has been set to 'utf-8', the output of this snippet should be:
    7c4a8d09ca3762af61e59520943dc26494f8941b
    """
    print(SHA1('123456'))