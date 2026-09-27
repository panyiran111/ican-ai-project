"""LLM 调用层：关心解码器两段式提示词（信息压缩 -> 情感意图解码）

无 API Key 时返回演示剧本数据，保证 Demo 永不翻车（D3 会接入完整演示模式）。
"""
import json
import os

try:
    from openai import OpenAI
except ImportError:  # 未安装依赖时仍可启动
    OpenAI = None

# ---------- 提示词（产品价值观：不辟谣打脸，只翻译爱） ----------
SYSTEM_PROMPT = """你是「家音」App 的关心解码器。用户会贴来父母发来的内容（养生文、语音转写、连环问候）。
你的任务分两步：

第一步 · 信息压缩：把冗长内容压缩成 1-2 句核心事实（妈妈到底说了什么）。
第二步 · 情感解码：解读言外之意——父母真正想表达/想问的是什么（例如"她其实想问：中秋回不回家"）。

原则：
1. 绝不嘲讽父母，绝不"辟谣打脸"式语气；伪科学内容只需温和标注可信度并给出关心内核。
2. 解码出的情感要具体、戳心但不煽情过度。
3. "建议回应点"给子女一个可落地的回应方向。

只输出如下 JSON（不要输出任何其他文字）：
{
  "core": "核心信息压缩（1-2句）",
  "emotion": "言外之意·情感解码（1-2句）",
  "intent": "建议回应点（1句）",
  "risk_level": "none|low|medium|high",
  "risk_note": "可信度提示：若无健康伪科学内容则为空字符串；若有则温和说明'文中健康说法多数不成立，但它翻译过来其实是：……担心'"
}"""


