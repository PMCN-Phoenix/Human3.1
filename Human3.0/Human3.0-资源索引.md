# Human 3.0 · 完整产物索引

> 整理日期：2026-10-11 ｜ 位置：`D:\11.project\iwen-dsh\doubao-list\allTest\Human3.0\`

## 一、文件夹结构

```
Human3.0\
├── Human3.0-四象限诊断与90天指南.md   ★ 本次核心交付（诊断+执行计划）
├── Human3.0-B站调研报告.md           视频内容调研（BV11FWDzZEmN）
├── Human3.0-MetaType-prompt.md       官方自测Prompt全文（可直接复制使用）
├── Human3.0-知识库-全文.md            官方知识库全文（RAG/对话语料）
├── Human3.0-知识库-原文.html          官方知识库页面存档（离线查看）
├── Human3.0-资源索引.md              本索引
└── 原始数据\
    ├── video_info.json               视频元信息（aid/cid）
    ├── comments_full.json            评论全量（13条含楼中楼）
    ├── fetch_human3.py / asr_whisper.py  复现脚本
    ├── fetch_log.txt / asr_out.txt / fetch_out.txt  执行日志
    └── 字幕\
        ├── BV11FWDzZEmN_asr.json     408段ASR转写（99.95%覆盖）
        └── BV11FWDzZEmN_纯文本.txt   按90秒分块的纯文本
```

## 二、各文件用途

| 文件 | 用途 |
| --- | --- |
| **四象限诊断与90天指南** | 你的诊断结果：MetaType=竞技者，L1.5–2.0，核心问题、最大杠杆点、90天三阶段计划 |
| **MetaType-prompt** | 复制「从这里开始/到这里结束」之间内容进 Claude/ChatGPT，做自测访谈 |
| **知识库-全文** | 粘贴进 AI 对话或当 RAG 语料，持续提问 |
| **调研报告** | 视频内容拆解 + 反面意见 + 待拍板项（含时间戳可回看） |
| **原始数据** | 抓取留档，供增量更新与复查 |

## 三、官方源（可溯源）

| 材料 | 官方链接 |
| --- | --- |
| HUMAN 3.0 完整知识库 | thedankoe.com/letters/a-complete-knowledge-base-of-human-3-0/ |
| HUMAN 3.0 基础文章（Top 1% 地图） | thedankoe.com/letters/human-3-0-a-map-to-reach-the-top-1 |
| MetaType Prompt 原文页 | letters.thedankoe.com/p/prompt-human-30-self-discovery-and |
| 视频（B站中英字幕，35:25） | bilibili.com/video/BV11FWDzZEmN |

## 四、推荐使用顺序

1. **读诊断**：先看 `四象限诊断与90天指南.md`，这是为你定制的结论。
2. **自测**：把 `MetaType-prompt.md` 复制进 Claude，认真答20分钟，验证诊断。
3. **执行**：按90天指南第1–30天开始——睡眠节律 + 选定真实竞技场。
4. **学习**：需要深入理解模型时，用 `知识库-全文.md` 当语料持续提问。

## 五、注意

- 框架免费可自用；付费产品（Superhuman90 等）可选不必须。
- 警惕「工具迷恋」：收集/研究这套资源 ≠ 使用它。90天指南第1条禁令就是禁止新开调研项目。
- AI 在本模型属于「Glitch/漏洞」：使用要有基础、有边界，别把思考外包。
