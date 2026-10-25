# AGENTS.md —— 香港 AI×EdTech 每日岗位推送系统（交接 / 从零重建指南）

> 本文档是**自包含的交接说明书**。如果你是一个新接手的智能体，读完本文件即可在不依赖历史对话的前提下，从零把整套系统重建出来。
> 当前状态：已有一个**可运行的 MVP** 与一次**创建但未验证稳定的定时任务**。用户决定**从零重做**，本文件供新智能体参考与重建（现有代码可参考，也可丢弃）。

---

## 0. 一句话目标

为**香港教育大学 BSc(AI&EdTech) 应届毕业生**做一个**每日自动**系统：抓取香港 AI / EdTech 相关岗位 → 官方链接校验 → 生成**静态网站** → 发布到 **GitHub Pages**，供学生参考。

- 仓库名（已确认）：**`AIETJobs`**（PascalCase，公开仓库，用于 GitHub Pages）
- 目标读者：仅**本科毕业应届生**，拒绝需要经验 / 执照 / 硕士的岗位
- 发布物：GitHub 上**只放静态站点**，不存任何个人隐私数据

---

## 1. 硬性约束（必须严格遵守，不可妥协）

### 1.1 目标人群
- **只收「本科可投 / Fresh graduate welcome / 经验为加分非必需」** 的岗位。
- 程序化过滤掉：要求 X 年经验、要求专业执照、要求硕士及以上学历、已截止、链接失效、非香港、非白名单来源。

### 1.2 信息来源白名单（两类，其余一律排除）
**✅ 允许：**
| 类别 | 站点 |
|---|---|
| 香港主流求职网站 | `jobs.gov.hk`（劳工处官方）、JobsDB、CTgoodjobs、Recruit、CPjobs |
| 香港所有大学空缺页 | HKU、CUHK、HKUST、PolyU、CityU、HKBU、Lingnan、EdUHK、HKSYU 等官方招聘系统 |

**🚫 明确排除（聚合 / 抓取 / 博客站，永不采用）：**
```
hiringcafe.com, joblum.com, careers.sh, bebee.com, hkese.net, offertoday.com,
thebigjobsite.com, postjobfree.com, indeed.com, linkedin.com, gradconnection.com,
jobfinder.com, hirelala.com, sigma.ai, imerit.com, glassdoor.com, ziprecruiter.com
```
> 规则：即便在上述站点看到心仪岗位，也只当线索，回雇主官网 / 官方 ATS 复核后才收录。

### 1.3 核心铁律：发现靠白名单，验证靠官方
- 岗位**必须从**「香港主流求职网站」或「香港各大学空缺页」**发现**。
- 推送给学生的**最终链接必须是公司 / 学校官方原帖**（官方招聘系统 / 官方校网），用来验证岗位是否**仍然存在**。
- **不长期依赖会失效的求职板深链**（实测 JobsDB 链接约 30 天下架；jobs.gov.hk 详情页用会话令牌，深链易跳错 / 失效）。商业板岗位应**每日重新发现**，官方链接作校验锚点。

### 1.4 五类岗位方向（分类与关键词体系）
| # | 方向 | 典型岗位 | 检索关键词（中/英，覆盖粤语写法） |
|---|---|---|---|
| ① | **大学里的 AI/EdTech** | RA、学习技术开发者、教育发展主任、多媒体开发 | `Research Assistant AI education` / `Learning Technology` / `Educational Development` / `Multimedia Developer` |
| ② | **业界人工智能与教育科技** | EdTech 公司 AI 开发、教育产品工程师 | `EdTech developer` / `AI education` / `教育科技` / `AI 教學` |
| ③ | **单纯人工智能** | AI/ML 工程师、数据科学培训生、算法岗 | `AI Engineer` / `Machine Learning` / `Data Science Graduate Trainee` / `NLP GenAI` |
| ④ | **当老师 / 在学校推 AI** | AI 教学助理、STEM/IT 教师、学校 ETO、**PGDE 路径** | `AI 教學助理` / `STEM Instructor` / `IT Teacher` / `Education Technology Officer` / `PGDE` |
| ⑤ | **数据分析 / 数据处理 / 数据标注** | 数据分析师、数据处理主任、数据标注员 | `Data Analyst fresh graduate` / `Data Processing` / `Data Annotation 數據標註` / `語音轉錄標註` |

