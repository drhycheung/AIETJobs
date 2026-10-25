"""
pipeline.py — 去重 / 分类 / ⭐ 契合度评分 / 合规过滤 / 排序
核心原则（AGENTS.md）：
- 仅收「本科可投 / fresh graduate welcome」岗位
- 程序化过滤：需经验/执照/硕士、已截止、链接失效、非香港、非白名单
- 最终链接必须是官方原帖，并经 is_live 校验
"""
from __future__ import annotations

import os
import sys
import re
import io

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
import fetch
from live import collect_all

try:
    from pypdf import PdfReader
    _HAVE_PYPDF = True
except Exception:
    _HAVE_PYPDF = False


# ---------------------------------------------------------------------------
# 分类
# ---------------------------------------------------------------------------
def _text_of(job: dict) -> str:
    return " ".join([
        job.get("title", ""), job.get("department", ""),
        job.get("employer", ""),
    ]).lower()


def assign_category(job: dict) -> tuple[int, int]:
    """返回 (最佳类别, 该类别关键词命中数)。命中数=0 表示与五类方向无关。"""
    text = _text_of(job)
    best, best_score = 3, 0  # 默认归入「单纯人工智能」并靠评分区分
    for cat_id, meta in config.CATEGORIES.items():
        score = sum(1 for kw in meta["keywords"] if kw.lower() in text)
        if score > best_score:
            best, best_score = cat_id, score
    return best, best_score


# ---------------------------------------------------------------------------
# ⭐ 契合度评分（BSc AI&EdTech 能力画像）
# ---------------------------------------------------------------------------
_STRONG = {"ai", "artificial intelligence", "machine learning", "ml", "nlp",
           "education", "educational", "edtech", "learning", "teaching",
           "computer vision", "人工智能", "教育", "教学", "學習"}


def fit_score(job: dict, cat_score: int = 0) -> tuple[int, str]:
    text = _text_of(job)
    hits = []
    raw = 0
    for kw in config.FIT_KEYWORDS:
        if kw.lower() in text:
            hits.append(kw)
            raw += 2 if kw.lower() in _STRONG else 1
    cat = assign_category(job)[0]
    cat_name = config.CATEGORIES[cat]["name"]
    # 大学 / 同领域岗优先
    if "eduhk" in job.get("official_link", "") or "university" in job.get("employer", "").lower():
        raw += 1
    stars = 1 if raw >= 1 else 0
    stars = 2 if raw >= 4 else stars
    stars = 3 if raw >= 7 else stars
    stars = max(stars, 1)
    reason = "命中关键词：" + ", ".join(hits[:6]) if hits else "通用 AI/数据岗"
    return stars, f"类别={cat_name}；{reason}"


# ---------------------------------------------------------------------------
# 合规：从官方 PDF 抽取文本，检查经验/学历要求
# ---------------------------------------------------------------------------
def _extract_pdf_text(url: str) -> str | None:
    if not _HAVE_PYPDF:
        return None
    status, data = fetch.fetch_url(url, binary=True)
    if status != 200 or not data:
        return None
    try:
        r = PdfReader(io.BytesIO(data))
        return "\n".join((p.extract_text() or "") for p in r.pages)
    except Exception:
        return None


def _extract_html_text(url: str) -> str | None:
    """商业求职板深链无 PDF，退而抓取页面 HTML 扫描经验/学历信号。"""
    status, html_text = fetch.fetch_url(url)
    if status != 200 or not html_text:
        return None
    return html_text


def _get_jd_text(job: dict) -> str | None:
    """取一次 JD 文本：官方岗取 PDF，商业板取页面 HTML（供合规 + 简介共用）。"""
    if job.get("official_type") == "employer_official":
        return _extract_pdf_text(job.get("official_link", ""))
    return _extract_html_text(job.get("official_link", ""))


