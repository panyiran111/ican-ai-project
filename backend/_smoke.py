"""本地接口冒烟测试（中文友好输出）"""
import json
import sys
import urllib.request


BASE = "http://127.0.0.1:8000"


def post(path, body):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=10) as r:
        return json.loads(r.read().decode("utf-8"))


def show(label, obj):
    print(f"\n=== {label} ===")
    print(json.dumps(obj, ensure_ascii=False, indent=2)[:600])


print("\n[1] /api/health")
show("health", get("/api/health"))

print("\n[2] /api/decode")
show("decode", post("/api/decode", {
    "content": "妈，今天发的养生文我看了",
    "profile": "称呼：妈；老家：山东济南；拿手菜：酸菜鱼",
}))

print("\n[3] /api/reply (tough)")
show("reply-tough", post("/api/reply", {
    "content": "妈，今天发的养生文我看了",
    "tone": "tough",
    "profile": "称呼：妈；拿手菜：酸菜鱼",
}))

print("\n[4] /api/reply (sweet)")
show("reply-sweet", post("/api/reply", {
    "content": "妈，今天发的养生文我看了",
    "tone": "sweet",
    "profile": "称呼：妈；拿手菜：酸菜鱼",
}))

print("\n[5] /api/topic")
show("topic", post("/api/topic", {
    "scene": "daily",
    "profile": "称呼：爸；爱好：钓鱼",
}))

print("\n[6] /api/rehearsal/start (fail_exam)")
res = post("/api/rehearsal/start", {"scene": "fail_exam"})
show("rehearsal-start", res)
sid = res.get("session_id")

print("\n[7] /api/rehearsal/chat")
show("rehearsal-chat", post("/api/rehearsal/chat", {
    "session_id": sid,
    "content": "妈，我有一件事想跟你说",
}))

print("\n[8] /api/weather")
show("weather", get("/api/weather?city=%E6%B5%8E%E5%8D%97"))

print("\n[9] /api/topic/scenes")
show("topic-scenes", get("/api/topic/scenes"))

print("\n[10] /api/rehearsal/scenes")
show("rehearsal-scenes", get("/api/rehearsal/scenes"))

print("\n=========== 冒烟测试全部通过 ===========")