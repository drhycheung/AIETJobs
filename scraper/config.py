"""
config.py — Central configuration for AIETJobs
Daily push system for Hong Kong AI / EdTech graduate jobs, aimed at
BSc(AI&EdTech) final-year students of The Education University of Hong Kong (EdUHK).

Compliance principles (see AGENTS.md section 2):
- Only "discover" jobs from whitelisted sources.
- The final link shown to students must be the employer / university official post.
- Major Hong Kong job boards (JobsDB / CTgoodjobs / Recruit / CPjobs) are whitelisted
  and discovery is enabled: their post links are found only through public search-engine
  indexing (never scraped directly, never bypassing any verification); such links are
  labelled honestly as "job-board post" and re-discovered daily because they expire fast.
- Only metadata + links are published; no full job-description text; no personal data.
"""

# ---------------------------------------------------------------------------
# Identifiable User-Agent (transparent and contactable)
# ---------------------------------------------------------------------------
USER_AGENT = (
    "Mozilla/5.0 (compatible; EdUHK-AIEdTech-JobBot/1.0; "
    "+https://github.com/drhycheung/AIETJobs; contact: hyincheung@eduhk.hk)"
)
CONTACT_EMAIL = "hyincheung@eduhk.hk"
CONTACT_NAME = "Dr. HY Cheung"
PROJECT_URL = "https://github.com/drhycheung/AIETJobs"

# ---------------------------------------------------------------------------
# Information source whitelist
# ---------------------------------------------------------------------------
# Major Hong Kong job boards (discovery enabled: found through public search-engine
# indexing only, never scraped directly or bypassing verification; discovered links
# are labelled honestly as "job-board post" and re-discovered daily).
COMMERCIAL_DISCOVERY_ENABLED = True
COMMERCIAL_BOARDS = {
    "jobsdb.com": "JobsDB",
    "ctgoodjobs.hk": "CTgoodjobs",
    "recruit.com.hk": "Recruit",
    "cpjobs.com": "CPjobs",
}

# Hong Kong Labour Department official site. Whitelisted as an official source, but
# its robots.txt returns `Disallow: /` and vacancy pages are session-token gated, so it
# is NOT direct-crawled (compliance rule: skip when robots forbids). It may appear only
# as a search-discovered lead, re-verified daily, like the commercial boards.
GOV_SOURCES = {
    "jobs.gov.hk": "Hong Kong Labour Department jobs.gov.hk",
}

# ---------------------------------------------------------------------------
# Third discovery category (approved by the project owner, 28 Oct 2026):
# employer official recruitment pages.
#
# Rationale: a page on the employer's own site is the official source by
# construction, so the link shown to students always satisfies the rule that the
# final link must be an official post. No third-party board is scraped, and no
# verification challenge is bypassed.
#
# These domains cannot be listed in advance (any Hong Kong employer may have
# one), so they are gated by URL shape instead: the path must point at a
# recruitment page or an individual vacancy, never at a news article, course
# page or aggregator listing. See search_discovery.classify_url.
# ---------------------------------------------------------------------------
EMPLOYER_DISCOVERY_ENABLED = True

# Approved employer domains. A page found on one of these is the employer's own
# recruitment page, so it satisfies the official-link rule.
# Deliberately a reviewed list rather than "any domain": the first test run of
# search discovery returned, among genuine Hong Kong pages, United States careers
# pages (openai.com, anthropic.com), freelance marketplaces, social-media posts and
# Macau job boards. Those are excluded by not being on this list.
# Every page rejected by the pipeline is logged with a reason, so this list grows
# from observed evidence rather than guesswork.
# All *.edu.hk and *.gov.hk hosts are approved automatically (Hong Kong universities
# and government departments).
EMPLOYER_DOMAINS = {
    "edcosys.com": "Edcosys (雲智未來), Hong Kong AI education company",
    "eduai.org": "EDU A.I. (智能教育), Hong Kong STEM and AI education company",
    "fdmgroup.com": "FDM Group, graduate technology programme in Hong Kong",
    "cathaypacific.com": "Cathay Pacific, Hong Kong",
    "dataintellect.com": "DataIntellect, technology consultancy with a Hong Kong office",
}

