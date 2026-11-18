/* ===== درجات: اختيار الرواية والقارئ — النسخة الجديدة (قائمتان تُمرَّران) =====
   يحلّ محلّ الدالة rwPick في وحدة «مصحف القراءات» داخل ملف nd (في nd69: من السطر الذي يبدأ بـ
   `function rwPick(){` إلى السطر الذي ينتهي بـ `qSheet("اختر الرواية والقارئ",...paint(box)})}`).
   يُلصق في المكان نفسه داخل الوحدة، لأنه يستعمل ما فيها: QURRA وC وrwRawis وcurRec وrwSet وH وON وRW وNAME وrwEsc وrwNum.
   الحفظ وتغيير الرواية كما في النسخة السابقة تمامًا (زر «ابدأ التلاوة» = زر rwb-go القديم).
   الأصناف كلها تبدأ بـ rwc- حتى لا تتعارض مع rp- الموجودة في التطبيق. */

/* الراوي وصاحب القراءة: [الاسم، البلد، الوفاة بالهجري] — تُراجَع قبل النشر */
const RWC_RAWI={hafs:["حفص بن سليمان الأسدي","الكوفة",180],shouba:["شعبة بن عيّاش، أبو بكر","الكوفة",193],
 qaloon:["عيسى بن مينا","المدينة",220],warsh:["عثمان بن سعيد المصري","مصر",197],
 bazzi:["أحمد بن محمد البزّي","مكة",250],qumbul:["محمد بن عبد الرحمن المخزومي","مكة",291],
 doori:["حفص بن عمر الدوري","بغداد",246],soosi:["صالح بن زياد السوسي","الرقّة",261],
 hisham:["هشام بن عمّار","دمشق",245],ibndhakwan:["عبد الله بن أحمد بن ذكوان","دمشق",242],
 khalaf:["خلف بن هشام البزّار","بغداد",229],khallad:["خلّاد بن خالد الصيرفي","الكوفة",220],
 abulharith:["الليث بن خالد البغدادي","بغداد",240],doorikisai:["حفص بن عمر الدوري","بغداد",246],
 ibnwardan:["عيسى بن وردان","المدينة",160],ibnjammaz:["سليمان بن مسلم بن جمّاز","المدينة",170],
 ruways:["محمد بن المتوكّل اللؤلؤي","البصرة",238],rawh:["روح بن عبد المؤمن","البصرة",234],
 ishaq:["إسحاق بن إبراهيم الورّاق","بغداد",286],idris:["إدريس بن عبد الكريم الحدّاد","بغداد",292]};
const RWC_IMAM={"نافع المدني":["نافع بن عبد الرحمن بن أبي نعيم","المدينة",169],"ابن كثير المكي":["عبد الله بن كثير الداري","مكة",120],
 "أبو عمرو البصري":["أبو عمرو زبّان بن العلاء","البصرة",154],"ابن عامر الشامي":["عبد الله بن عامر اليحصبي","دمشق",118],
 "عاصم الكوفي":["عاصم بن أبي النجود الأسدي","الكوفة",127],"حمزة الكوفي":["حمزة بن حبيب الزيّات","الكوفة",156],
 "الكسائي الكوفي":["علي بن حمزة الكسائي","الكوفة",189],"أبو جعفر المدني":["يزيد بن القعقاع","المدينة",130],
 "يعقوب الحضرمي":["يعقوب بن إسحاق الحضرمي","البصرة",205],"خلف العاشر":["خلف بن هشام البزّار","بغداد",229]};

