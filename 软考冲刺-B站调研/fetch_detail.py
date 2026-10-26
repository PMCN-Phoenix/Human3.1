# -*- coding: utf-8 -*-
"""软件设计师 B站调研 · 阶段2：精抓队列（评论+字幕）"""
import requests, re, json, time, hashlib, urllib.parse, os

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]

s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'})

import sys
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool
pool = BiliCookiePool()
s.headers['Cookie'] = pool.get_cookie()

nav = s.get('https://api.bilibili.com/x/web-interface/nav', timeout=20).json()
wbi = nav['data']['wbi_img']
img = wbi['img_url'].rsplit('/', 1)[-1].split('.')[0]
sub = wbi['sub_url'].rsplit('/', 1)[-1].split('.')[0]
mixin = ''.join((img + sub)[i] for i in MIXIN)[:32]

def sign(p):
    p = dict(p); p['wts'] = str(int(time.time()))
    q = urllib.parse.urlencode(sorted(p.items()))
    p['w_rid'] = hashlib.md5((q + mixin).encode()).hexdigest()
    return p

BASE = r"D:\11.project\iwen-dsh\doubao-list\allTest\软考冲刺-B站调研\软考冲刺-B站原始数据"
with open(os.path.join(BASE, '搜索清单_top40.json'), encoding='utf-8') as f:
    top40 = json.load(f)
bvid2info = {v['bvid']: v for v in top40}

# 精抓队列：按 12天冲刺适配度挑选（短时攻略/考点/技巧/真题→全抓字幕+评论；超长合集→只抓评论）
FULL = [  # 全量：字幕 + 评论
    'BV1eK42117J2',  # 希赛 数据流图精讲
    'BV1VXorB7EFB',  # 5小时高频考点
    'BV1W4em6fEMR',  # 真题2021-2026(长) → 仍抓字幕试试
    'BV1by5K6qEL2',  # 真题2021-2025(长)
]
# 从 top40 里按标题关键词再挑（补充短时冲刺类）
KEY = ['考前1小时', '两周快速备考', '通关攻略', '下午1数据流图', '下午题高频考点', '说它的强度',
       '别裸考', '挑战40天', '考后分享', '设计模式', '算法基础', '高频考点大合集', '备考成功经验',
       'UML专题', 'C语言算法', '必得分技巧', '冲刺总结', '急救', '模拟卷', '母题']
for v in top40:
    t = v['title']
    if any(k in t for k in KEY) and v['bvid'] not in FULL:
        FULL.append(v['bvid'])

# 只抓评论的超长合集（评论区常有资料/经验）
COMMENTS_ONLY = ['BV1U421S7QcA', 'BV1Sx421k7F8']  # 占位，下面按实际存在过滤

print(f'精抓队列共 {len(FULL)} 个:')
for b in FULL:
    print(' ', b, bvid2info[b]['title'][:40], f"({bvid2info[b]['dur']}s)")

out = {}
for bvid in FULL:
    info = bvid2info[bvid]
    dur = info['dur']
    print(f'\n=== {bvid} {info["title"][:36]} dur={dur}s ===')
    # ① 网页 HTML 拿 aid/cid
    try:
        r = s.get(f'https://www.bilibili.com/video/{bvid}/', timeout=25)
        m = (re.search(r'window\.__INITIAL_STATE__=(.*?);\(function', r.text, re.S)
             or re.search(r'window\.__INITIAL_STATE__=(.*?);\s*</script>', r.text, re.S))
        vd = json.loads(m.group(1))['videoData']
        aid, cid = vd['aid'], vd['cid']
        print(f'  aid={aid} cid={cid} title={vd["title"][:30]}')
    except Exception as e:
        print(f'  ERR video: {e}')
        continue

    rec = {'bvid': bvid, 'title': info['title'], 'aid': aid, 'cid': cid,
           'owner': info['author'], 'duration': dur, 'desc': info['desc'], 'count': 0, 'comments': []}

    # ② 评论（主评论 + 楼中楼）
    try:
        total, pn = None, 1
        while pn <= 12:
            d = s.get('https://api.bilibili.com/x/v2/reply',
                      params={'oid': aid, 'type': 1, 'pn': pn, 'ps': 20, 'sort': 2},
                      headers={'Referer': f'https://www.bilibili.com/video/{bvid}/'}, timeout=25).json()
            dd = d.get('data') or {}
            reps = dd.get('replies') or []
            if not reps: break
            if total is None:
                total = (dd.get('page') or {}).get('count') or 0
            for c in reps:
                cm = {'uname': c.get('member', {}).get('uname'), 'like': c.get('like'),
                      'rcount': c.get('rcount'), 'rpid': c.get('rpid'), 'message': c.get('message'), 'subs': []}
                if c.get('rcount', 0) > 0:
                    try:
                        d2 = s.get('https://api.bilibili.com/x/v2/reply/reply',
                                   params={'oid': aid, 'type': 1, 'root': c['rpid'], 'pn': 1, 'ps': 20},
                                   headers={'Referer': f'https://www.bilibili.com/video/{bvid}/'}, timeout=25).json()
                        for sc in (d2.get('data', {}).get('replies') or []):
                            cm['subs'].append({'uname': sc.get('member', {}).get('uname'),
                                               'like': sc.get('like'), 'message': sc.get('message')})
                        time.sleep(0.9)
                    except Exception as e:
                        print(f'    sub ERR {e}')
                rec['comments'].append(cm)
            rec['count'] = total if total else len(rec['comments'])
            if len(rec['comments']) >= (total or 1): break
            pn += 1
            time.sleep(1.2)
        print(f'  评论 {len(rec["comments"])} 条 / 总数 {rec["count"]}')
    except Exception as e:
        print(f'  ERR comments: {e}')

    # ③ 字幕（wbi 接口；长视频 >2h 跳过字幕）
    rec['subtitle'] = None
    if dur < 7200:
        try:
            q = sign({'bvid': bvid, 'cid': str(cid)})
            d = s.get('https://api.bilibili.com/x/player/wbi/v2', params=q,
                      headers={'Referer': f'https://www.bilibili.com/video/{bvid}/'}, timeout=20).json()
            subs = ((d.get('data') or {}).get('subtitle') or {}).get('subtitles') or []
            if subs:
                pick = next((x for pref in ['zh-Hans', 'zh-CN', 'zh', 'ai-zh'] for x in subs if x.get('lan') == pref), subs[0])
                u = pick['subtitle_url']
                if u.startswith('//'): u = 'https:' + u
                for attempt in range(4):
                    try:
                        body = s.get(u, headers={'Referer': f'https://www.bilibili.com/video/{bvid}/'}, timeout=25).json().get('body')
                        if body:
                            rec['subtitle'] = body
                            print(f'  字幕 {len(body)} 段 (lan={pick.get("lan")})')
                            break
                    except Exception:
                        time.sleep(3 + attempt)
                if not rec['subtitle']:
                    print('  字幕 URL 为空/获取失败（可能无AI字幕）')
            else:
                print('  无 AI 字幕（可能硬字幕）')
        except Exception as e:
            print(f'  ERR subtitle: {e}')

    out[bvid] = rec
    # 每视频落盘一次（防中断丢失）
    with open(os.path.join(BASE, '视频评论_逐条.json'), 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

print(f'\n=== 完成 {len(out)}/{len(FULL)} 个视频 ===')
