# -*- coding: utf-8 -*-
import base64, json, sys
sys.stdout.reconfigure(encoding="utf-8")
t = open(r"C:\Users\潘亦然\Desktop\家音.潘\docs\视频素材\token.txt", encoding="utf-8").read().strip()
parts = t.split(".")
print("总长度:", len(t), "| 段数:", len(parts), "| 各段长度:", [len(p) for p in parts])
for i, p in enumerate(parts[:2]):
    dec = base64.urlsafe_b64decode(p + "=" * (-len(p) % 4))
    print(f"\n--- part{i} 原始解码 ({len(dec)} bytes) ---")
    print(repr(dec.decode("utf-8", errors="replace")))
print("\n--- 签名 (part2) ---")
print(parts[2][:60], "...", parts[2][-20:], f"(len={len(parts[2])})")