# ---------- 演示剧本库：无 API Key 时的本地解码引擎 ----------
# 关键词匹配 -> 场景剧本。覆盖大学生最常收到的 10 类爸妈消息。
DEMO_SCENARIOS = [
    {
        "keywords": ["致癌", "外卖", "奶茶", "养生", "食物中毒", "隔夜"],
        "core": "妈妈转了一篇伪科学养生文，核心是担心你天天点外卖、奶茶当水喝。",
        "emotion": "她其实想说：你一个人在外面，我管不了你吃什么，只能转篇文章给你。",
        "intent": "回应她的担心而不是文章：告诉她你最近好好吃饭了，中秋回家让她做饭。",
        "risk_level": "medium",
        "risk_note": "文中「十种致癌食物」等说法多数不成立，但它翻译过来其实是：怕你吃不好。",
    },
    {
        "keywords": ["中秋", "回家", "国庆", "车票", "排骨", "日历"],
        "core": "爸妈在等你回家：爸爸嘴上不说，天天在日历上画圈；妈妈连排骨都留着等你回来买新鲜的。",
        "emotion": "她其实想问：中秋你到底回不回家？但又怕问了显得在催你。",
        "intent": "直接给一个确定的答案，哪怕回不去，也给他们一个具体的期待（如国庆回去）。",
        "risk_level": "none",
        "risk_note": "",
    },
    {
        "keywords": ["熬夜", "凌晨", "早点睡", "熬夜伤身", "别老熬夜"],
        "core": "妈妈看到你凌晨还在发朋友圈，提醒你别熬夜。",
        "emotion": "她其实想说：睡不着的时候，她会一直惦记着屏幕那头的你。",
        "intent": "今晚早点回一句「睡了」，并真的在十二点前放下手机——她会看你的在线状态。",
        "risk_level": "none",
        "risk_note": "",
    },
    {
        "keywords": ["加衣服", "降温", "天冷", "秋裤", "感冒", "变天"],
        "core": "降温了，妈妈让你加衣服、注意保暖。",
        "emotion": "她其实想说：你们城市的天气，她每天比你自己还先查一遍。",
        "intent": "回一张今天穿了外套的自拍，比一百句「知道了」都让她放心。",
        "risk_level": "none",
        "risk_note": "",
    },
    {
        "keywords": ["钱", "生活费", "吃点好的", "别省", "打钱", "买件"],
        "core": "爸妈问你钱够不够花，让你别省着。",
        "emotion": "他其实想说：宁愿自己省一点，也不想你在外面委屈自己。",
        "intent": "如果你过得不错，具体说一句「这个月还自己赚了点家教的钱」，让他们为你骄傲。",
        "risk_level": "none",
        "risk_note": "",
    },
    {
        "keywords": ["对象", "女朋友", "男朋友", "相亲", "结婚", "处对象"],
        "core": "妈妈又在问有没有对象，语气比上次更委婉。",
        "emotion": "她其实想说：怕你一个人太孤单，也怕自己等不到那一天。",
        "intent": "别只回「没有」。聊聊你对未来的真实想法——她要的从来不是答案，是参与感。",
        "risk_level": "none",
        "risk_note": "",
    },
    {
        "keywords": ["胃药", "药", "医院", "体检", "寄", "抽屉"],
        "core": "妈妈给你寄了胃药，叮嘱你按时吃饭、记得吃药。",
        "emotion": "她其实想说：你的胃是她心里的挂号处，她比你自己更清楚它什么时候疼。",
        "intent": "收到药后拍张照回复「按时吃着呢」，再加一句最近的健康近况。",
        "risk_level": "low",
        "risk_note": "用药请遵医嘱，妈妈寄的药如果是长期吃的处方药，建议抽空做一次正规检查。",
    },
    {
        "keywords": ["早上好", "晚安", "早安", "表情", "问候", "平安"],
        "core": "妈妈每天雷打不动发早安晚安表情包。",
        "emotion": "她其实想说：这是她确认「今天还和你有联系」的仪式感。",
        "intent": "偶尔也主动在早上先发一次——顺序反过来，她能高兴一整天。",
        "risk_level": "none",
        "risk_note": "",
    },
    {
        "keywords": ["工作", "实习", "加班", "压力", "辞职", "领导"],
        "core": "爸爸问起你的工作和实习近况，话不多。",
        "emotion": "他其实想说：想帮帮不上，只能问问。每一句「还行吗」都是他的牵挂。",
        "intent": "和爸爸聊一次具体的工作内容——他不一定懂，但他想懂你的世界。",
        "risk_level": "none",
        "risk_note": "",
    },
    {
        "keywords": ["讲座", "教授", "课程", "直播", "听课", "五点"],
        "core": "妈妈在跟养生讲座听课，想拉你一起听。",
        "emotion": "她其实想说：她认真生活着，也希望离你的生活近一点。",
        "intent": "夸她一句「妈你比我自律」，再陪她听十分钟——她会记住很久。",
        "risk_level": "low",
        "risk_note": "讲座多数为营销性质，买保健品前建议先和子女商量。",
    },
]

DEMO_DEFAULT = {
    "core": "妈妈的关心藏在絮叨里：提醒你吃好睡好，惦记着你的近况。",
    "emotion": "她其实想说：不能照顾你了，只能一遍遍提醒你照顾自己。",
    "intent": "回复一个具体的近况让她安心，比说「知道了」有效一百倍。",
    "risk_level": "none",
    "risk_note": "",
}


def _demo_result(content: str) -> dict:
    """无 Key 降级：关键词匹配场景剧本库，返回最贴近的解码结果"""
    for scene in DEMO_SCENARIOS:
        if any(kw in content for kw in scene["keywords"]):
            return {
                "core": scene["core"],
                "emotion": scene["emotion"],
                "intent": scene["intent"],
                "risk_level": scene["risk_level"],
                "risk_note": scene["risk_note"],
            }
    return dict(DEMO_DEFAULT)


def _profile_block(profile: str = "") -> str:
    """把画像摘要转成注入提示词的文本块"""
    return f"\n\n【这个家的专属信息（生成内容时尽量自然地带入这些细节）】{profile}" if profile else ""


