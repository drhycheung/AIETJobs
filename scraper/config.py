"""
config.py — AIETJobs 中央配置
香港教育大学 BSc(AI&EdTech) 应届生 AI/EdTech 岗位每日推送系统

合规原则（详见 AGENTS.md §2）：
- 仅从白名单来源「发现」岗位
- 推送给学生的「最终链接」必须是雇主/学校官方原帖
- 香港主流求职网站（JobsDB / CTgoodjobs / Recruit / CPjobs）**已纳入白名单且启用发现**：
  仅经搜索引擎公开索引「发现」帖子链接，不直爬、不绕过任何验证；
  商业板深链有效期短，每日重新发现，并以「求职板原帖」如实标注（区别于雇主官方原帖）
- 发布仅元数据 + 链接，不复制 JD 全文，不采集个人资料
"""

# ---------------------------------------------------------------------------
# 可识别的 User-Agent（透明、可联系）
# ---------------------------------------------------------------------------
USER_AGENT = (
    "Mozilla/5.0 (compatible; EdUHK-AIEdTech-JobBot/1.0; "
    "+https://github.com/drhycheung/AIETJobs; contact: jobs-bot@eduhk.hk)"
)
CONTACT_EMAIL = "jobs-bot@eduhk.hk"
PROJECT_URL = "https://github.com/drhycheung/AIETJobs"

# ---------------------------------------------------------------------------
# 信息来源白名单
# ---------------------------------------------------------------------------
# 香港主流求职网站（已启用「发现」：经搜索引擎公开索引发现帖子链接，
# 不直爬、不绕过验证；发现的链接作「求职板原帖」如实标注，每日重新发现）
COMMERCIAL_DISCOVERY_ENABLED = True
COMMERCIAL_BOARDS = {
    "jobsdb.com": "JobsDB",
    "ctgoodjobs.hk": "CTgoodjobs",
    "recruit.com.hk": "Recruit",
    "cpjobs.com": "CPjobs",
}

# 香港劳工处官方（可直接合规抓取）
GOV_SOURCES = {
    "jobs.gov.hk": "香港劳工处 jobs.gov.hk",
}

# 香港各大学官方空缺/招聘页（白名单，可直接合规抓取）
UNIVERSITY_SOURCES = {
    "eduhk.hk": "香港教育大学 EdUHK",
    "hkust.edu.hk": "香港科技大学 HKUST",
    "cuhk.edu.hk": "香港中文大学 CUHK",
    "hku.hk": "香港大学 HKU",
    "polyu.edu.hk": "香港理工大学 PolyU",
    "cityu.edu.hk": "香港城市大学 CityU",
    "hkbu.edu.hk": "香港浸会大学 HKBU",
    "ln.edu.hk": "岭南大学 LingnanU",
    "hkisyu.edu.hk": "香港树仁大学 HKSYU",
}

# 全部白名单域名（用于校验发现的链接是否合规）
ALLOWED_DOMAINS = set(UNIVERSITY_SOURCES) | set(GOV_SOURCES) | set(COMMERCIAL_BOARDS)

# ---------------------------------------------------------------------------
# 排除清单（聚合 / 抓取 / 博客站，永不采用；即便发现也只当线索回官方复核）
# ---------------------------------------------------------------------------
EXCLUDED_DOMAINS = {
    "hiringcafe.com", "joblum.com", "careers.sh", "bebee.com", "hkese.net",
    "offertoday.com", "thebigjobsite.com", "postjobfree.com", "indeed.com",
    "linkedin.com", "gradconnection.com", "jobfinder.com", "hirelala.com",
    "sigma.ai", "imerit.com", "glassdoor.com", "ziprecruiter.com",
    "jobstreet.com",  # 注意：ph.jobstreet.com 是菲律宾版，非香港
}

# ---------------------------------------------------------------------------
# 五类岗位方向
# ---------------------------------------------------------------------------
CATEGORIES = {
    1: {
        "name": "大学里的 AI / EdTech",
        "en": "AI/EdTech inside universities",
        "examples": "Research Assistant、学习技术开发者、教育发展主任、多媒体开发",
        "keywords": [
            "research assistant", "learning technology", "educational development",
            "multimedia developer", "teaching", "e-learning", "centre for learning",
        ],
    },
    2: {
        "name": "业界人工智能与教育科技",
        "en": "AI & EdTech industry",
        "examples": "EdTech 公司 AI 开发、教育产品工程师",
        "keywords": [
            "edtech", "education technology", "教育科技", "ai education",
            "教育", "教学", "ai 教學", "教學",
        ],
    },
    3: {
        "name": "单纯人工智能",
        "en": "Pure AI / ML",
        "examples": "AI/ML 工程师、数据科学培训生、算法岗",
        "keywords": [
            "ai engineer", "machine learning", "data science", "graduate trainee",
            "nlp", "genai", "computer vision", "算法", "人工智能",
        ],
    },
    4: {
        "name": "当老师 / 在学校推 AI",
        "en": "Teaching / promoting AI in schools",
        "examples": "AI 教学助理、STEM/IT 教师、学校 ETO、PGDE 路径",
        "keywords": [
            "ai 教學助理", "stem instructor", "it teacher", "education technology officer",
            "pgde", "教学助理", "教學助理", "teacher",
        ],
    },
    5: {
        "name": "数据分析 / 数据处理 / 数据标注",
        "en": "Data analysis / processing / annotation",
        "examples": "数据分析师、数据处理主任、数据标注员",
        "keywords": [
            "data analyst", "data processing", "data annotation", "數據標註",
            "語音轉錄標註", "data", "数据分析",
        ],
    },
}

