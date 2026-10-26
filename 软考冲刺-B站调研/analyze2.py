# -*- coding: utf-8 -*-
"""分析阶段 v2：wbi重抓后的评论高赞提取"""
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

BASE = r"D:\11.project\iwen-dsh\doubao-list\allTest\软考冲刺-B站调研\软考冲刺-B站原始数据"
with open(BASE + r"\视频评论_逐条.json", encoding="utf-8") as f:
    data = json.load(f)

lines = []
for bvid, rec in data.items():
    cs = rec['comments']
    has_msg = sum(1 for c in cs if c.get('message'))
    lines.append(f"## {bvid} {rec['title'][:34]}  抓{len(cs)}/总{rec['count']} 有正文{has_msg}")
    top = sorted(cs, key=lambda x: -(x.get('like') or 0))[:8]
    for c in top:
        msg = (c.get('message') or '').replace('\n', ' ')
        if not msg.strip(): continue
        lines.append(f"  [{c.get('like')}赞] {c.get('uname')}: {msg[:160]}")
        for sc in (c.get('subs') or [])[:4]:
            sm = (sc.get('message') or '').replace('\n', ' ')
            if sm.strip():
                lines.append(f"      └[{sc.get('like')}赞] {sc.get('uname')}: {sm[:130]}")
    lines.append("")

open(BASE + r"\评论高赞提取.txt", "w", encoding="utf-8").write("\n".join(lines))
print("WROTE", len(lines), "lines")