def decode_care(content: str, profile: str = "") -> dict:
    """两段式解码主入口"""
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
    model = os.getenv("LLM_MODEL", "deepseek-chat")

    if not api_key or OpenAI is None:
        return _demo_result(content)

    client = OpenAI(api_key=api_key, base_url=base_url)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT + _profile_block(profile)},
            {"role": "user", "content": content},
        ],
        temperature=0.7,
        response_format={"type": "json_object"},
    )
    text = resp.choices[0].message.content.strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return _demo_result(content)
    # 兜底字段
    for key in ("core", "emotion", "intent", "risk_level", "risk_note"):
        data.setdefault(key, "" if key != "risk_level" else "none")
    return data


# ---------- 回音壁：演示剧本库 ----------
# 三档语气：嘴硬（轻描淡写不煽情）/ 标准（温和得体）/ 撒娇（情感外露）
# 每个场景独立写三档，覆盖原 10 个关心场景。
DEMO_REPLY_SCENARIOS = [
    {
        "keywords": ["致癌", "外卖", "奶茶", "食物中毒", "隔夜", "十种", "伪科学"],
        "scene_name": "养生文",
        "replies": {
            "tough": "妈，我看过了，最近自己做饭吃得挺好的，你别担心。",
            "normal": "妈你说的那些我会注意的，最近吃得挺规律的，馋你做的排骨了，中秋回去给我炖一锅啊。",
            "sweet": "呜呜呜妈妈我爱你❤️ 我答应你从今天起少点外卖，回家吃你做的排骨！",
        },
    },
    {
        "keywords": ["中秋", "回家", "国庆", "车票", "排骨", "日历"],
        "scene_name": "中秋回家",
        "replies": {
            "tough": "回。几号的票我今晚就买，你们不用操心。",
            "normal": "妈我尽量回，国庆要是请不下假就提前两天先回，排骨给我留着啊。",
            "sweet": "想回家想回家想回家😭 我连请假理由都想好了！这周一定回！",
        },
    },
    {
        "keywords": ["熬夜", "凌晨", "早点睡", "熬夜伤身", "别老熬夜"],
        "scene_name": "熬夜提醒",
        "replies": {
            "tough": "嗯，今天弄完就睡。",
            "normal": "知道了妈，今天会早点睡，明天起来给你回消息。",
            "sweet": "马上睡马上睡～ 妈你先睡，别等我，我明天醒了一定第一个找你❤️",
        },
    },
    {
        "keywords": ["加衣服", "降温", "天冷", "秋裤", "感冒", "变天"],
        "scene_name": "降温加衣",
        "replies": {
            "tough": "穿了，外套出门就套上了。",
            "normal": "收到，今天特意穿了厚外套，你放心，明天再冷我就把秋裤翻出来。",
            "sweet": "呜呜妈妈你最暖～ 我这就去找秋裤！你也要注意保暖哦！",
        },
    },
    {
        "keywords": ["钱", "生活费", "吃点好的", "别省", "打钱", "买件"],
        "scene_name": "生活费",
        "replies": {
            "tough": "够用，我自己挣了点，不用总惦记。",
            "normal": "够花的妈，这个月还自己做家教赚了点，下个月不用打那么多。",
            "sweet": "收到收到～ 妈我爱你！周末请你吃顿好的（用你给的钱哈哈哈）",
        },
    },
    {
        "keywords": ["对象", "女朋友", "男朋友", "相亲", "结婚", "处对象"],
        "scene_name": "催对象",
        "replies": {
            "tough": "这事儿我有谱，你别催。",
            "normal": "妈，这事急不来，遇到合适的我一定带回来给你看，不让你操心。",
            "sweet": "妈～ 你先给我攒嫁妆吧缘分到了我第一个告诉你❤️",
        },
    },
    {
        "keywords": ["胃药", "药", "医院", "体检", "寄", "抽屉"],
        "scene_name": "寄药提醒",
        "replies": {
            "tough": "收到了，按时吃着。",
            "normal": "收到妈，今天就开始吃，最近胃没怎么疼，谢谢你惦记着。",
            "sweet": "收到啦❤️ 拍给你看——在吃了在吃了！妈你也记得去体检啊我们拉钩！",
        },
    },
    {
        "keywords": ["早上好", "晚安", "早安", "表情", "问候", "平安"],
        "scene_name": "早晚安",
        "replies": {
            "tough": "嗯，你也早/晚。",
            "normal": "早安妈，今天也好好照顾自己，我晚上忙完就找你。",
            "sweet": "妈我醒来第一个想到的就是你！今天也想你～ 中午我主动打给你❤️",
        },
    },
    {
        "keywords": ["工作", "实习", "加班", "压力", "辞职", "领导"],
        "scene_name": "工作近况",
        "replies": {
            "tough": "还行，能应付。",
            "normal": "挺好的爸，最近在做 XX 项目，等做完了跟你详细讲讲，不算太累。",
            "sweet": "爸爸～ 其实我最近有点累但很开心！周末跟你视频给你看看我工位上的小绿植🌿",
        },
    },
    {
        "keywords": ["讲座", "教授", "课程", "直播", "听课", "五点"],
        "scene_name": "养生讲座",
        "replies": {
            "tough": "听着呢，你讲得比我自律。",
            "normal": "妈你比我自律多了，回头把直播链接发我，我陪你看一次。",
            "sweet": "哇妈你太酷了！比我认识的教授都专业～ 下次直播叫上我一起听❤️",
        },
    },
]

