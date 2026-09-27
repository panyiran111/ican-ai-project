# -*- coding: utf-8 -*-
"""画像个性化端到端自测：带/不带 profile 的回音壁输出对比"""
import json
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = "http://localhost:8000"


def post(path, payload):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode("utf-8"))


content = "震惊！《十种致癌食物》你天天点外卖，转给你看看，千万要注意啊！"
profile = "称呼妈妈「老妈」；老家山东济南；妈妈拿手菜是酸菜鱼；爸爸爱好钓鱼；家里养了橘猫胖虎"

# 无画像
r1 = post("/api/reply", {"content": content})
# 有画像（拿手菜替换）
r2 = post("/api/reply", {"content": content, "profile": profile})

print("【无画像】normal:", r1["replies"]["normal"])
print("【有画像】normal:", r2["replies"]["normal"])

# 回家场景：话题卡话题里带爸爸爱好
r3 = post("/api/topic", {"scene": "before_home", "profile": profile})
print("\n【话题卡·画像】first:", r3["topics"][0])

# 爸爸爱好替换验证（下棋 -> 钓鱼）
r4 = post("/api/reply", {"content": "中秋你回不回家？你爸嘴上不说，天天在日历上画圈", "profile": profile})
print("【回家场景·画像】normal:", r4["replies"]["normal"])

ok1 = "酸菜鱼" in r2["replies"]["normal"] or "酸菜鱼" in r2["replies"]["sweet"]
ok2 = "排骨" not in json.dumps(r2, ensure_ascii=False)
print("\n拿手菜替换:", "PASS" if ok1 else "FAIL", "| 旧词已消失:", "PASS" if ok2 else "FAIL")