function rwPick(){
 /* المجموعات: لكل إمام رواياه معًا، وعاصم أولًا وحفص أول رواته */
 const G0=QURRA.map(([q,L])=>({q,R:rwRawis(L)})),isH=r=>r.paths.some(p=>p.rw==="hafs");
 const ai=G0.findIndex(g=>g.R.some(isH)),G=ai>0?[G0[ai]].concat(G0.slice(0,ai),G0.slice(ai+1)):G0;
 G.forEach(g=>{const h=g.R.findIndex(isH);if(h>0)g.R.unshift(g.R.splice(h,1)[0])});
 let sel=null;
 G.forEach((g,i)=>g.R.forEach((r,j)=>r.paths.forEach((p,m)=>{if(sel||p.rw!==RW)return;const c=curRec(p.rw);if(p.recs.some(x=>x.k===c))sel={i,j,m,k:c}})));
 if(!sel)G.forEach((g,i)=>g.R.forEach((r,j)=>r.paths.forEach((p,m)=>{if(!sel&&p.rw===RW)sel={i,j,m,k:(p.recs[0]||{}).k}})));
 if(!sel)sel={i:0,j:0,m:0,k:null};
 let qq="",info="";
 const P=()=>G[sel.i].R[sel.j].paths[sel.m],RW0=()=>G[sel.i].R[sel.j];
 const HF=()=>ON==="hafs"||!H.ok?RECF:H.F,HD=()=>ON==="hafs"||!H.ok?RECD:H.D;
 const full=(rw,k)=>rw==="hafs"?(HF()[k]||""):(((C.rec[rw]||[]).find(x=>x.k===k)||{}).f||"");
 const desc=(rw,k)=>rw==="hafs"?(HD()[k]||""):"";
 const RN=()=>{const q=P().recs.find(x=>x.k===sel.k);return q?q.s:""};
 const ini=s=>(String(s||"").replace(/^(ال|أبو |ابن |عبد )/,"").charAt(0));
 /* «عن عاصم»، «عن أبي عمرو»، «عن ابن كثير»، «عن خلف العاشر» */
 const imamShort=q=>{const w=q.split(" ");return w[0]==="أبو"?"أبي "+w[1]:w[0]==="ابن"?w[0]+" "+w[1]:q==="خلف العاشر"?q:w[0]};
 const lab=(g,r,p)=>r.n+" عن "+imamShort(g.q)+(r.paths.length>1?" · "+p.p:"");
 const tot=r=>r.paths.reduce((a,x)=>a+x.recs.length,0);
 const ar=n=>Number(n).toLocaleString("ar-EG",{useGrouping:false});
 const I={info:`<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 11v6M12 7.5v.5"/></svg>`,
  find:`<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>`,
  x:`<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18"/></svg>`,
  go:`<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 6l-6 6 6 6"/></svg>`};

 const infoHtml=()=>{if(!info)return"";const g=G[sel.i],r=RW0(),p=P();let h="",oth="",ot="",kick,title;
  const fact=(k,v)=>`<div class="rwc-f"><span>${k}</span><b>${rwEsc(v)}</b></div>`;
  const card=(t,n,f)=>`<div class="rwc-card"><small>${t}</small><b>${rwEsc(n)}</b>${f}</div>`;
  if(info==="rw"){const R=RWC_RAWI[r.paths[0].rw],M=RWC_IMAM[g.q];kick="عن الرواية";title="رواية "+r.n+" عن "+imamShort(g.q);
   if(R)h+=card("الراوي",R[0],fact("الوفاة",ar(R[2])+" هـ")+fact("البلد",R[1]));
   if(M)h+=card("صاحب القراءة (الإمام)",M[0],fact("الوفاة",ar(M[2])+" هـ")+fact("البلد",M[1]));
   h+=card("الطريق",p.p,fact("القرّاء في التطبيق",p.recs.length?rwNum(p.recs.length):"التلاوة قريبًا"));
   ot="الرواية الأخرى عن "+imamShort(g.q);
   g.R.forEach((x,j)=>{if(j!==sel.j)oth+=`<button type="button" class="rwc-chip" data-ij="${sel.i}.${j}">رواية ${rwEsc(x.n)}</button>`})}
  else{const k=sel.k,f=full(p.rw,k)||RN(),d=desc(p.rw,k);kick="عن القارئ";title=f;
   h+=card("القارئ",f,d?fact("التلاوة",d):"");
   ot="روايات أخرى بصوته في التطبيق";const F=f.trim();
   G.forEach((gg,i)=>gg.R.forEach((rr,j)=>rr.paths.forEach((pp,m)=>pp.recs.forEach(x=>{
    if(F&&full(pp.rw,x.k).trim()===F){const on=i===sel.i&&j===sel.j&&m===sel.m;
     oth+=`<button type="button" class="rwc-chip${on?" on":""}" aria-pressed="${on}" data-s="${i}.${j}.${m}" data-k="${rwEsc(x.k)}">${rwEsc(lab(gg,rr,pp))}</button>`}}))))}
  return `<div class="rwc-info"><button type="button" class="rwc-bd" data-a="noinfo" aria-label="إغلاق المعلومات"></button><div class="rwc-is" role="dialog" aria-label="${rwEsc(title)}">
   <div class="rwc-ih"><div><small>${kick}</small><h3>${rwEsc(title)}</h3></div><button type="button" class="rwc-ib" data-a="noinfo" aria-label="إغلاق">${I.x}</button></div>
   ${h}${oth?`<div><small class="rwc-ot">${rwEsc(ot)}</small><div class="rwc-chips">${oth}</div></div>`:""}</div></div>`};

 const paint=box=>{const g=G[sel.i],r=RW0(),p=P(),f=qq.trim();let h=`<label class="rwc-sr" for="rwc-q">ابحث عن قارئ أو رواية</label>
  <div class="rwc-search">${I.find}<input id="rwc-q" type="search" placeholder="ابحث: الحصري، ورش، قالون…" value="${rwEsc(qq)}" autocomplete="off">${f?`<button type="button" class="rwc-clr" data-a="clear" aria-label="مسح البحث">${I.x}</button>`:""}</div>`;
  if(!f){h+=`<div class="rwc-body"><div class="rwc-col rw"><h4>الرواية</h4><div class="rwc-scroll rw">${G.map((gg,i)=>
    `<div class="rwc-g${i===sel.i?" cur":""}" role="group" aria-label="عن ${rwEsc(imamShort(gg.q))}"><small>عن ${rwEsc(imamShort(gg.q))}</small>${gg.R.map((rr,j)=>{const on=i===sel.i&&j===sel.j,t=tot(rr);
     return `<button type="button" class="rwc-r${on?" on":""}" aria-pressed="${on}" data-ij="${i}.${j}"><b>${rwEsc(rr.n)}</b><small>${t?rwNum(t):"التلاوة قريبًا"}</small></button>`}).join("")}</div>`).join("")}</div></div>
   <div class="rwc-sep" aria-hidden="true"></div><div class="rwc-col q"><div class="rwc-qh"><h4>القارئ</h4><small>${p.recs.length?rwNum(p.recs.length):""}</small></div>
   ${r.paths.length>1?`<div class="rwc-seg" role="group" aria-label="الطريق">${r.paths.map((x,m)=>`<button type="button" class="${m===sel.m?"on":""}" aria-pressed="${m===sel.m}" data-m="${m}">${rwEsc(x.p)}</button>`).join("")}</div>`:""}
   <div class="rwc-scroll">${p.recs.length?p.recs.map(x=>{const on=x.k===sel.k;
    return `<button type="button" class="rwc-q${on?" on":""}" aria-pressed="${on}" data-k="${rwEsc(x.k)}"><span class="rwc-dot" aria-hidden="true">${rwEsc(ini(x.s))}</span><span class="rwc-n">${rwEsc(x.s)}</span></button>`}).join("")
    :`<p class="rwc-none">التلاوة قريبًا، والمصحف جاهز</p>`}</div></div></div>`}
  else{const hits=[];G.forEach((gg,i)=>gg.R.forEach((rr,j)=>rr.paths.forEach((pp,m)=>{const hr=(rr.n+" "+gg.q+" "+pp.p).includes(f);
    pp.recs.forEach(x=>{if(hr||x.s.includes(f)||full(pp.rw,x.k).includes(f))hits.push({gg,rr,pp,i,j,m,x})})})));
   h+=`<div class="rwc-hits"><div class="rwc-qh"><h4>نتائج البحث</h4><small>${ar(hits.length)} نتيجة</small></div><div class="rwc-scroll">${hits.length?hits.map(o=>{
    const on=o.i===sel.i&&o.j===sel.j&&o.m===sel.m&&o.x.k===sel.k;
    return `<button type="button" class="rwc-hit${on?" on":""}" aria-pressed="${on}" data-s="${o.i}.${o.j}.${o.m}" data-k="${rwEsc(o.x.k)}"><span class="rwc-dot" aria-hidden="true">${rwEsc(ini(o.x.s))}</span><span><b>${rwEsc(full(o.pp.rw,o.x.k)||o.x.s)}</b><small>رواية ${rwEsc(lab(o.gg,o.rr,o.pp))}</small></span></button>`}).join("")
    :`<p class="rwc-none">لا نتائج. جرّب اسمًا آخر أو اسم الرواية.</p>`}</div></div>`}
  h+=`<div class="rwc-foot"><div class="rwc-infos"><button type="button" data-a="irw">${I.info}<span>عن رواية ${rwEsc(r.n)}</span></button>${RN()?`<button type="button" data-a="iq">${I.info}<span>عن القارئ ${rwEsc(RN())}</span></button>`:""}</div>
   <button type="button" class="rwc-go"><span><b>${RN()?"ابدأ التلاوة":"اعرض المصحف بهذه الرواية"}</b><small>${rwEsc((RN()?RN()+" · ":"")+"رواية "+lab(g,r,p))}</small></span>${I.go}</button></div>${infoHtml()}`;
  const hadQ=document.activeElement&&document.activeElement.id==="rwc-q";
  box.innerHTML=h;
  if(hadQ){const i=box.querySelector("#rwc-q");i.focus();try{i.setSelectionRange(i.value.length,i.value.length)}catch(e){}}
  const c=box.querySelector(".rwc-r.on");if(c&&!box._scrolled){box._scrolled=1;try{c.scrollIntoView({block:"nearest"})}catch(e){}}};

 const pickPath=(i,j,m,k)=>{const x=G[i].R[j].paths[m],c=curRec(x.rw);sel={i,j,m,k:k||(x.recs.some(r=>r.k===c)?c:(x.recs[0]||{}).k)}};
 const go=box=>{const x=P(),k=sel.k;try{qStop(true)}catch(e){}   /* حفظ القارئ وتغيير الرواية: كما في النسخة السابقة */
  if(k){if(x.rw==="hafs"){if(ON==="hafs"){QRK_MEM=k;try{localStorage.setItem("nd.qrk",k)}catch(e){}}else{if(H.ok){H.mem=k;H.qrk=k}try{localStorage.setItem("nd.qrk.hafs",k)}catch(e){}}}
   else{try{localStorage.setItem("nd.qrk."+x.rw,k)}catch(e){}if(ON===x.rw)QRK_MEM=k}}
  box._close&&box._close();if(x.rw!==RW)rwSet(x.rw);else render()};

 qSheet("اختر الرواية والقارئ",`<div class="rwc"></div>`,(v,close)=>{const box=v.querySelector(".rwc");box._close=close;
  box.addEventListener("click",e=>{const b=e.target.closest("button");if(!b||!box.contains(b))return;const d=b.dataset;
   if(b.classList.contains("rwc-go"))return go(box);
   if(d.a==="clear")qq="";else if(d.a==="irw")info="rw";else if(d.a==="iq")info="q";else if(d.a==="noinfo")info="";
   else if(d.ij){const[i,j]=d.ij.split(".").map(Number);pickPath(i,j,0);if(info==="rw")info="rw"}
   else if(d.m!=null&&!d.s)pickPath(sel.i,sel.j,+d.m);
   else if(d.s){const[i,j,m]=d.s.split(".").map(Number);pickPath(i,j,m,d.k);qq="";if(info==="q")info=""}
   else if(d.k)sel.k=d.k;
   paint(box)});
  box.addEventListener("input",e=>{if(e.target.id==="rwc-q"){qq=e.target.value;paint(box)}});
  box.addEventListener("keydown",e=>{if(e.key==="Escape"&&info){e.stopPropagation();info="";paint(box)}},true);
  paint(box)})}