DEMO_REPLY_DEFAULT = {
    "scene_name": "通用",
    "replies": {
        "tough": "收到，我有数的。",
        "normal": "知道了妈/爸，我最近挺好的，你放心，周末给你打电话。",
        "sweet": "呜呜呜想你啦❤️ 我也想多陪你说话，最近忙完这阵我就回去！",
    },
}


def _demo_reply(content: str, profile: str = "") -> dict:
    """无 Key 降级：关键词匹配场景剧本库，返回对应三档回复；
    有画像时做细节替换（拿手菜/爸爸爱好），让演示也有专属感"""
    matched_scene = None
    matched_keywords = []
    for scene in DEMO_REPLY_SCENARIOS:
        hits = [kw for kw in scene["keywords"] if kw in content]
        if hits:
            matched_scene = scene
            matched_keywords = hits
            break

    if matched_scene is None:
        matched_scene = DEMO_REPLY_DEFAULT

    replies = matched_scene["replies"]
    if profile:
        import re
        for pattern, repl in _profile_swaps(profile):
            replies = {k: re.sub(pattern, repl, v) for k, v in replies.items()}

    return {
        "scene_name": matched_scene["scene_name"],
        "matched_keywords": matched_keywords,
        "replies": replies,
    }


def _profile_swaps(profile: str):
    """从画像摘要里提取「拿手菜/爸爸爱好」，返回 (正则, 替换词) 列表；提取不到返回空列表"""
    import re
    swaps = []
    m = re.search(r"拿手菜是(.+?)(?:；|$)", profile)
    if m:
        swaps.append(("排骨", m.group(1)))
    m = re.search(r"爸爸爱好(.+?)(?:；|$)", profile)
    if m:
        hobby = m.group(1)
        # 「下棋/那盘棋」统一替换为爱好动词短语
        if "钓" in hobby:
            swaps.append(("那盘棋下得怎么样了？赢了还是被老张头压制了", "钓到大家伙了没"))
            swaps.append(("下棋|下得怎么样", hobby))
        else:
            swaps.append(("下棋|那盘棋", hobby))
    return swaps