def _summarize(text: str, limit: int = 220) -> str:
    """从 JD 文本抽取一句简短职责简介（不含薪资/编号等表头噪声）。"""
    if not text:
        return ""
    # 优先找职责段落
    paras = re.split(r"\n\s*\n|(?:\r\n)+", text)
    best = None
    for p in paras:
        pl = p.lower()
        if any(k in pl for k in ("duties", "responsibilities", "the appointee",
                                 "job description", "main responsibilities", "role")):
            if len(p.strip()) > 40:
                best = p
                break
    if not best:
        for p in paras:
            s = p.strip()
            if len(s) > 50 and not re.match(
                    r"(ref|closing date|advertisement|salary|the education university|"
                    r"job ref|post\s*ref|apply|enquiries)", s.lower()):
                best = p
                break
    if not best:
        best = re.sub(r"\s+", " ", text)
    s = re.sub(r"\s+", " ", best).strip()
    if len(s) > limit:
        s = s[:limit].rstrip() + "…"
    return s


def _build_description(job: dict, jd_text: str | None) -> str:
    """岗位简介：优先用发现时附带的 description；否则从 JD 文本摘要。"""
    if job.get("description"):
        return job["description"].strip()
    if jd_text:
        return _summarize(jd_text)
    return ""


def assign_tags(job: dict) -> list[str]:
    """为多标签展示动态生成标签（方向标签 + 角色/来源标签）。"""
    text = _text_of(job)
    tags: list[str] = []
    for label, kws in config.DIRECTION_TAGS.items():
        if any(k in text for k in kws):
            tags.append(label)
    title_l = job.get("title", "").lower()
    exp = (job.get("experience", "") or "").lower()
    employer = (job.get("employer", "") or "").lower()
    if job.get("official_type") == "employer_official" and "university" in employer:
        tags.append("大学")
    elif job.get("official_type") == "commercial_board":
        tags.append("业界")
    if any(k in title_l for k in ("intern", "trainee", "part-time", "part time",
                                  "实习", "培训生", "培训生")):
        tags.append("实习／培训生")
    if any(k in exp for k in ("not required", "fresh graduate", "entry-level",
                              "welcome", "not specified")):
        tags.append("应届友好")
    # 去重保序
    seen: set[str] = set()
    out: list[str] = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def compliance_check(job: dict, jd_text: str | None = None) -> tuple[bool, str]:
    """返回 (是否保留, 说明)。jd_text 可由调用方预取以复用（避免重复下载）。"""
    title = job.get("title", "").lower()
    # 0) 学术/教职头衔（需博士，非本科应届生目标）
    for term in config.ACADEMIC_REJECT:
        if term in title:
            return False, f"学术/教职岗（通常需博士）「{term}」"
    # 1) 标题硬性拒绝（资深/管理/需经验）
    for term in config.EXPERIENCE_REJECT:
        if term in title:
            return False, f"标题含资深/经验信号「{term.strip()}」"
    # 2) 非香港（基于标题/部门/雇主）
    text = _text_of(job)
    for sig in config.NON_HK_SIGNALS:
        if sig in text:
            return False, f"疑似非香港岗位「{sig}」"
    # 3) 官方 JD 文本深度检查（经验/学历）：优先 PDF，其次页面 HTML
    scan = jd_text
    src = "PDF" if job.get("official_type") == "employer_official" else "页面 HTML"
    if scan is None:
        scan = _extract_pdf_text(job.get("official_link", ""))
        src = "PDF"
    if scan is None:
        scan = _extract_html_text(job.get("official_link", ""))
        src = "页面 HTML"
    if scan is None:
        return True, "（未取到 JD 文本，建议学生自行核对要求）"
    pl = scan.lower()
    # 学历要求需是「硬性要求」才算拒绝；「a plus / preferred / advantage」不算。
    _DEG_REQ = re.compile(
        r"(master'?s?|m\.?sc|m\.?phil|ph\.?d|doctorate|postgraduate).{0,45}?"
        r"(required|must|essential|minimum|necessar|qualif)", re.I)
    _DEG_REQ_ZH = re.compile(r"(硕士|博士).{0,12}(須|必须|要求|以上|學位)", re.I)
    _NEG = re.compile(r"\b(plus|advantage|preferred|asset|desirable|optional|nice to have|a plus)\b", re.I)
    for term in config.DEGREE_REJECT:
        if term not in pl:
            continue
        hit = _DEG_REQ.search(pl) or _DEG_REQ_ZH.search(pl)
        if hit:
            window = pl[hit.start(): hit.start() + 90]
            if not _NEG.search(window):
                return False, f"JD 要求较高学历「{term}」"
    # 经验要求：必须是「岗位硬性要求」语境，且非「not required」否定；
    # 排除公司简介里的「30+ years of experience」等噪声。
    _EXP1 = re.compile(
        r"(\d+)\s*\+?\s*years?'?\s*(?:of\s*)?experience\s+"
        r"(?:as a|as an|in|working|required|within)", re.I)
    _EXP2 = re.compile(
        r"(?:at least|minimum|require|must have|with at least)\s+"
        r"(\d+)\s*\+?\s*years?'?\s*(?:of\s*)?experience", re.I)
    _NEGEXP = re.compile(r"not required|no .{0,15}experience|experience (?:is )?not", re.I)
    m = _EXP1.search(pl) or _EXP2.search(pl)
    if m and not _NEGEXP.search(pl[max(0, m.start() - 50): m.start() + 80]):
        return False, "JD 要求多年经验"
    return True, f"JD（{src}）未见硬性经验/高学历门槛"


