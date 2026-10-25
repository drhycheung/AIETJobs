"""
generate.py — 生成 data/jobs.json（工作副本）、site/jobs.json（GitHub Pages 直接读取）、
site/index.html（学生页，含标签筛选、内嵌备份数据 + 运行时 fetch ./jobs.json），
以及 REPORT.md（开发者日志，含过滤明细与 Pages 部署说明）。

HTML 仅含岗位元数据 + 官方链接 + 简短简介，不复制 JD 全文；不含任何「已过滤/待复核」信息
（该信息仅写入 REPORT.md，供维护者查看）。
"""
from __future__ import annotations

import os
import sys
import json
import datetime
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
SITE_DIR = os.path.join(ROOT, "site")
TODAY = datetime.date.today().isoformat()


def _clean(v):
    return v if v not in (None, "", "N/A") else None


def build_records(jobs: list[dict]) -> list[dict]:
    recs = []
    for j in jobs:
        recs.append({
            "title": j.get("title"),
            "employer": j.get("employer"),
            "department": j.get("department"),
            "category": j.get("category"),
            "category_name": j.get("category_name"),
            "location": j.get("location"),
            "degree": j.get("degree"),
            "experience": j.get("experience"),
            "ai_edtech_fit": j.get("ai_edtech_fit"),
            "fit_reason": j.get("fit_reason"),
            "tags": j.get("tags") or [],
            "description": j.get("description") or "",
            "discover_source": j.get("discover_source"),
            "official_link": j.get("official_link"),
            "official_type": j.get("official_type"),
            "posted_date": _clean(j.get("posted_date")),
            "deadline": _clean(j.get("deadline")),
            "verified_date": j.get("verified_date"),
            "status": j.get("status"),
            "compliance_note": j.get("compliance_note"),
            "excluded_reason": j.get("excluded_reason"),
            "notes": j.get("notes"),
        })
    return recs


def write_json(jobs: list[dict]):
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(SITE_DIR, exist_ok=True)
    # data/jobs.json：完整工作副本（含所有状态，便于排错）
    full_payload = {
        "generated_at": TODAY,
        "target_audience": "EdUHK BSc(AI&EdTech) 应届毕业生",
        "total_listed": sum(1 for j in jobs if j.get("status") == "active"),
        "jobs": build_records(jobs),
    }
    p1 = os.path.join(DATA_DIR, "jobs.json")
    with open(p1, "w", encoding="utf-8") as f:
        json.dump(full_payload, f, ensure_ascii=False, indent=2)
    # site/jobs.json：GitHub Pages 直接读取的公开副本（仅 active，与学生页同目录 ./jobs.json）
    active_jobs = [j for j in jobs if j.get("status") == "active"]
    site_payload = {
        "generated_at": TODAY,
        "target_audience": "EdUHK BSc(AI&EdTech) 应届毕业生",
        "total_listed": len(active_jobs),
        "jobs": build_records(active_jobs),
    }
    p2 = os.path.join(SITE_DIR, "jobs.json")
    with open(p2, "w", encoding="utf-8") as f:
        json.dump(site_payload, f, ensure_ascii=False, indent=2)
    print(f"[generate] 写入 {p1} 与 {p2}")
    return full_payload


def _stars(n: int) -> str:
    n = max(0, min(3, int(n or 0)))
    return "★" * n + "☆" * (3 - n)


def _esc(s):
    if s is None:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _board_home(link: str) -> str:
    from urllib.parse import urlparse
    netloc = urlparse(link or "").netloc or "recruit.com.hk"
    return f"https://{netloc}/" if not netloc.startswith("http") else netloc