REPLY_SYSTEM_PROMPT = """你是「家音」App 的回音壁。用户是子女，要回父母一段关心话。
你需要根据子女选的「语气画像」生成三档回复文案：

- tough（嘴硬）：轻描淡写、不煽情，但要让爸妈安心。适合不爱表露情感、酷酷的子女。
- normal（标准）：温和得体、像平常说话，给出具体细节（吃了什么/做什么/下次怎么安排）。最常用。
- sweet（撒娇）：情感外露、会用表情符号（❤️😭🥺 等），表达对爸妈的想念和爱。

风格要求：
1. 第一人称「我」；称呼可用「妈」「爸」或「妈/爸」。
2. 像真人微信对话，不要公文腔、不要排比句。
3. 不要超过 60 字，短句为主，留出可继续对话的空间。
4. 不出现「转发」「链接」「养生」等词汇（避免又变成机器腔）。
5. 不要否定爸妈的关心，不要"辟谣打脸"。

只输出如下 JSON（不要输出任何其他文字）：
{
  "scene_name": "识别到的话题场景（4-6字）",
  "replies": {
    "tough": "嘴硬档文案",
    "normal": "标准档文案",
    "sweet": "撒娇档文案"
  }
}"""


def reply_care(content: str, tone: str = "normal", profile: str = "") -> dict:
    """回音壁主入口：三档回复文案生成

    Args:
        content: 父母发来的原文（也可理解为子女想回应的话题）
        tone: 子女画像偏好 —— tough/normal/sweet。LLM 模式下作为提示词倾向；
              无 Key 演示模式下仍返回全部三档，tone 仅作参考。
        profile: 家庭画像摘要（称呼/拿手菜/爸爸爱好等），用于个性化。
    """
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
    model = os.getenv("LLM_MODEL", "deepseek-chat")

    if not api_key or OpenAI is None:
        return _demo_reply(content, profile)

    client = OpenAI(api_key=api_key, base_url=base_url)
    user_msg = (
        f"【父母原文】{content}\n\n"
        f"【子女语气偏好】{tone}（请仍然输出三档，只是该档要更对应该偏好）"
    )
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": REPLY_SYSTEM_PROMPT + _profile_block(profile)},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.85,
        response_format={"type": "json_object"},
    )
    text = resp.choices[0].message.content.strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return _demo_reply(content)
    # 兜底字段
    data.setdefault("scene_name", "通用")
    replies = data.get("replies") or {}
    for key in ("tough", "normal", "sweet"):
        replies.setdefault(key, "")
    data["replies"] = replies
    return data


# ---------- 连心话题卡：提示词 + 演示剧本库 ----------
# 场景：回家前 / 节日 / 生日 / 普通通话。每个场景 5 个保底开放性问题。
# 话题原则：具体、有烟火气、问到爸妈自己的生活（让他们也有得说），避免查户口式提问。

TOPIC_SYSTEM_PROMPT = """你是「家音」App 的连心话题卡。用户（子女）即将和父母打电话/视频通话，
你会收到一个通话场景，请生成 5 个「开放性问题」，帮助子女打开话匣、不尬聊。

话题设计原则：
1. 问爸妈自己的生活与近况（他们的菜园、棋局、老朋友、年轻时的故事），让他们有得说。
2. 具体有烟火气，例如「爸最近那盘棋下得怎么样了」而不是「你最近好吗」。
3. 开放式问题，不能是「是/否」就能答完的。
4. 至少 1 个问题把子女自己也带进去（分享近况、约下次见面），形成双向交流。
5. 温暖不说教，不出现「沟通」「关爱」等书面词。

只输出如下 JSON（不要输出任何其他文字）：
{
  "scene_name": "场景名（2-6字）",
  "topics": ["话题1", "话题2", "话题3", "话题4", "话题5"]
}"""

