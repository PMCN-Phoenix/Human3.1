# -*- coding: utf-8 -*-
"""分析阶段：从抓取JSON提取高赞评论 + 字幕要点，供报告使用"""
import json, os, re

BASE = r"D:\11.project\iwen-dsh\doubao-list\allTest\软考冲刺-B站调研\软考冲刺-B站原始数据"
with open(os.path.join(BASE, '视频评论_逐条.json'), encoding='utf-8') as f:
    data = json.load(f)

# 1) 各视频评论概况 + 高赞评论 Top
print("=" * 70)
print("【评论概况与高赞评论】")
print("=" * 70)
for bvid, rec in data.items():
    title = rec['title'][:36]
    cs = rec['comments']
    if not cs:
        print(f"\n## {bvid} {title}\n  评论: 0")
        continue
    top = sorted(cs, key=lambda x: -(x.get('like') or 0))[:6]
    print(f"\n## {bvid} {title}  (抓{len(cs)}条/总数{rec['count']})")
    for c in top:
        msg = (c.get('message') or '').replace('\n', ' ')[:150]
        print(f"  [{c.get('like')}赞] {c.get('uname')}: {msg}")
        for sc in (c.get('subs') or [])[:3]:
            sm = (sc.get('message') or '').replace('\n', ' ')[:120]
            print(f"      └[{sc.get('like')}赞] {sc.get('uname')}: {sm}")

# 2) 字幕内容：输出全文到单独文件（供精读）
print("\n" + "=" * 70)
print("【字幕导出】")
print("=" * 70)
sub_out = os.path.join(BASE, '字幕')
os.makedirs(sub_out, exist_ok=True)
for bvid, rec in data.items():
    body = rec.get('subtitle')
    if not body:
        continue
    txt = ''.join(x.get('content', '') for x in body)
    txt = re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])', '', txt)
    with open(os.path.join(sub_out, f'{bvid}_字幕.txt'), 'w', encoding='utf-8') as f:
        f.write(f"标题: {rec['title']}\n作者: {rec['owner']}\n时长: {rec['duration']}s\n\n{txt}")
    print(f"  {bvid} {rec['title'][:30]}: {len(body)}段/{len(txt)}字 -> 字幕/{bvid}_字幕.txt")
