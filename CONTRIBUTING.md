# 贡献指南

感谢你想让这个工具变得更好。

## 最重要的一条：不要提交个人数据

本仓库是公开的。以下内容**已经在 `.gitignore` 中，请勿强制提交**：

- `jobs.json` / `jobs.json.bak*` —— 真实投递记录
- `秋招工作台.html` —— 内嵌了真实数据的构建产物
- `resume_extracted.txt` / `秋招投递跟踪表.xlsx` —— 简历原文
- `requests/` / `responses/` —— 研究请求与结果

提交前请自查（下面两条命令都不该输出个人文件）：

```bash
git status --short                                    # 不应出现 jobs.json / 秋招工作台.html 等
git check-ignore -v jobs.json 秋招工作台.html          # 应显示命中的忽略规则
```

## 改代码前的约定

1. **只改 `_app/template.html`**，不要直接改根目录的 `index.html` 或 `秋招工作台.html` —— 它们是构建产物，下次构建会被覆盖。
2. 改完执行 `python _app/build.py` 重新生成产物。
3. 跑一遍测试：
   ```bash
   node _app/smoke_test.js 秋招工作台.html
   node _app/oss_test.js
   ```
4. 保持**零外部依赖**：所有代码内联在单个 HTML 里。需要第三方库（如 pdf.js、JSZip）时，用 CDN 动态加载并做好失败降级。

## 数据结构的注意事项

- **记录以「公司」为单位**：同公司多岗位放进 `positions[]`，不要拆成多条记录。
- **列表字段必须是真数组**：`interviewStages`、`positions` 等不能写成 JSON 字符串，否则前端 `.some()` 会报错。
- **结构性变更要 bump `dataGen`**：改主键、合并/拆分记录、大改字段时，同步更新 `jobs.json` 的 `metadata.dataGen`，让浏览器能识别并重置过期数据。

## 视图粒度不要搞混

- **岗位级**（一行一岗）：投递总表、流程看板、概览统计
- **公司级**（一司一研究）：公司研究页，面试记录也在这里，**没有独立的面试 tab**

## 提交信息

用简洁的中文或英文描述，例如：

```
fix: 修复未配置 AI 时上传中心按钮报错
feat: JD 解析支持一次识别多个岗位
docs: 补充 AI 配置的 CORS 说明
```

## 提问

提 Issue 时请附上：浏览器版本、控制台报错截图、复现步骤。**不要粘贴含个人信息的 JSON。**
