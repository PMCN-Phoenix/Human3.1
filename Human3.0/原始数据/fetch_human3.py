# -*- coding: utf-8 -*-
"""B站单视频调研:验证Cookie + 抓视频信息 + 抓评论 + 抓字幕 (BV11FWDzZEmN)"""
import requests, re, json, time, hashlib, urllib.parse, os, sys

PY = sys.executable
BVID = "BV11FWDzZEmN"
BASE = r"D:\11.project\iwen-codex\codex-list\Human3.0-B站原始数据"
COOKIE_PATH = r"D:\11.project\iwen-codex\bilibili-cookie.txt"

s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'})
cookie = open(COOKIE_PATH, encoding='utf-8-sig').read().strip()
s.headers['Cookie'] = cookie

log = []
def logp(msg):
    log.append(str(msg))
    print(msg, flush=True)

# ---- 1. 验证登录 ----
try:
    nav = s.get('https://api.bilibili.com/x/web-interface/nav', timeout=20).json()
    dd = nav.get('data') or {}
    logp(f"[nav] isLogin={dd.get('isLogin')} uname={dd.get('uname')} uid={dd.get('mid')}")
except Exception as e:
    logp(f"[nav] FAIL {e}")

# ---- 2. 视频网页 HTML 拿 aid/cid ----
r = s.get(f'https://www.bilibili.com/video/{BVID}/', timeout=25)
t = r.text
m = re.search(r'window\.__INITIAL_STATE__=(.*?);\(function', t, re.S) or re.search(r'window\.__INITIAL_STATE__=(.*?);\s*</script>', t, re.S)
d = json.loads(m.group(1))
v = d['videoData']
aid, cid = v['aid'], v['cid']
title = v['title']
owner = v['owner']['name']
duration = v['duration']
desc = (v.get('desc') or '')[:1200]
logp(f"[info] aid={aid} cid={cid} dur={duration}s title={title} owner={owner}")
info = {'bvid': BVID, 'aid': aid, 'cid': cid, 'title': title, 'owner': owner,
        'duration': duration, 'desc': desc, 'pubdate': v.get('pubdate')}
os.makedirs(BASE, exist_ok=True)
with open(os.path.join(BASE, 'video_info.json'), 'w', encoding='utf-8') as f:
    json.dump(info, f, ensure_ascii=False, indent=2)

# ---- 3. 抓评论 ----
comments = []
total = 0
try:
    for pn in range(1, 20):
        rr = s.get('https://api.bilibili.com/x/v2/reply',
                   params={'oid': aid, 'type': 1, 'pn': pn, 'ps': 20, 'sort': 2},
                   headers={'Referer': f'https://www.bilibili.com/video/{BVID}/'}, timeout=25).json()
        data = rr.get('data') or {}
        reps = data.get('replies') or []
        if not reps:
            break
        total = (data.get('page') or {}).get('count', 0)
        for c in reps:
            item = {'rpid': c['rpid'], 'uname': c['member']['uname'], 'like': c['like'],
                    'rcount': c.get('rcount', 0), 'message': c['content']['message']}
            if item['rcount'] > 0:
                subs = []
                try:
                    r2 = s.get('https://api.bilibili.com/x/v2/reply/reply',
                               params={'oid': aid, 'type': 1, 'root': c['rpid'], 'pn': 1, 'ps': 20},
                               headers={'Referer': f'https://www.bilibili.com/video/{BVID}/'}, timeout=25).json()
                    for sc in (r2.get('data') or {}).get('replies') or []:
                        subs.append({'uname': sc['member']['uname'], 'like': sc['like'],
                                     'message': sc['content']['message']})
                except Exception as e:
                    logp(f"[sub] rpid={c['rpid']} FAIL {e}")
                time.sleep(0.8)
                item['subs'] = subs
            comments.append(item)
        logp(f"[comments] page={pn} got={len(reps)} total={total}")
        if len(comments) >= total and total > 0:
            break
        time.sleep(1.2)
except Exception as e:
    logp(f"[comments] FAIL {e}")

with open(os.path.join(BASE, 'comments_full.json'), 'w', encoding='utf-8') as f:
    json.dump({BVID: {'title': title, 'aid': aid, 'owner': owner, 'count': total,
                      'comments': comments}}, f, ensure_ascii=False, indent=2)
logp(f"[comments] DONE total={total} saved={len(comments)}")

# ---- 4. 抓字幕 (wbi 签名) ----
try:
    nav2 = s.get('https://api.bilibili.com/x/web-interface/nav', timeout=20).json()
    wbi = nav2['data']['wbi_img']
    img = wbi['img_url'].rsplit('/', 1)[-1].split('.')[0]
    sub = wbi['sub_url'].rsplit('/', 1)[-1].split('.')[0]
    MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,57,62,11,36,20,34,44,52]
    mixin = ''.join((img+sub)[i] for i in MIXIN)[:32]
    p = {'bvid': BVID, 'cid': str(cid), 'wts': str(int(time.time()))}
    q = urllib.parse.urlencode(sorted(p.items()))
    p['w_rid'] = hashlib.md5((q+mixin).encode()).hexdigest()
    rr = s.get('https://api.bilibili.com/x/player/wbi/v2', params=p,
               headers={'Referer': f'https://www.bilibili.com/video/{BVID}/'}, timeout=20).json()
    subs = ((rr.get('data') or {}).get('subtitle') or {}).get('subtitles') or []
    logp(f"[subtitle] available: {[x.get('lan') for x in subs]}")
    pick = None
    for pref in ['zh-Hans', 'zh-CN', 'zh', 'ai-zh']:
        pick = next((x for x in subs if x.get('lan') == pref), None)
        if pick: break
    if pick:
        u = pick['subtitle_url']
        if u.startswith('//'): u = 'https:' + u
        body = s.get(u, headers={'Referer': f'https://www.bilibili.com/video/{BVID}/'}, timeout=25).json()['body']
        os.makedirs(os.path.join(BASE, '字幕'), exist_ok=True)
        with open(os.path.join(BASE, '字幕', BVID + '.json'), 'w', encoding='utf-8') as f:
            json.dump(body, f, ensure_ascii=False, indent=2)
        cover = body[-1]['to'] / duration if body and duration else 0
        logp(f"[subtitle] SAVED segments={len(body)} last_to={body[-1]['to'] if body else 0} cover={cover:.2%}")
    else:
        logp("[subtitle] NO AI subtitle (need ASR fallback)")
except Exception as e:
    logp(f"[subtitle] FAIL {e}")

logp("[ALL DONE]")
with open(os.path.join(BASE, 'fetch_log.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(log))