window.rwPick=rwPick;

/* ---------- المظهر (يُضاف إلى نصّ الأنماط في الوحدة نفسها، أو في <style> مستقل) ---------- */
(()=>{const s=document.createElement("style");s.textContent=`
.rp-sheet:has(.rwc){overflow:hidden}
.rwc{--a:#5f6d22;position:relative;display:flex;flex-direction:column;gap:10px;height:min(74vh,660px);color:#2e2a1f}
.rwc svg{width:18px;height:18px;flex:none;fill:none;stroke:currentColor;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round}
.rwc-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.rwc-search{display:flex;align-items:center;gap:10px;height:48px;padding:0 14px;border-radius:16px;background:#fff;border:1px solid #e4dbc2;color:#6b6250}
.rwc-search input{flex:1;min-width:0;border:0;background:transparent;font:400 16px "Noto Naskh Arabic",serif;color:#2e2a1f;outline:none}
.rwc-clr{width:32px;height:32px;border-radius:16px;border:0;background:#efe6cd;color:#4a4434;display:flex;align-items:center;justify-content:center;padding:0;cursor:pointer}
.rwc-clr svg{width:14px;height:14px}
.rwc-body{display:flex;gap:8px;flex:1;min-height:0}
.rwc-col{display:flex;flex-direction:column;gap:6px;min-height:0}
.rwc-col.rw{width:138px;flex:none}.rwc-col.q{flex:1;min-width:0}
.rwc h4{margin:0;font:600 13px "Noto Naskh Arabic",serif;color:#6b6250}
.rwc-sep{width:1px;background:#e4dbc2;margin:26px 0 10px}
.rwc-scroll{display:flex;flex-direction:column;gap:6px;overflow-y:auto;flex:1;min-height:0;padding-bottom:10px;-webkit-overflow-scrolling:touch}
.rwc-scroll.rw{gap:10px}
.rwc-g{flex:none;display:flex;flex-direction:column;gap:4px;padding:6px;border-radius:16px;background:#f3ecd8;border:1px solid #e4dbc2}
.rwc-g.cur{border-color:var(--a)}
.rwc-g>small{font:600 12px/1.5 "Noto Naskh Arabic",serif;color:#6b6250;padding:0 4px}
.rwc-r{min-height:52px;padding:4px 12px;border-radius:12px;display:flex;flex-direction:column;align-items:flex-start;justify-content:center;text-align:right;background:#fff;color:#2e2a1f;border:1px solid #e4dbc2;cursor:pointer;font-family:"Noto Naskh Arabic",serif}
.rwc-r b{font:700 16px/1.4 "Noto Naskh Arabic",serif}.rwc-r small{font-size:11px;opacity:.85}
.rwc-qh{display:flex;align-items:baseline;justify-content:space-between;gap:6px}.rwc-qh small{font-size:12px;color:#6b6250}
.rwc-seg{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:3px;padding:3px;border-radius:12px;background:#efe6cd}
.rwc-seg button{min-height:40px;border-radius:9px;border:0;background:transparent;color:#2e2a1f;font:600 13px "Noto Naskh Arabic",serif;cursor:pointer}
.rwc-q,.rwc-hit{flex:none;display:flex;align-items:center;gap:10px;min-height:52px;padding:4px 10px;border-radius:14px;background:#fff;color:#2e2a1f;border:1px solid #e4dbc2;text-align:right;cursor:pointer;font-family:"Noto Naskh Arabic",serif}
.rwc-hit{min-height:60px;padding:6px 14px}.rwc-hit b{display:block;font-size:16px}.rwc-hit small{font-size:12px;opacity:.82}
.rwc-dot{flex:none;width:34px;height:34px;border-radius:17px;display:flex;align-items:center;justify-content:center;font:700 15px "Noto Naskh Arabic",serif;background:#efe6cd;color:#4a4434}
.rwc-n{flex:1;min-width:0;font:700 15px/1.4 "Noto Naskh Arabic",serif;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rwc .on{background:var(--a)!important;color:#fff!important;border-color:var(--a)!important}
.rwc .on .rwc-dot{background:rgba(255,255,255,.22);color:#fff}
.rwc-r.on{box-shadow:0 3px 10px rgba(46,42,31,.2)}
.rwc-hits{display:flex;flex-direction:column;gap:6px;flex:1;min-height:0}
.rwc-none{margin:20px 0;text-align:center;font:400 15px "Noto Naskh Arabic",serif;color:#6b6250}
.rwc-foot{display:flex;flex-direction:column;gap:8px;padding-top:8px;border-top:1px solid #e4dbc2}
.rwc-infos{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}
.rwc-infos button{min-height:44px;display:flex;align-items:center;gap:6px;padding:4px 10px;border-radius:12px;border:1px solid #e4dbc2;background:#f3ecd8;color:#2e2a1f;font:400 13px "Noto Naskh Arabic",serif;text-align:right;min-width:0;cursor:pointer}
.rwc-infos svg{color:var(--a)}.rwc-infos span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rwc-go{width:100%;min-height:58px;border:0;border-radius:18px;background:var(--a);color:#fff;display:flex;align-items:center;justify-content:space-between;gap:10px;padding:6px 18px;cursor:pointer;box-shadow:0 4px 14px rgba(46,42,31,.2)}
.rwc-go>span{display:flex;flex-direction:column;align-items:flex-start;min-width:0}
.rwc-go b{font:700 17px/1.4 "Noto Naskh Arabic",serif}.rwc-go small{font:400 12px/1.3 "Noto Naskh Arabic",serif;opacity:.9;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%}
.rwc-info{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:flex-end;z-index:2}
.rwc-bd{position:absolute;inset:0;border:0;padding:0;background:rgba(46,42,31,.35);border-radius:14px}
.rwc-is{position:relative;max-height:86%;overflow-y:auto;background:#fffbf1;border-radius:20px 20px 0 0;padding:12px 16px 16px;display:flex;flex-direction:column;gap:12px;box-shadow:0 -8px 24px rgba(46,42,31,.25)}
.rwc-ih{display:flex;align-items:center;justify-content:space-between;gap:12px}.rwc-ih small{color:#6b6250;font-size:12px}
.rwc-ih h3{margin:0;font:700 20px/1.4 "Noto Naskh Arabic",serif}
.rwc-ib{width:44px;height:44px;flex:none;border-radius:22px;border:1px solid #e4dbc2;background:#f3ecd8;color:var(--a);display:flex;align-items:center;justify-content:center;padding:0;cursor:pointer}
.rwc-card{display:flex;flex-direction:column;gap:6px;padding:12px 14px;border-radius:16px;background:#fff;border:1px solid #e4dbc2}
.rwc-card>small,.rwc-ot{font:600 12px "Noto Naskh Arabic",serif;color:#6b6250}.rwc-card>b{font:700 18px/1.5 "Noto Naskh Arabic",serif}
.rwc-f{display:flex;justify-content:space-between;gap:10px;font:400 14px/1.6 "Noto Naskh Arabic",serif;border-top:1px solid #efe6cd;padding-top:4px}
.rwc-f span{color:#6b6250}.rwc-f b{text-align:left;font-weight:600}
.rwc-chips{display:flex;gap:6px;flex-wrap:wrap;margin-top:6px}
.rwc-chip{min-height:40px;padding:4px 14px;border-radius:20px;background:#fff;color:#2e2a1f;border:1px solid #e4dbc2;font:400 14px "Noto Naskh Arabic",serif;cursor:pointer}
.rwc button:focus-visible,.rwc input:focus-visible{outline:3px solid #b8892a;outline-offset:2px}
:root[data-theme="dark"] .rwc{--a:#c9d27a;color:#efe6d0}
:root[data-theme="dark"] .rwc-search,:root[data-theme="dark"] .rwc-r,:root[data-theme="dark"] .rwc-q,:root[data-theme="dark"] .rwc-hit,:root[data-theme="dark"] .rwc-card,:root[data-theme="dark"] .rwc-chip{background:#2c261b;color:#efe6d0;border-color:#3d3526}
:root[data-theme="dark"] .rwc-g,:root[data-theme="dark"] .rwc-infos button,:root[data-theme="dark"] .rwc-ib,:root[data-theme="dark"] .rwc-seg{background:#221d14;color:#efe6d0;border-color:#3d3526}
:root[data-theme="dark"] .rwc-search input,:root[data-theme="dark"] .rwc-seg button{color:#efe6d0}
:root[data-theme="dark"] .rwc-is{background:#221d14}:root[data-theme="dark"] .rwc-dot,:root[data-theme="dark"] .rwc-clr{background:#3d3526;color:#efe6d0}
:root[data-theme="dark"] .rwc h4,:root[data-theme="dark"] .rwc-g>small,:root[data-theme="dark"] .rwc-qh small,:root[data-theme="dark"] .rwc-f span,:root[data-theme="dark"] .rwc-ot,:root[data-theme="dark"] .rwc-card>small,:root[data-theme="dark"] .rwc-none{color:#b9ad90}
:root[data-theme="dark"] .rwc .on{color:#1d1a12!important}:root[data-theme="dark"] .rwc-go{color:#1d1a12}
@media (prefers-reduced-motion:reduce){.rwc *{scroll-behavior:auto}}`;document.head.appendChild(s)})();
