# -*- coding: utf-8 -*-
"""家音演示视频 · AI 素材批量生成工具
用法:
  python gen_videos.py submit   # 提交全部片段（不等待），写 jobs.json
  python gen_videos.py poll     # 轮询所有任务，下载已完成的到 ./素材/
提示词来源: docs/家音-AI视频提示词方案v2.md
"""
import json
import os
import sys
import time
import subprocess
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
JOBS_FILE = os.path.join(HERE, "jobs.json")
OUT_DIR = os.path.join(HERE, "素材")
BUDDY = r"d:\CodeBuddy CN\resources\app\extensions\genie\out\extension\builtin\buddy-multimodal-generation\scripts\buddy-cloud.py"
TOKEN = os.environ.get("BUDDY_CLOUD_TOKEN", "").strip()
if not TOKEN:
    _tf = os.path.join(HERE, "token.txt")
    if os.path.exists(_tf):
        TOKEN = open(_tf, encoding="utf-8").read().strip()

COMMON = "，竖屏构图，写实电影感，画面中无任何文字、水印和乱码"

SEGMENTS = {
    "01_深夜刷手机": "深夜大学宿舍，一名22岁中国男大学生，黑色短发，深灰色连帽卫衣，躺在床上侧身看手机，台灯发出暖黄光，手机冷光映亮他的脸，镜头缓慢推近，暖色调，浅景深",
    "02_妈妈发消息": "中国家庭客厅，傍晚，一位55岁中国母亲，齐耳短发有少许白发，枣红色针织开衫，坐沙发上戴老花镜看手机，神情温柔牵挂，茶几上一杯热茶冒着热气，镜头缓慢推近，暖黄色调",
    "03_桌前思考": "深夜书桌前，一名22岁中国男大学生，黑色短发，深灰色连帽卫衣，坐着凝视手中的手机，台灯暖光打在侧脸，若有所思的表情，固定镜头中景，暖色调，浅景深",
    "04_深呼吸打电话": "深夜宿舍窗边，一名22岁中国男大学生，黑色短发，深灰色连帽卫衣，戴耳机，手持手机贴在耳边，闭眼深呼吸，神情紧张忐忑，窗外城市夜景灯火，暖光轮廓，镜头缓慢推近面部特写",
    "05_通话中微笑": "深夜宿舍窗边，一名22岁中国男大学生，黑色短发，深灰色连帽卫衣，戴耳机打电话，缓慢露出温暖的笑容，眼中有微微泪光，肩膀放松，窗外夜景虚化成光斑，面部特写，浅景深，暖色调",
    "06_妈妈接电话笑": "中国家庭厨房，晚上，一位55岁中国母亲，齐耳短发有少许白发，枣红色针织开衫，系围裙，拿手机贴耳边打电话，先是安静倾听，然后开心地笑起来，眼角带笑纹，身旁锅里冒热气，中景缓慢推近面部，暖黄色调",
    "07_空镜热汤": "中国家庭餐桌特写，一碗冒着热气的汤，旁边几样家常菜和碗筷，暖黄灯光从上方洒下，热气袅袅上升，镜头缓慢下移，浅景深，治愈系暖色调，写实慢镜头",
    "08a_空镜城市灯火": "深夜城市居民楼外景，千家万户的窗户透出暖黄灯光，一扇窗里有年轻人的剪影，镜头缓慢拉远，夜空有星星，深情温暖，写实空镜",
    "08b_空镜小镇窗光": "傍晚中国小镇的老居民楼，一扇窗户透出温暖的黄光，窗台上有一盆绿植，镜头缓慢上摇到天空，宁静温馨，写实空镜",
}


def run_buddy(args):
    r = subprocess.run([sys.executable, BUDDY] + args + ["--token", TOKEN],
                       capture_output=True, text=True, encoding="utf-8")
    out = r.stdout.strip()
    try:
        return json.loads(out[out.index("{"):]), r.stderr
    except (ValueError, json.JSONDecodeError):
        return {"error": "PARSE_FAIL", "raw": out[:500], "stderr": r.stderr[-500:]}, r.stderr


