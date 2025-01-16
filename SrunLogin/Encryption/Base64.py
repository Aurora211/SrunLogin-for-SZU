# ===== Srun Network Python Decrypter =====
# Base64 encode a string.
# DO NOT MODIFY THIS FILE UNLESS YOU KNOW WHAT YOU ARE DOING.
# =========================================
# Author: Aurora211
# Date: 2025-01-14
# Version: 0.1.0
# =========================================

__PADDING_CHARACTER = "="
__BASE64_ALPHA = "LVoJPiCN2R8G90yg+hmFHuacZ1OWMnrsSTXkYpUq/3dlbfKwv6xztjI7DeBE45QA"

def _get_byte(s, i):
    x = ord(s[i])
    if x > 255:
        raise ValueError("Invalid character: %r" % s[i])
    return x

def Base64(s):
    """
    Base64 encode a string.
    """
    i = 0
    b10 = 0
    x = []
    i_max = len(s) - len(s) % 3
    
    if len(s) == 0:
        return s
    
    for i in range(0, i_max, 3):
        b10 = (_get_byte(s, i) << 16) | (_get_byte(s, i + 1) << 8) | _get_byte(s, i + 2)
        x.append(__BASE64_ALPHA[(b10 >> 18) & 63])
        x.append(__BASE64_ALPHA[(b10 >> 12) & 63])
        x.append(__BASE64_ALPHA[(b10 >> 6) & 63])
        x.append(__BASE64_ALPHA[b10 & 63])
    
    i = i_max

    if len(s) - i_max == 1:
        b10 = _get_byte(s, i) << 16
        x.append(__BASE64_ALPHA[(b10 >> 18) & 63])
        x.append(__BASE64_ALPHA[(b10 >> 12) & 63] + __PADDING_CHARACTER * 2)
    elif len(s) - i_max == 2:
        b10 = (_get_byte(s, i) << 16) | (_get_byte(s, i + 1) << 8)
        x.append(__BASE64_ALPHA[(b10 >> 18) & 63])
        x.append(__BASE64_ALPHA[(b10 >> 12) & 63])
        x.append(__BASE64_ALPHA[(b10 >> 6) & 63] + __PADDING_CHARACTER)
    else:
        pass
    
    return "".join(x)

if __name__ == "__main__":
    """
    If __BASE64_PADDING_CHARACTER and __BASE64_ALPHA has been set to "=" and "LVoJPiCN2R8G90yg+hmFHuacZ1OWMnrsSTXkYpUq/3dlbfKwv6xztjI7DeBE45QA" respectively,
    then the following code will output "9F2z0JHI" which is the base64 encoding
    """
    print(Base64("123456"))