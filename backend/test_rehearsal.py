# -*- coding: utf-8 -*-
"""彩排室端到端自测：挂科了场景 5 轮 + 场景列表 + 404 兜底"""
import json
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = "http://localhost:8000"


def post(path, payload, expect=200):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))


# 1. 场景列表
with urllib.request.urlopen(BASE + "/api/rehearsal/scenes") as r:
    scenes = json.loads(r.read().decode("utf-8"))["scenes"]
print("scenes:", ", ".join(f'{k}={v["scene_name"]}({v["parent"]})' for k, v in scenes.items()))
assert len(scenes) == 4

# 2. 开始挂科了会话
code, s = post("/api/rehearsal/start", {"scene": "fail_exam"})
print(f"\n[start {code}] {s['parent_emoji']} {s['parent']} | {s['scene_name']}")
print("  开场白:", s["opening"])
assert code == 200 and s["opening"]

# 3. 5 轮对话
turns = ["妈…我挂了一科", "还行 就是那阵子社团太忙了", "补考下个月 不用表哥啦", "不用打钱!我自己有", "好 周末视频"]
sid = s["session_id"]
for t in turns:
    code, r = post("/api/rehearsal/chat", {"session_id": sid, "content": t})
    print(f"[turn{r['turn']}] {r['reply']}")
    assert code == 200

# 4. 剧本走完后兜底台词继续
code, r = post("/api/rehearsal/chat", {"session_id": sid, "content": "嗯 我好多了"})
print(f"[turn{r['turn']}] {r['reply']}")

# 5. 无效会话 404
code, r = post("/api/rehearsal/chat", {"session_id": "no-such-id", "content": "在吗"})
print(f"\n[404 check] code={code} detail={r.get('detail')}")
assert code == 404

# 6. 未知场景兜底到挂科了
code, s2 = post("/api/rehearsal/start", {"scene": "whatever"})
print(f"[unknown scene] -> {s2['scene_name']}")
assert s2["scene_name"] == "挂科了"

print("\nALL REHEARSAL TESTS PASSED")
