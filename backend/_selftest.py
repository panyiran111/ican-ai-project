import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from llm import _demo_reply

cases = [
    ('养生文', '震惊！《十种致癌食物，年轻人天天在吃！》你天天点外卖，奶茶当水喝'),
    ('中秋回家', '儿子，中秋到底回不回家？你爸天天在日历上画圈。'),
    ('熬夜提醒', '别老熬夜，凌晨还在发朋友圈我看到了'),
    ('降温加衣', '降温了记得加衣服别感冒'),
    ('生活费', '生活费够不够花？别省着'),
    ('催对象', '有对象了吗？年纪也不小了'),
    ('寄药', '胃药我给你寄了两盒，记得吃'),
    ('早晚安', '早上好！今天也要好好的'),
    ('工作', '工作怎么样？最近累不累'),
    ('讲座', '我今天听了王教授的养生讲座特别好'),
    ('默认兜底', '今天天气不错随便问问'),
]

for label, c in cases:
    r = _demo_reply(c)
    print(f'[{label:>6}] -> scene={r["scene_name"]:>6}  kw={r["matched_keywords"]}')
    for k in ['tough', 'normal', 'sweet']:
        print(f'    {k:>6}: {r["replies"][k]}')
    print()