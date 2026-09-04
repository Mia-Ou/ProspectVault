#!/usr/bin/env python3
"""v2.0.15 — report style v3: 
1. each field = independent small card (bg + border + radius)
2. content split into bullet points (detect ①②③ or 。separators)
3. key data highlighted with low-sat colors (numbers=blue, money=green, ✓△✗=color)
"""
import re, io

PATH = r'_app/template.html'
with io.open(PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# ====== 1. CSS changes ======
OLD_CSS = """.r-card-item{margin-bottom:10px}
.r-card-item:last-child{margin-bottom:0}
.r-card-item .fi{font-size:11px;font-weight:600;color:#64748b;margin-bottom:3px}
.r-card-item .fc{font-size:13px;line-height:1.65;color:#334155}
.r-card-src{font-size:10px;color:#94a3b8;margin-top:8px;padding-top:6px;border-top:1px solid #f1f5f9}"""

NEW_CSS = """.r-card-item{background:#f8fafc;border:1px solid #e8ecf1;border-radius:8px;padding:10px 12px;margin-bottom:8px}
.r-card-item:last-child{margin-bottom:0}
.r-card-item .fi{font-size:11px;font-weight:700;color:#475569;margin-bottom:6px;letter-spacing:.3px}
.r-card-item .fc{font-size:13px;line-height:1.7;color:#334155}
.r-card-item .fc ul{margin:0;padding:0 0 0 2px;list-style:none}
.r-card-item .fc ul li{position:relative;padding-left:14px;margin-bottom:4px}
.r-card-item .fc ul li:last-child{margin-bottom:0}
.r-card-item .fc ul li::before{content:'';position:absolute;left:0;top:8px;width:5px;height:5px;border-radius:50%;background:#94a3b8}
.r-card-item .fc .hl-num{color:#2563eb;font-weight:600}
.r-card-item .fc .hl-money{color:#059669;font-weight:600}
.r-card-item .fc .hl-pos{color:#16a34a;font-weight:600}
.r-card-item .fc .hl-neg{color:#dc2626;font-weight:600}
.r-card-item .fc .hl-neutral{color:#ca8a04;font-weight:600}
.r-card-item .fc .hl-tag{background:#e0f2fe;color:#0369a1;padding:1px 5px;border-radius:4px;font-size:12px;font-weight:600}
.r-card-src{font-size:10px;color:#94a3b8;margin-top:8px;padding-top:6px;border-top:1px solid #f1f5f9}"""

if OLD_CSS in content:
    content = content.replace(OLD_CSS, NEW_CSS)
    print('OK: CSS updated')
else:
    print('WARN: CSS old block not found, trying regex')
    # fallback: find by unique marker
    pattern = re.compile(r'\.r-card-item\{margin-bottom:10px\}.*?\.r-card-src\{[^}]+\}', re.DOTALL)
    m = pattern.search(content)
    if m:
        content = content[:m.start()] + NEW_CSS + content[m.end():]
        print('OK: CSS updated via regex')
    else:
        print('ERROR: CSS not found')

# ====== 2. Update itemHTML function to add bullet splitting + highlighting ======
OLD_ITEM = """  function itemHTML(name,obj){
    if(!obj)return '';
    var text=(typeof obj==='string')?obj:obj.text;
    var src=(typeof obj==='string')?'\\u63a8\\u65ad':obj.src;
    return '<div class="r-card-item"><div class="fi">'+esc(name)+'</div><div class="fc">'+esc(text||'\\u6682\\u65e0')+'</div></div>';
  }"""

NEW_ITEM = r"""  function parseBullets(text){
    if(!text) return '';
    // Split on ①②③... markers
    var circled = /[\u2460-\u2469\u24ea\u2473-\u2492]/;
    if(circled.test(text)){
      var parts = text.split(/([\u2460-\u2469\u24ea\u2473-\u2492])/);
      var items = [];
      for(var i=1;i<parts.length;i+=2){
        var bullet = parts[i];
        var body = (parts[i+1]||'').replace(/^\uff1a?\s*/, '');
        if(body) items.push(bullet + body);
      }
      if(items.length) return items;
    }
    // Split on 。for long text (>60 chars)
    if(text.length > 60){
      var sentences = text.split(/\u3002/).filter(function(s){return s.trim()});
      if(sentences.length >= 2) return sentences.map(function(s){return s.trim()});
    }
    return null; // not splittable
  }
  function highlightText(s){
    var e = esc(s);
    // highlight numbers with units: 70%, 3人, 100万, 1.5亿, 15-20%, Top15, etc
    e = e.replace(/(\d[\d,.]*[\u4e07\u4ebf%])/g, '<span class="hl-money">$1</span>');
    e = e.replace(/(\d+[\u5bb6\u4eba\u5c97\u4e2a\u6708\u5e74\u65e5])(?![^<]*>)/g, '<span class="hl-num">$1</span>');
    e = e.replace(/(Top\s*\d+)/gi, '<span class="hl-num">$1</span>');
    // highlight percentages
    e = e.replace(/(\d+[\-~]\d+%)/g, '<span class="hl-money">$1</span>');
    e = e.replace(/((?:\d+\.?\d*)%)/g, '<span class="hl-money">$1</span>');
    // highlight salary ranges: 18-25万, 8-12K, etc
    e = e.replace(/(\d+[\-~]\d+\s*[Kk万])/g, '<span class="hl-money">$1</span>');
    // highlight ✓ △ ✗ marks
    e = e.replace(/(\u2713\u2581?)/g, '<span class="hl-pos">$1</span>');
    e = e.replace(/(\u25b3\u2581?)/g, '<span class="hl-neutral">$1</span>');
    e = e.replace(/(\u2717\u2581?)/g, '<span class="hl-neg">$1</span>');
    // highlight 【】brackets
    e = e.replace(/\u3010([^\u3011]+)\u3011/g, '<span class="hl-tag">$1</span>');
    return e;
  }
  function itemHTML(name,obj){
    if(!obj)return '';
    var text=(typeof obj==='string')?obj:obj.text;
    if(!text) return '';
    var bullets = parseBullets(text);
    var bodyHTML;
    if(bullets && bullets.length > 1){
      bodyHTML = '<ul>' + bullets.map(function(b){return '<li>'+highlightText(b)+'</li>';}).join('') + '</ul>';
    } else {
      bodyHTML = highlightText(text);
    }
    return '<div class="r-card-item"><div class="fi">'+esc(name)+'</div><div class="fc">'+bodyHTML+'</div></div>';
  }"""

if OLD_ITEM in content:
    content = content.replace(OLD_ITEM, NEW_ITEM)
    print('OK: itemHTML updated')
else:
    # Try regex
    pattern = re.compile(r"  function itemHTML\(name,obj\)\{.*?return '<div class=\"r-card-item\">.*?'</div></div>';\s*\}", re.DOTALL)
    m = pattern.search(content)
    if m:
        content = content[:m.start()] + NEW_ITEM + content[m.end():]
        print('OK: itemHTML updated via regex')
    else:
        print('ERROR: itemHTML not found')
        # Debug
        idx = content.find('function itemHTML')
        if idx >= 0:
            print('  Found at pos', idx)
            print('  Context:', repr(content[idx:idx+300]))

with io.open(PATH, 'w', encoding='utf-8') as f:
    f.write(content)
print('DONE')
