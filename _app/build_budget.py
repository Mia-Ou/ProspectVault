# -*- coding: utf-8 -*-
"""
从 research.report.compensation['净收入计算'] 文本中解析出结构化「月度预算」，
写入 compensation['月度预算'] = {text, src, budget:{...}}

口径说明（重要）：
- 到手月薪 = 税前月薪 × (1 - 社保公积金及个税综合扣除率)
- 月盈余 = 到手月薪 - 月支出（房租 + 生活费细项）
- 年净储蓄 = 月盈余 × 12 + 到手月薪 × (发薪月数 - 12)   # 年终奖税后计入储蓄
  自检：示例·某基金 18k×14薪，扣25% → 到手13.5k；租6k+生活4k → 月盈余3.5k
       年净储蓄 = 3.5k×12 + 13.5k×2 = 4.2万 + 2.7万 = 6.9万  ✓ 与原文本一致
"""
import json, re, shutil, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

JOBS = 'jobs.json'

# 生活费细项拆分比例（按城市典型消费结构估算，合计 100%）
LIVING_SPLIT = [
    ('餐饮', 0.55),
    ('交通通勤', 0.12),
    ('通讯网络', 0.05),
    ('社交娱乐', 0.18),
    ('日常购物', 0.10),
]

CITY_TIER = {
    '上海': 1, '北京': 1, '深圳': 1, '广州': 1,
    '杭州': 2, '成都': 2, '厦门': 2, '武汉': 2, '苏州': 2, '南京': 2, '徐州': 2, '昆明': 2,
}

# 城市默认月房租（合租，元）——仅在文本未给出租房数字时兜底
CITY_RENT = {
    '上海': 6500, '北京': 8000, '深圳': 7000, '广州': 5500,
    '杭州': 4000, '成都': 3000, '厦门': 2500, '武汉': 3000,
    '苏州': 3500, '南京': 3500, '徐州': 2000, '昆明': 2200,
}


def num(s):
    try:
        return float(str(s).replace(',', ''))
    except Exception:
        return None


def detect_city(blob, location, company):
    """城市优先从薪资文本里『XX租房』提取（比岗位 location 更贴近实际工作地）"""
    m = re.search(r'([一-龥]{2,4})\s*/?\s*[一-龥]{0,4}\s*租房', blob)
    if m:
        c = m.group(1)
        if c in CITY_RENT:
            return c
    m = re.search(r'([一-龥]{2,4})\s*生活成本', blob)
    if m and m.group(1) in CITY_RENT:
        return m.group(1)
    for c in CITY_RENT:
        if c in (location or ''):
            return c
    return (location or '—')[:6].strip() or '—'


