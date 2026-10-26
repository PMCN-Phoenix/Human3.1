# -*- coding: utf-8 -*-
"""修正评论抓取：改用 wbi 签名接口 /x/v2/reply/wbi/main（非 wbi 已被硬封锁返回 null）"""
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
print('isLogin:', nav['data'].get('isLogin'), '| uname:', nav['data'].get('uname'))
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
with open(os.path.join(BASE, '视频评论_逐条.json'), encoding='utf-8') as f:
    data = json.load(f)

def fetch_main(aid, bvid):
    """wbi 主评论分页"""
    out = []
    total, pn = None, 1
    while pn <= 15:
        try:
            p = sign({'oid': aid, 'type': 1, 'pn': pn, 'ps': 20, 'sort': 2})
            r = s.get('https://api.bilibili.com/x/v2/reply/wbi/main', params=p,
                      headers={'Referer': f'https://www.bilibili.com/video/{bvid}/'}, timeout=25)
            d = r.json()
            if d.get('code') == -412:
                print(f'    412 on pn={pn}, sleep 5s'); time.sleep(5); continue
            dd = d.get('data') or {}
            reps = dd.get('replies') or []
            if not reps: break
            if total is None:
                total = (dd.get('cursor') or {}).get('all_count') or 0
            out.extend(reps)
            if len(out) >= (total or 1) or len(reps) < 20: break
            pn += 1
            time.sleep(1.2)
        except Exception as e:
            print(f'    ERR pn={pn}: {e}')
            break
    return out, total

def fetch_subs(aid, root, bvid):
    """wbi 楼中楼"""
    subs = []
    pn = 1
    while pn <= 3:
        try:
            p = sign({'oid': aid, 'type': 1, 'root': root, 'pn': pn, 'ps': 20})
            r = s.get('https://api.bilibili.com/x/v2/reply/wbi/reply', params=p,
                      headers={'Referer': f'https://www.bilibili.com/video/{bvid}/'}, timeout=25)
            d = r.json()
            if d.get('code') == -412:
                time.sleep(4); continue
            reps = (d.get('data') or {}).get('replies') or []
            if not reps: break
            subs.extend(reps)
            if len(reps) < 20: break
            pn += 1
            time.sleep(1.0)
        except Exception as e:
            print(f'    sub ERR: {e}')
            break
    return subs

for bvid, rec in data.items():
    aid = rec.get('aid')
    if not aid: continue
    print(f"=== {bvid} {rec['title'][:30]} ===")
    try:
        reps, total = fetch_main(aid, bvid)
        print(f"  主评论 {len(reps)} / 总数 {total}")
        new_comments = []
        for c in reps:
            cm = {'uname': c.get('member', {}).get('uname'), 'like': c.get('like'),
                  'rcount': c.get('rcount'), 'rpid': c.get('rpid'),
                  'message': c.get('content', {}).get('message') if isinstance(c.get('content'), dict) else c.get('message'),
                  'subs': []}
            if c.get('rcount', 0) > 0:
                for sc in fetch_subs(aid, c['rpid'], bvid):
                    cm['subs'].append({'uname': sc.get('member', {}).get('uname'),
                                       'like': sc.get('like'),
                                       'message': sc.get('content', {}).get('message') if isinstance(sc.get('content'), dict) else sc.get('message')})
            new_comments.append(cm)
        rec['comments'] = new_comments
        rec['count'] = total if total else len(new_comments)
        with open(os.path.join(BASE, '视频评论_逐条.json'), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        print(f"  已更新: {len(new_comments)} 条")
    except Exception as e:
        print(f'  ERR: {e}')
    time.sleep(1.0)

print('\n=== 全部评论重抓完成 ===')