> 关键词同时用**中文 + 英文 + 粤语常见写法**（如「數據標註」「教學助理」「教學」），覆盖本地招聘用语。

### 1.5 契合度优先
- 按 EdUHK BSc(AI&EdTech) 能力画像评分 **⭐（1–3 星）**：ML/NLP/CV、智能导学、学习技术、EdTech、Python、教育实习背景优先；大学 / 同领域岗优先。
- 加分词：`ai, artificial intelligence, machine learning, nlp, computer vision, education, educational, edtech, learning, teaching, stem, python, multimedia, data, language, smart`。

---

## 2. 合规与伦理红线（公开仓库的生死线，绝不能碰）

仓库**公开**，任何做法必须「可公开辩护」：

1. **绝不绕过人机验证（CAPTCHA）**：商业板只经搜索引擎公开索引「发现」并给出链接，**不写脚本撞它的验证**。
2. **绝不规避 IP 封禁**：**不启用代理 / IP 轮换**绕封禁；靠低频 + 限速 + 可识别 UA 自然避免被拦。
3. **遵守 `robots.txt` 与各站《服务条款》**：抓取前解析，命中禁止路径即跳过。
4. **可识别访问身份**：固定 UA 并附联系邮箱，透明可联系。示例：
   ```
   EdUHK-AIEdTech-JobBot/1.0 (+https://github.com/<owner>/AIETJobs; contact: jobs-bot@example.com)
   ```
5. **低频、低负载**：每日一次、单站请求极少、请求间随机间隔；不给服务器造成可感知负担。
6. **版权**：发布**仅元数据 + 链接**（岗位名 / 雇主 / 地点 / 学历 / 经验 / 截止日），**不整段复制 JD 正文**。
7. **不采集任何个人资料**（recruiter 联系方式、申请人数据等 PDPO 意义上的个人信息），仅处理公开招聘信息。
8. **opt-out**：README 留联系邮箱；任何站点所有者来函要求下架，立即排除该来源并删除相关数据。
9. **质量红线**：任何「疑似失效 / 无法确认 / 命中合规禁止」的岗位，**宁可当日不推或标注 ⚠️ 待复核**，也不推死链、虚假帖或违规内容。

### 公开公示的 README 合规声明（建议原文保留）
```
本项目是一个非商业、教育用途的公开信息聚合工具，服务于香港教育大学
BSc(AI&EdTech) 应届毕业生。我们：
- 仅直接抓取各大学官方招聘页与香港劳工处 jobs.gov.hk 等公开数据；
- 商业求职板岗位经搜索引擎公开索引发现，仅提供链接，不作 bot 直爬、不绕过任何验证；
- 每日低频访问，遵守 robots.txt，使用可识别 User-Agent 并附联系邮箱；
- 仅发布岗位元数据与链接，不复制 JD 全文，不采集任何个人资料；
- 尊重版权与站点意愿，收到下架请求将立即处理。
如有疑问或下架请求，请联系：<email>
```

---

## 3. 推荐技术架构（两种调度方案，见 §6 取舍）

```
[1 发现] 大学官方空缺页 + jobs.gov.hk：直接抓取（低频、合规）
         商业求职板：经搜索引擎索引「发现」→ 帖子 URL（不直爬、不绕验证）
   ↓
[2 解析] 提取字段（标题/雇主/地点/学历/经验/AI属性/发布日/截止日/原始链接）
   ↓
[3 官方校验] 每雇主去官网 / 官方 ATS 找官方原帖 → 确认岗位是否仍存在
           找不到 → 官网主页 + 官方邮箱，标注「无自托管原帖」
   ↓
[4 合规过滤] 剔除：需经验/执照/硕士、已截止、链接失效、非香港、非白名单、robots 禁止、个人资料类
   ↓
[5 排序] 按契合度评 ⭐，大学 / 同领域岗优先；去重
   ↓
[6 生成] Markdown（源）+ HTML（GitHub Pages 模板，仅元数据 + 链接）
   ↓
[7 发布] 推送 GitHub Pages（gh-pages 分支）
   ↓
[8 日志] 记录失效链接、当日新剔除项、校验失败项 → 复盘调优
```