def render_html(jobs: list[dict]) -> str:
    records = build_records(jobs)
    active = [r for r in records if r.get("status") == "active"]
    active_json = json.dumps(active, ensure_ascii=False).replace("</", "<\\/")

    wl = "、".join(config.UNIVERSITY_SOURCES.values()) + "、香港劳工处 jobs.gov.hk"
    excl = "、".join(sorted(config.EXCLUDED_DOMAINS))

    html = f"""<!DOCTYPE html>
<html lang="zh-HK">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>香港 AI×EdTech 应届岗 · EdUHK BSc(AI&EdTech)</title>
<style>
  :root {{
    --bg:#f6f8fb; --card:#ffffff; --ink:#1f2933; --muted:#5b6b7b;
    --brand:#0b6bcb; --brand2:#0a4f9c; --line:#e2e8f0; --warn:#b45309; --ok:#15803d;
  }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"PingFang HK","Microsoft YaHei",sans-serif;
         background:var(--bg); color:var(--ink); line-height:1.6; }}
  header {{ background:linear-gradient(135deg,var(--brand),var(--brand2)); color:#fff; padding:32px 20px; }}
  .wrap {{ max-width:1040px; margin:0 auto; }}
  header h1 {{ margin:0 0 6px; font-size:1.7rem; }}
  header p {{ margin:4px 0; opacity:.95; }}
  main {{ max-width:1040px; margin:0 auto; padding:24px 20px 60px; }}
  .sub {{ color:var(--muted); font-size:.9rem; margin:0 0 14px; }}
  .notice {{ background:#eaf2fc; border:1px solid #cfe2fb; color:#0a4f9c; padding:12px 16px; border-radius:10px; font-size:.9rem; margin:18px 0; }}
  .filter {{ display:flex; gap:8px; flex-wrap:wrap; margin:16px 0 20px; }}
  .fbtn {{ background:#fff; border:1px solid var(--line); color:var(--brand2); padding:6px 14px; border-radius:999px; cursor:pointer; font-size:.85rem; }}
  .fbtn.active {{ background:var(--brand); color:#fff; border-color:var(--brand); }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(300px,1fr)); gap:14px; }}
  .card {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:16px; box-shadow:0 1px 2px rgba(16,24,40,.04); }}
  .card-head {{ display:flex; justify-content:space-between; align-items:flex-start; gap:8px; }}
  .card-head h3 {{ margin:0; font-size:1.02rem; }}
  .fit {{ color:#f59e0b; font-size:1.05rem; white-space:nowrap; }}
  .src {{ display:inline-block; background:#eef2f7; color:var(--brand2); border:1px solid #d6e2f0;
         border-radius:999px; padding:1px 8px; font-size:.72rem; margin-top:2px; }}
  .meta {{ display:flex; flex-direction:column; gap:2px; margin:8px 0; font-size:.85rem; color:var(--muted); }}
  .tags {{ display:flex; gap:6px; flex-wrap:wrap; margin:8px 0; }}
  .tag {{ background:#e8f1fb; color:var(--brand2); border:1px solid #cfe2fb; border-radius:6px; padding:2px 8px; font-size:.75rem; }}
  .desc {{ font-size:.85rem; color:var(--ink); background:#f8fafc; border-left:3px solid var(--brand); padding:6px 10px; border-radius:0 8px 8px 0; margin:8px 0; }}
  .links {{ display:flex; gap:8px; flex-wrap:wrap; margin-top:6px; }}
  .btn {{ text-decoration:none; font-size:.85rem; padding:7px 12px; border-radius:8px; }}
  .btn.primary {{ background:var(--brand); color:#fff; }}
  .btn.ghost {{ background:#eef2f7; color:var(--brand2); border:1px solid #d6e2f0; }}
  .empty {{ color:var(--muted); grid-column:1/-1; text-align:center; padding:30px; }}
  .panel {{ background:var(--card); border:1px solid var(--line); border-radius:14px; padding:18px; margin:24px 0; }}
  .panel h2 {{ margin-top:0; }}
  .redflags li {{ color:var(--warn); }}
  footer {{ text-align:center; color:var(--muted); font-size:.8rem; padding:24px; }}
  code {{ background:#eef2f7; padding:1px 5px; border-radius:4px; }}
</style>
</head>
<body>
<header>
  <div class="wrap">
    <h1>香港 AI × EdTech 应届岗位推送</h1>
    <p>面向：香港教育大学 <b>BSc(AI&amp;EdTech)</b> 应届毕业生 · 仅收「本科可投 / Fresh graduate welcome」</p>
    <p>更新日期：{TODAY} · 数据经官方链接存活校验</p>
  </div>
</header>
<main>
  <p class="sub">当前可投岗位：<b id="count">{len(active)}</b> 个 · 来源：大学官方招聘页 + 香港主流求职网站（JobsDB / CTgoodjobs / Recruit / CPjobs）</p>

  <div class="notice">
    ⚠️ 本页仅汇总公开招聘<b>元数据、标签与简短简介</b>，不复制职位描述全文。请点击链接核对最新要求、截止日期与申请方式。
    链接分两类，均经存活校验：<b>「官方原帖」</b>指向雇主 / 学校官方页面；<b>「求职板原帖」</b>来自香港主流求职网站
    经搜索引擎公开索引发现，其深链有效期较短，请尽快申请并回官方确认。
  </div>

  <div class="filter" id="filter"><!-- 标签筛选按钮由脚本生成 --></div>

  <div class="grid" id="grid"><!-- 岗位卡片由脚本生成 --></div>

  <section class="panel">
    <h2>🛡️ 防骗提示（求职红旗）</h2>
    <ul class="redflags">
      <li>要求先交费 / 押金、购买产品才能入职</li>
      <li>索取身份证、银行户口或密码等敏感资料</li>
      <li>仅以私人邮箱（如 Gmail / 126）联系，无公司域名</li>
      <li>薪酬明显偏离市场行情（过高或过低）</li>
    </ul>
    <p>二次核查：香港网络安全防骗视伏器 <a href="https://cyberdefender.hk/scameter/" target="_blank" rel="noopener">Scameter ↗</a></p>
  </section>

  <section class="panel">
    <h2>📋 数据来源与合规</h2>
    <p><b>允许来源（白名单）：</b>{wl}。</p>
    <p><b>排除来源：</b>{excl} 等聚合 / 抓取 / 博客站（仅当线索，回官方复核后才收录）。</p>
    <p>本项目为非商业、教育用途的公开信息聚合工具：仅直接抓取各大学官方招聘页与香港劳工处等公开数据；
    商业求职板经搜索引擎公开索引发现、仅提供链接、不作 bot 直爬、不绕过任何验证；每日低频访问、遵守
    <code>robots.txt</code>、使用可识别 User-Agent 并附联系邮箱；仅发布岗位元数据、标签与简短简介，不复制 JD 全文，
    不采集任何个人资料。如有疑问或下架请求，请联系 <code>{config.CONTACT_EMAIL}</code>。</p>
  </section>
</main>
<footer>
  由 EdUHK-AIEdTech-JobBot 生成 · {TODAY} · 仅供参考，最终以雇主 / 学校官方信息为准
</footer>

<script>
const FALLBACK = {active_json};
function esc(s){{ return String(s==null?'':s).replace(/[&<>"]/g, c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c])); }}
function stars(n){{ n=+n||0; return '★'.repeat(n)+'☆'.repeat(3-n); }}
function boardHome(link){{ try{{ return 'https://'+new URL(link).hostname+'/'; }}catch(e){{ return 'https://recruit.com.hk/'; }} }}
function cardHTML(j){{
  const tags=(j.tags||[]).map(t=>'<span class="tag">'+esc(t)+'</span>').join('');
  const isOff=j.official_type==='employer_official';
  const pLabel=isOff?'官方原帖 ↗':'求职板原帖 ↗';
  const gLabel=isOff?'大学空缺总页 ↗':'求职板总页 ↗';
  const gHref=isOff?'https://eduhk.hk/en/current-openings':boardHome(j.official_link);
  const src='<span class="src">'+esc(j.discover_source||'')+'</span>';
  const desc=j.description?'<p class="desc">'+esc(j.description)+'</p>':'';
  const dl=j.deadline||'N/A（持续招聘）';
  const dept=j.department?'<span>📂 '+esc(j.department)+'</span>':'';
  return '<article class="card" data-tags="'+((j.tags||[]).map(esc).join(' '))+'">'
    +'<div class="card-head"><h3>'+esc(j.title)+'</h3><span class="fit" title="契合度">'+stars(j.ai_edtech_fit)+'</span></div>'
    +'<div class="meta"><span>🏛️ '+esc(j.employer)+'</span>'+dept+'<span>📍 '+esc(j.location||'')+'</span><span>⏰ 截止：'+esc(dl)+'</span>'+src+'</div>'
    +'<div class="tags">'+tags+'</div>'+desc
    +'<div class="links"><a class="btn primary" href="'+esc(j.official_link)+'" target="_blank" rel="noopener">'+pLabel+'</a>'
    +'<a class="btn ghost" href="'+esc(gHref)+'" target="_blank" rel="noopener">'+gLabel+'</a></div>'
    +'</article>';
}}
let ACTIVE=[]; let FILTER=new Set();
function allTags(list){{ const s=new Set(); list.forEach(j=>(j.tags||[]).forEach(t=>s.add(t))); return [...s].sort(); }}
function renderFilter(list){{
  const tags=allTags(list);
  let html='<button class="fbtn active" data-t="">全部</button>';
  tags.forEach(t=>{{ html+='<button class="fbtn" data-t="'+esc(t)+'">'+esc(t)+'</button>'; }});
  const box=document.getElementById('filter'); box.innerHTML=html;
  box.querySelectorAll('.fbtn').forEach(b=>b.onclick=()=>{{
    const t=b.getAttribute('data-t');
    FILTER=new Set(t?[t]:[]);
    box.querySelectorAll('.fbtn').forEach(x=>x.classList.toggle('active', x.getAttribute('data-t')===t));
    renderGrid();
  }});
}}
function renderGrid(){{
  const list=ACTIVE.filter(j=>FILTER.size===0||(j.tags||[]).some(t=>FILTER.has(t)));
  document.getElementById('grid').innerHTML = list.map(cardHTML).join('') || '<p class="empty">该标签下暂时没有岗位。</p>';
  document.getElementById('count').textContent=list.length;
}}
function render(list){{
  ACTIVE=list.slice().sort((a,b)=>((+b.ai_edtech_fit||0)-(+a.ai_edtech_fit||0)) || ((a.deadline||'9')<(b.deadline||'9')?-1:1));
  renderFilter(ACTIVE); renderGrid();
}}
render(FALLBACK);
fetch('./jobs.json').then(r=>r.ok?r.json():Promise.reject()).then(d=>{{
  render((d.jobs||[]).filter(j=>j.status==='active'));
}}).catch(()=>{{ /* 静态预览无服务器时用内嵌备份数据 */ }});
</script>
</body>
</html>"""
    return html