def parse_compensation(comp, company, location):
    """返回 budget dict 或 None"""
    src_obj = comp.get('净收入计算') or {}
    text = src_obj.get('text', '') if isinstance(src_obj, dict) else str(src_obj or '')
    struct = comp.get('薪资结构', {})
    stext = struct.get('text', '') if isinstance(struct, dict) else str(struct or '')
    blob = text + '\n' + stext

    # ---------- 1. 发薪月数（先算，供年包折算月薪使用） ----------
    months = 12
    m = re.search(r'×\s*(\d+)\s*薪', blob)
    if m:
        months = int(m.group(1))
    elif re.search(r'(\d+)\s*薪', blob):
        months = int(re.search(r'(\d+)\s*薪', blob).group(1))

    # ---------- 2. 税前月薪 ----------
    gross = None
    # 最优先：整段以年包举例，如「以50万/年为例」
    m = re.search(r'以\s*([\d.]+)\s*万\s*/\s*年', text)
    if m:
        gross = round(num(m.group(1)) * 10000 / months / 1000, 1)
    # 次优先「以 Xk/月为例」
    if not gross:
        m = re.search(r'以\s*([\d.]+)\s*k\s*/\s*月', text)
        if m:
            gross = num(m.group(1))
    if not gross:
        m = re.search(r'(?:月薪|底薪)\s*([\d.]+)\s*k', blob)
        if m:
            gross = num(m.group(1))
    if not gross:
        m = re.search(r'([\d.]+)\s*k\s*/\s*月\s*×\s*(\d+)\s*薪', blob)
        if m:
            gross = num(m.group(1))
    if not gross:
        # Base: 10-12k/月 → 取中值
        m = re.search(r'(?:Base|base)[：: ]*\s*([\d.]+)\s*-\s*([\d.]+)\s*k\s*/\s*月', blob)
        if m:
            gross = (num(m.group(1)) + num(m.group(2))) / 2
    if not gross:
        # 只有年包/总包：X-Y万/年 → 取中值按月数折算
        m = re.search(r'(?:年包|总包|年薪)[^\d]{0,6}([\d.]+)\s*-\s*([\d.]+)\s*万', blob)
        if m:
            annual = (num(m.group(1)) + num(m.group(2))) / 2
            gross = round(annual * 10000 / months / 1000, 1)
        else:
            m = re.search(r'(?:年包|总包|年薪)[^\d]{0,6}([\d.]+)\s*万', blob)
            if m:
                gross = round(num(m.group(1)) * 10000 / months / 1000, 1)
    if not gross:
        return None
    gross = int(round(gross * 1000))

    # ---------- 3. 综合扣除率 ----------
    # 首选：用文本中已算好的「净到手约 X 万/年」反推，最可靠
    rate = None
    m = re.search(r'净到手约\s*([\d.]+)\s*万', text)
    if m and gross:
        net_annual = num(m.group(1)) * 10000
        gross_annual = gross * months
        if gross_annual > 0:
            r = 1 - net_annual / gross_annual
            if 0.03 < r < 0.6:
                rate = round(r, 3)
    if rate is None:
        # 次选：社保与个税分列相加，如「社保公积金（约15%）+个税（约10%）」
        parts = re.findall(r'(\d+)\s*%', text)
        if len(parts) >= 2:
            rate = (num(parts[0]) + num(parts[1])) / 100
        elif len(parts) == 1:
            rate = num(parts[0]) / 100
    if rate is None or rate <= 0 or rate >= 0.6:
        rate = 0.22
    rate = round(rate, 3)

    net_monthly = int(round(gross * (1 - rate) / 100) * 100)

    # ---------- 4. 房租 ----------
    rent = None
    m = re.search(r'租房[（(]?[^）)]*[）)]?[：: ]\s*([\d,.]+)\s*k\s*/\s*月', text)
    if not m:
        m = re.search(r'房租[（(]?[^）)]*[）)]?[：: ]\s*([\d,.]+)\s*k', text)
    if not m:
        m = re.search(r'租房[（(]?[^）)]*[）)]?[：: ]\s*([\d,.]+)\s*k', text)
    if not m:
        # 「成都租房约2-4k/月」这类在生活成本里
        m = re.search(r'租房约\s*([\d.]+)\s*-\s*([\d.]+)\s*k', blob)
        if m:
            rent = (num(m.group(1)) + num(m.group(2))) / 2
    if m and rent is None:
        rent = num(m.group(1))
    if rent is None:
        # 「上海租房约5-8k/月（合租）」在性价比里
        m = re.search(r'租房约\s*([\d.]+)\s*[kK]', blob)
        if m:
            rent = num(m.group(1))
    city_pre = detect_city(blob, location, company)
    if rent is None:
        rent = CITY_RENT.get(city_pre)
        if rent:
            rent = rent / 1000
    if rent is None:
        return None
    rent = int(round(rent * 1000))

    # ---------- 5. 生活费 ----------
    living = None
    m = re.search(r'生活费[（(]?[^）)]*[）)]?[：: ]\s*([\d,.]+)\s*k', text)
    if m:
        living = num(m.group(1))
    if living is None:
        m = re.search(r'生活费[（(]?[^：:]*[）)]?[：: ]\s*([\d,.]+)\s*k', text)
        if m:
            living = num(m.group(1))
    if living is None:
        living = round(rent * 0.6 / 1000, 1)  # 兜底：房租的 60%（k 单位）
    living = int(round(living * 1000))

    # ---------- 6. 城市 ----------
    city = city_pre

    # ---------- 6.5 福利可折算节省（如食堂/宿舍/补充医疗） ----------
    welfare = 0
    m = re.search(r'福利节省[^\d]{0,14}([\d.]+)\s*-\s*([\d.]+)\s*万', text)
    if m:
        welfare = (num(m.group(1)) + num(m.group(2))) / 2 * 10000
    else:
        m = re.search(r'福利节省[^\d]{0,14}([\d.]+)\s*万', text)
        if m:
            welfare = num(m.group(1)) * 10000
    welfare = int(round(welfare))

    return assemble(city, gross, months, rate, net_monthly, rent, living, welfare)


def assemble(city, gross, months, rate, net_monthly, rent, living, welfare=0):
    """按统一口径组装 budget 字典（元）"""
    gross = int(round(gross))
    rent = int(round(rent))
    living = int(round(living))
    net_monthly = int(round(net_monthly / 100) * 100)
    expenses = [{'name': '房租（合租）', 'amount': rent, 'kind': 'fixed'}]
    acc = 0
    for i, (nm, p) in enumerate(LIVING_SPLIT):
        if i == len(LIVING_SPLIT) - 1:
            amt = living - acc
        else:
            amt = int(round(living * p / 100) * 100)
            acc += amt
        expenses.append({'name': nm, 'amount': amt, 'kind': 'living'})
    total_exp = sum(e['amount'] for e in expenses)
    surplus = net_monthly - total_exp
    annual_surplus = surplus * 12 + net_monthly * max(0, months - 12) + int(round(welfare or 0))
    return {
        'city': city,
        'grossMonthly': gross,
        'months': months,
        'deductionRate': round(rate, 3),
        'netMonthly': net_monthly,
        'welfareAnnual': int(round(welfare or 0)),
        'expenses': expenses,
        'totalExpense': total_exp,
        'surplus': surplus,
        'annualSurplus': annual_surplus,
        'surplusRate': round(surplus / net_monthly * 100, 1) if net_monthly else 0,
        'expenseRate': round(total_exp / net_monthly * 100, 1) if net_monthly else 0,
        'livingEstimated': True,  # 生活费细项为按城市典型结构估算
    }


