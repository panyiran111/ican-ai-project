# -*- coding: utf-8 -*-
"""从 JWKS 获取真实 kid，重建 header，验签修复 token.txt
- payload 已本地验证完全正确
- header 用 JWKS 发布的真实 kid 重构（消除转写误差）
- 签名若验证通过 = 整个 Token 逐字节正确
"""
import base64, json, sys, requests
sys.stdout.reconfigure(encoding="utf-8")
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

PATH = r"C:\Users\潘亦然\Desktop\家音.潘\docs\视频素材\token.txt"
t = open(PATH, encoding="utf-8").read().strip()
p0, p1, p2 = t.split(".")

# 1. 拉 JWKS
jwks = requests.get("https://www.codebuddy.cn/auth/realms/copilot/protocol/openid-connect/certs", timeout=20).json()
kids = [k["kid"] for k in jwks["keys"]]
print("JWKS kids:", kids)

def b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")

def try_verify(hdr_b64: str) -> bool:
    for k in jwks["keys"]:
        if k["alg"] != "RS256":
            continue
        n = int.from_bytes(base64.urlsafe_b64decode(k["n"] + "=="), "big")
        e = int.from_bytes(base64.urlsafe_b64decode(k["e"] + "=="), "big")
        pub = rsa.RSAPublicNumbers(e, n).public_key()
        sig = base64.urlsafe_b64decode(p2 + "=" * (-len(p2) % 4))
        try:
            pub.verify(sig, f"{hdr_b64}.{p1}".encode(), padding.PKCS1v15(), hashes.SHA256())
            return True
        except Exception:
            continue
    return False

# 2. 对每个真实 kid 构造候选 header（Keycloak 标准键序 & 紧凑格式），逐一验签
fixed = None
for kid in kids:
    for hdr_obj in (
        {"alg": "RS256", "kid": kid, "typ": "JWT"},
    ):
        hdr_b64 = b64u(json.dumps(hdr_obj, separators=(",", ":")).encode())
        if try_verify(hdr_b64):
            fixed = f"{hdr_b64}.{p1}.{p2}"
            print(f"[PASS] kid={kid} 验签成功！")
            break
    if fixed:
        break

if fixed:
    open(PATH, "w", encoding="utf-8").write(fixed)
    print(f"已写回修复后的 token（长度 {len(fixed)}）—— 云端视频生成可用")
    sys.exit(0)
else:
    print("[FAIL] 所有候选 header 均验签失败 —— 签名段转写有误，转备选方案")
    sys.exit(1)
