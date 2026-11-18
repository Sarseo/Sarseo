# -*- coding: utf-8 -*-
# قياس حقيقي لأثر عتبة CTC_THR على نموذج التسميع، معزول عن الخدمة العاملة.
# يشغّل نموذجكم (Reviewer من ctc.py) على عيّنة من التسجيلات المحفوظة، بقيم عتبة مختلفة،
# ويعدّ near / miss / sub / vowel عند كل قيمة. لا يمسّ قاعدة البيانات ولا الخادم (port 8001).
#
# التشغيل داخل حاوية ctc (فيها torch و soundfile والنموذج):
#   docker exec -i darajat-ctc-1 python /tmp/thr-measure.py 150
#   (الوسيط = عدد التسجيلات من العيّنة؛ احذفه لكل التسجيلات)
import os, sys, json, time

# استورد وحدة النموذج دون تشغيل خادمها (محميّ بـ __main__)
sys.argv = [sys.argv[0]]            # لئلا يلتبس argparse داخل الوحدة إن وُجد
import importlib.util
CTC = "/app/ctc.py"
spec = importlib.util.spec_from_file_location("ctcmod", CTC)
ctc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ctc)

import soundfile as sf
import numpy as np

SR = getattr(ctc, "SR", 16000)
LEARN = os.path.join(getattr(ctc, "DATA", "/data"), "learn")
if not os.path.isdir(LEARN):
    LEARN = "/learn"                # احتياط: مجلد الأحكام في حاوية التطبيق
IDX = os.path.join(LEARN, "index.jsonl")

N = int(sys.argv[1]) if len(sys.argv) > 1 else 0
THRS = [-1.6, -1.8, -2.0, -2.2, -2.4]   # العتبة الحالية -1.8 في الوسط

print("تحميل النموذج…", flush=True)
RV = ctc.Reviewer()
RV.run(np.zeros(SR, np.float32), ["بِسْمِ"])   # إحماء
print("جاهز. المجلد:", LEARN, flush=True)

rows = [json.loads(l) for l in open(IDX, encoding="utf8") if l.strip()]
if N:
    rows = rows[:N]
print("عدد التسجيلات في العيّنة:", len(rows), flush=True)

def load(fname):
    p = os.path.join(LEARN, fname)
    if not os.path.isfile(p):
        return None
    x, sr = sf.read(p, dtype="float32")
    if x.ndim > 1:
        x = x.mean(axis=1)
    return x

# حمّل كل الصوت مرة واحدة، ثم كرّر على العتبات
clips = []
skipped = 0
for r in rows:
    w = r.get("w") or []
    x = load(r.get("f", ""))
    if x is None or len(x) < SR // 2 or not w:
        skipped += 1
        continue
    clips.append((x, w))
print("صالحة:", len(clips), "· متجاهَلة:", skipped, flush=True)

THR0 = ctc.THR
results = {}
for thr in THRS:
    ctc.THR = thr
    c = {"near": 0, "miss": 0, "sub": 0, "vowel": 0, "clips_with_near": 0, "clips_clean": 0}
    t0 = time.time()
    for x, w in clips:
        try:
            bad, vow, near = RV.run_all(x, w, None, "", "test")
        except Exception as e:
            continue
        nmiss = sum(1 for b in bad if b[1] == "miss")
        nsub = sum(1 for b in bad if b[1] == "sub")
        c["miss"] += nmiss; c["sub"] += nsub
        c["vowel"] += len(vow); c["near"] += len(near)
        if near: c["clips_with_near"] += 1
        if not (bad or vow or near): c["clips_clean"] += 1
    c["sec"] = round(time.time() - t0, 1)
    results[thr] = c
    print("  عتبة %.1f ← %s (%.1fs)" % (thr, json.dumps(c, ensure_ascii=False), c["sec"]), flush=True)
ctc.THR = THR0

print("\n=== النتيجة: عدد التنبيهات على %d تسجيلًا عند كل عتبة ===" % len(clips))
print("العتبة   near   miss   sub   vowel   نظيفة")
for thr in THRS:
    c = results[thr]
    mark = "  ← الحالية" if abs(thr - THR0) < 1e-6 else ""
    print(" %5.1f   %4d   %4d   %4d   %4d   %4d%s" %
          (thr, c["near"], c["miss"], c["sub"], c["vowel"], c["clips_clean"], mark))
print("\nالقراءة: كلما خفّضنا العتبة (أكثر سالبية) تسامح النموذج أكثر، فيقلّ near والأخطاء.")
print("الأفضل: أقل near ممكن مع بقاء miss/sub قريبًا من قيمتها الحالية (لا نريد إخفاء الأخطاء).")
print("القرار النهائي لأي عتبة يحتاج حكم المشرف على عيّنة، لكن هذا يبيّن الاتجاه بالأرقام الحقيقية.")
