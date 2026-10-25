# AIETJobs 运行报告（开发者视角）· 2026-10-25

> 本文件仅供维护者查看（含过滤明细）。学生页 `site/index.html` 不含任何「已过滤/待复核」信息。

- 目标人群：EdUHK BSc(AI&EdTech) 应届毕业生
- 原始抓取：64 条
- **学生页展示（active）：9 条**
- 自动过滤 / 待复核：55 条

## ✅ 当日向学生展示的岗位

- ⭐3 **Research Assistant II** — The Education University of Hong Kong (EdUHK) · Centre for Learning, Teaching and Technology · 标签：大学、应届友好 · 截止 03 Nov 2026 · [EdUHK official vacancies](https://eduhk.hk/cms/f/career/35042/RAII_LTTC_2600894.pdf)
- ⭐3 **Educational Development Officer** — The Education University of Hong Kong (EdUHK) · Artificial Intelligence and Digital Competency Education Centre · 标签：人工智能、大学、应届友好 · 截止 27 Oct 2026 · [EdUHK official vacancies](https://eduhk.hk/cms/f/career/35044/EDO_AIDCEC_2600925.pdf)
- ⭐2 **Multimedia Developer** — The Education University of Hong Kong (EdUHK) · Faculty of Education and Human Development · 标签：多媒体、大学、应届友好 · 截止 04 Nov 2026 · [EdUHK official vacancies](https://eduhk.hk/cms/f/career/35050/PO_ProjA_FEHD_2600928.pdf)
- ⭐2 **Teaching Assistant** — The Education University of Hong Kong (EdUHK) · Department of Curriculum and Instruction · 标签：教学、大学、应届友好 · 截止 29 Oct 2026 · [EdUHK official vacancies](https://eduhk.hk/cms/f/career/35022/TAsst_C%26I_2600918.pdf)
- ⭐1 **Research Assistant I/II (Part-time)** — The Education University of Hong Kong (EdUHK) · Department of Social Sciences and Policy Studies · 标签：大学、实习／培训生、应届友好 · 截止 06 Nov 2026 · [EdUHK official vacancies](https://eduhk.hk/cms/f/career/35073/RAI_RAII_SSPS_2600932.pdf)
- ⭐1 **Java Developer** — FDM Group HK Limited · 标签：业界、应届友好 · 截止 N/A · [Recruit（求职板发现）](http://recruit.com.hk/jobseeker/JobDetail.aspx?jobOrder=L060421659)
- ⭐1 **Analyst Programmer** — Society of Rehabilitation and Crime Prevention, HK (SRACP) · Wan Chai · 标签：人工智能、业界、应届友好 · 截止 N/A · [Recruit（求职板发现）](http://recruit.com.hk/jobseeker/JobDetail.aspx?jobOrder=L059335869)
- ⭐1 **Project Consultant Trainee (Web Solution)** — TOGO Pacific Limited · Kwun Tong · 标签：人工智能、业界、实习／培训生、应届友好 · 截止 N/A · [Recruit（求职板发现）](http://recruit.com.hk/job-detail/togo-pacific-limited/project-consultant-trainee-web-solution/L0601125520)
- ⭐1 **IT Intern (Programming) (Part-time)** — The Education University of Hong Kong (EdUHK) · Office of the Chief Information Officer · 标签：大学、实习／培训生、应届友好 · 截止 N/A · [EdUHK official vacancies](https://eduhk.hk/cms/f/career/32500/SH_OCIO_2501246.pdf)

## 🚫 自动过滤原因分布（不向学生展示，仅供维护）

- 36 条：与 AI/EdTech/数据/教学五类方向无关键词关联
- 13 条：学术/教职岗（通常需博士）「professor」
- 4 条：学术/教职岗（通常需博士）「head of」
- 1 条：标题含资深/经验信号「manager」
- 1 条：标题含资深/经验信号「senior」

## ⚠️ 待办 / 注意

- 商业求职板（JobsDB / CTgoodjobs / Recruit / CPjobs）深链有效期约 30 天，每日重新发现；当前依赖 `data/discovered.json` 人工落地（未配置搜索 API）。接入搜索 API 后可全自动。
- 其余 7 所大学（HKU / CUHK / HKUST / PolyU / CityU / HKBU / Lingnan）ATS 在沙箱内多为 JS 壳/证书/网关问题，尚未接入；`live.py` 已留框架，接入后每日扩大覆盖。
- 链接均经 `is_live` 存活校验；校验失败者置为 `expired` 不向学生展示。

## 🚀 GitHub Pages 部署（让 Pages 直接读取数据）

学生页 `site/index.html` 在加载时会 `fetch('./jobs.json')`：
1. 将本仓库的 **`site/` 目录**作为 Pages 源（`Settings → Pages → Build from a branch` 选 `main` 与目录 `/site`）。
2. 生成器已把同一份数据同时写入 `site/jobs.json` 与 `site/index.html`（同目录），因此 Pages 上 `index.html` 能直接相对读取 `./jobs.json`，每次提交即更新。
3. 若用根目录发布，把 `site/` 内两文件移到仓库根亦可（相对路径不变）。
4. 本地 `file://` 预览无法 fetch，已内嵌备份数据，故本地打开也能看到当日岗位。

## 运行

```bash
python -m scraper.run   # 抓取→过滤→生成 site/ 与 REPORT.md
```
（须用含 pypdf 的 venv python：PDF 简介抽取依赖它。）