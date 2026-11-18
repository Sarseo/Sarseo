// تقدير أثر كبح تنبيهات «لم تتضح» (near) بحسب ثقة النموذج lo — بلا حكم مشرف.
// حدّ: index.jsonl لا يحفظ درجات الحروف الخام، فهذا تقدير بالوكالة عبر lo،
// لا إعادة حساب دقيقة لعتبة CTC_THR. القياس الدقيق يحتاج إعادة تشغيل النموذج أو حكم المشرف.
import { readFileSync } from 'node:fs';

const path = process.argv[2] || '/learn/index.jsonl';
const L = readFileSync(path, 'utf8').trim().split('\n').map(x => JSON.parse(x));

const REAL = new Set(['miss', 'sub', 'vowel']);
const loNear = [], loReal = [], loClean = [];
let recNear = 0, recReal = 0, recClean = 0, totAlerts = 0, nearAlerts = 0;

for (const r of L) {
  const bad = r.bad || [];
  const hasReal = bad.some(b => REAL.has(b[1]));
  const hasNear = bad.some(b => b[1] === 'near');
  const lo = r.lo ?? 0;
  totAlerts += bad.length;
  nearAlerts += bad.filter(b => b[1] === 'near').length;
  if (hasReal) { recReal++; loReal.push(lo); }
  else if (hasNear) { recNear++; loNear.push(lo); }
  else { recClean++; loClean.push(lo); }
}

const pct = (a, b) => b ? Math.round(100 * a / b) + '%' : '-';
const q = (a, p) => { if (!a.length) return NaN; const s = [...a].sort((x, y) => x - y); return s[Math.min(s.length - 1, Math.floor(s.length * p))]; };
const f = n => Number.isFinite(n) ? n.toFixed(3) : '-';

console.log('=== سلوك النموذج على ' + L.length + ' تسجيلًا ===');
console.log('تنبيهات كليًا: ' + totAlerts + ' · منها near: ' + nearAlerts + ' (' + pct(nearAlerts, totAlerts) + ')');
console.log('تسجيلات: نظيفة ' + recClean + ' · near فقط ' + recNear + ' · فيها خطأ حقيقي ' + recReal);

console.log('\n=== توزيع ثقة lo (وسيط · أدنى 10% · أعلى 10%) ===');
console.log('near فقط      : ' + f(q(loNear, .5)) + ' · ' + f(q(loNear, .1)) + ' · ' + f(q(loNear, .9)));
console.log('خطأ حقيقي     : ' + f(q(loReal, .5)) + ' · ' + f(q(loReal, .1)) + ' · ' + f(q(loReal, .9)));
console.log('نظيفة         : ' + f(q(loClean, .5)) + ' · ' + f(q(loClean, .1)) + ' · ' + f(q(loClean, .9)));

// هل الكبح آمن؟ نقارن: عند كل عتبة، كم near نكبح، وكم خطأ حقيقي قد نكبح بالخطأ.
console.log('\n=== لو كبحنا كل تنبيه near ثقته lo ≥ العتبة ===');
console.log('العتبة   near مكبوح      خطأ حقيقي مكبوح (خطر)');
for (const t of [0.90, 0.92, 0.94, 0.96, 0.98]) {
  const nearSup = loNear.filter(x => x >= t).length;
  const realSup = loReal.filter(x => x >= t).length;  // أخطاء حقيقية ثقتها عالية = قد تُكبح بالخطأ
  console.log(' ' + t.toFixed(2) + '    ' +
    String(nearSup).padEnd(4) + '(' + pct(nearSup, recNear) + ' من near)   ' +
    String(realSup).padEnd(4) + '(' + pct(realSup, recReal) + ' من الأخطاء)');
}

console.log('\nالقراءة: عتبة جيدة = تكبح كثيرًا من near وقليلًا جدًا من الأخطاء الحقيقية.');
console.log('إن كانت الأخطاء الحقيقية ثقتها lo منخفضة (العمود الأوسط أعلاه)، فالكبح آمن.');
console.log('ملاحظة: هذا تقدير بالوكالة عبر lo، لا عبر CTC_THR مباشرة. للقياس الدقيق: حكم المشرف.');