DEMO_TOPIC_SCENARIOS = {
    "before_home": {
        "scene_name": "回家前",
        "topics": [
            "爸最近那盘棋下得怎么样了？赢了还是被老张头压制了？",
            "妈，我回去那几天你最想给我做哪顿饭？我现在就开始馋了",
            "家里最近有什么新变化吗？阳台的花、小区门口的店都算",
            "这次回去有什么想让我陪你一起办的事吗？上医院、买东西都行",
            "我要带点这边特产回去，你们最想要啥？别又说『啥都不缺』",
        ],
    },
    "festival": {
        "scene_name": "节日",
        "topics": [
            "今年中秋家里的月饼是谁买的？还是妈自己烙的饼？",
            "爸，你们中秋节那天打算怎么过？跟谁一起吃团圆饭？",
            "家里过节还有什么老讲究？我好像只记得小时候吃鸭子了",
            "妈，你小时候的中秋是怎么过的？那时候有月饼吃吗？",
            "咱们视频一起吃顿『云团圆饭』吧，你吃你的我吃我的，互相汇报吃了啥",
        ],
    },
    "birthday": {
        "scene_name": "生日",
        "topics": [
            "妈，你今年生日想要什么礼物？这次不许说『别乱花钱』",
            "爸，你年轻时候生日都怎么过的？姥姥那时候给你煮鸡蛋吗？",
            "今年生日咱们视频，我给你唱首生日歌，你得给我鼓掌",
            "你们生日那天我请客，你俩想吃什么？海底捞还是家里的锅子？",
            "说好了，明年生日我人到场，你把日子给我记在日历上",
        ],
    },
    "daily": {
        "scene_name": "普通通话",
        "topics": [
            "爸，最近那个电视剧你追到第几集了？好看在哪我听听",
            "妈，你跳广场舞的队伍里最近有什么新八卦？给我讲讲",
            "家里那只猫/狗最近又干啥坏事了？拍照给我看看",
            "你们最近体检了吗？结果怎么样？哪些指标咱得注意着点",
            "我最近学会做一道新菜，周末视频我做给你看，你给打个分",
        ],
    },
}

TOPIC_SCENE_KEYS = list(DEMO_TOPIC_SCENARIOS.keys())


def _demo_topic(scene: str, profile: str = "") -> dict:
    """无 Key 降级：按场景返回保底 5 话题（有画像时做细节替换）；未知场景落到普通通话"""
    scenario = DEMO_TOPIC_SCENARIOS.get(scene) or DEMO_TOPIC_SCENARIOS["daily"]
    topics = list(scenario["topics"])
    if profile:
        import re
        for pattern, repl in _profile_swaps(profile):
            topics = [re.sub(pattern, repl, t) for t in topics]
    return {
        "scene_name": scenario["scene_name"],
        "topics": topics,
    }


def topic_care(scene: str = "daily", profile: str = "") -> dict:
    """连心话题卡主入口：按通话场景生成 5 个开放性问题"""
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
    model = os.getenv("LLM_MODEL", "deepseek-chat")

    if not api_key or OpenAI is None:
        return _demo_topic(scene, profile)

    scenario = DEMO_TOPIC_SCENARIOS.get(scene) or DEMO_TOPIC_SCENARIOS["daily"]
    user_msg = f"【通话场景】{scenario['scene_name']}\n请生成 5 个该场景下的开放性话题。"
    client = OpenAI(api_key=api_key, base_url=base_url)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": TOPIC_SYSTEM_PROMPT + _profile_block(profile)},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.9,
        response_format={"type": "json_object"},
    )
    text = resp.choices[0].message.content.strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return _demo_topic(scene)
    # 兜底字段
    data.setdefault("scene_name", scenario["scene_name"])
    topics = data.get("topics") or []
    if not isinstance(topics, list) or not topics:
        topics = list(scenario["topics"])
    data["topics"] = [str(t) for t in topics][:5]
    return data


# ---------- 彩排室：会话引擎 + 演示剧本 + 爸妈人设提示词 ----------
# 多轮对话：子女在开口前先和「AI 爸妈」彩排最难说出口的话。
# 无 Key 时按剧本推进（爸妈先心疼、再问情况、最后给托底），Key 后走真实 LLM 多轮。

