#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
秋招工作台 V2 构建脚本（开源版）
- 输入: _app/template.html  (应用模板) + jobs.json (个人数据源, 可选, 不入 git)
- 状态: _app/state.json     (记录每条记录的哈希与 updatedAt, 保证只把"真正改动"的记录标记为新版, 不覆盖用户本地编辑)
- 产出:
   1) index.html            公开版(空数据, 任何人可直接双击打开 / 部署到 GitHub Pages)
   2) webapp/index.html     同上, 保留在 webapp 目录便于部署
   3) 秋招工作台.html        个人完整版(含 jobs.json 的全部数据, 已 gitignore)
用法: python _app/build.py
说明: 没有 jobs.json 也能构建 —— 会产出空白工作台, 数据由使用者在自己的浏览器里录入。
"""
import json, hashlib, os, sys, datetime, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP  = os.path.join(ROOT, "_app")
TPL  = os.path.join(APP, "template.html")
JOBS = os.path.join(ROOT, "jobs.json")
STATE= os.path.join(APP, "state.json")
OUT_FULL  = os.path.join(ROOT, "秋招工作台.html")
OUT_SHELL = os.path.join(ROOT, "webapp", "index.html")
OUT_ROOT  = os.path.join(ROOT, "index.html")

def now_iso():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")

def sha(obj):
    s = json.dumps(obj, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]

def strip_updated(obj):
    """去掉 updatedAt 后计算哈希, 避免自己动自己"""
    if isinstance(obj, dict):
        return {k: strip_updated(v) for k, v in obj.items() if k != "updatedAt"}
    if isinstance(obj, list):
        return [strip_updated(x) for x in obj]
    return obj

def main():
    with open(TPL, encoding="utf-8") as f:
        template = f.read()
    if "__SEED_JSON__" not in template:
        sys.exit("[错误] 模板缺少 __SEED_JSON__ 占位符")

    # jobs.json 是个人数据（已 gitignore）。缺失时构建空白工作台，保证任何人 clone 后都能跑
    if os.path.exists(JOBS):
        with open(JOBS, encoding="utf-8") as f:
            jobs = json.load(f)
        has_personal = True
    else:
        jobs = {"metadata": {"created": now_iso(), "dataGen": "empty"},
                "records": [], "resume": None, "discoveredJobs": []}
        has_personal = False

    # 载入状态
    state = {"build": 0, "records": {}, "resume": None}
    if os.path.exists(STATE):
        try:
            with open(STATE, encoding="utf-8") as f:
                state = json.load(f)
        except Exception:
            pass
    build_no = int(state.get("build", 0)) + 1

    records = []
    for rec in jobs.get("records", []):
        rec = dict(rec)
        rec.setdefault("id", "job_%s" % (hashlib.sha1(json.dumps(rec, ensure_ascii=False, default=str).encode()).hexdigest()[:10],))
        h = sha(strip_updated(rec))
        old = state["records"].get(rec["id"], {})
        if old.get("h") == h and old.get("u"):
            rec["updatedAt"] = old["u"]          # 未改动: 沿用旧时间, 不覆盖用户编辑
        else:
            rec["updatedAt"] = now_iso()          # 新增或改动: 标记为新时间
        state["records"][rec["id"]] = {"h": h, "u": rec["updatedAt"]}
        records.append(rec)

    resume = jobs.get("resume")
    if resume:
        resume = dict(resume)
        rh = sha(strip_updated(resume))
        if state.get("resume") and state["resume"].get("h") == rh and state["resume"].get("u"):
            resume["updatedAt"] = state["resume"]["u"]
        else:
            resume["updatedAt"] = now_iso()
        state["resume"] = {"h": rh, "u": resume["updatedAt"]}
    state["build"] = build_no
    state["builtAt"] = now_iso()

    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    meta_full = {
        "version": "2.0.%d" % build_no,
        "builtAt": now_iso(),
        "created": jobs.get("metadata", {}).get("created", ""),
        "dataGen": jobs.get("metadata", {}).get("dataGen", ""),
        "description": "秋招工作台本地完整版(内置种子数据)",
        "mode": "full",
        "seedCount": len(records),
    }
    meta_shell = {
        "version": "2.0.%d" % build_no,
        "builtAt": now_iso(),
        "created": jobs.get("metadata", {}).get("created", ""),
        "dataGen": jobs.get("metadata", {}).get("dataGen", ""),
        "description": "秋招工作台在线空壳版(为隐私不含数据, 请导入同步码/备份)",
        "mode": "shell",
        "seedCount": 0,
    }

    def esc_json(obj):
        s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
        return s.replace("</", "<\\/").replace("<!--", "<\\!--")

    discovered_jobs = jobs.get("discoveredJobs", [])

    full_payload = {"metadata": meta_full, "records": records, "resume": resume, "deletedIds": [], "discoveredJobs": discovered_jobs}
    shell_payload = {"metadata": meta_shell, "records": [], "resume": None, "deletedIds": [], "discoveredJobs": []}

    def render(payload):
        return template.replace("__SEED_JSON__", esc_json(payload))

    full_html = render(full_payload)
    shell_html = render(shell_payload)

    os.makedirs(os.path.dirname(OUT_SHELL), exist_ok=True)
    with open(OUT_FULL, "w", encoding="utf-8") as f:
        f.write(full_html)
    with open(OUT_SHELL, "w", encoding="utf-8") as f:
        f.write(shell_html)
    shutil.copyfile(OUT_SHELL, OUT_ROOT)

    print("构建完成 v2.0.%d" % build_no)
    print("  jobs.json 记录数 :", len(records), "(无 jobs.json 时为 0，空白工作台)" if not has_personal else "")
    print("  公开版 index.html :", OUT_ROOT, "%.1f KB" % (os.path.getsize(OUT_ROOT) / 1024))
    print("  公开版 webapp/    :", OUT_SHELL, "%.1f KB" % (os.path.getsize(OUT_SHELL) / 1024))
    print("  个人完整版        :", OUT_FULL, "%.1f KB" % (os.path.getsize(OUT_FULL) / 1024))
    print("  状态已保存        :", STATE)

if __name__ == "__main__":
    main()
