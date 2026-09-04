const fs = require('fs');
const path = require('path');
const { JSDOM, VirtualConsole } = require('jsdom');

const file = process.argv[2] || path.join(__dirname, '..', '秋招工作台.html');
const html = fs.readFileSync(file, 'utf-8');

const errors = [];
const vc = new VirtualConsole();
vc.on('jsdomError', e => errors.push('jsdomError: ' + e.message));
vc.on('error', m => errors.push('error: ' + m));
vc.on('warn', () => { });

const dom = new JSDOM(html, {
  runScripts: 'dangerously',
  resources: 'usable',
  virtualConsole: vc,
  url: 'http://localhost/',
  pretendToBeVisual: true,
});
const { window } = dom;
window.addEventListener('error', e => errors.push('window.error: ' + e.message));

let pass = 0, fail = 0;
function assert(name, cond, extra) {
  const ok = !!cond;
  ok ? pass++ : fail++;
  console.log((ok ? '  ✅ ' : '  ❌ ') + name + (extra != null ? '  → ' + extra : ''));
  return ok;
}
function skip(name, why) { console.log('  ⏭  ' + name + '  → ' + why); }

setTimeout(() => {
  const d = window.document;
  console.log('=== 冒烟测试: ' + path.basename(file) + ' ===');

  // 期望值从内嵌种子数据动态推导，避免数据变动后误报
  let seed = null;
  try { seed = JSON.parse(d.getElementById('seed-data').textContent); } catch (e) { }
  const expCo = seed && Array.isArray(seed.records) ? seed.records.length : 0;
  const expPos = seed && Array.isArray(seed.records)
    ? seed.records.reduce((n, r) => n + ((r.positions && r.positions.length) || 1), 0) : 0;

  // 1. boot 无致命错误
  assert('boot 无 JS 致命错误', errors.length === 0, errors.slice(0, 3).join(' | ') || 'clean');

  // 2. 视图粒度：无独立面试 tab，面试研究已并入公司研究
  const tabs = [...d.querySelectorAll('.tab')].map(t => t.dataset.tab);
  assert('无独立面试 tab（面试研究已并入公司研究）', tabs.indexOf('interview') === -1, JSON.stringify(tabs));
  ['dash', 'table', 'board', 'research'].forEach(t =>
    assert('存在 tab: ' + t, tabs.indexOf(t) !== -1));

  // 3. 投递总表 = 岗位级（一行一岗）
  const rows = [...d.querySelectorAll('#tableWrap tbody tr')];
  const keys = rows.map(tr => (tr.querySelector('.co') ? tr.querySelector('.co').textContent.trim() : '') + '||' + (tr.querySelector('.po') ? tr.querySelector('.po').getAttribute('title') || tr.querySelector('.po').textContent.trim() : ''));
  const dupSet = keys.filter((k, i) => keys.indexOf(k) !== i);
  if (expPos > 0) assert('投递总表行数 = 岗位数（' + expPos + '）', rows.length === expPos, rows.length);
  else skip('投递总表行数', '空壳版无种子数据');
  assert('投递总表无重复 (公司+岗位)', dupSet.length === 0, dupSet.length ? dupSet.join('; ') : 'none');

  // 4. 看板 = 岗位级
  const bcards = [...d.querySelectorAll('.bcard')];
  if (expPos > 0) assert('看板卡片数 = 岗位数（' + expPos + '）', bcards.length === expPos, bcards.length);
  else skip('看板卡片数', '空壳版无种子数据');

  // 5. 公司研究 = 公司级（一司一卡）
  const rsTab = d.querySelector('.tab[data-tab="research"]');
  if (rsTab) rsTab.click();
  const picks = [...d.querySelectorAll('.r-pick')];
  const coNames = picks.map(p => p.querySelector('.co') ? p.querySelector('.co').textContent.trim() : '');
  const dupCo = coNames.filter((c, i) => coNames.indexOf(c) !== i);
  if (expCo > 0) assert('公司研究卡片数 = 公司数（' + expCo + '）', picks.length === expCo, picks.length);
  else skip('公司研究卡片数', '空壳版无种子数据');
  assert('公司研究无重复公司', dupCo.length === 0, dupCo.length ? dupCo.join('; ') : 'none');

  // 6. 公司研究页含「面试记录」与「竞争力/offer 概率」段
  if (picks.length) picks[0].click();
  const bodyTx = d.body.textContent;
  assert('公司研究页含「面试记录」段', /面试记录/.test(bodyTx));
  assert('公司研究页含「拿 offer 可能性」段', /offer|竞争力/.test(bodyTx));

  // 7. 交互：点行打开编辑弹窗
  const before = errors.length;
  const tTab = d.querySelector('.tab[data-tab="table"]');
  if (tTab) tTab.click();
  // 空数据时会渲染「暂无数据」占位行，只挑真正的数据行
  const firstRow = [...d.querySelectorAll('#tableWrap tbody tr')].find(tr => tr.querySelector('.co'));
  if (firstRow) firstRow.click();
  const dlgOpen = d.querySelector('#mask-detail') && d.querySelector('#mask-detail').classList.contains('open');
  if (firstRow) assert('点击岗位行打开编辑弹窗（open 接线正常）', dlgOpen && errors.length === before, dlgOpen ? 'dialog open' : 'no dialog');
  else skip('点击岗位行', '无数据行');

  // 8. 交互：推进按钮
  const before2 = errors.length;
  const nextBtn = d.querySelector('#tableWrap [data-cmd="next"]');
  if (nextBtn) { nextBtn.click(); assert('点击推进按钮（next 接线正常）', errors.length === before2, errors.length === before2 ? 'ok' : errors.slice(before2).join('|')); }
  else skip('点击推进按钮', '无数据行');

  // 9. 开源化功能入口
  assert('顶部含「导入资料」入口', !!d.querySelector('[data-cmd="upload"]'));
  assert('顶部含「AI 设置」入口', !!d.querySelector('[data-cmd="aiset"]'));
  assert('底部含「关于/隐私」入口', !!d.querySelector('[data-cmd="about"]'));

  console.log('=== 结果: ' + pass + ' 通过 / ' + fail + ' 失败 ===');
  if (errors.length) { console.log('--- 收集到的错误 ---'); errors.forEach(e => console.log('  ' + e)); }
  process.exit(fail === 0 && errors.length === 0 ? 0 : 1);
}, 400);
