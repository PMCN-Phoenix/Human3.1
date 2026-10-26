# -*- coding: utf-8 -*-
"""软件设计师(软考中级) B站调研 · 阶段1：多方向关键词搜索 + 打分筛选"""
import requests, re, json, time, hashlib, urllib.parse, os

MIXIN = [46,47,18,2,53,8,23,32,15,50,10,31,58,3,45,35,27,43,5,49,33,9,42,19,29,28,14,39,
         12,38,41,13,37,48,7,16,24,55,40,61,26,17,0,1,60,51,30,4,22,25,54,21,56,59,6,63,
         57,62,11,36,20,34,44,52]

s = requests.Session()
s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                  'Referer': 'https://www.bilibili.com/'})

# Cookie 池（用 account1 散祁晔，通过 cookie_manager 取）
import sys
sys.path.insert(0, r"D:\11.project\iwen-codex\bilibili-cookies")
from cookie_manager import BiliCookiePool
pool = BiliCookiePool()
cookie = pool.get_cookie()
s.headers['Cookie'] = cookie

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

# 关键词：按主题方向分组（非堆近义词）
GROUPS = {
    '备考策略': ['软考 软件设计师 备考', '软考 软件设计师 冲刺', '软考 中级 软件设计师 经验', '软件设计师 一次过', '软考 软件设计师 复习'],
    '科目核心': ['软件设计师 数据流图', '软件设计师 UML', '软件设计师 数据库设计', '软件设计师 设计模式', '软考 软件设计师 算法'],
    '真题刷题': ['软件设计师 真题', '软考 软件设计师 历年真题', '软件设计师 题库', '软考 刷题 软件设计师'],
    '高频考点': ['软件设计师 高频考点', '软考 软件设计师 机考', '软件设计师 知识点', '软考 软件设计师 常考'],
}

def dur2sec(d):
    try:
        parts = [int(x) for x in str(d).split(':')]
        return sum(x * 60 ** (len(parts) - 1 - i) for i, x in enumerate(parts))
    except Exception:
        return 0

seen = {}
for gname, kws in GROUPS.items():
    for kw in kws:
        try:
            p = sign({'search_type': 'video', 'keyword': kw, 'page': 1, 'page_size': 30})
            r = s.get('https://api.bilibili.com/x/web-interface/wbi/search/type', params=p, timeout=25)
            res = r.json().get('data', {}).get('result') or []
            for v in res:
                bvid = v.get('bvid')
                if not bvid: continue
                title = re.sub(r'<[^>]+>', '', v.get('title', '') or '')
                desc = (v.get('description') or '')[:200]
                seen.setdefault(bvid, {
                    'bvid': bvid, 'title': title, 'author': v.get('author'),
                    'play': v.get('play') or 0, 'dur': dur2sec(v.get('duration')),
                    'pubdate': v.get('pubdate'), 'desc': desc,
                    'groups': set(), 'kws': set()})
                seen[bvid]['groups'].add(gname)
                seen[bvid]['kws'].add(kw)
            print(f'[{gname}] {kw}: {len(res)} 条')
        except Exception as e:
            print(f'[{gname}] {kw}: ERR {e}')
        time.sleep(1.2)

# 打分
def score(v):
    t = (v['title'] + ' ' + v['desc']).lower()
    s = 0.0
    weights = [('软件设计师', 12), ('软考', 8), ('中级', 4),
               ('备考', 6), ('冲刺', 6), ('一次过', 5), ('经验', 4), ('复习', 3),
               ('真题', 6), ('题库', 4), ('刷题', 4), ('历年', 3),
               ('数据流图', 7), ('uml', 7), ('数据库', 5), ('设计模式', 6), ('算法', 4),
               ('高频考点', 5), ('考点', 3), ('机考', 3), ('知识点', 3),
               ('数据流', 6), ('e-r', 4), ('er图', 4), ('面向对象', 4), ('案例', 3)]
    for k, w in weights:
        if k in t: s += w
    # 反向下调：无关考试方向
    for k in ['高考', '考研数学', '教师资格', '驾驶', '健身', '考研英语']:
        if k in t: s -= 6
    p = v['play'] or 0
    s += 3 if p > 300000 else 2 if p > 100000 else 1 if p > 30000 else -1
    if v['dur'] < 120: s -= 2
    if v['dur'] > 3600: s -= 1
    return s

for v in seen.values():
    v['score'] = score(v)
    v['groups'] = sorted(v['groups'])

ranked = sorted(seen.values(), key=lambda x: -x['score'])
print(f'\n=== 去重后共 {len(ranked)} 个视频 ===')
for i, v in enumerate(ranked[:40], 1):
    print(f"{i:2d} {v['score']:5.1f} | {v['play']:>8} | {v['dur']:>5}s | {v['title'][:42]} | {v['author']} | {v['groups']}")

outdir = r"D:\11.project\iwen-dsh\doubao-list\allTest\软考冲刺-B站调研\软考冲刺-B站原始数据"
os.makedirs(outdir, exist_ok=True)
with open(os.path.join(outdir, '搜索清单_全部去重.json'), 'w', encoding='utf-8') as f:
    json.dump([{**v, 'groups': list(v['groups']), 'kws': list(v['kws'])} for v in ranked], f, ensure_ascii=False, indent=1)
with open(os.path.join(outdir, '搜索清单_top40.json'), 'w', encoding='utf-8') as f:
    json.dump([{**v, 'groups': list(v['groups'])} for v in ranked[:40]], f, ensure_ascii=False, indent=1)
print('\nSAVED to', outdir)