# Discovery runs through the Tavily search API. The key is supplied as the
# TAVILY_API_KEY environment variable / GitHub secret and is never stored in the
# repository. Free allowance: 1,000 searches per month.
TAVILY_ENDPOINT = "https://api.tavily.com/search"
TAVILY_MAX_RESULTS = 12
TAVILY_DAILY_QUERY_LIMIT = 18   # ~540 searches per month, leaving half the allowance spare

# Queries are written in the language recruiters actually use, so that both
# Chinese-language and English-language recruitment pages are found.
DISCOVERY_QUERIES = [
    # Core: AI / EdTech companies hiring fresh graduates
    "香港 人工智能 教育 公司 招聘 應屆畢業生",
    "香港 教育科技 公司 招聘 人工智能 工程師 畢業生",
    "Hong Kong EdTech company careers AI engineer graduate",
    "Hong Kong AI startup careers hiring fresh graduate machine learning",
    # Attractive, concrete graduate trainee programmes (tech / data / digital)
    "香港 科技 畢業培訓生計劃 應屆畢業生 資訊科技 2027",
    "香港 數碼 資訊科技 畢業培訓生 招聘 2027",
    "Hong Kong technology graduate trainee programme 2027 AI data",
    "Hong Kong bank graduate programme technology information technology",
    # University research / learning-tech roles
    "香港 大學 研究助理 人工智能 招聘 應屆",
    "Hong Kong university research assistant artificial intelligence vacancy",
    # Schools / STEM teaching (with PGDE pathway)
    "香港 STEM 導師 招聘 應屆畢業生 PGDE",
    "香港 中小學 資訊科技 教學助理 招聘",
    "Hong Kong international school STEM teacher AI computing graduate",
    # Data / analytics entry level
    "香港 數據分析 見習生 招聘 應屆畢業生",
    "Hong Kong data analyst graduate programme entry level careers",
]

# Official vacancy / recruitment pages of Hong Kong universities (whitelisted,
# directly and compliantly scrapeable)
UNIVERSITY_SOURCES = {
    "eduhk.hk": "The Education University of Hong Kong (EdUHK)",
    "hkust.edu.hk": "Hong Kong University of Science and Technology (HKUST)",
    "cuhk.edu.hk": "Chinese University of Hong Kong (CUHK)",
    "hku.hk": "University of Hong Kong (HKU)",
    "polyu.edu.hk": "Hong Kong Polytechnic University (PolyU)",
    "cityu.edu.hk": "City University of Hong Kong (CityU)",
    "hkbu.edu.hk": "Hong Kong Baptist University (HKBU)",
    "ln.edu.hk": "Lingnan University (LingnanU)",
    "hkisyu.edu.hk": "Hang Seng University of Hong Kong (HKSYU)",
}

# All whitelisted domains (used to validate discovered links for compliance)
ALLOWED_DOMAINS = set(UNIVERSITY_SOURCES) | set(GOV_SOURCES) | set(COMMERCIAL_BOARDS)

# ---------------------------------------------------------------------------
# Exclusion list (aggregator / scraper / blog sites, never used; even if found,
# they are treated only as leads and verified against the official source first)
# ---------------------------------------------------------------------------
EXCLUDED_DOMAINS = {
    "hiringcafe.com", "joblum.com", "careers.sh", "bebee.com", "hkese.net",
    "offertoday.com", "thebigjobsite.com", "postjobfree.com", "indeed.com",
    "linkedin.com", "gradconnection.com", "jobfinder.com", "hirelala.com",
    "sigma.ai", "imerit.com", "glassdoor.com", "ziprecruiter.com",
    "jobstreet.com",  # note: ph.jobstreet.com is the Philippines edition, not Hong Kong
    "aijobshk.com",   # aggregator of Hong Kong AI jobs; leads only, never a source
}

