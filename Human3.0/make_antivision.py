# -*- coding: utf-8 -*-
"""反愿景警示页 PDF 生成 — A4 竖版，可打印贴墙（压缩版，确保一页放下）"""
from fpdf import FPDF

pdf = FPDF(orientation='P', unit='mm', format='A4')
pdf.set_auto_page_break(auto=False)
pdf.add_page()

pdf.add_font('yahei', '', r'C:\Windows\Fonts\msyh.ttc')
pdf.add_font('yahei', 'B', r'C:\Windows\Fonts\msyhbd.ttc')
pdf.add_font('hei', '', r'C:\Windows\Fonts\simhei.ttf')

W = 210
M = 16
cw = W - M * 2

def banner(text, fill):
    pdf.set_fill_color(*fill)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('hei', '', 13.5)
    y0 = pdf.get_y()
    pdf.rect(M, y0, cw, 8, 'F')
    pdf.set_xy(M + 4, y0 + 0.6)
    pdf.cell(cw - 8, 6.5, text)
    pdf.set_y(y0 + 8.4)

def body(text, size=11.5, key=False):
    pdf.set_font('yahei', 'B' if key else '', size)
    pdf.set_text_color((20, 20, 20) if key else (70, 70, 70))
    pdf.set_x(M + 6)
    pdf.multi_cell(cw - 6, size * 0.55, text)
    pdf.ln(0.6)

def sep():
    pdf.set_draw_color(205, 205, 205)
    pdf.line(M, pdf.get_y(), W - M, pdf.get_y())
    pdf.ln(2.2)

# ===== 顶部标题区 =====
pdf.set_fill_color(15, 15, 15)
pdf.rect(0, 0, W, 36, 'F')
pdf.set_xy(0, 6)
pdf.set_font('hei', '', 11)
pdf.set_text_color(255, 200, 90)
pdf.cell(W, 5, 'ANTI-VISION · 反愿景', align='C')
pdf.set_xy(0, 12.5)
pdf.set_font('hei', '', 23)
pdf.set_text_color(255, 255, 255)
pdf.cell(W, 9, '三年后，我拒绝成为这种人', align='C')
pdf.set_xy(0, 22.5)
pdf.set_font('yahei', '', 10)
pdf.set_text_color(200, 200, 200)
pdf.cell(W, 5, '—— 每天看一次。这不是预言，是警告 ——', align='C')
pdf.set_y(41)

quadrants = [
    ('① 身份 · 我是什么人', (200, 40, 40), [
        ('一个小公司的小职员', True),
        ('没有钱。存款经不起任何一场意外。', False),
        ('家里出任何事——生病、急用钱、需要帮忙——我都拿不出手，只能干着急。', False),
        ('家人需要我的时候，我帮不上。', True),
        ('和别人无法进行日常的、正向的交往——开口就冷场，关系都停留在表面。', False),
        ('没有一份工作让我觉得"这就是我"。', False),
        ('没有值得我献身的人，也没有值得我献身的事业。', True),
    ]),
    ('② 日常 · 我每天在做什么', (220, 120, 40), [
        ('做自己不喜欢的事情。', True),
        ('做着机械的、人人可替代的工作——换掉我，对世界没有任何影响。', False),
        ('上班等下班，下班刷手机，一天又一天。', False),
        ('没有任何一件事是"非我不可"的。', True),
        ('学过的技术全部生锈，AI 时代里被工具替代。', False),
    ]),
    ('③ 身体 · 我的状态', (60, 130, 220), [
        ('满身肥肉，或者虚弱异常——两者都是。', True),
        ('走两步就喘，体检报告一年比一年长。', False),
        ('浑身不健康，不好看。', True),
        ('镜子里的自己，我不想多看一眼。', False),
        ('曾经能打的、健康的身体，被我亲手还了回去。', False),
    ]),
    ('④ 关系 · 我和谁在一起', (150, 80, 200), [
        ('自己独身，没有任何人陪着。', True),
        ('晚上回到空房间，没人可以说话。', False),
        ('曾经有机会靠近的人，因为我的退缩和沉默，都走远了。', False),
        ('连"值得献身的人"都没有出现，因为我从没认真走向过谁。', False),
        ('孤独不是突然来的，是每天一点点攒出来的。', True),
    ]),
]

for title, fill, lines in quadrants:
    banner(title, fill)
    for text, is_key in lines:
        body(text, key=is_key)
    sep()

# ===== 底部 =====
pdf.set_font('hei', '', 13.5)
pdf.set_text_color(200, 40, 40)
pdf.multi_cell(cw, 6.2, '我现在的每一个"明天再说"，都在把这张纸变成现实。', align='C')
pdf.ln(0.8)
pdf.set_font('yahei', 'B', 11.5)
pdf.set_text_color(70, 70, 70)
pdf.multi_cell(cw, 5.8, '反面的路只有一条：今天去做一件不可替代的事。', align='C')
pdf.ln(0.8)
pdf.set_font('yahei', '', 9.5)
pdf.set_text_color(150, 150, 150)
pdf.multi_cell(cw, 5, 'Human 3.0 诊断 · 2026-10-11 · 打印贴于书桌前', align='C')

out = r"D:\11.project\iwen-dsh\doubao-list\allTest\Human3.0\反愿景-警示页.pdf"
pdf.output(out)
print("SAVED", out, "final y:", pdf.get_y())