# ---------------------------------------------------------------------------
# 多标签体系（取代固定五类分区）
# 每个岗位按其命中的关键词动态贴标签，因此某方向「暂时没有岗位」时版面不会显得突兀。
# 其中「方向标签」由下方关键词匹配；「角色/来源标签」（大学/业界/实习/应届友好）
# 由 pipeline.assign_tags 依据 official_type / 标题 / 经验字段追加。
# ---------------------------------------------------------------------------
DIRECTION_TAGS = {
    "人工智能": ["ai", "artificial intelligence", "machine learning", "ml", "nlp",
               "computer vision", "genai", "deep learning", "算法", "人工智能"],
    "教育科技": ["edtech", "education technology", "教育科技", "ai education",
               "ai 教學", "教學科技", "e-learning"],
    "数据分析": ["data analyst", "data science", "data processing", "data annotation",
               "數據", "数据", "数据分析", "big data", "bigdata"],
    "多媒体": ["multimedia", "多媒体", "frontend", "前端", "web developer"],
    "教学": ["teacher", "teaching assistant", "教学助理", "教學助理",
            "stem instructor", "pgde", "教育", "教学", "教學"],
}

# ---------------------------------------------------------------------------
# 契合度加分词（BSc AI&EdTech 能力画像）
# ---------------------------------------------------------------------------
FIT_KEYWORDS = [
    "ai", "artificial intelligence", "machine learning", "ml", "nlp",
    "computer vision", "education", "educational", "edtech", "learning",
    "teaching", "stem", "python", "multimedia", "data", "language", "smart",
    "人工智能", "教育", "教学", "数据", "程式", "程式設計",
]

# ---------------------------------------------------------------------------
# 相关性闸门：命中任一关键词即视为「与 AI/EdTech/数据/教学方向相关」
# （用于放行 IT Intern、Research Assistant、Developer 等技术/实习/研究岗，
#   同时把 Executive Officer、Residential Officer 等通用行政岗挡在门外）
# ---------------------------------------------------------------------------
RELEVANCE_KEYWORDS = [
    "intern", "research assistant", "trainee", "developer", "programmer",
    "engineer", "analyst", "multimedia", "data", " ai ", "machine learning",
    "education", "teaching", "learning", "stem", "software", "programming",
    "technology", "digital", "it ", "computer", "science", "edtech",
    "artificial intelligence", "language", "smart",
]

# ---------------------------------------------------------------------------
# 合规过滤：必须在标题/描述中「拒绝」的信号（需要经验/执照/硕士/已截止/非香港）
# ---------------------------------------------------------------------------
# 学术 / 教职头衔（通常需博士，绝非本科应届生目标）→ 直接拒绝
ACADEMIC_REJECT = [
    "professor", "lecturer", "dean", "chair professor", "postdoctoral",
    "post-doc", "postdoc", "research fellow", "head of", "principal",
]
# 经验要求（本科应届生不符）
EXPERIENCE_REJECT = [
    " years of experience", " yrs experience", " year experience",
    " 5 years", " 4 years", " 3 years", " 2 years", "experienced",
    "senior", "lead", "principal", "head of", "manager",
]
# 学历要求（需硕士/博士/执照）
DEGREE_REJECT = [
    "master", "m.sc", "msc", "m.phil", "phd", "doctorate", "postgraduate",
    "professional qualification", "licensed", "certified", "chartered",
    "pgde required", "master's degree required", "硕士", "博士", "执照",
]
# 非香港信号
NON_HK_SIGNALS = ["mainland china", "overseas", "singapore", "remote (overseas)"]

# ---------------------------------------------------------------------------
# 部署（由 GitHub Actions 自动部署 site/ 到 GitHub Pages；
#       详见 .github/workflows/deploy.yml，无需在此配置 token）
# ---------------------------------------------------------------------------
PUSH_GITHUB = True
GH_TOKEN = ""        # 不再使用：部署改由 Actions 的 GITHUB_TOKEN 完成
GH_OWNER = "drhycheung"
GH_REPO = "AIETJobs"

# ---------------------------------------------------------------------------
# 网络与限速
# ---------------------------------------------------------------------------
REQUEST_TIMEOUT = 25
MIN_INTERVAL = 2.0      # 单站请求最小间隔（秒）
MAX_INTERVAL = 5.0
RETRIES = 2
