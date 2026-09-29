# -*- coding: utf-8 -*-
"""本地校验 token.txt：
1. 结构校验：3 段、长度、header/payload 均为合法 JSON、关键字段与已知值一致
2. 验签校验：从 codebuddy.cn JWKS 拉公钥，RS256 验签（密码学级确认逐字节无误）
"""
import base64, json, sys
sys.stdout.reconfigure(encoding="utf-8")

t = open(r"C:\Users\潘亦然\Desktop\家音.潘\docs\视频素材\token.txt", encoding="utf-8").read().strip()
parts = t.split(".")
ok = True

def die(msg):
    global ok
    ok = False
    print("[FAIL]", msg)

print(f"总长度: {len(t)}  各段长度: {[len(p) for p in parts]}")
if len(parts) != 3:
    die("段数不是 3")
    sys.exit(1)

hdr = json.loads(base64.urlsafe_b64decode(parts[0] + "=" * (-len(parts[0]) % 4)))
pld = json.loads(base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4)))
print("header:", json.dumps(hdr, ensure_ascii=False))
print("payload 关键字段:")
for k in ["iss", "aud", "exp", "iat", "jti", "nickname", "sub", "typ", "token_source"]:
    print(f"  {k} = {pld.get(k)!r}")
print("  realm_access.roles =", pld.get("realm_access", {}).get("roles"))

# 结构断言
asserts = [
    (hdr.get("kid") == "myfVzp783Ki_JCx8Vns3X_iz6jZrb6Cf5NOMkGZMPI3s", "kid 错误"),
    (pld.get("jti") == "8727cc30-a7ee-48c1-acc9-9c894beaae6a", "jti 错误"),
    (pld.get("iss") == "https://www.codebuddy.cn/auth/realms/copilot", "iss 错误"),
    (pld.get("sub") == "1e89a5ac-e5b7-41df-b400-d7f8261fb716", "sub 错误"),
    ("default-roles" in pld.get("realm_access", {}).get("roles", []), "roles 缺 default-roles"),
    (pld.get("typ") == "Bearer", "typ 应为 Bearer"),
    (pld.get("token_source") == "enterprise_switch", "token_source 错误"),
    (pld.get("auth_time") == 1789985513 and pld.get("exp") == 1793089377 and pld.get("iat") == 1790497377, "时间戳错误"),
    (len(parts[2]) == 342, f"签名长度 {len(parts[2])} != 342"),
]
for cond, msg in asserts:
    if not cond:
        die(msg)
    else:
        print("[ok]", msg)

# 密码学验签
try:
    import requests
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives import hashes
    jwks = requests.get("https://www.codebuddy.cn/auth/realms/copilot/protocol/openid-connect/certs", timeout=15).json()
    key = None
    for k in jwks["keys"]:
        if k["kid"] == hdr["kid"]:
            key = k
            break
    if not key:
        die("JWKS 中无匹配 kid")
    else:
        n = int.from_bytes(base64.urlsafe_b64decode(key["n"] + "=="), "big")
        e = int.from_bytes(base64.urlsafe_b64decode(key["e"] + "=="), "big")
        pub = rsa.RSAPublicNumbers(e, n).public_key()
        sig = base64.urlsafe_b64decode(parts[2] + "=" * (-len(parts[2]) % 4))
        signing_input = f"{parts[0]}.{parts[1]}".encode()
        pub.verify(sig, signing_input, padding.PKCS1v15(), hashes.SHA256())
        print("[PASS] RS256 签名验证通过 —— Token 逐字节无误！")
except ImportError:
    print("[WARN] 缺 cryptography/requests，跳过验签（结构校验已过则提交一试）")
except Exception as ex:
    die(f"验签失败: {ex}")

print("\n结论:", "✅ Token 可用，可以提交" if ok else "❌ Token 仍有误，转备选方案")
sys.exit(0 if ok else 1)