**技术选型建议**
- 语言：**Python 3.11**
- 官方页抓取：`requests`（**强制 IPv4**，见 §5 坑）+ `BeautifulSoup`
- JS 渲染兜底：Playwright **仅用于「渲染官方页」**，**绝不用于绕过 CAPTCHA**
- 搜索发现：搜索 API（Google Programmable Search 免费额度 / Bing / SerpAPI）或免费搜索引擎 HTML（见坑：沙箱内搜索引擎直连常超时）
- 合规：`urllib.robotparser` 解析 robots + 可识别 UA + 单站限速
- 存储：`jobs.json`（当日）+ `archive/`（历史归档，便于趋势与去重）
- 模板：Jinja2 渲染 HTML
- 发布：git push → `gh-pages` → GitHub Pages

**数据模型（每条岗位字段）**
```
title, employer, category(①–⑤), category_name, location,
degree, experience, ai_edtech_fit(⭐×1-3), fit_reason,
discover_source, official_link, official_type,
posted_date, deadline, verified_date, status(active|expired|unknown), notes
```
> 以 **JSON** 为中间存储，再渲染 Markdown 与 HTML。**发布内容仅含上表元数据与链接，不嵌入 JD 全文。**

---

## 4. 现有 MVP（参考实现，可保留或丢弃）

沙箱内已有一个能跑通的实现，文件位于 `/workspace`：

```
scraper/
  config.py        # 白名单、排除域、大学官方页、五类关键词、UA、PUSH_GITHUB 开关
  fetch.py         # fetch_url(强制IPv4+代理兜底) / search_discover(搜索发现，仅留商业板链接)
  pipeline.py      # run(queries, seeds) → 去重 + 评分 + 过滤
  live.py          # collect() 真实抓取大学官方页（PolyU/HKBU/CUHK/HKUST/EdUHK）
  verify.py        # is_live(url) 存活检查
  generate.py      # 生成 site/index.html + data/jobs.json + data/daily-report.md
  deploy.py        # push() 受 PUSH_GITHUB + GH_TOKEN 网关（审查期不触发）
  run.py           # 入口：pipeline.run → generate → 视开关 deploy
  seeds.json       # 6 条预核实真实岗位（兜底）
site/index.html    # 生成的静态站
data/jobs.json     # 当日数据
README.md          # 合规声明 + 部署指南
design-methodology-architecture.md  # 方法论与架构（V2 合规版，必读）
verification-report.md              # 调度可执行 + 真实数据可取的验证记录
```

> MVP 实测：手动运行 `python3.11 run.py` 可生成 7 条岗位（其中 4 条来自真实大学官方空缺页），并在「审查期」正确停在**不推送 GitHub**。

---

## 5. 踩坑清单 / 经验教训（重建时务必避免）

1. **聚合站 / 错链**：BYTEWISE 的 jobs.gov.hk 令牌链跳到了按摩广告；HKUST Interfolio 链接已失效；`ph.jobstreet.com` 是菲律宾版（非香港）——**最终链接一律换成雇主 / 学校的官方原帖**。
2. **沙箱 Python 直连**：Python 能直连 `jobs.gov.hk`、`cuhk.taleo.net`、`polyu`、`hkust`（200），但**大学站点 IPv6 直连易失败 → 强制 IPv4**（`requests` 适配器 `family=socket.AF_INET`，或 `curl -4`）。
3. **搜索发现超时**：DuckDuckGo / Bing HTML 在沙箱内经常 3+ 分钟挂起 → 用**短超时 + 快速失败**，绝不重试拖垮每日任务。
4. **live_collect 返回 0**：网络抖动 + 异常被吞掉导致静默失败 → 加日志、显式异常、重试退避。
5. **坏标题**：JS 渲染页抓到 "Description" / "Breadcrumb" 等导航文本 → 加 `_JOB_WORDS` 关键词过滤；JS 页回退到**预核实的 TARGET 标题**。
6. **GitHub 鉴权**：沙箱内对 github.com 的 **POST 超时**（GET 可用），device-code OAuth 不可用 → GitHub 写操作交由**云端运行时 / 用户提供的 PAT（repo 权限）** 处理，不要在沙箱内硬跑 OAuth。
7. **JobsDB 30 天失效**：求职板深链不能长期存，必须**每日重新发现**，官方链接作锚点。
8. **部分中小企 EdTech 无自托管原帖**（如 eClass、Popular e-Learning、BYTEWISE）：官网只有品牌页 → 只能给「官网主页 + 官方邮箱」并**如实标注**。
9. **质量优先于覆盖率**：放弃直爬 / 绕验证后，商业板覆盖率低于全量直爬——这是合规换来的取舍，可接受（大学页与 jobs.gov.hk 仍稳定直抓兜底）。

