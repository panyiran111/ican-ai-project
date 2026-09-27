"""家音 · AI 家庭沟通翻译官 —— 后端服务"""
import json
import os
import urllib.request
from urllib.parse import quote

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from llm import (
    decode_care, reply_care, topic_care, TOPIC_SCENE_KEYS,
    rehearsal_start, rehearsal_chat, DEMO_REHEARSAL_SCENARIOS,
)

load_dotenv()

app = FastAPI(title="家音 Jiayin API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class DecodeRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000, description="父母发来的原文（养生文/语音转写）")
    profile: str = Field(default="", max_length=300, description="家庭画像摘要（可选），用于个性化生成")


class ReplyRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000, description="父母发来的原文（子女想回应的话题）")
    tone: str = Field(default="normal", description="子女语气偏好：tough(嘴硬)/normal(标准)/sweet(撒娇)")
    profile: str = Field(default="", max_length=300, description="家庭画像摘要（可选），用于个性化生成")


class TopicRequest(BaseModel):
    scene: str = Field(default="daily", description="通话场景：before_home(回家前)/festival(节日)/birthday(生日)/daily(普通通话)")
    profile: str = Field(default="", max_length=300, description="家庭画像摘要（可选），用于个性化生成")


class RehearsalStartRequest(BaseModel):
    scene: str = Field(default="fail_exam", description="彩排场景：fail_exam(挂科了)/breakup(分手了)/quit_job(想辞职)/money_short(生活费不够)")


class RehearsalChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, description="彩排会话 ID（由 /api/rehearsal/start 返回）")
    content: str = Field(..., min_length=1, max_length=2000, description="子女这轮想练习说的话")


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "jiayin", "llm_ready": bool(os.getenv("LLM_API_KEY"))}


@app.post("/api/decode")
def decode(req: DecodeRequest):
    """关心解码器：两段式解码（信息压缩 + 情感意图），无 Key 时降级为演示数据"""
    result = decode_care(req.content, req.profile)
    return result


@app.post("/api/reply")
def reply(req: ReplyRequest):
    """回音壁：基于父母原文 + 子女语气画像，生成三档回复文案（嘴硬/标准/撒娇）"""
    result = reply_care(req.content, req.tone, req.profile)
    return result


@app.get("/api/topic/scenes")
def topic_scenes():
    """话题卡支持的场景列表"""
    return {"scenes": TOPIC_SCENE_KEYS}


@app.post("/api/topic")
def topic(req: TopicRequest):
    """连心话题卡：按通话场景生成 5 个不尬聊的开放性问题"""
    result = topic_care(req.scene, req.profile)
    return result


@app.get("/api/rehearsal/scenes")
def rehearsal_scenes():
    """彩排室支持的场景列表（key -> 场景名/扮演的家长）"""
    return {
        "scenes": {
            key: {"scene_name": s["scene_name"], "parent": s["parent"], "parent_emoji": s["parent_emoji"]}
            for key, s in DEMO_REHEARSAL_SCENARIOS.items()
        }
    }


@app.post("/api/rehearsal/start")
def rehearsal_begin(req: RehearsalStartRequest):
    """彩排室：创建会话，AI 爸妈先起话头（返回开场白）"""
    return rehearsal_start(req.scene)


@app.post("/api/rehearsal/chat")
def rehearsal_talk(req: RehearsalChatRequest):
    """彩排室：多轮对话，子女练习开口，AI 爸妈接住"""
    result = rehearsal_chat(req.session_id, req.content)
    if result is None:
        raise HTTPException(status_code=404, detail="会话不存在或已过期，请重新开始彩排")
    return result


# ---------- 老家天气（Open-Meteo 免费无 Key；失败降级示例数据，永不翻车） ----------

WEATHER_CODES = {
    0: ("晴", "☀️"), 1: ("多云", "⛅"), 2: ("多云", "🌤️"), 3: ("阴", "☁️"),
    45: ("雾", "🌫️"), 48: ("雾凇", "🌫️"),
    51: ("毛毛雨", "🌦️"), 53: ("毛毛雨", "🌦️"), 55: ("毛毛雨", "🌦️"),
    61: ("小雨", "🌧️"), 63: ("中雨", "🌧️"), 65: ("大雨", "🌧️"),
    66: ("冻雨", "🌧️"), 67: ("冻雨", "🌧️"),
    71: ("小雪", "🌨️"), 73: ("中雪", "❄️"), 75: ("大雪", "❄️"), 77: ("雪粒", "🌨️"),
    80: ("阵雨", "🌦️"), 81: ("阵雨", "🌧️"), 82: ("强阵雨", "⛈️"),
    85: ("阵雪", "🌨️"), 86: ("阵雪", "🌨️"),
    95: ("雷阵雨", "⛈️"), 96: ("雷阵雨伴冰雹", "⛈️"), 99: ("雷阵雨伴冰雹", "⛈️"),
}


def _http_json(url: str, timeout: int = 6) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "jiayin/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _weather_tip(desc: str, temp) -> str:
    """把天气翻译成一句关心建议"""
    if "雨" in desc:
        return f"老家{desc}，提醒爸妈出门带伞、走路慢一点"
    if "雪" in desc:
        return f"老家{desc}了，问问爸妈保暖的衣裳够不够"
    if isinstance(temp, (int, float)):
        if temp <= 8:
            return f"老家只有 {temp}℃，给爸妈发一句「加件衣服」吧"
        if temp >= 32:
            return f"老家 {temp}℃ 高温，提醒爸妈中午少出门、多喝水"
    return "把老家的天气发给爸妈，就是一句现成的关心"


@app.get("/api/weather")
def weather(city: str = ""):
    """老家天气：city 为小档案里的「老家」字段；网络失败时返回示例数据（demo=True）"""
    city = (city or "").strip()[:20]
    if not city:
        raise HTTPException(status_code=400, detail="请先在「我家小档案」填写老家")
    try:
        geo = _http_json(
            f"https://geocoding-api.open-meteo.com/v1/search?name={quote(city)}&count=1&language=zh&format=json"
        )
        results = geo.get("results") or []
        if not results and len(city) > 2:
            # 「山东济南」→「济南」重试
            geo = _http_json(
                f"https://geocoding-api.open-meteo.com/v1/search?name={quote(city[-2:])}&count=1&language=zh&format=json"
            )
            results = geo.get("results") or []
        if not results:
            raise ValueError("geocoding empty")
        r = results[0]
        w = _http_json(
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={r['latitude']}&longitude={r['longitude']}"
            "&current=temperature_2m,weather_code"
            "&daily=temperature_2m_max,temperature_2m_min&forecast_days=1&timezone=auto"
        )
        cur = w.get("current") or {}
        temp = cur.get("temperature_2m")
        desc, emoji = WEATHER_CODES.get(cur.get("weather_code"), ("多云", "🌤️"))
        daily = w.get("daily") or {}
        tmax = (daily.get("temperature_2m_max") or [None])[0]
        tmin = (daily.get("temperature_2m_min") or [None])[0]
        return {
            "ok": True, "demo": False, "city": r.get("name") or city,
            "temp": temp, "desc": desc, "emoji": emoji, "tmax": tmax, "tmin": tmin,
            "tip": _weather_tip(desc, temp),
        }
    except Exception:
        return {
            "ok": False, "demo": True, "city": city,
            "temp": 18, "desc": "晴", "emoji": "☀️", "tmax": 23, "tmin": 12,
            "tip": "把老家的天气发给爸妈，就是一句现成的关心",
        }
