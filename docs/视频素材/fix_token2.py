# -*- coding: utf-8 -*-
"""候选 header 矩阵验签：不同键序/格式逐一尝试，任一通过即修复 token.txt"""
import base64, json, sys, itertools, requests
sys.stdout.reconfigure(encoding="utf-8")
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

PATH = r"C:\Users\潘亦然\Desktop\家音.潘\docs\视频素材\token.txt"
t = open(PATH, encoding="utf-8").read().strip()
p0, p1, p2 = t.split(".")

jwks = requests.get("https://www.codebuddy.cn/auth/realms/copilot/protocol/openid-connect/certs", timeout=20).json()
keys = [k for k in jwks["keys"] if k.get("alg") == "RS256"]

def b64u(b):
    return base64.urlsafe_b64encode(b).decode().rstrip("=")

def verify(hdr_b64):
    for k in keys:
        n = int.from_bytes(base64.urlsafe_b64decode(k["n"] + "=="), "big")
        e = int.from_bytes(base64.urlsafe_b64decode(k["e"] + "=="), "big")
        pub = rsa.RSAPublicNumbers(e, n).public_key()
        sig = base64.urlsafe_b64decode(p2 + "=" * (-len(p2) % 4))
        try:
            pub.verify(sig, f"{hdr_b64}.{p1}".encode(), padding.PKCS1v15(), hashes.SHA256())
            return k["kid"]
        except Exception:
            continue
    return None

# 候选：真实 kid 的不同键序与格式变体
candidates = []
for kid in [k["kid"] for k in keys]:
    variants = [
        {"alg": "RS256", "kid": kid, "typ": "JWT"},
        {"typ": "JWT", "alg": "RS256", "kid": kid},
        {"alg": "RS256", "typ": "JWT", "kid": kid},
        {"kid": kid, "alg": "RS256", "typ": "JWT"},
    ]
    for v in variants:
        candidates.append(json.dumps(v, separators=(",", ":")))
        candidates.append(json.dumps(v, separators=(", ", ": ")))  # 带空格变体

# 也直接试当前文件里已有的 header（原样）
candidates.insert(0, None)  # None = 用 p0 原样

for cand in candidates:
    hdr_b64 = p0 if cand is None else b64u(cand.encode())
    kid = verify(hdr_b64)
    if kid:
        token = f"{hdr_b64}.{p1}.{p2}"
        open(PATH, "w", encoding="utf-8").write(token)
        print(f"[PASS] 验签成功！kid={kid}")
        print(f"已写回 token.txt（{len(token)} chars），header={'原样' if cand is None else cand}")
        sys.exit(0)
    print("[x]", "p0原样" if cand is None else cand[:80])

print("[FAIL] 全部候选失败 —— 签名段转写有误")
sys.exit(1)
