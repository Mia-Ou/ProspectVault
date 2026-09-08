// 招聘页面 JD 提取书签let
(function(){
  'use strict';
  
  // 提取页面文字
  const selectors = [
    '.job-detail', '.position-detail', '.job-content', '.job-info',
    '.recruitment-detail', '.job-desc', '.job-description',
    '.post-content', '.detail-content', '.main-content',
    'article', '.content', 'main', '#content', '.container'
  ];
  
  let text = '';
  
  // 尝试从结构化容器提取
  for (const sel of selectors) {
    const el = document.querySelector(sel);
    if (el && el.innerText && el.innerText.length > 50) {
      text = el.innerText.trim();
      break;
    }
  }
  
  // 如果没找到，取整个 body
  if (!text || text.length < 50) {
    document.querySelectorAll('script,style,noscript,svg,nav,footer,header,iframe,.comment,.sidebar').forEach(e => e.remove());
    text = (document.body.innerText || '').replace(/\s+/g, ' ').trim();
  }
  
  // 构造结果
  const result = {
    url: location.href,
    title: document.title,
    text: text.slice(0, 8000)
  };
  
  // 复制到剪贴板
  const json = JSON.stringify(result, null, 2);
  
  // 方法1：现代 Clipboard API
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(json).then(() => {
      showMsg('✅ 已复制 JD 到剪贴板（' + text.length + ' 字）<br>切到 ProspectVault，按 Ctrl+V 粘贴');
    }).catch(() => {
      fallbackCopy(json, text.length);
    });
  } else {
    fallbackCopy(json, text.length);
  }
  
  function fallbackCopy(str, len) {
    const ta = document.createElement('textarea');
    ta.value = str;
    ta.style.cssText = 'position:fixed;left:-9999px';
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand('copy');
      showMsg('✅ 已复制 JD 到剪贴板（' + len + ' 字）<br>切到 ProspectVault，按 Ctrl+V 粘贴');
    } catch (e) {
      showMsg('⚠️ 复制失败，请手动选中下方文字复制：<br><textarea style="width:100%;height:200px;margin-top:8px">' + str + '</textarea>');
    }
    document.body.removeChild(ta);
  }
  
  function showMsg(html) {
    const div = document.createElement('div');
    div.style.cssText = 'position:fixed;top:20px;left:50%;transform:translateX(-50%);background:#1d4ed8;color:#fff;padding:14px 20px;border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,.2);z-index:999999;font-size:14px;line-height:1.6;max-width:90vw';
    div.innerHTML = html;
    document.body.appendChild(div);
    setTimeout(() => { div.style.opacity = '0'; div.style.transition = 'opacity .5s'; }, 4000);
    setTimeout(() => div.remove(), 5000);
  }
})();