---

## 6. 调度方案取舍（本次重建的关键决策点）

原方法论推荐 **GitHub Actions**（每日 cron 触发脚本 + 部署 gh-pages），理由是沙箱 / 本地无法「永远在线」，而 Actions 提供免费稳定的每日算力。

> ⚠️ **本次遗留问题（需新智能体决策）**：曾用 **WorkBuddy 云端定时任务**（任务 ID `13622729`，Cron `0 0 8 * * *` Asia/Shanghai，每天 08:00 HKT，审查期不推送 GitHub）做了一次创建，但用户反馈「那边好像有问题」。该任务可能不稳定或未经验证。
> **建议**：新智能体优先评估回到 **GitHub Actions** 原生调度（更可控、与 GitHub Pages 同源、无需额外 PAT 注入到第三方调度器），或在确认 WorkBuddy 调度确实可用后再用。无论哪种，**审查期都先不推送 GitHub，让用户观察几天再开 `PUSH_GITHUB=1`**。

### 部署到 GitHub 的步骤（待用户提供 PAT 后执行）
1. 创建公开仓库 **`AIETJobs`**（用户习惯：每字大写开头，无连字符）。
2. 配置部署凭证：`GH_TOKEN`（repo 权限）、`GH_OWNER`（用户名）、`PUSH_GITHUB=1`。
3. 推送静态站到 `gh-pages`（或 main + Pages 指向 `/site` / `docs`），启用 GitHub Pages。
4. 在 README 公示合规声明（见 §2）。

---

## 7. 待完成清单（交给下一位智能体）

- [ ] 决策调度方案：GitHub Actions（推荐）还是修复 WorkBuddy 定时任务。
- [ ] 重建 / 完善抓取器（大学适配器 9+ 校 + jobs.gov.hk，合规直抓）。
- [ ] 重建搜索发现模块（调用搜索 API 搜商业板帖 URL，不直爬、不绕验证）。
- [ ] 官方链接解析与存活检查（404 / Expired 检测）。
- [ ] 合规过滤 + ⭐ 评分 + 排序 + 去重。
- [ ] GitHub Pages 模板（五类分区、⭐、双链接、防骗与合规板块）。
- [ ] `.github/workflows/daily.yml`（若选 Actions）：每日 cron 发现 + 校验 + 部署。
- [ ] 端到端跑通一次，输出当天报告，确认官方页抓取 / 搜索发现 / 校验可行。
- [ ] **审查期**：先不推送，让用户观察几天；确认无误后再建仓库 + 开推送。
- [ ] 提供「部署到你自己的 GitHub 仓库」操作说明 + README 合规声明模板。

### 防骗保障（写入页面固定板块）
- 红旗：先交费 / 押金、索身份证或银行资料、私人邮箱联系、薪酬明显偏离市场。
- 二次核查：香港网络安全防骗视伏器 https://cyberdefender.hk/scameter/
- 页面明示白名单、排除清单与合规声明，接受监督。

---

## 8. 已知待确认 / 占位项

| 项 | 当前值 | 说明 |
|---|---|---|
| 联系邮箱 | `jobs-bot@example.com` | **占位**，部署前替换为真实可联系邮箱 |
| 仓库 URL | `https://github.com/example/AIETJobs` | **占位**，替换为真实 owner |
| `GH_OWNER` | 空 | 建好仓库后填入，或用环境变量注入 |
| `GH_TOKEN` | 不进仓库 | 仅部署阶段配置（repo 权限） |
| `PUSH_GITHUB` | 默认 `0`（关） | 审查期关闭；确认后设 `1` |

> ⚠️ 任何含密钥（GH_TOKEN）的配置都**不得进入公开仓库**，只能通过环境变量 / Secrets 注入。
