# -*- coding: utf-8 -*-
"""最终修复尝试：规范化 payload + 标准 header（两种kid）验签"""
import base64, json, sys, requests
sys.stdout.reconfigure(encoding="utf-8")
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes

PATH = r"C:\Users\潘亦然\Desktop\家音.潘\docs\视频素材\token.txt"
t = open(PATH, encoding="utf-8").read().strip()
p0, p1, p2 = t.split(".")

# 规范化 payload：解码 -> 紧凑重编码（ensure_ascii=False）
pld = json.loads(base64.urlsafe_b64decode(p1 + "=" * (-len(p1) % 4)))
p1_canon = base64.urlsafe_b64encode(
    json.dumps(pld, separators=(",", ":"), ensure_ascii=False).encode()
).decode().rstrip("=")
print(f"p1 原长度 {len(p1)} -> 规范化 {len(p1_canon)}  {'(一致)' if p1_canon == p1 else '(有差异，用规范化版)'}")

jwks = requests.get("https://www.codebuddy.cn/auth/realms/copilot/protocol/openid-connect/certs", timeout=20).json()
kids = [k["kid"] for k in jwks["keys"]]

def b64u(b):
    return base64.urlsafe_b64encode(b).decode().rstrip("=")

def verify(hdr_b64, pl):
    for k in jwks["keys"]:
        try:
            n = int.from_bytes(base64.urlsafe_b64decode(k["n"] + "=="), "big")
            e = int.from_bytes(base64.urlsafe_b64decode(k["e"] + "=="), "big")
        except Exception:
            continue
        pub = rsa.RSAPublicNumbers(e, n).public_key()
        sig = base64.urlsafe_b64decode(p2 + "=" * (-len(p2) % 4))
        try:
            pub.verify(sig, f"{hdr_b64}.{pl}".encode(), padding.PKCS1v15(), hashes.SHA256())
            return True
        except Exception:
            continue
    return False

cands = []
for kid in kids:
    cands += [
        b64u(json.dumps({"alg": "RS256", "kid": kid, "typ": "JWT"}, separators=(",", ":")).encode()),
        b64u(json.dumps({"alg": "RS256", "typ": "JWT", "kid": kid}, separators=(",", ":")).encode()),
        b64u(json.dumps({"typ": "JWT", "alg": "RS256", "kid": kid}, separators=(",", ":")).encode()),
        # 奇异变体：重复 alg（首版转写解码出的形态）
        b64u(('{"alg":"RS256","kid":"%s","typ":"JWT","alg":"RS256"}' % kid).encode()),
    ]
for pl in {p1, p1_canon}:
    for h in cands:
        if verify(h, pl):
            token = f"{h}.{pl}.{p2}"
            open(PATH, "w", encoding="utf-8").write(token)
            print(f"[PASS] 验签成功！token 已修复（{len(token)} chars）")
            sys.exit(0)
print("[FAIL] 最终尝试失败 —— 签名无法恢复，切换备选方案（AI生图+ffmpeg动效）")
sys.exit(1)