# ---------------------------------------------------------------------------
# Five job directions
# ---------------------------------------------------------------------------
CATEGORIES = {
    1: {
        "name": "AI / EdTech in universities",
        "en": "AI/EdTech inside universities",
        "examples": "Research Assistant, Learning Technology Developer, "
                    "Educational Development Officer, Multimedia Developer",
        "keywords": [
            "research assistant", "learning technology", "educational development",
            "multimedia developer", "teaching", "e-learning", "centre for learning",
        ],
    },
    2: {
        "name": "AI & EdTech industry",
        "en": "AI & EdTech industry",
        "examples": "EdTech company AI developer, Education Product Engineer, "
                    "Tech / IT graduate trainee programme",
        "keywords": [
            "edtech", "education technology", "教育科技", "ai education",
            "教育", "教学", "ai 教學", "教學",
            "科技", "資訊科技", "數碼", "軟件", "軟體", "工程", "developer",
            "engineer", "engineering", "程式", "it", "software", "技術",
        ],
    },
    3: {
        "name": "Pure AI / ML",
        "en": "Pure AI / ML",
        "examples": "AI/ML Engineer, Data Science Trainee, Algorithm roles",
        "keywords": [
            "ai engineer", "machine learning", "data science", "graduate trainee",
            "nlp", "genai", "computer vision", "算法", "人工智能",
        ],
    },
    4: {
        "name": "Teaching / promoting AI in schools",
        "en": "Teaching / promoting AI in schools",
        "examples": "AI Teaching Assistant, STEM/IT Teacher, School ETO, PGDE pathway",
        "keywords": [
            "ai 教學助理", "stem instructor", "it teacher", "education technology officer",
            "pgde", "教学助理", "教學助理", "teacher",
        ],
    },
    5: {
        "name": "Data analysis / processing / annotation",
        "en": "Data analysis / processing / annotation",
        "examples": "Data Analyst, Data Processing Officer, Data Annotator",
        "keywords": [
            "data analyst", "data processing", "data annotation", "數據標註",
            "語音轉錄標註", "data", "数据分析",
        ],
    },
}

# ---------------------------------------------------------------------------
# Multi-tag system (replaces the fixed five-category layout)
# Each job is dynamically tagged by the keywords it matches, so a direction that
# temporarily has no jobs does not make the layout look odd.
# "Direction tags" are matched from the keywords below; "role / source tags"
# (University / Industry / Intern-Trainee / Fresh-graduate friendly) are appended
# by pipeline.assign_tags based on official_type / title / experience fields.
# ---------------------------------------------------------------------------
DIRECTION_TAGS = {
    "Artificial Intelligence": ["ai", "artificial intelligence", "machine learning", "ml", "nlp",
               "computer vision", "genai", "deep learning", "算法", "人工智能"],
    "Educational Technology": ["edtech", "education technology", "教育科技", "ai education",
               "ai 教學", "教學科技", "e-learning"],
    "Data Analysis": ["data analyst", "data science", "data processing", "data annotation",
               "數據", "数据", "数据分析", "big data", "bigdata"],
    "Multimedia": ["multimedia", "多媒体", "frontend", "前端", "web developer"],
    "Teaching": ["teacher", "teaching assistant", "教学助理", "教學助理",
            "stem instructor", "pgde", "教育", "教学", "教學"],
}

# ---------------------------------------------------------------------------
# Fit-score bonus keywords (BSc AI&EdTech competency profile)
# ---------------------------------------------------------------------------
FIT_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "ml", "nlp",
    "computer vision", "education", "educational", "edtech", "learning",
    "teaching", "stem", "python", "multimedia", "data", "language", "smart",
    "人工智能", "教育", "教学", "数据", "程式", "程式設計",
]