def parse_arrow(comp, company, location):
    """解析箭头式简写（示例数据/手写录入常用）：
    「月薪13,000 → 到手约10,200 → 房租-4,000 → 通勤餐饮-2,000 → 剩余约4,200元/月」
    """
    src_obj = comp.get('净收入计算') or {}
    text = src_obj.get('text', '') if isinstance(src_obj, dict) else str(src_obj or '')
    struct = comp.get('薪资结构', {})
    stext = struct.get('text', '') if isinstance(struct, dict) else str(struct or '')
    blob = text + '\n' + stext
    if '\u2192' not in text and '->' not in text:
        return None

    g = re.search(r'月薪\s*([\d,]+)', text) or re.search(r'月薪\s*([\d,]+)', blob)
    n = re.search(r'到手\s*约?\s*([\d,]+)', text)
    if not (g and n):
        return None
    gross = num(g.group(1))
    net = num(n.group(1))
    if not gross or not net or net >= gross:
        return None

    rent = None
    m = re.search(r'房租\s*[-\u2212]?\s*([\d,]+)', text)
    if m:
        rent = num(m.group(1))
    living = None
    m = re.search(r'(?:通勤餐饮|生活费|生活|日常开支)\s*[-\u2212]?\s*([\d,]+)', text)
    if m:
        living = num(m.group(1))

    city = detect_city(blob, location, company)
    if rent is None:
        rent = CITY_RENT.get(city) or CITY_RENT['上海']
    if living is None:
        living = round(rent * 0.6)
    # 若文本有「房租-4,000 / 通勤餐饮-2,000」但单位被写成 k，统一折算
    if re.search(r'房租\s*[-\u2212]?\s*[\d,.]+\s*k', text) and rent and rent < 100:
        rent *= 1000
    if re.search(r'(?:通勤餐饮|生活费|生活)\s*[-\u2212]?\s*[\d,.]+\s*k', text) and living and living < 100:
        living *= 1000

    # 发薪月数：×12-14薪 → 取中值
    months = 12
    m = re.search(r'\u00d7\s*(\d+)\s*-\s*(\d+)\s*薪', blob)
    if m:
        months = int((int(m.group(1)) + int(m.group(2))) / 2)
    else:
        m = re.search(r'\u00d7\s*(\d+)\s*薪', blob)
        if m:
            months = int(m.group(1))
        elif re.search(r'(\d+)\s*薪', blob):
            months = int(re.search(r'(\d+)\s*薪', blob).group(1))

    rate = round(1 - net / gross, 3)
    return assemble(city, gross, months, rate, net, rent, living, 0)


def main(path=None):
    target = path or JOBS
    shutil.copy(target, target + '.bak-budget')
    d = json.load(open(target, encoding='utf-8'))
    ok, skip = [], []
    for r in d['records']:
        res = r.setdefault('research', {}).setdefault('report', {})
        comp = res.get('compensation') or {}
        if not comp:
            skip.append(r['company'])
            continue
        b = parse_arrow(comp, r.get('company', ''), r.get('location', '')) \
            or parse_compensation(comp, r.get('company', ''), r.get('location', ''))
        if not b:
            skip.append(r['company'])
            continue
        src = ''
        s = comp.get('净收入计算')
        if isinstance(s, dict):
            src = s.get('src', '')
        note = '以{city}为基准：到手月薪 {net:,} 元 − 月支出 {exp:,} 元 = 月盈余 {sur:,} 元（占到手 {sr}%）'
        if b.get('welfareAnnual'):
            note += '；另有食堂/宿舍等福利折算约 {w:,.0f} 万/年'.format(w=b['welfareAnnual'] / 10000)
        note += '。'
        comp['月度预算'] = {
            'text': note.format(city=b['city'], net=b['netMonthly'], exp=b['totalExpense'],
                                sur=b['surplus'], sr=int(round(b['surplusRate']))),
            'src': src or '推断（基于薪资测算+城市生活成本）',
            'budget': b,
        }
        res['compensation'] = comp
        ok.append((r['company'], b['city'], b['grossMonthly'], b['netMonthly'],
                   b['totalExpense'], b['surplus'], round(b['annualSurplus'] / 10000, 1)))
    json.dump(d, open(target, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('写入 %s' % target)
    print('OK %d / SKIP %d' % (len(ok), len(skip)))
    print('%-28s %-6s %8s %8s %8s %8s %8s' % ('公司', '城市', '税前', '到手', '支出', '月盈余', '年储蓄万'))
    for row in ok:
        print('%-28s %-6s %8d %8d %8d %8d %8.1f' % row)
    if skip:
        print('SKIP:', '、'.join(skip))


if __name__ == '__main__':
    # 用法: python _app/build_budget.py                    → jobs.json（个人数据）
    #       python _app/build_budget.py jobs.example.json  → 开源示例数据
    main(sys.argv[1] if len(sys.argv) > 1 else None)
