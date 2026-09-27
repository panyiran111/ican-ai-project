"""家音 · AI 家庭沟通翻译官 —— 后端服务"""
import os
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
