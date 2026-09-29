# -*- coding: utf-8 -*-
import sqlite3, json, sys
sys.stdout.reconfigure(encoding="utf-8")
DB = r"c:\Users\潘亦然\AppData\Roaming\CodeBuddy CN\User\globalStorage\state.vscdb"
con = sqlite3.connect(DB)
cur = con.cursor()
tables = [r[0] for r in cur.execute("select name from sqlite_master where type='table'").fetchall()]
print("表:", tables)
for t in tables:
    cols = [c[1] for c in cur.execute(f"PRAGMA table_info({t})").fetchall()]
    print(t, "列:", cols)
    for key in ["secret://{\"extensionId\":\"tencent-cloud.coding-copilot\",\"key\":\"planning-genie.new.accessTokencn\"}", "Tencent-Cloud.coding-copilot"]:
        try:
            row = cur.execute(f"select * from {t} where key=?", (key,)).fetchone()
            if row:
                print(f"\n=== {t} / {key} ===")
                for c, v in zip(cols, row):
                    s = str(v)
                    print(f"[{c}] ({len(s)} chars):", s[:300].replace("\n", " "))
        except Exception:
            pass