REHEARSAL_SYSTEM_PROMPT = """你是「家音」App 彩排室里的 AI 爸爸/妈妈。用户（子女）选择了一个「难以开口」的场景，
要在真正打电话之前，先和你把这段对话练一遍。

人设与口吻：
1. 接地气、有烟火气：说话像微信语音，会提排骨、炖汤、天气、老家的猫，不说书面语。
2. 第一反应永远是心疼，不是质问：先「没事没事，别急」，再慢慢问情况。
3. 不说教、不评判、不翻旧账；孩子说什么你先接住情绪，再往下聊。
4. 会主动托底：「大不了回家」「妈给你打钱」「爸养你两个月」这类话要自然说出来。
5. 每轮回复 2-4 句、不超过 80 字，留出让孩子继续说的空间。
6. 偶尔带点爸妈式的小唠叨或玩笑，让对话不那么沉重。

对话推进策略：孩子越说越具体时，你也从心疼转向出主意、给安排（补考时间、回家车票、打钱），
最后给一个温暖的收尾，让孩子觉得「其实没那么难开口」。"""

# 演示剧本：每条 scene 一个爸妈多轮台本，第 0 条是开场白（爸妈先起话头）
DEMO_REHEARSAL_SCENARIOS = {
    "fail_exam": {
        "scene_name": "挂科了",
        "parent": "妈妈",
        "parent_emoji": "👩",
        "script": [
            "儿子，吃饭没？妈今天炖了排骨，可惜你吃不着……对了，你上回说的那个考试，出分了没？",
            "啊？挂了？……没事没事，先别急，一门课而已，天塌不下来。妈问你，是不是那阵子太忙没休息好？",
            "补考什么时候？别自己闷头慌，你表哥当年也挂过，后来补考稳稳过的，回头妈让他跟你唠唠经验。",
            "补考要交钱不？妈明天给你转点过去，这钱不许省啊。",
            "行了，这事就这么定了。周末视频，妈给你看看排骨炖得啥样，考试的事咱不提了。",
        ],
    },
    "breakup": {
        "scene_name": "分手了",
        "parent": "妈妈",
        "parent_emoji": "👩",
        "script": [
            "闺女，你这两天朋友圈怎么不更新了？妈瞅着心里不踏实，是不是有啥事？",
            "……是不是跟那孩子吵架了？还是……分了？你说，妈听着呢，不怪你。",
            "哭了吧？傻孩子，难受就哭出来，别憋着。妈年轻时候也经历过，妈懂那滋味。",
            "他要是欺负你了你跟妈说，妈嘴笨不会讲道理，但妈能陪你说到天亮。",
            "饭要好好吃，觉要好好睡。缓过来跟妈视频，家里的猫又胖了，给你看看。",
        ],
    },
    "quit_job": {
        "scene_name": "想辞职",
        "parent": "爸爸",
        "parent_emoji": "👨",
        "script": [
            "儿子，你妈说你这礼拜话很少。工作上的事，跟爸说说？",
            "想辞？……爸不催你下结论。你先说说，是身体累着了，还是跟人处不来了？",
            "真想好了就辞，回来住俩月，爸养你。爸这辈子就想让你知道，家一直在。",
            "不过爸多句嘴：看看手里的钱能撑多久，骑驴找马最稳当。主意你自己拿，爸都支持。",
            "行了，别熬太晚。周末给你妈打个电话，她嘴上不说，比我还惦记你。",
        ],
    },
    "money_short": {
        "scene_name": "生活费不够",
        "parent": "妈妈",
        "parent_emoji": "👩",
        "script": [
            "宝，妈看你上礼拜说月底了……是不是钱不凑手了？跟妈说实话，妈不怪你。",
            "跟妈还客气啥？缺多少，妈明儿一早给你转过去。",
            "是谈恋爱花多了，还是又让直播带货忽悠着买了？——妈就是想知道，不骂你。",
            "下个月妈多打三百，兼职别接那么多了，身体要紧，听见没。",
            "记住啊，钱不够就跟妈要，不丢人。千万别碰那些网贷，天大的事有妈呢。",
        ],
    },
}

