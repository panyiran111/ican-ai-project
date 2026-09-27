import json
import urllib.request

CASES = [
    "早上好！天冷了记得加衣服，别老熬夜，胃药我给你寄了两盒在抽屉里。",
    "儿子，中秋到底回不回家？你爸天天在日历上画圈。",
    "妈问你钱够不够花，别省着，想吃啥吃点好的。",
]

for c in CASES:
    payload = json.dumps({"content": c}).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:8000/api/decode",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    print("INPUT :", c[:20], "...")
    print("  core    =", data["core"])
    print("  emotion =", data["emotion"])
    print("  risk    =", data["risk_level"])
    print()
