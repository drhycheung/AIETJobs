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

# Hong Kong Labour Department official site (directly and compliantly scrapeable)
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
    "香港 人工智能 教育 公司 招聘 應屆畢業生",
    "香港 教育科技 公司 招聘 人工智能 工程師",
    "香港 大學 教學助理 人工智能 招聘",
    "香港 STEM 導師 招聘 應屆畢業生",
    "香港 數據分析 見習生 招聘 應屆畢業生",
    "香港 多媒體 設計 教育 招聘 應屆畢業生",
    "香港 中小學 資訊科技 教學助理 招聘",
    "Hong Kong EdTech company careers AI engineer graduate",
    "Hong Kong AI startup careers hiring fresh graduate machine learning",
    "Hong Kong university research assistant artificial intelligence vacancy",
    "Hong Kong education technology developer vacancy apply graduate",
    "Hong Kong data annotation transcription entry level careers",
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
        "examples": "EdTech company AI developer, Education Product Engineer",
        "keywords": [
            "edtech", "education technology", "教育科技", "ai education",
            "教育", "教学", "ai 教學", "教學",
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
# Relevance gate: matching any keyword marks the post as relevant to the
# AI/EdTech/data/teaching directions. This lets through technical / internship /
# research roles (IT Intern, Research Assistant, Developer) while blocking generic
# administrative roles (Executive Officer, Residential Officer).
# ---------------------------------------------------------------------------
RELEVANCE_KEYWORDS = [
    "intern", "research assistant", "trainee", "developer", "programmer",
    "engineer", "analyst", "multimedia", "data", " ai ", "machine learning",
    "education", "teaching", "learning", "stem", "software", "programming",
    "technology", "digital", "it ", "computer", "science", "edtech",
    "artificial intelligence", "language", "smart",
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
