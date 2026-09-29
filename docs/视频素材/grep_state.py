# -*- coding: utf-8 -*-
import sqlite3, json, re, sys
sys.stdout.reconfigure(encoding="utf-8")
DB = r"c:\Users\潘亦然\AppData\Roaming\CodeBuddy CN\User\globalStorage\state.vscdb"
con = sqlite3.connect(DB)
cur = con.cursor()
row = cur.execute("select value from ItemTable where key='Tencent-Cloud.coding-copilot'").fetchone()
val = row[0]
# 找所有 key 里带 token/jwt/temp/secret 的字段及其值开头
def walk(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}" if path else k
            if re.search(r"token|jwt|temp|secret|credential|auth", k, re.I) and not isinstance(v, (dict, list)):
                s = str(v)
                print(f"[{p}] = {s[:120]}{'...' if len(s) > 120 else ''} (len={len(s)})")
            walk(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:5]):
            walk(v, f"{path}[{i}]")
walk(json.loads(val))