# 剧本走完后的兜底台词（循环使用，保持对话继续）
REHEARSAL_FALLBACK_LINES = [
    "嗯嗯，妈听着呢，你接着说。",
    "后来呢？妈想知道你心里怎么想的。",
    "傻孩子，说出来是不是好受多了？",
    "行，这事妈记下了。还有啥想跟妈说的不？",
]

# 内存会话表：session_id -> {scene, history: [{role, content}]}
REHEARSAL_SESSIONS: dict = {}
REHEARSAL_MAX_SESSIONS = 200


def _new_session_id() -> str:
    import time
    import random
    return f"{int(time.time() * 1000):x}{random.randint(100, 999)}"


def rehearsal_start(scene: str = "fail_exam") -> dict:
    """彩排室入口：创建会话，返回爸妈开场白"""
    scenario = DEMO_REHEARSAL_SCENARIOS.get(scene)
    if scenario is None:
        scene, scenario = "fail_exam", DEMO_REHEARSAL_SCENARIOS["fail_exam"]
    session_id = _new_session_id()
    opening = scenario["script"][0]
    REHEARSAL_SESSIONS[session_id] = {
        "scene": scene,
        "history": [{"role": "assistant", "content": opening}],
    }
    # 会话数超限时丢掉最老的（dict 保持插入序）
    while len(REHEARSAL_SESSIONS) > REHEARSAL_MAX_SESSIONS:
        REHEARSAL_SESSIONS.pop(next(iter(REHEARSAL_SESSIONS)))
    return {
        "session_id": session_id,
        "scene_name": scenario["scene_name"],
        "parent": scenario["parent"],
        "parent_emoji": scenario["parent_emoji"],
        "opening": opening,
    }


def _demo_rehearsal_reply(session: dict) -> str:
    """无 Key 降级：按剧本轮次返回爸妈台词，走完用兜底台词循环"""
    scenario = DEMO_REHEARSAL_SCENARIOS.get(session["scene"]) or DEMO_REHEARSAL_SCENARIOS["fail_exam"]
    turn = sum(1 for m in session["history"] if m["role"] == "user")  # 孩子已说过的轮数
    script = scenario["script"]
    if turn < len(script):
        return script[turn]
    return REHEARSAL_FALLBACK_LINES[(turn - len(script)) % len(REHEARSAL_FALLBACK_LINES)]


def rehearsal_chat(session_id: str, content: str):
    """彩排室多轮对话：返回 {reply, turn}；会话不存在返回 None"""
    session = REHEARSAL_SESSIONS.get(session_id)
    if session is None:
        return None

    session["history"].append({"role": "user", "content": content})
    turn = sum(1 for m in session["history"] if m["role"] == "user")

    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL", "https://api.deepseek.com")
    model = os.getenv("LLM_MODEL", "deepseek-chat")

    if not api_key or OpenAI is None:
        reply = _demo_rehearsal_reply(session)
    else:
        scenario = DEMO_REHEARSAL_SCENARIOS.get(session["scene"]) or DEMO_REHEARSAL_SCENARIOS["fail_exam"]
        system = (
            f"{REHEARSAL_SYSTEM_PROMPT}\n\n"
            f"【本次设定】你扮演孩子的{scenario['parent']}，场景：孩子要开口说「{scenario['scene_name']}」这件事。"
        )
        client = OpenAI(api_key=api_key, base_url=base_url)
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": system}] + session["history"],
                temperature=0.9,
            )
            reply = resp.choices[0].message.content.strip()
        except Exception:
            reply = _demo_rehearsal_reply(session)

    session["history"].append({"role": "assistant", "content": reply})
    return {"reply": reply, "turn": turn}
