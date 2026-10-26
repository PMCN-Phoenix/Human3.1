# -*- coding: utf-8 -*-
"""faster-whisper 英文转写 BV11FWDzZEmN 音轨"""
from faster_whisper import WhisperModel
import json, time

WAV = r"D:\11.project\iwen-codex\codex-list\Human3.0-B站原始数据\audio16k.wav"
OUT = r"D:\11.project\iwen-codex\codex-list\Human3.0-B站原始数据\字幕\BV11FWDzZEmN_asr.json"

t0 = time.time()
model = WhisperModel("small", device="cuda", compute_type="float16")
segments, info = model.transcribe(WAV, beam_size=5, vad_filter=True)
print(f"language={info.language} prob={info.language_probability:.2f}", flush=True)
rows = []
for seg in segments:
    rows.append({"from": round(seg.start, 2), "to": round(seg.end, 2), "content": seg.text.strip()})
    if len(rows) % 50 == 0:
        print(f"...{len(rows)} segs {seg.end:.0f}s", flush=True)
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)
print(f"DONE segs={len(rows)} last_to={rows[-1]['to']} time={time.time()-t0:.0f}s", flush=True)
