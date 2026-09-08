<p align="center">
  <img src="assets/logo.png" width="128" height="128" alt="ProspectVault logo">
</p>

<h1 align="center">ProspectVault · 把求职当 deal 做</h1>

<p align="center">
  <b>一个 HTML 文件管完秋招</b>　·　投了哪些、到哪一步、哪家有戏——全在这里<br>
  零安装 · 零注册 · 断网可用 · 数据 100% 留本机
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT"></a>
  <img src="https://img.shields.io/badge/version-2.0.84-green.svg" alt="version">
  <img src="https://img.shields.io/badge/single--file-239KB-orange.svg" alt="size">
  <img src="https://img.shields.io/badge/offline--ready-brightgreen.svg" alt="offline">
  <img src="https://img.shields.io/badge/AI-optional-9cf.svg" alt="ai optional">
</p>

---

## 名字的来历

**Prospect** = 勘探者（VC 视角下，每家公司、每个赛道都是一片矿）  
**Vault** = 宝库（你的判断、笔记、面试复盘都存在这里）

秋招不是答卷，是**一系列 deal**。每家公司都是一次下注——你要做的是把信息差打到最小，把决策成本压到最低。

---

## 为什么是 ProspectVault

| 其它求职追踪工具 | ProspectVault |
|---|---|
| 要注册账号、数据上云 | 浏览器本地存储，**不上传任何数据** |
| 套餐分级、付费解锁功能 | 全功能免费、**无任何收费** |
| 简历/面经经常被拿去训练模型 | 你的数据**不属于任何云端** |
| 闭源、想改一行都难 | 源码在 `_app/template.html`，**欢迎改、欢迎 PR** |
| 几百 MB 客户端 / 移动端 APP | **一个 239KB 的 HTML 文件**，双击即用 |

---

## 30 秒上手

```bash
1.  下载 index.html（仓库根目录那个，公开版，0 数据）
2.  双击打开
3.  左侧点 📤 导入资料 → 上传简历
4.  点 ＋ 新增岗位 → 粘贴 JD → 开干
```

不需要 Node、不需要 Python、不需要联网。

---

## 五个页面

| 页面 | 粒度 | 干什么 |
|---|---|---|
| **概览** | 全局 | KPI、到期提醒、快捷入口 |
| **投递总表** | 一岗一行 | 搜索、筛选、编辑、CSV 导出 |
| **流程看板** | 一岗一卡 | 按阶段看进度，拖拽推进 |
| **公司研究** | 一司一份 | 业务分析 + 面试记录 + 拿 offer 可能性 |
| **发现** | — | AI 推荐的高匹配岗位（可选） |

> 同一公司投了 3 个岗，总表里 3 行，研究页只 1 份。

---

## 拿 offer 可能性

每家公司带一个百分比和标签，**提前告诉你值不值得重点押**：

| 标签 | 概率 | 建议 |
|---|---|---|
| 🟢 有希望 | ≥40% | 重点投入，好好准备 |
| 🟡 冲一冲 | 20-39% | 可以投，但别只押这一家 |
| 🔴 困难 | <20% | 投了不亏，别抱期望 |

评估结合你的简历 + 公司行业地位 + 岗位匹配度。点进公司研究页能看到详细分析（你的优势、差距在哪）。

---

## AI（可选，零成本可启动）

**不配 AI 也能用全部功能**，只是「自动解析」和「竞争力评估」要手动填。

配了之后能偷懒：

- 上传简历 → 自动提取院校 / 实习 / 技能
- 粘贴 JD → 自动识别公司 / 岗位 / 城市 / 截止日期
- 粘贴面经 → 自动整理成结构化面试记录
- 自动算拿 offer 可能性

**怎么配**：左侧 🤖 AI → 选预设（**DeepSeek / Kimi** 便宜好用）→ 粘贴 API Key → 测试连接。

**隐私**：Key 只存本机浏览器 `localStorage`；AI 请求直接从你浏览器发到服务商，**没有中间人**。

