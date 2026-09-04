import re

with open('_app/template.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the function using regex
pattern = r'function reportSec\(r\)\{[\s\S]*?\n\}'
m = re.search(pattern, content)
if not m:
    print('ERROR: reportSec function not found')
    exit(1)

print(f'Found at {m.start()}-{m.end()}, length={len(m.group())}')

new_func = '''function reportSec(r){
  const rpt=r.research&&r.research.report;
  if(!rpt) return '<div class="r-report" style="opacity:.7;text-align:center;padding:24px">\\u{1f4ca} \\u6682\\u65e0\\u79cb\\u62db\\u51b3\\u7b56\\u62a5\\u544a<br><span style="font-size:12px;color:var(--tx2)">\\u7b49\\u5f85 AI \\u7814\\u7a76\\u586b\\u5145...</span></div>';
  var srcCls={'JD':'src-JD','\\u5b98\\u7f51':'src-\\u5b98\\u7f51','\\u6c42\\u804c\\u8005':'src-\\u6c42\\u804c\\u8005','\\u5de5\\u5546':'src-\\u5de5\\u5546','\\u7b80\\u5386':'src-\\u7b80\\u5386','\\u9762\\u8bd5\\u8bb0\\u5f55':'src-\\u9762\\u8bd5\\u8bb0\\u5f55','\\u641c\\u7d22':'src-\\u641c\\u7d22','WebFetch':'src-WebFetch','\\u63a8\\u65ad':'src-\\u63a8\\u65ad'};
  function srcTag(s){return '<span class="src-tag '+(srcCls[s]||'src-\\u63a8\\u65ad')+'">'+(esc(s||'\\u672a\\u77e5'))+'</span>';}
  function fld(name,obj){
    if(!obj)return '';
    var text=(typeof obj==='string')?obj:obj.text;
    var src=(typeof obj==='string')?'\\u63a8\\u65ad':obj.src;
    return '<div class="r-card-item"><div class="fi">'+esc(name)+' '+srcTag(src)+'</div><div class="fc">'+esc(text||'\\u6682\\u65e0')+'</div></div>';
  }
  function radar(data){
    var items=[['\\u85aa\\u8d44\\u786e\\u5b9a\\u6027','#22c55e'],['\\u8f6c\\u6b63\\u6982\\u7387','#3b82f6'],['WLB','#f59e0b'],['\\u884c\\u4e1a\\u524d\\u666f','#8b5cf6'],['\\u516c\\u53f8\\u7a33\\u5b9a\\u6027','#ef4444']];
    return '<div class="r-radar">'+items.map(function(p){var k=p[0],c=p[1];var v=(data&&data[k])||0;return '<div class="r-radar-row"><div class="lb">'+k+'</div><div class="trk"><div class="fill" style="width:'+v+'%;background:'+c+'"></div></div><div class="val">'+v+'</div></div>';}).join('')+'</div>';
  }
  var CARDS=[
    {k:'company_profile',ic:'\\u{1f3e2}',t:'\\u516c\\u53f8\\u753b\\u50cf',fs:['\\u5b9a\\u6027','\\u4e1a\\u52a1\\u6a21\\u5f0f','\\u884c\\u4e1a\\u5730\\u4f4d','\\u878d\\u8d44/\\u80a1\\u4e1c'],cls:''},
    {k:'position_analysis',ic:'\\u{1f4bc}',t:'\\u5c97\\u4f4d\\u6df1\\u5ea6\\u62c6\\u89e3',fs:['\\u771f\\u5b9e\\u5de5\\u4f5c\\u5185\\u5bb9','\\u80fd\\u529b\\u6210\\u957f','\\u8df3\\u69fd\\u8def\\u5f84','JD\\u8981\\u6c42\\u9010\\u6761\\u5bf9\\u7167'],cls:''},
    {k:'compensation',ic:'',t:'\\u85aa\\u8d44\\u4e0e\\u4ee3\\u4ef7',fs:['\\u85aa\\u8d44\\u7ed3\\u6784','\\u6027\\u4ef7\\u6bd4','\\u8f6c\\u6b63\\u7387'],cls:''},
    {k:'match_analysis',ic:'\\u{1f3af}',t:'\\u5339\\u914d\\u5ea6\\u5206\\u6790',fs:['\\u786c\\u5339\\u914d','\\u8f6f\\u5339\\u914d','\\u9762\\u8bd5\\u53ef\\u884c\\u6027'],cls:'blue'},
    {k:'risk_radar',ic:'\\u26a0\\ufe0f',t:'\\u98ce\\u9669\\u96f7\\u8fbe',tp:'radar',cls:'warn',full:false},
    {k:'interview_info',ic:'\\u{1f3a4}',t:'\\u9762\\u8bd5\\u5b98\\u4fe1\\u606f',fs:['\\u4e00\\u9762','\\u4e8c\\u9762','\\u7ec8\\u9762'],cls:''},
    {k:'timeline',ic:'\\u{1f4c5}',t:'\\u79cb\\u62db\\u65f6\\u95f4\\u7ebf',fs:['\\u7f51\\u7533\\u622a\\u6b62','\\u7b14\\u8bd5/\\u9762\\u8bd5\\u8282\\u594f','\\u5f53\\u524d\\u8fdb\\u5ea6','\\u5269\\u4f59\\u5173\\u952e\\u8282\\u70b9'],cls:''},
    {k:'competitor_compare',ic:'',t:'\\u6c60\\u5185\\u5bf9\\u6807',fs:['\\u6700\\u63a5\\u8fd1\\u76842-3\\u4e2a\\u673a\\u4f1a','\\u4f18\\u5148\\u7ea7','\\u673a\\u4f1a\\u6210\\u672c'],cls:''},
    {k:'decision',ic:'\\u{1f4a1}',t:'\\u51b3\\u7b56\\u5efa\\u8bae',fs:['\\u6295\\u4e0d\\u6295','\\u4f18\\u5148\\u7ea7','\\u9762\\u8bd5\\u7b56\\u7565','offer\\u9009\\u62e9'],cls:'green',full:true}
  ];
  var h='<div class="r-report"><div class="r-report-hdr"><h3>\\u{1f4ca} \\u79cb\\u62db\\u51b3\\u7b56\\u62a5\\u544a</h3><span class="tag">AI \\u751f\\u6210</span></div><div class="r-rpt-grid">';
  for(var i=0;i<CARDS.length;i++){
    var c=CARDS[i];
    var cls='r-card';
    if(c.full) cls+=' full';
    if(c.cls) cls+=' '+c.cls;
    h+='<div class="'+cls+'"><div class="r-card-h"><span class="ic">'+c.ic+'</span>'+c.t+'</div>';
    if(c.tp==='radar') h+=radar(rpt[c.k]);
    else{var d=rpt[c.k]||{};for(var j=0;j<c.fs.length;j++) h+=fld(c.fs[j],d[c.fs[j]]);}
    h+='</div>';
  }
  return h+'</div></div>';
}'''

content = content[:m.start()] + new_func + content[m.end():]

with open('_app/template.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('OK: reportSec replaced with grid layout')
