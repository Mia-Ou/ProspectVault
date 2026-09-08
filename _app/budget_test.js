// 薪资卡片·月度预算可视化专项测试
// 跑法: NODE_PATH=C:/Users/H/.workbuddy/binaries/node/workspace/node_modules node _app/budget_test.js
const { JSDOM } = require('jsdom');
const fs = require('fs');

let pass = 0, fail = 0;
function assert(name, cond, got) {
  if (cond) { pass++; console.log('  \u2705 ' + name + (got !== undefined ? '  \u2192 ' + got : '')); }
  else { fail++; console.log('  \u274c ' + name + '  \u2192 ' + got); }
}

const html = fs.readFileSync('秋招工作台.html', 'utf8');
const dom = new JSDOM(html, { runScripts: 'dangerously', pretendToBeVisual: true });
const w = dom.window;

setTimeout(() => {
  const DATA = w.eval('DATA');
  const recs = DATA.records;
  console.log('=== 月度预算可视化测试 ===');

  // 1. 结构化预算覆盖率
  const withB = recs.filter(r => {
    const c = ((r.research || {}).report || {}).compensation || {};
    return c['月度预算'] && c['月度预算'].budget;
  });
  assert('每家公司都有结构化月度预算', withB.length === recs.length, withB.length + '/' + recs.length);

  // 注入 budgetHTML（函数在 IIFE 内，抽取源码）
  const src = fs.readFileSync('_app/template.html', 'utf8');
  const a = src.indexOf('function budgetHTML(obj)');
  const bEnd = src.indexOf('function sectionHTML(');
  w.eval('window.__bh = (' + src.slice(a, bEnd).replace(/^function budgetHTML\(obj\)/, 'function(obj)').replace(/\}\s*$/, '}') + ');');

  const render = i => {
    const host = w.document.createElement('div');
    host.innerHTML = w.window.__bh(w.eval('DATA.records[' + i + '].research.report.compensation["月度预算"]'));
    return host;
  };
  const idx = n => recs.findIndex(r => r.company.indexOf(n) >= 0);

  // 2. 每一家都能渲染出完整结构
  let bad = [];
  recs.forEach((r, i) => {
    const h = render(i);
    const ok = h.querySelector('.rb-kpis') && h.querySelectorAll('.rb-kpi').length === 3 &&
      h.querySelectorAll('.rb-seg').length >= 6 && h.querySelectorAll('.rb-row').length >= 6 &&
      h.querySelector('.rb-foot');
    if (!ok) bad.push(r.company);
  });
  assert('全部公司渲染出 3 KPI + 堆叠条 + 明细行', bad.length === 0, bad.join(';') || 'none');

  // 3. 口径：到手 = 税前 × (1-扣除率)，盈余 = 到手 - 支出
  let calErr = [];
  recs.forEach((r, i) => {
    const b = r.research.report.compensation['月度预算'].budget;
    const net = Math.round(b.grossMonthly * (1 - b.deductionRate) / 100) * 100;
    const exp = b.expenses.reduce((s, e) => s + e.amount, 0);
    if (Math.abs(net - b.netMonthly) > 200) calErr.push(r.company + ':net');
    if (Math.abs(exp - b.totalExpense) > 1) calErr.push(r.company + ':exp');
    if (Math.abs(b.netMonthly - b.totalExpense - b.surplus) > 1) calErr.push(r.company + ':sur');
  });
  assert('到手/支出/盈余三者自洽', calErr.length === 0, calErr.join(';') || 'ok');

  // 4. 正常场景（华安）：盈余为正，有绿色盈余段
  const h0 = render(idx('华安基金'));
  const kpi0 = [...h0.querySelectorAll('.rb-kpi-v')].map(x => x.textContent);
  assert('华安 KPI = 18,000 / 13,500 / 3,500',
    kpi0.join('|') === '¥18,000|¥13,500|¥3,500', kpi0.join(' | '));
  assert('华安年净储蓄 6.9 万（与原文一致）',
    /6\.9 \u4e07/.test(h0.querySelector('.rb-foot').textContent),
    (h0.querySelector('.rb-foot').textContent.match(/年净储蓄[^；]*/) || [''])[0]);
  assert('华安显示健康提示', !!h0.querySelector('.rb-ok'));

  // 5. 超支场景（原子创投）：到手线 + 红色预警
  const h1 = render(idx('原子创投'));
  assert('超支时显示「超支」段', /超支/.test(h1.textContent));
  assert('超支时显示到手刻度线', !!h1.querySelector('.rb-netline'),
    h1.querySelector('.rb-netline') ? h1.querySelector('.rb-netline').style.left : 'NONE');
  assert('超支时红色预警', !!h1.querySelector('.rb-warn'),
    (h1.querySelector('.rb-warn') || {}).textContent);

  // 6. 低盈余场景（中投中财）：预警阈值生效
  const h2 = render(idx('中投中财'));
  assert('盈余率 <10% 触发预警', !!h2.querySelector('.rb-warn'),
    (h2.querySelector('.rb-warn') || {}).textContent);

  // 7. 占比合计 ≈ 100%
  const pcts = [...h0.querySelectorAll('.rb-seg')].map(s => parseFloat(s.style.width));
  const sum = pcts.reduce((a, b) => a + b, 0);
  assert('堆叠条占比合计 ≈ 100%', Math.abs(sum - 100) < 0.5, sum.toFixed(2) + '%');

  // 8. 以到手而非年薪为基准
  assert('基准标注为到手月薪', /基准 = 到手/.test(h0.textContent));

  console.log('\n=== 结果: ' + pass + ' 通过 / ' + fail + ' 失败 ===');
  process.exit(fail ? 1 : 0);
}, 1500);