> CORS 报错换 **硅基流动** 或 **智谱**，这两家对浏览器请求最友好。

---

## Bookmarklet：从招聘网站一键抓 JD

1. 打开工作台 → 📤 导入资料 → 招聘信息 tab
2. 蓝色区域里找到「📋 抓JD」按钮，**拖到浏览器书签栏**
3. 以后在任何招聘网站（Boss / 拉勾 / 猎聘 / 公司官网…）岗位页 → 点书签栏「📋 抓JD」→ JD 自动到剪贴板
4. 切回工作台 → Ctrl+V → 🤖 AI 智能解析

省掉选文字复制粘贴的几秒钟。

---

## 日常怎么用

**第一次打开**：导入简历 → 加几个目标岗位 → 完事。  
**每天打开**：看概览到期提醒 → 更新状态（网申/笔试/面试/Offer）→ 面试完在公司研究页写复盘。  
**一个岗投出去了**：总表里把它改成「已投递」。

---

## 数据安全

**数据存在浏览器里，清浏览器缓存 = 数据全没。** 定期点 ☁️ 同步备份：

| 操作 | 干嘛的 |
|---|---|
| 导出 JSON | 下载备份文件，存 U 盘 / 网盘 |
| 生成同步码 | 复制一段文字，粘到另一台电脑的同页面里恢复 |

**两个 HTML 文件的区别**：

| 文件 | 数据 | 用途 |
|---|---|---|
| `index.html` | 空的，0 条记录 | 分享、部署到网站 |
| `秋招工作台.html` | 含你的真实数据 | 自己本地用（文件名是历史遗留，构建脚本产出就是这个） |

> **别人用就发 `index.html`**，里面没有任何个人信息，**安全分享**。

---

## 进阶：本地服务器（可选）

如果你想要：

- 数据落盘（不怕清浏览器缓存）
- 跨设备同步

仓库里有个 `server.py`，运行它：

```bash
python _app/server.py
# 打开 http://localhost:8765
```

不需要可以不运行。

---

## 技术栈

- **零框架**纯 HTML + CSS + JavaScript（单文件 < 240KB）
- `pdf.js` / `JSZip` 解析 PDF / Word（jsdelivr CDN，失败降级为粘贴）
- 可选 OpenAI 兼容 AI（DeepSeek / Kimi / 智谱 / 硅基流动 / OpenAI / 自定义）
- 可选本地服务 `server.py`（Python 标准库，**零依赖**）

---

## 开发者

```bash
# 构建（需要先填 jobs.json，或留空产空白工作台）
python _app/build.py

# 从「净收入计算」文本生成结构化月度预算（薪资卡片可视化的数据源）
python _app/build_budget.py                    # → 读 jobs.json（个人数据）
python _app/build_budget.py jobs.example.json   # → 公开示例数据

# 跑测试
NODE_PATH=... node _app/smoke_test.js index.html
NODE_PATH=... node _app/oss_test.js
NODE_PATH=... node _app/budget_test.js
```

- 源码在 `_app/template.html`，改完跑 `build.py` 重新构建
- 数据格式见 [`jobs.example.json`](jobs.example.json)
- 改了数据结构记得 bump `dataGen` 并同步 `_app/template.html` 里的 `sampleData()`（公开版「载入示例数据」用的是它）
- 欢迎 Issue 和 PR，详见 [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 已知限制

- 扫描件 PDF（图片型）无法直接提取文字，需先 OCR
- `.doc` 旧格式不支持，另存为 `.docx`
- AI 评估仅供参考，模型可能编造细节，请自行判断
- 多设备不实时同步，靠手动备份搬运

---

## Roadmap（已规划）

- [ ] 移动端 PWA（离线安装到桌面）
- [ ] 浏览器扩展（直接在招聘网站标注「已投递」）
- [ ] 多用户轻协同（基于 Git 的 PR 式共享）

---

## License

[MIT](LICENSE) · 随便用、随便改、随便分发出处留个名就行。