def submit():
    os.makedirs(OUT_DIR, exist_ok=True)
    jobs = {}
    if os.path.exists(JOBS_FILE):
        jobs = json.load(open(JOBS_FILE, encoding="utf-8"))
    for name, prompt in SEGMENTS.items():
        if name in jobs and jobs[name].get("status") in ("DONE", "SUBMITTED"):
            print(f"[skip] {name} 已提交/完成")
            continue
        print(f"[submit] {name} ...")
        res, _ = run_buddy(["video", prompt + COMMON, "--no-poll"])
        jid = res.get("job_id") or (res.get("raw_result") or {}).get("JobId") or ""
        if jid:
            jobs[name] = {"job_id": jid, "status": "SUBMITTED", "prompt": prompt}
            print(f"  -> job {jid}")
        else:
            jobs[name] = {"status": "FAIL", "res": res}
            print(f"  -> 失败: {json.dumps(res, ensure_ascii=False)[:300]}")
        json.dump(jobs, open(JOBS_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps({k: v.get("job_id", v.get("status")) for k, v in jobs.items()},
                     ensure_ascii=False, indent=2))


def download(url, path):
    print(f"  下载 -> {os.path.basename(path)}")
    urllib.request.urlretrieve(url, path)


def poll(max_wait=900):
    os.makedirs(OUT_DIR, exist_ok=True)
    jobs = json.load(open(JOBS_FILE, encoding="utf-8"))
    todo = {k: v for k, v in jobs.items() if v.get("status") not in ("DONE",)}
    start = time.time()
    while todo and time.time() - start < max_wait:
        for name in list(todo):
            jid = todo[name].get("job_id")
            if not jid:
                todo.pop(name)
                continue
            res, _ = run_buddy(["status", jid, "--type", "video"])
            raw = res.get("raw_result") or res
            status = (res.get("status") or raw.get("Status") or "").upper()
            if status in ("DONE", "SUCCESS", "FINISH", "FINISHED") or res.get("result_url"):
                url = res.get("result_url") or raw.get("ResultVideoUrl") or raw.get("VideoUrl") or ""
                if url:
                    try:
                        download(url, os.path.join(OUT_DIR, f"{name}.mp4"))
                        jobs[name].update(status="DONE", url=url)
                        print(f"[DONE] {name}")
                    except Exception as e:
                        print(f"  下载失败 {name}: {e}，保留 URL 稍后重试")
                        jobs[name].update(status="DONE", url=url)
                else:
                    jobs[name]["status"] = "DONE"
                    jobs[name]["res"] = res
                    print(f"[?] {name} 完成但无 URL: {json.dumps(res, ensure_ascii=False)[:300]}")
                todo.pop(name)
            elif status in ("FAIL", "FAILED", "ERROR"):
                jobs[name]["status"] = "FAIL"
                jobs[name]["res"] = res
                print(f"[FAIL] {name}: {json.dumps(res, ensure_ascii=False)[:300]}")
                todo.pop(name)
            else:
                print(f"[..] {name}: {status or 'RUN'}")
            json.dump(jobs, open(JOBS_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
        if todo:
            time.sleep(20)
    if todo:
        print(f"仍有 {len(todo)} 个任务未完成，稍后再运行 poll: {list(todo)}")
    done = [k for k, v in jobs.items() if v.get("status") == "DONE"]
    print(f"\n完成 {len(done)}/{len(jobs)}: {done}")


if __name__ == "__main__":
    if not TOKEN:
        sys.exit("请先设置环境变量 BUDDY_CLOUD_TOKEN")
    cmd = sys.argv[1] if len(sys.argv) > 1 else "poll"
    {"submit": submit, "poll": poll}[cmd]()
