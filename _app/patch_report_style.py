import re

with open('_app/template.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# 1. Replace CSS: old r-report / r-card / src-tag styles
# ============================================================

old_css_start = content.find('/* ---------- research report ---------- */')
old_css_end = content.find('.r-card.red{border-left:3px solid #ef4444}')
if old_css_end > 0:
    old_css_end = content.find('\n', old_css_end) + 1
else:
    old_css_end = content.find('.r-card.red', old_css_start + 100)
    old_css_end = content.find('\n', old_css_end) + 1

new_css = """/* ---------- research report (v2.0.14, reference image style) ---------- */
.r-report{background:#f8fafb;border:1px solid #e2e8f0;border-radius:10px;margin-bottom:16px;overflow:hidden}
.r-report-hdr{background:#f1f5f9;padding:14px 18px;border-bottom:1px solid #e2e8f0;display:flex;align-items:center;gap:10px}
.r-report-hdr h3{font-size:15px;font-weight:700;margin:0;color:#1e293b}
.r-report-hdr .tag{font-size:10px;background:#e2e8f0;color:#64748b;padding:2px 8px;border-radius:4px;font-weight:500}
.r-rpt-grid{display:grid;grid-template-columns:1fr 1fr;gap:0}
.r-rpt-grid>.r-card{border:1px solid #e8ecf1;border-top:none;border-left:none;padding:14px 16px;background:#fff}
.r-rpt-grid>.r-card:nth-child(2n+1){border-left:none}
.r-rpt-grid>.r-card:nth-child(-n+2){border-top:none}
.r-card-h{font-size:13px;font-weight:700;color:#334155;margin-bottom:10px;padding-bottom:7px;border-bottom:1px solid #eef1f5;display:flex;align-items:center;gap:6px}
.r-card-h .ic{font-size:14px;opacity:.7}
.r-card-item{margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid #f4f5f7}
.r-card-item:last-child{margin-bottom:0;padding-bottom:0;border-bottom:none}
.r-card-item .fi{font-size:11px;font-weight:600;color:#64748b;margin-bottom:4px}
.r-card-item .fc{font-size:13px;line-height:1.7;color:#334155}
.r-card-src{font-size:10px;color:#94a3b8;margin-top:8px;padding-top:6px;border-top:1px solid #f4f5f7}
.r-radar{display:flex;flex-direction:column;gap:8px}
.r-radar-row{display:flex;align-items:center;gap:8px}
.r-radar-row .lb{width:72px;font-size:11px;color:#64748b;text-align:right;flex-shrink:0;font-weight:500}
.r-radar-row .trk{flex:1;height:10px;background:#eef1f5;border-radius:5px;overflow:hidden}
.r-radar-row .fill{height:100%;border-radius:5px;transition:width .4s}
.r-radar-row .val{width:32px;font-size:11px;font-weight:600;color:#475569;text-align:right;flex-shrink:0}
.r-card.full{grid-column:1/-1}
.r-card.wide-bg{background:#f0f7f6;border-top:none;border-left:none}
"""

content = content[:old_css_start] + new_css + content[old_css_end:]
print(f'OK: replaced CSS ({old_css_end - old_css_start} -> {len(new_css)} chars)')

# ============================================================
# 2. Replace reportSec function
# ============================================================

# Find the function
func_start = content.find('function reportSec(r){')
func_end_marker = '\n\nfunction detailHTML(r){'
func_end = content.find(func_end_marker, func_start)
if func_end < 0:
    # fallback
    func_end = content.find('\nfunction detailHTML', func_start)

new_func = r"""function reportSec(r){
  var rpt=r.research&&r.research.report;
  if(!rpt) return '<div class="r-report" style="text-align:center;padding:24px;color:#64748b">暂无秋招决策报告</div>';

  function radar(data){
    var items=[['\u85aa\u8d44\u786e\u5b9a\u6027','#60a5fa'],['\u8f6c\u6b63\u6982\u7387','#34d399'],['WLB','#fbbf24'],['\u884c\u4e1a\u524d\u666f','#a78bfa'],['\u516c\u53f8\u7a33\u5b9a\u6027','#f87171']];
    var h='<div class="r-radar">';
    for(var i=0;i<items.length;i++){
      var k=items[i][0],c=items[i][1];
      var v=(data&&data[k])||0;
      h+='<div class="r-radar-row"><div class="lb">'+k+'</div><div class="trk"><div class="fill" style="width:'+v+'%;background:'+c+'"></div></div><div class="val">'+v+'</div></div>';
    }
    return h+'</div>';
  }

  function itemHTML(name, obj){
    if(!obj) return '';
    var text=(typeof obj==='string')?obj:(obj.text||'');
    var src=(typeof obj==='string')?'推断':(obj.src||'');
    return '<div class="r-card-item"><div class="fi">'+esc(name)+'</div><div class="fc">'+esc(text||'\u6682\u65e0')+'</div></div>';
  }

  function sectionHTML(title, fields, data, isFull, isWide){
    if(!data) data={};
    var cls='r-card';
    if(isFull) cls+=' full';
    if(isWide) cls+=' wide-bg';
    var h='<div class="'+cls+'"><div class="r-card-h">'+esc(title)+'</div>';
    var sources=[];
    for(var i=0;i<fields.length;i++){
      var f=fields[i];
      var obj=data[f]||{};
      var text=(typeof obj==='string')?obj:(obj.text||'');
      var src=(typeof obj==='string')?'推断':(obj.src||'');
      if(text) h+=itemHTML(f, obj);
      if(src && sources.indexOf(src)<0) sources.push(src);
    }
    if(sources.length) h+='<div class="r-card-src">\u6765\u6e90\uff1a'+sources.join(' / ')+'</div>';
    return h+'</div>';
  }

  var h='<div class="r-report"><div class="r-report-hdr"><h3>\u{1f4ca} \u79cb\u62db\u51b3\u7b56\u62a5\u544a</h3><span class="tag">AI \u751f\u6210</span></div><div class="r-rpt-grid">';

  // Row 1: 4 cards
  var cp=rpt.company_profile||{};
  h+=sectionHTML('\u{1f3e2} \u516c\u53f8\u753b\u50cf', ['\u5b9a\u6027','\u4e1a\u52a1\u6a21\u5f0f','\u884c\u4e1a\u5730\u4f4d','\u878d\u8d44/\u80a1\u4e1c'], cp, false, false);

  var pa=rpt.position_analysis||{};
  h+=sectionHTML('\u{1f4bc} \u5c97\u4f4d\u6df1\u5ea6\u62c6\u89e3', ['\u771f\u5b9e\u5de5\u4f5c\u5185\u5bb9','\u80fd\u529b\u6210\u957f','\u8df3\u69fd\u8def\u5f84','JD\u8981\u6c42\u9010\u6761\u5bf9\u7167'], pa, false, false);

  var comp=rpt.compensation||{};
  h+=sectionHTML('\u{1f4b0} \u85aa\u8d44\u4e0e\u4ee3\u4ef7', ['\u85aa\u8d44\u7ed3\u6784','\u6027\u4ef7\u6bd4','\u8f6c\u6b63\u7387'], comp, false, false);

  var match=rpt.match_analysis||{};
  h+=sectionHTML('\u{1f3af} \u5339\u914d\u5ea6\u5206\u6790', ['\u786c\u5339\u914d','\u8f6f\u5339\u914d','\u9762\u8bd5\u53ef\u884c\u6027'], match, false, false);

  // Row 2: risk radar (full width)
  var rr=rpt.risk_radar||{};
  h+='<div class="r-card full"><div class="r-card-h">\u{26a0}\ufe0f \u98ce\u9669\u96f7\u8fbe</div>'+radar(rr)+'</div>';

  // Row 3: interview + timeline
  var iv=rpt.interview_info||{};
  h+=sectionHTML('\u{1f3a4} \u9762\u8bd5\u5b98\u4fe1\u606f', ['\u4e00\u9762','\u4e8c\u9762','\u7ec8\u9762'], iv, false, false);

  var tl=rpt.timeline||{};
  h+=sectionHTML('\u{1f4c5} \u79cb\u62db\u65f6\u95f4\u7ebf', ['\u7f51\u7533\u622a\u6b62','\u7b14\u8bd5/\u9762\u8bd5\u8282\u594f','\u5f53\u524d\u8fdb\u5ea6','\u5269\u4f59\u5173\u952e\u8282\u70b9'], tl, false, false);

  // Row 4: competitor (full width, wide bg)
  var cc=rpt.competitor_compare||{};
  h+=sectionHTML('\u{1f4ca} \u6c60\u5185\u5bf9\u6807', ['\u6700\u63a5\u8fd1\u76842-3\u4e2a\u673a\u4f1a','\u4f18\u5148\u7ea7','\u673a\u4f1a\u6210\u672c'], cc, true, true);

  // Row 5: decision (full width)
  var dec=rpt.decision||{};
  h+=sectionHTML('\u{1f4a1} \u51b3\u7b56\u5efa\u8bae', ['\u6295\u4e0d\u6295','\u4f18\u5148\u7ea7','\u9762\u8bd5\u7b56\u7565','offer\u9009\u62e9'], dec, true, false);

  return h+'</div></div>';
}
"""

if func_start >= 0 and func_end >= 0:
    content = content[:func_start] + new_func + content[func_end:]
    print(f'OK: replaced reportSec function')
else:
    print(f'WARN: func_start={func_start}, func_end={func_end}')

with open('_app/template.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('DONE')
