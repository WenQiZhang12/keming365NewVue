# -*- coding: utf-8 -*-
"""
Assessment App - JWT 加密/解密工具
模拟 Java JWT 类的 encryptAndSign / verifyAndDecrypt 方法
使用 AES-256 加密 payload + HMAC-SHA1 签名
"""

import base64
import hashlib
import hmac
import json
import time
import struct
from Crypto.Cipher import AES

# ECBD 补位
_PAD = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
_UNPAD = lambda s: s[0:-s[-1]]


def _aes_key_from_b64(b64_key: str) -> bytes:
    """将 base64 编码的 AES 密钥解码为 bytes"""
    raw = base64.b64decode(b64_key)
    # 取前 32 字节作为 AES-256 密钥
    return raw[:32].ljust(32, b'\0')


def _sha1_hex(*args) -> str:
    """SHA-1 十六进制摘要"""
    data = ''.join(str(a) for a in args).encode('utf-8')
    return hashlib.sha1(data).hexdigest()


def encrypt_payload(payload_json: str, secret: str, aes_b64_key: str, issue_id: int, expire_ms: int) -> str:
    """
    加密 payload，模拟 Java JWT.encryptAndSign(Type.SYS, ...)
    
    返回 URL 编码后的 base64 token 字符串
    """
    now_ms = int(time.time() * 1000)
    expire_at = now_ms + expire_ms

    # 1. 用 AES 加密 payload
    aes_key = _aes_key_from_b64(aes_b64_key)
    cipher = AES.new(aes_key, AES.MODE_ECB)
    padded = _PAD(payload_json).encode('utf-8')
    encrypted = cipher.encrypt(padded)
    encrypted_b64 = base64.b64encode(encrypted).decode('ascii')

    # 2. 构造 header (类似 Java 的 type + issueId + timestamp + 随机数)
    nonce = struct.pack('>Q', int(time.time() * 1e9))  # nanoTime 近似
    nonce_b64 = base64.b64encode(nonce).decode('ascii')

    # 3. SHA-1 签名
    sig_raw = _sha1_hex(secret, encrypted_b64, nonce_b64, str(issue_id))
    
    # 4. 组装 token: base64(encrypted).base64(nonce).hex(signature)
    token = f"{encrypted_b64}.{nonce_b64}.{sig_raw}"
    
    # URL 编码
    import urllib.parse
    return urllib.parse.quote(token, safe='')


def decrypt_token(token: str, secret: str, aes_b64_key: str, issue_id: int, max_age_ms: int = 3600000) -> str:
    """
    解密并验证 token，返回原始 JSON payload 字符串
    
    验证：
    - 签名匹配
    - 未过期（max_age_ms 内）
    """
    import urllib.parse
    token = urllib.parse.unquote(token)

    parts = token.split('.')
    if len(parts) != 3:
        raise ValueError("token 格式错误")

    encrypted_b64, nonce_b64, sig_hex = parts

    # 1. 验证签名
    expected_sig = _sha1_hex(secret, encrypted_b64, nonce_b64, str(issue_id))
    if sig_hex != expected_sig:
        raise ValueError("签名验证失败")

    # 2. AES 解密
    aes_key = _aes_key_from_b64(aes_b64_key)
    cipher = AES.new(aes_key, AES.MODE_ECB)
    encrypted = base64.b64decode(encrypted_b64)
    decrypted_padded = cipher.decrypt(encrypted)
    decrypted = _UNPAD(decrypted_padded).decode('utf-8')

    # 3. 验证时间戳（如果 payload 中有 timestamp 字段）
    try:
        payload = json.loads(decrypted)
        ts = payload.get('timestamp')
        if ts:
            now_ms = int(time.time() * 1000)
            if now_ms - int(ts) > max_age_ms:
                raise ValueError("token 已过期")
    except (json.JSONDecodeError, ValueError):
        pass

    return decrypted