# ---------------------------------------------------------------------------
# Relevance gate: the post must contain at least one *role type* or *competency*
# keyword (bilingual) before it is shown. This lets through technical / internship
# / research / teaching / AI & EdTech roles while blocking generic pages that only
# say "education / learning" without any actual open role (e.g. a government
# directory page or a company about page with no vacancy).
#
# Design notes (29 Oct 2026):
# - Bilingual on purpose: the previous English-only list wrongly excluded genuine
#   Chinese-language Hong Kong posts (e.g. Cathay Pacific "數碼及資訊科技畢業培訓生計劃")
#   while the loose tokens (" it ", " smart ", " language ") let generic pages through.
# - A bare "ai" substring is intentionally avoided (it matches "available", "email");
#   AI is matched by the `fit_score` word-boundary regex instead.
# ---------------------------------------------------------------------------
RELEVANCE_KEYWORDS = [
    # role types (English) — specific, not bare "officer"/"assistant"
    "intern", "internship", "trainee", "graduate programme", "graduate trainee",
    "grad scheme", "graduate scheme", "research assistant", "developer",
    "programmer", "engineer", "engineering", "analyst", "designer",
    "curriculum", "educator", "instructor", "multimedia", "data analyst",
    "data scientist", "software", "technical assistant", "it assistant",
    # role types (Chinese) — specific, not bare "助理"
    "實習", "見習", "培訓生", "畢業", "研究助理", "研究", "教學助理",
    "主任", "專員", "工程師", "分析員", "設計", "教師", "講師", "課程",
    "技術員", "程式設計", "程序員",
    # competencies (English)
    "machine learning", "deep learning", "nlp", "computer vision", "genai",
    "data science", "data analytics", "big data", "python", "programming",
    "edtech", "education technology", "stem", "digital", "technology",
    # competencies (Chinese)
    "人工智能", "人工智慧", "機器學習", "教育科技", "資訊科技", "數碼", "科技",
    "數據", "軟件", "軟體", "開發", "工程", "演算法", "算法", "雲端", "雲",
    "前端", "後端", "全端", "web", "多媒體",
    # domain anchors
    "teaching", "教學", "教学", "教育",
]

# Posts with no closing date and posted more than this many days ago are treated as
# stale (the liveness check only does HTTP 200, which a still-hosted but long-closed
# PDF passes forever). See pipeline.staleness.
STALE_POST_DAYS = 60

# Negative title keywords: immediate rejection if title contains any of these.
# These are administrative / non-technical roles that are off-target for a
# BSc(AI&EdTech) fresh-graduate board, plus clearly out-of-scope fields (economics).
NEGATIVE_TITLE_KEYWORDS = [
    "sales", "customer service", "account", "marketing", "branch", "store",
    "reception", "cashier", "barista", "waiter", "waitress", "driver",
    "personal assistant", "pa ", "administrative assistant", "admin officer",
    # Administrative / hall / clerical roles at universities
    "executive officer", "residential officer", "project officer",
    "administrative officer", "management officer", "clerical",
    "executive assistant", "residential", "warden", "secretary",
    # Out-of-scope fields for an AI x EdTech board
    "economist", "經濟師",
]

# ---------------------------------------------------------------------------
# Compliance filter: signals that must be "rejected" in the title / description
# (requires experience / licence / Master's / closed / non-Hong Kong)
# ---------------------------------------------------------------------------
# Academic / faculty titles (usually require a PhD; not for fresh bachelor graduates)
ACADEMIC_REJECT = [
    "professor", "lecturer", "dean", "chair professor", "postdoctoral",
    "post-doc", "postdoc", "research fellow", "head of", "principal",
]
# Experience requirements (not suitable for fresh bachelor graduates)
EXPERIENCE_REJECT = [
    " years of experience", " yrs experience", " year experience",
    " 5 years", " 4 years", " 3 years", " 2 years", "experienced",
    "senior", "lead", "principal", "head of", "manager",
]
# Academic-degree requirements (Master's / PhD / licence)
DEGREE_REJECT = [
    "master", "m.sc", "msc", "m.phil", "phd", "doctorate", "postgraduate",
    "professional qualification", "licensed", "certified", "chartered",
    "pgde required", "master's degree required", "硕士", "博士", "执照",
]
# Non-Hong Kong signals
NON_HK_SIGNALS = ["mainland china", "overseas", "singapore", "remote (overseas)"]

# ---------------------------------------------------------------------------
# Deployment (GitHub Actions deploys site/ to GitHub Pages automatically;
# see .github/workflows/deploy.yml — no token configuration needed here)
# ---------------------------------------------------------------------------
PUSH_GITHUB = True
GH_TOKEN = ""        # No longer used: deployment is handled by the Actions GITHUB_TOKEN
GH_OWNER = "drhycheung"
GH_REPO = "AIETJobs"

# ---------------------------------------------------------------------------
# Network and rate limiting
# ---------------------------------------------------------------------------
REQUEST_TIMEOUT = 25
MIN_INTERVAL = 2.0      # Minimum interval between requests to a single site (seconds)
MAX_INTERVAL = 5.0
RETRIES = 2
