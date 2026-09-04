"""
v2.0.14 patch: 参考图片风格改造

风格要点（来自参考图片）：
1. 低饱和度：卡片背景 #f8fafc / #f1f5f9，边框 #e2e8f0
2. 字段标签和内容在同一个卡片内（不是标签一个框、内容另一个框）
3. 标签是小字灰字在上方，内容在下方
4. 卡片有微边框 + 轻阴影，圆角 8-10px
5. Section 标题用小字 + 底部细线分隔
6. 来源标注用极小的灰色文字在卡片底部统一标注
7. 全宽卡片（如关联全景）用淡绿/淡蓝背景区分
8. 去掉高饱和度彩色左边框
9. 风险雷达用柔和颜色
"""
import re, json

with open('_app/template.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# 1. Replace old CSS with new low-saturation style
# ============================================================
old_css_pattern = re.compile(
    r'/\* -+ research report.*?-+ \*/\n'
    r'\.r-report\{.*?\n'
    r'\.r-report-hdr\{.*?\n'
    r'\.r-report-hdr h3\{.*?\n'
    r'\.r-report-hdr \.tag\{.*?\n'
    r'\.r-rpt-grid\{.*?\n'
    r'\.r-rpt-grid>\.r-card\{.*?\n'
    r'\.r-rpt-grid>\.r-card:nth-child\(2n\+1\)\{.*?\n'
    r'\.r-rpt-grid>\.r-card:nth-child\(-n\+2\)\{.*?\n'
    r'\.r-card-h\{.*?\n'
    r'\.r-card-h \.ic\{.*?\n'
    r'\.r-card-item\{.*?\n'
    r'\.r-card-item:last-child\{.*?\n'
    r'\.r-card-item \.fi\{.*?\n'
    r'\.r-card-item \.fc\{.*?\n'
    r'\.src-tag\{.*?\n'
    r'\.src-JD\{.*?\n'
    r'\.src-官网\{.*?\n'
    r'\.src-求职者\{.*?\n'
    r'\.src-工商\{.*?\n'
    r'\.src-简历\{.*?\n'
    r'\.src-面试记录\{.*?\n'
    r'\.src-搜索\{.*?\n'
    r'\.src-WebFetch\{.*?\n'
    r'\.src-推断\{.*?\n'
    r'\.r-radar\{.*?\n'
    r'\.r-radar-row\{.*?\n'
    r'\.r-radar-row \.lb\{.*?\n'
    r'\.r-radar-row \.trk\{.*?\n'
    r'\.r-radar-row \.fill\{.*?\n'
    r'\.r-radar-row \.val\{.*?\n'
    r'\.r-card\.full\{.*?\n'
    r'\.r-card\.warn\{.*?\n'
    r'\.r-card\.green\{.*?\n'
    r'\.r-card\.blue\{.*?\n'
    r'\.r-card\.red\{.*?\n',
    re.DOTALL
)

new_css = """/* ---------- research report (v2, low-saturation reference style) ---------- */
.r-report{background:#fff;border:1px solid #e2e8f0;border-radius:12px;box-shadow:0 1px 3px rgba(0,0,0,.04);margin-bottom:16px;overflow:hidden}
.r-report-hdr{background:linear-gradient(135deg,#f8fafc,#f1f5f9);padding:16px 20px;border-bottom:1px solid #e2e8f0;display:flex;align-items:center;gap:10px}
.r-report-hdr h3{font-size:15px;font-weight:700;margin:0;color:#1e293b}
.r-report-hdr .tag{font-size:11px;background:#e2e8f0;color:#64748b;padding:2px 8px;border-radius:10px;font-weight:500}
.r-rpt-grid{display:grid;grid-template-columns:1fr 1fr;gap:0}
.r-rpt-grid>.r-card{border:1px solid #e8ecf1;border-top:none;border-left:none;padding:14px 16px}
.r-rpt-grid>.r-card:nth-child(2n+1){border-left:none}
.r-rpt-grid>.r-card:nth-child(-n+2){border-top:none}
.r-card-h{font-size:13px;font-weight:700;color:#334155;margin-bottom:10px;padding-bottom:7px;border-bottom:1px solid #eef1f5;display:flex;align-items:center;gap:6px}
.r-card-h .ic{font-size:14px;opacity:.7}
.r-card-item{margin-bottom:10px}
.r-card-item:last-child{margin-bottom:0}
.r-card-item .fi{font-size:11px;font-weight:600;color:#64748b;margin-bottom:3px}
.r-card-item .fc{font-size:13px;line-height:1.65;color:#334155}
.r-card-src{font-size:10px;color:#94a3b8;margin-top:8px;padding-top:6px;border-top:1px solid #f1f5f9}
.r-radar{display:flex;flex-direction:column;gap:8px}
.r-radar-row{display:flex;align-items:center;gap:8px}
.r-radar-row .lb{width:72px;font-size:11px;color:#64748b;text-align:right;flex-shrink:0;font-weight:500}
.r-radar-row .trk{flex:1;height:10px;background:#eef1f5;border-radius:5px;overflow:hidden}
.r-radar-row .fill{height:100%;border-radius:5px;transition:width .4s}
.r-radar-row .val{width:32px;font-size:11px;font-weight:600;color:#475569;text-align:right;flex-shrink:0}
.r-card.full{grid-column:1/-1}
.r-card.wide-bg{background:#f0f9f7;border-top:none;border-left:none}
"""

m = old_css_pattern.search(content)
if m:
    content = content[:m.start()] + new_css + content[m.end():]
    print(f'OK: replaced CSS ({m.end()-m.start()} -> {len(new_css)} chars)')
else:
    # Fallback: find by line range
    css_start = content.find('.r-report{background:#fff;border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh);margin-bottom:16px;overflow:hidden}')
    css_end = content.find('.r-card.red{border-left:3px solid #ef4444}')
    if css_start >= 0 and css_end >= 0:
        css_end = content.find('\n', css_end) + 1
        content = content[:css_start] + new_css + content[css_end:]
        print(f'OK: replaced CSS (fallback, {css_end-css_start} chars)')
    else:
        print('ERROR: CSS not found')

# ============================================================
# 2. Replace reportSec function
# ============================================================
func_start = content.find('function reportSec(r){')
if func_start < 0:
    print('ERROR: reportSec function not found')
else:
    # Find end: next \n\nfunction or \nfunction at same indent
    func_end = content.find('\n\nfunction detailHTML', func_start)
    if func_end < 0:
        func_end = content.find('\nfunction detailHTML', func_start)
    if func_end < 0:
        print('ERROR: cannot find end of reportSec')
    else:
        new_func = r'''function reportSec(r){
  var rpt=r.research&&r.research.report;
  if(!rpt) return '<div class="r-report" style="text-align:center;padding:24px;color:#64748b">\u{1f4ca} \u6682\u65e0\u79cb\u62db\u51b3\u7b56\u62a5\u544a<br><span style="font-size:12px">\u7b49\u5f85 AI \u7814\u7a76\u586b\u5145...</span></div>';
  function radar(data){
    var items=[['\u85aa\u8d44\u786e\u5b9a\u6027','#7dd3a8'],['\u8f6c\u6b63\u6982\u7387','#93c5fd'],['WLB','#fde047'],['\u884c\u4e1a\u524d\u666f','#c4b5fd'],['\u516c\u53f8\u7a33\u5b9a\u6027','#fca5a5']];
    return '<div class="r-radar">'+items.map(function(p){var k=p[0],c=p[1];var v=(data&&data[k])||0;return '<div class="r-radar-row"><div class="lb">'+k+'</div><div class="trk"><div class="fill" style="width:'+v+'%;background:'+c+'"></div></div><div class="val">'+v+'</div></div>';}).join('')+'</div>';
  }
  function itemHTML(name,obj){
    if(!obj)return '';
    var text=(typeof obj==='string')?obj:obj.text;
    var src=(typeof obj==='string')?'\u63a8\u65ad':obj.src;
    return '<div class="r-card-item"><div class="fi">'+esc(name)+'</div><div class="fc">'+esc(text||'\u6682\u65e0')+'</div></div>';
  }
  function sectionHTML(title,fields,data,isFull,isWide){
    if(!data)data={};
    var cls='r-card';if(isFull)cls+=' full';if(isWide)cls+=' wide-bg';
    var h='<div class="'+cls+'"><div class="r-card-h">'+title+'</div>';
    var sources=[];
    for(var i=0;i<fields.length;i++){
      var f=fields[i];var obj=data[f];if(!obj)continue;
      var src=(typeof obj==='string')?'\u63a8\u65ad':obj.src;
      if(src&&sources.indexOf(src)<0)sources.push(src);
      h+=itemHTML(f,obj);
    }
    if(sources.length)h+='<div class="r-card-src">\u6765\u6e90\uff1a'+sources.join(' / ')+'</div>';
    return h+'</div>';
  }
  var CARDS=[
    {k:'company_profile',t:'\u{1f3e2} \u516c\u53f8\u753b\u50cf',fs:['\u5b9a\u6027','\u4e1a\u52a1\u6a21\u5f0f','\u884c\u4e1a\u5730\u4f4d','\u878d\u8d44/\u80a1\u4e1c']},
    {k:'position_analysis',t:'\u{1f4bc} \u5c97\u4f4d\u6df1\u5ea6\u62c6\u89e3',fs:['\u771f\u5b9e\u5de5\u4f5c\u5185\u5bb9','\u80fd\u529b\u6210\u957f','\u8df3\u69fd\u8def\u5f84','JD\u8981\u6c42\u9010\u6761\u5bf9\u7167']},
    {k:'compensation',t:'\u{1f4b0} \u85aa\u8d44\u4e0e\u4ee3\u4ef7',fs:['\u85aa\u8d44\u7ed3\u6784','\u6027\u4ef7\u6bd4','\u8f6c\u6b63\u7387']},
    {k:'match_analysis',t:'\u{1f3af} \u5339\u914d\u5ea6\u5206\u6790',fs:['\u786c\u5339\u914d','\u8f6f\u5339\u914d','\u9762\u8bd5\u53ef\u884c\u6027']},
    {k:'risk_radar',t:'\u{26a0}\ufe0f \u98ce\u9669\u96f7\u8fbe',tp:'radar'},
    {k:'interview_info',t:'\u{1f3a4} \u9762\u8bd5\u5b98\u4fe1\u606f',fs:['\u4e00\u9762','\u4e8c\u9762','\u7ec8\u9762']},
    {k:'timeline',t:'\u{1f4c5} \u79cb\u62db\u65f6\u95f4\u7ebf',fs:['\u7f51\u7533\u622a\u6b62','\u7b14\u8bd5/\u9762\u8bd5\u8282\u594f','\u5f53\u524d\u8fdb\u5ea6','\u5269\u4f59\u5173\u952e\u8282\u70b9']},
    {k:'competitor_compare',t:'\u{1f4ca} \u6c60\u5185\u5bf9\u6807',fs:['\u6700\u63a5\u8fd1\u76842-3\u4e2a\u673a\u4f1a','\u4f18\u5148\u7ea7','\u673a\u4f1a\u6210\u672c'],wide:true},
    {k:'decision',t:'\u{1f4a1} \u51b3\u7b56\u5efa\u8bae',fs:['\u6295\u4e0d\u6295','\u4f18\u5148\u7ea7','\u9762\u8bd5\u7b56\u7565','offer\u9009\u62e9'],full:true}
  ];
  var h='<div class="r-report"><div class="r-report-hdr"><h3>\u{1f4ca} \u79cb\u62db\u51b3\u7b56\u62a5\u544a</h3><span class="tag">AI \u751f\u6210</span></div><div class="r-rpt-grid">';
  for(var i=0;i<CARDS.length;i++){
    var c=CARDS[i];
    if(c.tp==='radar'){
      h+='<div class="r-card full"><div class="r-card-h">'+c.t+'</div>'+radar(rpt[c.k])+'</div>';
    }else{
      h+=sectionHTML(c.t,c.fs,rpt[c.k],c.full,c.wide);
    }
  }
  return h+'</div></div>';
}'''
        content = content[:func_start] + new_func + content[func_end:]
        print(f'OK: replaced reportSec function ({func_end-func_start} chars)')

# ============================================================
# 3. Update compensation data in jobs.json with city-specific costs
# ============================================================
# City data for salary calculation
CITY_DATA = {
    'co_huaan':    {'city': '上海',   'rent': '3500-5000', 'insurance_rate': '22%', 'tax_note': '按年薪计个税约15-20%'},
    'co_cdb':      {'city': '北京',   'rent': '4000-6000', 'insurance_rate': '22%', 'tax_note': '按年薪计个税约15-20%'},
    'co_btn':      {'city': '昆明',   'rent': '1500-2500', 'insurance_rate': '20%', 'tax_note': '按年薪计个税约10-15%'},
    'co_yuanzi':   {'city': '上海',   'rent': '3500-5000', 'insurance_rate': '22%', 'tax_note': '按年薪计个税约10-15%'},
    'co_yuanjia':  {'city': '上海',   'rent': '3500-5000', 'insurance_rate': '22%', 'tax_note': '按年薪计个税约10-15%'},
    'co_zhuoer':   {'city': '上海',   'rent': '3500-5000', 'insurance_rate': '22%', 'tax_note': '按年薪计个税约10-15%'},
    'co_xidao':    {'city': '上海',   'rent': '3500-5000', 'insurance_rate': '22%', 'tax_note': '按年薪计个税约10-15%'},
}

jobs_path = 'jobs.json'
with open(jobs_path, 'r', encoding='utf-8') as f:
    jobs = json.load(f)

updated = 0
for rec in jobs['records']:
    rpt = rec.get('research', {}).get('report', {})
    comp = rpt.get('compensation', {})
    cid = rec['id']
    cd = CITY_DATA.get(cid)
    if not cd:
        continue

    salary_field = comp.get('薪资结构', {})
    salary_text = ''
    salary_src = ''
    if isinstance(salary_field, dict):
        salary_text = salary_field.get('text', '')
        salary_src = salary_field.get('src', '')
    elif isinstance(salary_field, str):
        salary_text = salary_field
        salary_src = '推断'

    # Build enriched salary text with city costs
    city = cd['city']
    rent = cd['rent']
    ins_rate = cd['insurance_rate']
    tax_note = cd['tax_note']

    enriched_parts = []
    if salary_text:
        enriched_parts.append(salary_text)
    enriched_parts.append(f'五险一金个人缴纳比例约{ins_rate}，到手约为税前×78%。')
    enriched_parts.append(f'{city}通勤1h内月租约{rent}元（合租/整租）。')
    enriched_parts.append(f'水电燃气+网费月均约200-400元。{tax_note}。')

    new_salary_text = ' '.join(enriched_parts)

    if isinstance(salary_field, dict):
        salary_field['text'] = new_salary_text
    else:
        comp['薪资结构'] = {'text': new_salary_text, 'src': salary_src}

    # Also update 性价比 to mention net income
    cost_field = comp.get('性价比', {})
    if isinstance(cost_field, dict):
        cost_text = cost_field.get('text', '')
        if cost_text and '到手' not in cost_text:
            cost_field['text'] = cost_text + f' 扣除五险一金({ins_rate})和{city}生活成本(房租{rent}+水电网200-400/月)后，实际到手购买力需重新评估。'
    updated += 1

print(f'OK: updated {updated} companies compensation data')

with open(jobs_path, 'w', encoding='utf-8') as f:
    json.dump(jobs, f, ensure_ascii=False, indent=2)
print(f'OK: wrote {jobs_path}')

# ============================================================
# 4. Write template.html
# ============================================================
with open('_app/template.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('ALL DONE')