def write_html(jobs: list[dict]):
    os.makedirs(SITE_DIR, exist_ok=True)
    html = render_html(jobs)
    path = os.path.join(SITE_DIR, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[generate] 写入 {path}")
    return path


def write_report(jobs: list[dict]):
    """生成开发者日志 REPORT.md（含过滤明细与 Pages 部署说明）。"""
    records = build_records(jobs)
    active = [r for r in records if r.get("status") == "active"]
    excluded = [r for r in records if r.get("status") != "active"]
    lines = []
    lines.append(f"# AIETJobs 运行报告（开发者视角）· {TODAY}\n")
    lines.append("> 本文件仅供维护者查看（含过滤明细）。学生页 `site/index.html` 不含任何「已过滤/待复核」信息。\n")
    lines.append(f"- 目标人群：EdUHK BSc(AI&EdTech) 应届毕业生")
    lines.append(f"- 原始抓取：{len(records)} 条")
    lines.append(f"- **学生页展示（active）：{len(active)} 条**")
    lines.append(f"- 自动过滤 / 待复核：{len(excluded)} 条\n")

    lines.append("## ✅ 当日向学生展示的岗位\n")
    for j in active:
        tags = "、".join(j.get("tags") or [])
        lines.append(f"- ⭐{j['ai_edtech_fit']} **{j['title']}** — {j['employer']}"
                     + (f" · {j['department']}" if j.get("department") else "")
                     + f" · 标签：{tags}"
                     + f" · 截止 {j.get('deadline') or 'N/A'} · [{j['discover_source']}]({j['official_link']})")
    lines.append("")

    lines.append("## 🚫 自动过滤原因分布（不向学生展示，仅供维护）\n")
    c = Counter(j.get("excluded_reason", "") for j in excluded)
    if c:
        for reason, n in c.most_common():
            lines.append(f"- {n} 条：{reason}")
    else:
        lines.append("- 无（当日全部通过）")
    lines.append("")

    lines.append("## ⚠️ 待办 / 注意\n")
    lines.append("- 商业求职板（JobsDB / CTgoodjobs / Recruit / CPjobs）深链有效期约 30 天，每日重新发现；"
                 "当前依赖 `data/discovered.json` 人工落地（未配置搜索 API）。接入搜索 API 后可全自动。")
    lines.append("- 其余 7 所大学（HKU / CUHK / HKUST / PolyU / CityU / HKBU / Lingnan）ATS 在沙箱内多为 JS 壳/证书/网关问题，"
                 "尚未接入；`live.py` 已留框架，接入后每日扩大覆盖。")
    lines.append("- 链接均经 `is_live` 存活校验；校验失败者置为 `expired` 不向学生展示。")
    lines.append("")

    lines.append("## 🚀 GitHub Pages 部署（让 Pages 直接读取数据）\n")
    lines.append("学生页 `site/index.html` 在加载时会 `fetch('./jobs.json')`：")
    lines.append("1. 将本仓库的 **`site/` 目录**作为 Pages 源（`Settings → Pages → Build from a branch` 选 `main` 与目录 `/site`）。")
    lines.append("2. 生成器已把同一份数据同时写入 `site/jobs.json` 与 `site/index.html`（同目录），"
                 "因此 Pages 上 `index.html` 能直接相对读取 `./jobs.json`，每次提交即更新。")
    lines.append("3. 若用根目录发布，把 `site/` 内两文件移到仓库根亦可（相对路径不变）。")
    lines.append("4. 本地 `file://` 预览无法 fetch，已内嵌备份数据，故本地打开也能看到当日岗位。\n")

    lines.append("## 运行\n")
    lines.append("```bash\npython -m scraper.run   # 抓取→过滤→生成 site/ 与 REPORT.md\n```")
    lines.append("（须用含 pypdf 的 venv python：PDF 简介抽取依赖它。）")

    path = os.path.join(ROOT, "REPORT.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[generate] 写入 {path}")
    return path


def generate(jobs: list[dict]):
    write_json(jobs)
    write_html(jobs)
    write_report(jobs)


if __name__ == "__main__":
    from pipeline import run
    generate(run())
