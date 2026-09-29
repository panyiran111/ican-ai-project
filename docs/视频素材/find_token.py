# -*- coding: utf-8 -*-
import sqlite3, re, json, sys
sys.stdout.reconfigure(encoding="utf-8")
DB = r"c:\Users\潘亦然\AppData\Roaming\CodeBuddy CN\User\globalStorage\state.vscdb"
con = sqlite3.connect(DB)
cur = con.cursor()
rows = cur.execute("select key from ItemTable").fetchall()
pat = re.compile(r"token|cloud|genie|auth|secret|cred|cos|jwt|bearer", re.I)
keys = [k for k, in rows if pat.search(k)]
print("匹配的键：")
for k in keys:
    print(" -", k)
print("总键数:", len(rows))
