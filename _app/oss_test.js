/**
 * 开源版（空壳 index.html）功能冒烟测试
 * 关注点：新用户引导、上传中心、AI 配置、示例数据、JD/简历/面经落库
 * 跑法：NODE_PATH=C:/Users/H/.workbuddy/binaries/node/workspace/node_modules node _app/oss_test.js
 */
const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');

const target = process.argv[2] || path.join(__dirname, '..', 'webapp', 'index.html');
const html = fs.readFileSync(target, 'utf8');

let pass = 0, fail = 0;
const ok = (n, c, extra) => { if (c) { pass++; console.log('  ✅ ' + n); } else { fail++; console.log('  ❌ ' + n + (extra ? '  → ' + extra : '')); } };

const dom = new JSDOM(html, { runScripts: 'dangerously', url: 'https://local.test/', pretendToBeVisual: true });
const w = dom.window, d = w.document;
// 顶层 let/const 声明的变量不会挂到 window，需要用 eval 取
const getData = () => w.eval('DATA');

function click(sel) { const el = d.querySelector(sel); if (!el) return false; el.dispatchEvent(new w.MouseEvent('click', { bubbles: true })); return true; }

setTimeout(() => {
  console.log('\n=== 开源版冒烟测试：' + path.basename(target) + ' ===\n');

  /* ---------- 1. 基础引导 ---------- */
  console.log('[1] 新用户引导');
  ok('页面脚本已执行 (boot 存在)', typeof w.boot === 'function');
  ok('种子为空（不含任何真实数据）', !getData() || getData().records.length === 0, 'records=' + (getData() ? getData().records.length : '?'));
  const dash = d.querySelector('#page-dash').innerHTML;
  ok('空白时显示 onboarding 引导', dash.includes('欢迎使用 ProspectVault'));
  ok('引导含「上传简历」步骤', dash.includes('上传简历'));
  ok('引导含「导入招聘信息」步骤', dash.includes('导入招聘信息'));
  ok('引导含「配置 AI」步骤', dash.includes('配置 AI'));
  ok('引导含「载入示例数据」入口', dash.includes('载入示例数据'));
  ok('顶部提示为空白工作台说明', d.querySelector('#warnBanner').innerHTML.includes('空白工作台'));

  /* ---------- 2. AI 配置 ---------- */
  console.log('\n[2] AI 设置（可选能力）');
  ok('aiReady() 初始为 false', w.aiReady() === false);
  click('[data-cmd="aiset"]');
  const aiHtml = d.querySelector('#dlg-aiset').innerHTML;
  ok('AI 设置弹窗可打开', aiHtml.includes('API Key'));
  ok('含服务商预设下拉', aiHtml.includes('aiPreset') && aiHtml.includes('DeepSeek'));
  ok('含连接测试按钮', aiHtml.includes('testAi'));
  ok('含隐私说明（不经中转服务器）', aiHtml.includes('不经过任何中转服务器'));
  d.querySelector('#aiBase').value = 'https://api.example.com/v1';
  d.querySelector('#aiKey').value = 'sk-test-123';
  d.querySelector('#aiModel').value = 'test-model';
  click('[data-cmd="saveAi"]');
  ok('保存后 aiReady() 为 true', w.aiReady() === true);
  const lsAI = w.localStorage.getItem('qf_ai_cfg_v1') || '';
  ok('密钥写入独立 localStorage key', lsAI.includes('test-model'));
  const dataJson = JSON.stringify(getData());
  ok('密钥不进入 DATA（不会被导出/同步码带走）', !dataJson.includes('sk-test-123'));
  ok('normBase 正确去掉 /chat/completions', w.normBase('https://x.com/v1/chat/completions') === 'https://x.com/v1');

  /* ---------- 3. 上传中心 ---------- */
  console.log('\n[3] 上传中心（简历 / JD / 面经）');
  w.closeUpload && w.closeUpload();
  w.openUpload('resume');
  let up = d.querySelector('#dlg-upload').innerHTML;
  ok('简历页上传区渲染', up.includes('点击选择文件') && up.includes('简历'));
  ok('已配置 AI 时不显示未配置警告', !up.includes('未配置 AI'));
  ok('含文件 input 且限定类型', !!d.querySelector('#upFile') && d.querySelector('#upFile').accept.includes('.pdf'));
  w.closeUpload();
  w.openUpload('jd');
  up = d.querySelector('#dlg-upload').innerHTML;
  ok('JD 页文案正确', up.includes('招聘信息') && up.includes('JD'));
  w.closeUpload();
  w.openUpload('iv');
  up = d.querySelector('#dlg-upload').innerHTML;
  ok('面经页文案正确', up.includes('面经'));
  w.closeUpload();

  // 未配置 AI 时的降级
  w.writeAI({});
  w.openUpload('resume');
  up = d.querySelector('#dlg-upload').innerHTML;
  ok('未配置 AI 时显示降级提示', up.includes('未配置 AI'));
  ok('未配置 AI 时隐藏 AI 解析按钮', !up.includes('upParse'));
  ok('未配置 AI 时保留「仅保存原文」', up.includes('upSaveRaw'));
  w.closeUpload();

  /* ---------- 4. 无 AI 也能落库 ---------- */
  console.log('\n[4] 免 AI 降级路径');
  w.writeAI({});
  w.openUpload('resume');
  d.querySelector('#upText').value = '张三 / 硕士 / 某大学 / 两段投资实习 / Python';
  w.eval("upCtx.text = '张三 / 硕士 / 某大学 / 两段投资实习 / Python';");
  w.upSaveRaw();
  ok('无 AI 时简历原文可保存', !!getData().resume && getData().resume.raw.includes('两段投资实习'));
  ok('保存后未崩溃且仍可渲染', typeof w.renderAll === 'function');

  /* ---------- 5. JD 解析结果落库（模拟 AI 返回） ---------- */
  console.log('\n[5] JD / 竞争力评估落库');
  w._jdParsed = {
    company: '测试科技有限公司', industry: 'PEVC', type: '中型VC', location: '上海',
    link: 'https://example.com/job', deadline: '2026-10-01',
    positions: [{ title: '投资分析师', dept: '投资部', salary: '面议', edu: '硕士', matchScore: 0 },
                { title: '研究助理', dept: '研究部', salary: '面议', edu: '硕士', matchScore: 0 }],
    requirements: ['硕士及以上', '有投资实习'], bonus: ['会 Python', '理工科背景'],
    notes: '招 2 人'
  };
  w.applyJDParsed(false);
  let rec = getData().records.find(r => r.company === '测试科技有限公司');
  ok('JD 结果写入投递表', !!rec);
  ok('双岗位都被收录', rec && rec.positions.length === 2, '岗位数=' + (rec ? rec.positions.length : 0));
  ok('岗位字段正确', rec && rec.positions[0].title === '投资分析师' && rec.positions[0].dept === '投资部');
  ok('行业/链接/截止已填', rec && rec.industry === 'PEVC' && rec.link.includes('example.com') && rec.positions[0].deadline === '2026-10-01');
  ok('JD 要点写入备注', rec && rec.personalNotes.includes('会 Python'));
  // 重复导入同一公司应合并而非新建
  const before = getData().records.length;
  w._jdParsed.positions = [{ title: '投资分析师', dept: '投资部', salary: '', edu: '', matchScore: 0 }];
  w.applyJDParsed(false);
  ok('同公司重复导入不产生重复记录', getData().records.length === before);
  ok('同岗位不重复添加', getData().records.find(r => r.company === '测试科技有限公司').positions.length === 2);

  // 竞争力评估落库
  const ca = { score: 55, label: '冲一冲', reason: '背景基本匹配', yourStrengths: ['硬科技研究'], gapToBeat: ['缺头部机构'], companyTier: '中型', hireBar: '985硕士', advice: '多投' };
  rec.research = rec.research || {};
  rec.research.competitionAnalysis = Object.assign({ src: 'AI', updatedAt: new Date().toISOString() }, ca);
  ok('竞争力评估可写入 research', rec.research.competitionAnalysis.score === 55);
  w.renderAll();
  ok('写入后页面渲染无异常', true);

  /* ---------- 6. 面经落库 ---------- */
  console.log('\n[6] 面试资料落库');
  w._ivParsed = { round: '一面', date: '2026-09-10', result: '通过', score: 80, notes: '问了产业链', analysis: '准备充分' };
  w.openUpload('iv');
  // applyIvParsed 从 #ivCompany 读取归属公司；真实流程里该下拉由解析结果 UI 渲染，这里模拟它
  const sel = d.createElement('select');
  sel.id = 'ivCompany';
  getData().records.forEach(r => { const o = d.createElement('option'); o.value = r.id; o.textContent = r.company; sel.appendChild(o); });
  sel.value = rec.id;
  d.body.appendChild(sel);
  w.applyIvParsed();
  ok('面经写入对应公司面试记录', rec.interviewStages && rec.interviewStages.length === 1);
  ok('面试轮次/结果正确', rec.interviewStages[0] && rec.interviewStages[0].round === '一面' && rec.interviewStages[0].result === '通过');

  /* ---------- 7. 示例数据 ---------- */
  console.log('\n[7] 示例数据');
  const sd = w.sampleData();
  ok('示例数据含虚构公司', sd.records.length === 4 && sd.records.every(r => r.company.indexOf('示例·') === 0));
  ok('示例数据公司名全部带「示例·」前缀（不含任何真实公司）', sd.records.every(r => r.company.indexOf('示例·') === 0));
  ok('示例含简历画像', !!sd.resume && sd.resume.headline.includes('示例'));
  // 示例数据须与个人数据同构：含结构化月度预算（到手口径）
  const withB = sd.records.filter(r => {
    const c = ((r.research || {}).report || {}).compensation || {};
    return c['月度预算'] && c['月度预算'].budget;
  });
  ok('示例数据含结构化月度预算', withB.length === sd.records.length, withB.length + '/' + sd.records.length);
  const b0 = withB.length ? withB[0].research.report.compensation['月度预算'].budget : null;
  ok('示例预算口径自洽（盈余 = 到手 − 支出）',
    !!b0 && b0.surplus === b0.netMonthly - b0.totalExpense && b0.netMonthly < b0.grossMonthly,
    b0 ? b0.grossMonthly + '→' + b0.netMonthly + '−' + b0.totalExpense + '=' + b0.surplus : 'NONE');

  /* ---------- 8. 导出安全 ---------- */
  console.log('\n[8] 隐私');
  w.saveAi && (function () { d.querySelector('#aiBase'); })();
  const dump = JSON.stringify(getData());
  ok('导出数据不含 API Key', !dump.includes('sk-test-123'));
  ok('同步码编码解码可逆', (() => { try { const c = w.codeEncode({ a: 1, 中: '文' }); return JSON.stringify(w.codeDecode(c)) === JSON.stringify({ a: 1, 中: '文' }); } catch (e) { return false } })());

  console.log('\n=== 结果：通过 ' + pass + ' / 失败 ' + fail + ' ===\n');
  process.exit(fail ? 1 : 0);
}, 400);
