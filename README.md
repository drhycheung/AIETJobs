# AIETJobs — 香港 AI × EdTech 应届岗位每日推送

为**香港教育大学 BSc(AI&EdTech) 应届毕业生**做的每日自动系统：抓取香港 AI / EdTech 相关岗位
→ 官方链接校验 → 生成静态网站 → 发布，供学生参考。

> 当前阶段（审查期）：**先不推送 GitHub Pages**，仅本地产出，并同步发布到 WorkBuddy 资料库
> （个人空间），供跨设备查看。确认无误后再建公开仓库、开推送。

---

## 合规声明（公开可辩护）

本项目是一个非商业、教育用途的公开信息聚合工具，服务于香港教育大学
BSc(AI&EdTech) 应届毕业生。我们：

- 仅直接抓取各大学官方招聘页与香港劳工处 jobs.gov.hk 等公开数据；
- **香港主流求职网站（JobsDB / CTgoodjobs / Recruit / CPjobs）已纳入白名单并启用发现**：
  岗位经搜索引擎公开索引「发现」帖子链接，不作 bot 直爬、不绕过任何验证；发现的链接以
  「求职板原帖」如实标注（区别于雇主官方原帖），且求职板深链有效期短，每日重新发现；
- 每日低频访问，遵守 `robots.txt`，使用可识别 User-Agent 并附联系邮箱；
- 仅发布岗位元数据与链接，不复制 JD 全文，不采集任何个人资料；
- 尊重版权与站点意愿，收到下架请求将立即处理。

如有疑问或下架请求，请联系：`jobs-bot@eduhk.hk`

---

## 数据来源白名单

- **香港各大学官方空缺页**（直抓）：HKU、CUHK、HKUST、PolyU、CityU、HKBU、Lingnan、EdUHK、HKSYU
- **香港劳工处**：`jobs.gov.hk`
- **商业求职板**（已启用发现，仅取链接，不直爬）：JobsDB、CTgoodjobs、Recruit、CPjobs

**排除**（聚合 / 抓取 / 博客站，永不采用）：hiringcafe、joblum、indeed、linkedin、
gradconnection、glassdoor、ziprecruiter 等（完整清单见 `scraper/config.py` 的 `EXCLUDED_DOMAINS`）。

---

## 运行

```bash
# 准备环境（首次）
python -m venv .venv && . .venv/bin/activate
pip install pypdf requests beautifulsoup4   # pypdf 用于校验 JD 中的学历/经验要求

# 每日运行（抓取→过滤→生成 JSON + HTML）
python -m scraper.run
```

产出：

- `site/jobs.json` — **GitHub Pages 直接读取的数据文件**（与学生页同目录，相对路径 `./jobs.json`；同时写入 `data/jobs.json` 作为工作副本）
- `site/index.html` — 静态岗位板（**多标签展示**、⭐ 契合度、**简短岗位简介**、双链接、防骗与合规板块；运行时 `fetch('./jobs.json')`，并内嵌当日备份数据供本地 `file://` 预览）
- `REPORT.md` — **开发者日志**（含当日过滤明细、待办与 Pages 部署说明）；学生页不含任何「已过滤/待复核」信息

> 学生页不再按固定五类分区，而是给每个岗位动态贴**标签**（方向：人工智能 / 教育科技 / 数据分析 / 多媒体 / 教学；角色：大学 / 业界 / 实习·培训生 / 应届友好），因此某方向暂时没有岗位时版面不会显得突兀。

---

## 架构

```
scraper/
  config.py       白名单 / 排除域 / 方向标签关键词 / UA / 合规阈值 / 部署开关
  fetch.py        强制 IPv4 + 可识别 UA + robots 解析 + is_live 链接校验
  live.py         官方页直抓适配器（EdUHK 已完整实现；其余大学框架占位）
  search_discovery.py  商业板搜索发现（WebSearch 落地 + 搜索 API 就绪；未配置 API 时读取 data/discovered.json，不编造）
  pipeline.py     去重 / 多标签 / ⭐ 评分 / 合规过滤（含 PDF 文本深度校验 + 简介抽取）/ 排序
  generate.py     生成 site/jobs.json + site/index.html + REPORT.md
  deploy.py       GitHub Pages 推送（PUSH_GITHUB 开关，审查期关闭）
  run.py          每日入口
```

---

## 启用 GitHub Pages（让 Pages 直接读取数据）

学生页 `site/index.html` 在加载时执行 `fetch('./jobs.json')`，因此把 **`site/` 目录**作为 Pages 源即可，无需构建步骤：

1. 创建公开仓库 `AIETJobs`（PascalCase）。
2. `Settings → Pages → Build from a branch`：选 `main` 分支、目录 **`/site`**。
3. 生成器已把同一份数据写入 `site/jobs.json`（与 `index.html` 同目录），Pages 上相对路径
   `./jobs.json` 即可命中；每次提交即更新页面数据。
4. 若用根目录发布（而非 `/site`），把 `site/` 内两文件移到仓库根亦可（相对路径不变）。
5. 建议改用 **GitHub Actions** 原生调度（每日 cron）运行 `python -m scraper.run` 并提交，
   与 Pages 同源、无需第三方调度器。

---

## 质量红线（过滤明细见 REPORT.md）

任何「疑似失效 / 无法确认 / 命中合规禁止」的岗位，宁可当日不推或标注「⚠️ 待复核」，
也不推死链、虚假帖或违规内容。当前运行：从 70 条原始抓取（EdUHK 67 + 商业板 3）中保留 9 条
（本科可投、AI/EdTech/数据/教学相关），其余因「需博士 / 资深经验 / 与方向无关」被自动过滤；
过滤明细仅写入 `REPORT.md`，不进入学生页。