# ---------------------------------------------------------------------------
# 链接存活校验
# ---------------------------------------------------------------------------
def verify(job: dict) -> None:
    live, note = fetch.is_live(job.get("official_link", ""))
    job["verified_date"] = __import__("datetime").date.today().isoformat()
    if not live:
        job["status"] = "expired"
        job["notes"] = (job.get("notes", "") + f" 链接校验失败：{note}").strip()
    else:
        job["status"] = "active"
        job["notes"] = (job.get("notes", "") + f" 链接校验通过：{note}").strip()


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def _dedupe_key(job: dict) -> str:
    return (job.get("title", "").strip().lower(), job.get("employer", "").strip().lower())


def run() -> list[dict]:
    raw = collect_all()
    print(f"[pipeline] 原始岗位 {len(raw)} 条")

    seen = {}
    for job in raw:
        cat, cat_score = assign_category(job)
        job["category"] = cat
        job["category_name"] = config.CATEGORIES[cat]["name"]
        stars, reason = fit_score(job, cat_score)
        job["ai_edtech_fit"] = stars
        job["fit_reason"] = reason
        # 相关性闸门（基于「标题」，避免部门含关键词误放行行政岗）：
        # 标题未命中任一方向关键词 且 未命中角色相关性关键词 → 与目标人群无关
        title_l = job.get("title", "").lower()
        cat_title_score = sum(
            1 for meta in config.CATEGORIES.values()
            for kw in meta["keywords"] if kw in title_l
        )
        rel_hit = any(k in title_l for k in config.RELEVANCE_KEYWORDS)
        if cat_title_score == 0 and not rel_hit:
            job["status"] = "excluded"
            job["excluded_reason"] = "与 AI/EdTech/数据/教学五类方向无关键词关联"
            seen[_dedupe_key(job)] = job
            continue
        jd_text = _get_jd_text(job)
        keep, why = compliance_check(job, jd_text=jd_text)
        job["compliance_note"] = why
        if not keep:
            job["status"] = "excluded"
            job["excluded_reason"] = why
            seen[_dedupe_key(job)] = job
            continue
        # 简介 + 标签（供学生页展示）
        job["description"] = _build_description(job, jd_text)
        job["tags"] = assign_tags(job)
        verify(job)
        k = _dedupe_key(job)
        if k in seen:
            continue
        seen[k] = job

    jobs = list(seen.values())
    # 排序：活跃优先 → 契合度 → 截止日近优先
    def sort_key(j):
        active = 0 if j.get("status") == "active" else 1
        stars = -(j.get("ai_edtech_fit", 0))
        dl = j.get("deadline") or "9999-12-31"
        return (active, stars, dl)
    jobs.sort(key=sort_key)

    active = [j for j in jobs if j.get("status") == "active"]
    print(f"[pipeline] 合规后保留 {len(active)} 条（活跃），"
          f"剔除/待复核 {len(jobs) - len(active)} 条")
    return jobs


if __name__ == "__main__":
    out = run()
    for j in out:
        print(f"[{j['status']}] ⭐{j['ai_edtech_fit']} {j['category']} "
              f"{j['title']} | {j['deadline']} | {j.get('compliance_note','')[:40]}")
