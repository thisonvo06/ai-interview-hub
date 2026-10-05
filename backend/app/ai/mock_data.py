import random
from typing import Dict, Any, List
MOCK_RESUME_PARSED = {
    "education": [
        {
            "school": "北京航空航天大学",
            "major": "计算机科学与技术",
            "degree": "本科",
            "start_date": "2020-09",
            "end_date": "2024-06"
        }
    ],
    "work_experience": [
        {
            "company": "字节跳动",
            "title": "后端开发实习生",
            "description": "参与电商营销平台核心业务开发，负责优惠券中台与秒杀限流服务重构，优化 Redis 缓存与 MySQL 索引。",
            "start_date": "2023-07",
            "end_date": "2024-02"
        }
    ],
    "projects": [
        {
            "name": "高并发电商秒杀与订单中心",
            "role": "核心开发",
            "description": "基于 Spring Boot + Redis + RocketMQ 构建高并发秒杀系统，设计分布式锁与双写一致性保障，支撑单机 5000+ QPS。",
            "technologies": "Java, Spring Boot, Redis, MySQL, RocketMQ",
            "start_date": "2023-09",
            "end_date": "2023-12"
        },
        {
            "name": "企业级微服务权限治理中台",
            "role": "项目负责人",
            "description": "采用 Spring Cloud Alibaba + Gateway + Spring Security 实现细粒度 RBAC 权限控制与动态路由，集成 JWT 与 Redis 令牌黑名单。",
            "technologies": "Spring Cloud, Nacos, Sentinel, Redis, JWT",
            "start_date": "2023-02",
            "end_date": "2023-06"
        }
    ],
    "skills": [
        {"skill_name": "Java", "level": "熟练", "evidence": "熟练掌握 JVM 内存模型、垃圾回收与并发编程"},
        {"skill_name": "Spring Boot", "level": "熟练", "evidence": "深入理解自动装配原理与微服务架构开发"},
        {"skill_name": "MySQL", "level": "熟练", "evidence": "精通 InnoDB 存储引擎、B+树索引优化及事务隔离"},
        {"skill_name": "Redis", "level": "熟练", "evidence": "熟练掌握五大基础数据结构、缓存穿透/击穿/雪崩解决方案与 Redisson 分布式锁"},
        {"skill_name": "计算机网络", "level": "熟练", "evidence": "深入理解 TCP/IP 三次握手四次挥手及 HTTP/HTTPS 协议机制"}
    ],
    "certificates": ["全国计算机等级考试四级", "CET-6 (580分)"],
    "warnings": []
}

MOCK_JD_PARSED = {
    "title": "Java高级后端开发工程师",
    "category": "后端开发",
    "city": "北京",
    "salary_min": 20,
    "salary_max": 35,
    "education": "本科及以上",
    "experience": "1-3年",
    "type": "全职",
    "description": "我们正在寻找一位对高并发、分布式架构有深厚热情与工程实践的后端工程师，负责核心业务中台建设。",
    "duties": "1. 负责核心业务微服务的架构设计、研发与性能调优；\n2. 解决大流量、高并发场景下的可用性与一致性挑战；\n3. 参与关键技术预研与攻关，推动工程效能提升。",
    "requirements": "1. 统招本科及以上学历，计算机相关专业，1-3年 Java 后端研发经验；\n2. 深入理解 Java 基础、JVM 原理、多线程与并发编程；\n3. 熟练掌握 Spring Boot/Cloud 生态与主流持久层框架；\n4. 熟练掌握 MySQL 调优及 Redis 缓存架构设计。",
    "bonus": "具备大厂高并发架构经验或开源项目核心贡献者优先。",
    "skills": [
        {"skill_name": "Java", "level": "熟练", "required": True},
        {"skill_name": "Spring Boot", "level": "熟练", "required": True},
        {"skill_name": "Redis", "level": "熟练", "required": True},
        {"skill_name": "MySQL", "level": "熟练", "required": True},
        {"skill_name": "分布式系统", "level": "熟悉", "required": False}
    ],
    "competencies": [
        {"competency_name": "专业基础", "weight": 30.0, "required_score": 80.0},
        {"competency_name": "项目经验", "weight": 25.0, "required_score": 75.0},
        {"competency_name": "系统设计", "weight": 20.0, "required_score": 75.0},
        {"competency_name": "沟通表达", "weight": 15.0, "required_score": 80.0},
        {"competency_name": "综合素质", "weight": 10.0, "required_score": 80.0}
    ]
}

INTERVIEW_QUESTION_POOL = [
    {
        "skill_name": "Redis",
        "stage": "专业基础",
        "difficulty": "MEDIUM",
        "question": "请详细介绍一下在你的高并发项目中，如何利用 Redis 优化系统性能？在高并发读写下又是如何保障缓存与数据库一致性的？"
    },
    {
        "skill_name": "Redis",
        "stage": "深度探究",
        "difficulty": "HARD",
        "question": "如果在突发极端流量下，热点 Key 发生失效导致‘缓存击穿’，你会采取什么具体方案来防范？互斥锁与逻辑过期在实践中各有什么优劣取舍？"
    },
    {
        "skill_name": "Java并发",
        "stage": "专业基础",
        "difficulty": "MEDIUM",
        "question": "请结合底层源码或内存屏障，聊聊 Java 中 volatile 关键字的作用原理？它能保证线程安全原子性吗，为什么？"
    },
    {
        "skill_name": "MySQL",
        "stage": "专业基础",
        "difficulty": "MEDIUM",
        "question": "在 MySQL InnoDB 中，聚集索引与非聚集索引的底层组织方式有什么区别？为什么我们通常建议使用自增主键？"
    },
    {
        "skill_name": "项目经验",
        "stage": "项目深挖",
        "difficulty": "MEDIUM",
        "question": "请挑选你简历中印象最深的一个项目，详细讲讲你在其中负责的核心模块设计、遇到的最棘手技术难题以及最终的解决思路和量化收益。"
    },
    {
        "skill_name": "系统设计",
        "stage": "系统设计",
        "difficulty": "HARD",
        "question": "如果让你设计一个能够支撑千万级日活的分布式全局唯一发号器（如雪花算法或号段模式），你会如何设计并规避时钟回拨与单点瓶颈？"
    }
]

# 岗位大类识别关键词：把 job_title 映射到出题池分组（顺序即优先级，越靠前越专属）。
# 覆盖技术岗与非技术岗，避免所有岗位都套 Java/Redis 题。
_JOB_CATEGORY_KEYWORDS = [
    ("前端", ["前端", "web前端", "javascript", "typescript", "react", "vue", "小程序", "h5", "ui工程"]),
    ("客户端", ["安卓", "android", "ios", "鸿蒙", "客户端", "移动端", "flutter", "swift", "kotlin"]),
    ("人工智能", ["算法", "机器学习", "深度学习", "ai", "nlp", "大模型", "推荐", "cv", "数据挖掘", "llm"]),
    ("大数据", ["大数据", "数仓", "数据仓库", "数据平台", "hadoop", "spark", "flink", "hive", "etl", "数据开发"]),
    ("运维安全", ["运维", "devops", "sre", "安全", "网络工程", "系统架构", "基础架构", "云计算"]),
    ("测试", ["测试", "qa", "质量保障", "自动化测试"]),
    ("后端", ["后端", "java", "golang", "go", "python", "c++", "php", "node", "服务端", "研发", "软件工程师", "架构师"]),
    ("产品", ["产品经理", "产品", "pm", "需求分析"]),
    ("运营", ["运营", "增长", "用户运营", "内容运营", "活动运营", "私域"]),
    ("销售", ["销售", "商务", "客户经理", "大客户", "bd", "售前"]),
    ("人力", ["人力资源", "hr", "招聘", "人事", "绩效", "薪酬"]),
    ("财务", ["财务", "会计", "审计", "税务", "出纳"]),
    ("市场品牌", ["市场", "品牌", "公关", "营销", "广告", "媒介"]),
    ("设计", ["设计", "ui", "ux", "交互", "视觉", "平面", "工业设计师"]),
    ("客户成功", ["客户成功", "售后", "客户支持", "实施顾问", "cs"]),
]

# 按岗位大类的出题池：每组 6 题，覆盖 专业基础/深度探究/项目深挖/系统设计/综合素养/压力应对，
# 保证任意 seq 与追问（答好 DEEP / 答差 SIMPLIFY）都有同岗位、不同题干的题可选，避免重复。
MOCK_QUESTION_BANK_BY_CATEGORY: Dict[str, List[Dict[str, Any]]] = {
    "后端": INTERVIEW_QUESTION_POOL,  # 复用既有 Java/Redis 池
    "前端": [
        {"skill_name": "前端框架", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "请谈谈 Vue3 响应式的实现原理（Proxy 相比 defineProperty 的优势），以及 diff 算法在 patch 阶段做了哪些优化？"},
        {"skill_name": "前端工程化", "stage": "深度探究", "difficulty": "HARD",
         "question": "大型前端项目如何设计构建与性能优化方案？请从代码分割、Tree Shaking、缓存策略、首屏加载（FCP/LCP）等角度展开。"},
        {"skill_name": "浏览器与网络", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "从输入 URL 到页面渲染，浏览器经历了哪些关键阶段？其中如何减少重排重绘、利用浏览器缓存？"},
        {"skill_name": "项目经验", "stage": "项目深挖", "difficulty": "MEDIUM",
         "question": "请挑一个你负责的前端项目，讲讲你解决过的最棘手的问题（如性能瓶颈、复杂交互、兼容性），以及量化收益。"},
        {"skill_name": "综合素养", "stage": "综合素养", "difficulty": "EASY",
         "question": "你如何跟进前端快速迭代的技术生态？请举一个你主动学习并落地到项目中的新技术例子。"},
        {"skill_name": "抗压能力", "stage": "压力应对", "difficulty": "HARD",
         "question": "线上页面因你的改动出现白屏故障，正值大促高峰，你的前 30 分钟会怎么处理？"},
    ],
    "客户端": [
        {"skill_name": "移动端基础", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "请谈谈 Android/iOS 应用启动优化的关键手段，以及主线程卡顿（ANR）的成因与排查思路。"},
        {"skill_name": "性能与内存", "stage": "深度探究", "difficulty": "HARD",
         "question": "列表滑动卡顿与内存抖动是常见问题，你会如何定位并优化？请结合缓存复用、图片加载、内存泄漏检测说明。"},
        {"skill_name": "架构设计", "stage": "系统设计", "difficulty": "HARD",
         "question": "为一个多业务线 App 设计组件化/模块化架构，你会如何做模块拆分、路由通信与依赖管理？"},
        {"skill_name": "项目经验", "stage": "项目深挖", "difficulty": "MEDIUM",
         "question": "讲一个你主导的客户端功能，说明技术难点（如跨端、离线、复杂动画）与最终的性能/体验收益。"},
        {"skill_name": "综合素养", "stage": "综合素养", "difficulty": "EASY",
         "question": "客户端发版受应用商店审核约束，你如何规划灰度与热修复策略以降低线上风险？"},
        {"skill_name": "抗压能力", "stage": "压力应对", "difficulty": "HARD",
         "question": "版本上线后崩溃率突然飙升且难以复现，你如何在压力下系统性地定位与止损？"},
    ],
    "人工智能": [
        {"skill_name": "机器学习基础", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "请解释过拟合的成因与常见缓解手段（正则化、Dropout、早停、数据增强），并举例你在项目中如何判断模型过拟合。"},
        {"skill_name": "模型与训练", "stage": "深度探究", "difficulty": "HARD",
         "question": "训练大模型时显存不足怎么办？请从混合精度、梯度累积、激活重计算、并行策略等角度说明取舍。"},
        {"skill_name": "评估指标", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "分类任务中准确率为什么可能具有误导性？请结合精确率、召回率、F1、AUC 说明如何根据业务选择指标。"},
        {"skill_name": "项目经验", "stage": "项目深挖", "difficulty": "MEDIUM",
         "question": "讲一个你落地的算法/模型项目：问题定义、数据构造、baseline 到优化的迭代，以及线上收益如何量化。"},
        {"skill_name": "综合素养", "stage": "综合素养", "difficulty": "EASY",
         "question": "面对一个业务指标提升需求，你如何判断该用规则、传统模型还是深度模型？"},
        {"skill_name": "抗压能力", "stage": "压力应对", "difficulty": "HARD",
         "question": "模型离线评估很好但上线后效果大幅下跌，团队质疑你的方案，你会如何排查并沟通？"},
    ],
    "大数据": [
        {"skill_name": "数据仓库", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "请说明数仓分层（ODS/DWD/DWS/ADS）的意义，以及维度建模中事实表与维度表如何设计。"},
        {"skill_name": "计算引擎", "stage": "深度探究", "difficulty": "HARD",
         "question": "Spark 任务出现数据倾斜时，你如何定位并解决？请结合 key 加盐、广播连接、重分区等方案说明。"},
        {"skill_name": "数据质量", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "如何保障离线/实时数据链路的准确性与及时性？请从校验规则、监控告警、口径一致性角度说明。"},
        {"skill_name": "项目经验", "stage": "项目深挖", "difficulty": "MEDIUM",
         "question": "讲一个你处理的大数据量任务：遇到的性能/成本瓶颈，你做了哪些优化，效果如何量化？"},
        {"skill_name": "综合素养", "stage": "综合素养", "difficulty": "EASY",
         "question": "实时计算与离线计算各适合什么场景？你会如何为一个指标选择合适的链路？"},
        {"skill_name": "抗压能力", "stage": "压力应对", "difficulty": "HARD",
         "question": "核心报表在业务高峰前迟迟未产出且下游催逼，你如何排查并对外沟通？"},
    ],
    "运维安全": [
        {"skill_name": "系统与网络", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "一台服务器 CPU 或负载突然飙高，你的排查步骤与常用命令是什么？如何快速定位到进程与根因？"},
        {"skill_name": "高可用架构", "stage": "深度探究", "difficulty": "HARD",
         "question": "如何设计一套支撑业务连续性的部署与容灾方案？请从负载均衡、多活、监控告警、故障演练说明。"},
        {"skill_name": "安全基础", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "常见 Web 攻击（SQL 注入、XSS、CSRF）的原理与防御措施分别是什么？"},
        {"skill_name": "项目经验", "stage": "项目深挖", "difficulty": "MEDIUM",
         "question": "讲一次你主导的稳定性/成本优化：如何发现问题、采取什么措施、可用性（SLA）或成本改善了多少？"},
        {"skill_name": "综合素养", "stage": "综合素养", "difficulty": "EASY",
         "question": "你如何看待自动化运维与人工介入的边界？哪些操作必须保留人工审批？"},
        {"skill_name": "抗压能力", "stage": "压力应对", "difficulty": "HARD",
         "question": "线上发生大范围服务不可用，你作为值班负责人，第一优先级是什么？如何组织止血与通报？"},
    ],
    "测试": [
        {"skill_name": "测试基础", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "拿到一个需求，你如何设计测试用例？请说明等价类、边界值、场景法等方法的运用。"},
        {"skill_name": "自动化", "stage": "深度探究", "difficulty": "HARD",
         "question": "如何设计一套稳定的 UI/接口自动化测试框架？面对用例易碎（flaky）问题你会怎么治理？"},
        {"skill_name": "缺陷分析", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "线上漏测了一个严重 Bug，你会如何做根因分析并改进测试流程？"},
        {"skill_name": "项目经验", "stage": "项目深挖", "difficulty": "MEDIUM",
         "question": "讲一个你负责的质量保障项目：测试策略、自动化覆盖率、缺陷逃逸率等指标如何改善？"},
        {"skill_name": "综合素养", "stage": "综合素养", "difficulty": "EASY",
         "question": "开发说某个问题“不是 Bug 是特性”，你如何判断并处理这类分歧？"},
        {"skill_name": "抗压能力", "stage": "压力应对", "difficulty": "HARD",
         "question": "版本明天上线但还有关键用例未测完，你如何在质量与进度之间权衡并向上反馈？"},
    ],
    "产品": [
        {"skill_name": "需求优先级", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "多个业务方同时提需求而研发资源有限，你如何决定优先级？请介绍你用过的框架（RICE/KANO）及一次真实取舍。"},
        {"skill_name": "数据驱动", "stage": "深度探究", "difficulty": "HARD",
         "question": "某功能上线一周核心指标不升反降，你如何排查并做出继续/回滚的决策？"},
        {"skill_name": "用户洞察", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "你如何判断一个用户反馈的需求是真痛点还是伪需求？请说明你的验证方法。"},
        {"skill_name": "项目经验", "stage": "项目深挖", "difficulty": "MEDIUM",
         "question": "讲一个你主导的产品从 0 到 1：如何定义目标用户、验证需求、衡量上线后的业务结果？"},
        {"skill_name": "综合素养", "stage": "综合素养", "difficulty": "EASY",
         "question": "研发认为你的需求技术上不合理并拒绝推进，你会怎么处理？"},
        {"skill_name": "抗压能力", "stage": "压力应对", "difficulty": "HARD",
         "question": "老板拍板一个你强烈不认同的需求并要求立即上线，你如何应对？"},
    ],
    "运营": [
        {"skill_name": "用户分层", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "请介绍你常用的用户分层/分群方法，以及针对不同层级如何设计差异化运营策略。"},
        {"skill_name": "增长实验", "stage": "深度探究", "difficulty": "HARD",
         "question": "设计一个提升新用户次日留存的方案，并说明你如何用对照实验验证它真的有效。"},
        {"skill_name": "活动复盘", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "一场线上活动 ROI 不达预期，你会如何从漏斗与成本结构复盘并改进？"},
        {"skill_name": "项目经验", "stage": "项目深挖", "difficulty": "MEDIUM",
         "question": "讲一个你操盘过的运营项目：目标、策略、关键动作，以及可量化的业务结果。"},
        {"skill_name": "综合素养", "stage": "综合素养", "difficulty": "EASY",
         "question": "如何衡量私域社群的真实价值，而不是只看群数量？"},
        {"skill_name": "抗压能力", "stage": "压力应对", "difficulty": "HARD",
         "question": "你策划的活动上线即被用户大量投诉，运营群炸锅，你的前 30 分钟做什么？"},
    ],
    "销售": [
        {"skill_name": "销售漏斗", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "请描述你从线索到成交的完整打法，你如何管理销售漏斗与各阶段转化率？"},
        {"skill_name": "异议处理", "stage": "深度探究", "difficulty": "HARD",
         "question": "客户说“你们价格太贵了”，你会如何探询真实异议并重构价值，而不是直接降价？"},
        {"skill_name": "客户开发", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "面对一个全新行业/区域市场，你如何从 0 开拓客户并建立管道？"},
        {"skill_name": "项目经验", "stage": "项目深挖", "difficulty": "MEDIUM",
         "question": "讲一个你拿下的最难客户：决策链、竞争格局、你的关键动作与最终业绩。"},
        {"skill_name": "综合素养", "stage": "综合素养", "difficulty": "EASY",
         "question": "如何判断一个商机是否值得投入精力？你会用哪些标准筛选线索？"},
        {"skill_name": "抗压能力", "stage": "压力应对", "difficulty": "HARD",
         "question": "连续两个月没完成业绩指标，主管开始质疑你，你会怎么做？"},
    ],
    "人力": [
        {"skill_name": "招聘效能", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "如何提升一个难招岗位的招聘达成率与招聘质量？请从画像、渠道、流程效率说明。"},
        {"skill_name": "绩效体系", "stage": "深度探究", "difficulty": "HARD",
         "question": "KPI 与 OKR 有什么本质区别？在什么样的组织情境下你会推荐哪一种？"},
        {"skill_name": "员工关系", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "公司要优化一名绩效不达标的员工，作为 HR 你如何合规且妥善地处理？"},
        {"skill_name": "项目经验", "stage": "项目深挖", "difficulty": "MEDIUM",
         "question": "讲一个你主导的 HR 项目（如招聘攻坚、体系搭建、文化落地）：目标、做法与量化成效。"},
        {"skill_name": "综合素养", "stage": "综合素养", "difficulty": "EASY",
         "question": "用人部门提了一个你认为不合理的招聘要求，你如何沟通与引导？"},
        {"skill_name": "抗压能力", "stage": "压力应对", "difficulty": "HARD",
         "question": "多个部门同时催招聘且都说是最高优先级，资源有限你如何应对？"},
    ],
    "财务": [
        {"skill_name": "财务报表", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "三大财务报表的关系是什么？为什么一家公司利润为正却可能出现资金链断裂？"},
        {"skill_name": "成本分析", "stage": "深度探究", "difficulty": "HARD",
         "question": "你如何分析一个产品的盈利能力并给出定价建议？请结合单位经济模型与盈亏平衡说明。"},
        {"skill_name": "内控审计", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "如果发现某部门存在费用报销舞弊迹象，你会如何调查与处置？"},
        {"skill_name": "项目经验", "stage": "项目深挖", "difficulty": "MEDIUM",
         "question": "讲一个你参与的财务分析/预算/降本增效项目：你做了什么，带来了多少可量化的价值？"},
        {"skill_name": "综合素养", "stage": "综合素养", "difficulty": "EASY",
         "question": "业务部门抱怨财务流程太慢影响效率，你如何在合规与效率之间平衡？"},
        {"skill_name": "抗压能力", "stage": "压力应对", "difficulty": "HARD",
         "question": "临近结账发现一处较大金额差错且原因未明，管理层在催报表，你如何处理？"},
    ],
    "市场品牌": [
        {"skill_name": "品牌定位", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "为一个新消费品牌做定位你会怎么做？你如何衡量定位是否成功？"},
        {"skill_name": "投放增长", "stage": "深度探究", "difficulty": "HARD",
         "question": "预算有限时，你如何在多渠道投放中分配预算并用增量实验持续优化 ROI？"},
        {"skill_name": "内容营销", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "如何策划一次能带来有效销售线索的内容营销活动，而不只是刷阅读量？"},
        {"skill_name": "项目经验", "stage": "项目深挖", "difficulty": "MEDIUM",
         "question": "讲一个你主导的市场/品牌 campaign：目标、创意、渠道组合与可量化的效果。"},
        {"skill_name": "综合素养", "stage": "综合素养", "difficulty": "EASY",
         "question": "如何区分品牌广告的长期价值与效果广告的短期转化，你会如何向老板解释预算分配？"},
        {"skill_name": "抗压能力", "stage": "压力应对", "difficulty": "HARD",
         "question": "品牌突然在社交媒体遭遇负面舆情，你会如何应对？"},
    ],
    "设计": [
        {"skill_name": "设计流程", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "请介绍你完成一个产品设计需求的完整流程与方法论（如何发现问题、验证方案）。"},
        {"skill_name": "设计决策", "stage": "深度探究", "difficulty": "HARD",
         "question": "当业务目标（如强曝光广告位）与用户体验冲突时，你如何取舍并用证据推动决策？"},
        {"skill_name": "设计系统", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "为什么要建设计系统？你会如何推动它在团队真正落地而非沦为摆设？"},
        {"skill_name": "项目经验", "stage": "项目深挖", "difficulty": "MEDIUM",
         "question": "讲一个你通过优化交互/视觉细节显著提升转化或体验的案例，用数据说明结果。"},
        {"skill_name": "综合素养", "stage": "综合素养", "difficulty": "EASY",
         "question": "你如何评估自己的设计是否“好”？会用哪些标准或数据？"},
        {"skill_name": "抗压能力", "stage": "压力应对", "difficulty": "HARD",
         "question": "你的设计方案被业务方当众否定并要求大改，你如何应对？"},
    ],
    "客户成功": [
        {"skill_name": "客户健康度", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "如何构建客户健康度评分体系，提前识别流失风险？"},
        {"skill_name": "续约增购", "stage": "深度探究", "difficulty": "HARD",
         "question": "如何提升 SaaS 客户的续费率，并在合适的时机创造增购机会？"},
        {"skill_name": "客户挽留", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "一个重要客户因产品问题非常不满并提出解约，你会如何处理？"},
        {"skill_name": "项目经验", "stage": "项目深挖", "difficulty": "MEDIUM",
         "question": "讲一个你成功挽回或深度服务并带来增购的客户案例：你的关键动作与结果。"},
        {"skill_name": "综合素养", "stage": "综合素养", "difficulty": "EASY",
         "question": "如何设计新客户的 onboarding 流程，让客户尽快获得价值（缩短 time to value）？"},
        {"skill_name": "抗压能力", "stage": "压力应对", "difficulty": "HARD",
         "question": "客户在大群里公开投诉你负责的账户，措辞很难听，你的前 30 分钟做什么？"},
    ],
    # 兜底：识别不出具体大类时使用的通用职业题（行业无关）
    "通用": [
        {"skill_name": "项目经验", "stage": "项目深挖", "difficulty": "MEDIUM",
         "question": "请挑选你简历中印象最深的一段经历，讲讲你的角色、遇到的最大困难、解决思路与量化成果。"},
        {"skill_name": "岗位理解", "stage": "专业基础", "difficulty": "MEDIUM",
         "question": "谈谈你对应聘岗位核心职责的理解，以及你认为胜任这个岗位最关键的三项能力是什么？"},
        {"skill_name": "学习能力", "stage": "综合素养", "difficulty": "EASY",
         "question": "举例说明你如何在短时间内掌握一门新知识/新技能并应用到实际工作中？"},
        {"skill_name": "协作沟通", "stage": "综合素养", "difficulty": "MEDIUM",
         "question": "描述一次你需要跨部门协作才能完成的任务，你如何推动并处理分歧？"},
        {"skill_name": "职业规划", "stage": "综合素养", "difficulty": "EASY",
         "question": "未来两三年你的职业目标是什么？你打算如何补齐现状与目标之间的差距？"},
        {"skill_name": "抗压能力", "stage": "压力应对", "difficulty": "HARD",
         "question": "你负责的一项工作临近截止却出现重大返工，你如何在压力下调整并交付？"},
    ],
}


def detect_job_category(job_title: str) -> str:
    """根据岗位标题/描述关键词识别大类，命中优先级按 _JOB_CATEGORY_KEYWORDS 顺序。"""
    t = (job_title or "").lower()
    for category, keywords in _JOB_CATEGORY_KEYWORDS:
        if any(k in t for k in keywords):
            return category
    return "通用"


# 技术类大类（雷达用"系统设计"）；其余大类为非技术（雷达用"业务理解"）
_TECH_CATEGORIES = {"后端", "前端", "客户端", "人工智能", "大数据", "运维安全", "测试"}


def is_technical_role(job_title: str) -> bool:
    """岗位是否属于技术类：驱动报告雷达维度命名与反馈文案的自适应。"""
    return detect_job_category(job_title) in _TECH_CATEGORIES


def report_dimension_names(job_title: str) -> List[str]:
    """按岗位类型返回五维雷达维度名（非技术岗用"业务理解"替代"系统设计"）。"""
    if is_technical_role(job_title):
        return ["专业基础", "项目经验", "系统设计", "沟通表达", "综合素质"]
    return ["专业基础", "项目经验", "业务理解", "沟通表达", "综合素质"]


def _report_wording(job_title: str) -> Dict[str, str]:
    """报告反馈文案的技术/非技术措辞集。"""
    if is_technical_role(job_title):
        return {
            "core_label": "技术",
            "high_extra": "极端异常场景的容灾方案可进一步细化",
            "high_sugg": "面试时主动对比不同技术方案的优劣取舍，展现架构选型思考；补充线上故障排查案例，真实踩坑经验比理论方案更有说服力",
            "mid_weak": "回答偏向工具/流程的表面使用，对底层原理与边界条件探讨较浅",
            "mid_sugg": "建议深入学习本岗位核心知识的底层原理，不要只停留在操作层面",
            "low_sugg": "建议从最基础的概念开始学习，先建立完整的知识框架",
            "summary_hi": "在核心技术栈上有较深入的理解。建议继续深化高并发与分布式架构的实战经验。",
            "summary_mid": "对岗位所需专业知识有基本了解，但深度和广度都有明显提升空间。",
            "summary_low": "对岗位涉及的专业知识了解较少，建议系统性地复习基础知识并加强实战练习。",
        }
    return {
        "core_label": "专业",
        "high_extra": "对行业趋势与业务全局的思考可进一步展开",
        "high_sugg": "面试时主动展示数据化成果与跨部门协作案例，体现方法论沉淀；用 STAR 结构量化每项工作的业务影响",
        "mid_weak": "回答偏向日常流程的表面描述，缺少方法论沉淀与量化成果",
        "mid_sugg": "建议深入学习本岗位的核心方法论与行业知识，不要只停留在执行层面",
        "low_sugg": "建议从岗位的基础知识与行业常识开始学习，先建立完整的业务认知框架",
        "summary_hi": "对本岗位所需的专业能力有较扎实的理解。建议继续深化行业认知与方法论沉淀。",
        "summary_mid": "对岗位所需的专业知识有基本了解，但深度和广度都有明显提升空间。",
        "summary_low": "对岗位涉及的专业知识了解较少，建议系统性地学习基础知识并加强实践。",
    }


def _pick_category_question(category: str, seq: int, used_texts=None, prefer_difficulty: str = None) -> Dict[str, Any]:
    """从指定大类出题池选一道题：优先避开已用题干，其次按 seq 轮转，可选难度偏好优先。"""
    pool = MOCK_QUESTION_BANK_BY_CATEGORY.get(category) or MOCK_QUESTION_BANK_BY_CATEGORY["通用"]
    used = set(used_texts or [])
    fresh = [q for q in pool if q["question"] not in used]
    candidates = fresh or pool
    if prefer_difficulty:
        matched = [q for q in candidates if q["difficulty"] == prefer_difficulty]
        if matched:
            candidates = matched
    return dict(candidates[(max(1, seq) - 1) % len(candidates)])


def generate_mock_evaluation(question_text: str, answer_text: str, seq: int) -> Dict[str, Any]:
    ans = (answer_text or "").strip()
    ans_lower = ans.lower()
    q = question_text or ""

    # ========== 1. 多维度特征检测 ==========
    # 消极/敷衍回答检测
    negative_patterns = ["不知道", "没用过", "随便", "不会", "不懂", "不清楚", "没接触过", "跳过", "没做过", "忘了", "大概"]
    is_negative = any(p in ans for p in negative_patterns)
    is_very_short = len(ans) < 20

    # 技术深度关键词（按类别分组）
    tech_keywords = {
        "缓存一致性": ["双删", "延迟双删", "canal", "binlog", "最终一致性", "强一致性", "缓存与数据库一致性", "先更新数据库", "先删缓存"],
        "缓存问题": ["缓存击穿", "缓存穿透", "缓存雪崩", "布隆过滤器", "互斥锁", "逻辑过期", "热点key"],
        "分布式锁": ["分布式锁", "redisson", "redlock", "setnx", "看门狗", "watchdog", "租约", "幂等"],
        "并发底层": ["volatile", "内存屏障", "指令重排", "happens-before", "cas", "aqs", "synchronized", "线程池", "threadlocal"],
        "MySQL索引": ["聚簇索引", "非聚簇索引", "b+树", "回表", "覆盖索引", "最左前缀", "索引下推", "explain", "慢查询"],
        "事务MVCC": ["mvcc", "undo log", "redo log", "隔离级别", "可重复读", "幻读", "间隙锁", "next-key lock"],
        "分布式架构": ["分库分表", "雪花算法", "时钟回拨", "分布式事务", "2pc", "tcc", "seata", "幂等设计", "消息队列"],
        "项目量化": ["qps", "tps", "tp99", "压测", "提升了", "降低了", "优化了"],
        "STAR结构": ["项目背景", "我负责", "我做的", "遇到的问题", "解决方案", "最终结果", "效果", "收益"],
    }

    matched_categories = []
    matched_details = []
    for cat, kws in tech_keywords.items():
        found = [kw for kw in kws if kw in ans_lower]
        if found:
            matched_categories.append(cat)
            matched_details.extend(found[:2])

    # 回答质量分档
    word_count = len(ans)
    has_structure = any(p in ans for p in ["第一", "第二", "第三", "首先", "其次", "然后", "最后", "1.", "2.", "3."])
    has_numbers = any(c.isdigit() for c in ans) and any(p in ans_lower for p in ["qps", "tps", "%", "倍", "ms", "万"])

    # 纯乱码/重复字符检测：键盘乱敲、刷屏重复等不视为有效作答
    has_cjk = any('一' <= c <= '鿿' for c in ans)
    unique_ratio = len(set(ans)) / max(1, len(ans))
    is_repeat = len(ans) >= 6 and unique_ratio < 0.28
    is_pure_ascii_gibberish = (not has_cjk) and (' ' not in ans) and len(matched_categories) == 0
    is_gibberish = is_repeat or is_pure_ascii_gibberish

    # ========== 2. 分档评分与反馈生成 ==========
    if is_negative or is_gibberish or (is_very_short and len(matched_categories) == 0):
        # ---- 差/敷衍回答 ----
        prof = round(random.uniform(32.0, 45.0), 1)
        rel = round(random.uniform(38.0, 50.0), 1)
        comp = round(random.uniform(28.0, 40.0), 1)
        logic = round(random.uniform(38.0, 48.0), 1)
        depth = round(random.uniform(22.0, 35.0), 1)
        comm = round(random.uniform(42.0, 52.0), 1)
        total_score = round(prof * 0.30 + rel * 0.20 + comp * 0.15 + logic * 0.15 + depth * 0.15 + comm * 0.05, 1)
        action = "SIMPLIFY"

        q_short = q[:40] + ("..." if len(q) > 40 else "")
        evidence = [
            f"回答篇幅较短（{word_count}字），未围绕题目「{q_short}」展开系统性阐述",
            "未提及任何核心技术概念或实践方案，无法判断技术掌握程度"
        ]
        weaknesses = [
            "对题目考察的核心技术点缺乏基本认知，未能给出任何方向性回答",
            "面试中遇到不会的问题时，应先说明已知的相关背景，再尝试给出思路框架，而非直接放弃"
        ]
        missing = [
            f"本题考察的核心概念：{q_short}",
            "该技术点的典型应用场景与基本工作原理",
            "至少 1-2 个主流实现方案的名称与适用场景"
        ]
        suggestions = [
            f"建议先系统学习「{q_short.split('，')[0]}」相关基础知识，从官方文档入门",
            "面试答题技巧：即使不完全确定，也可先复述问题要点、给出思路框架，展现思考过程比空白更有价值",
            "推荐：针对该技术点做一次专题笔记，整理核心概念 + 常见面试题 + 参考答案"
        ]

    elif len(matched_categories) >= 3 or (word_count >= 150 and has_structure and has_numbers):
        # ---- 优秀回答 ----
        prof = round(random.uniform(85.0, 93.0), 1)
        rel = round(random.uniform(87.0, 95.0), 1)
        comp = round(random.uniform(82.0, 90.0), 1)
        logic = round(random.uniform(84.0, 92.0), 1)
        depth = round(random.uniform(84.0, 92.0), 1)
        comm = round(random.uniform(83.0, 90.0), 1)
        total_score = round(prof * 0.30 + rel * 0.20 + comp * 0.15 + logic * 0.15 + depth * 0.15 + comm * 0.05, 1)
        action = "DEEP" if seq < 5 else "FINISH"

        cats_str = "、".join(matched_categories[:3])
        details_str = "、".join(matched_details[:4])
        evidence = [
            f"回答覆盖了【{cats_str}】多个技术维度，深度与广度兼备",
            f"准确提及了 {details_str} 等关键技术点，说明有实际项目经验",
            f"回答结构清晰（{'分点阐述' if has_structure else '逻辑连贯'}），篇幅 {word_count} 字，内容充实"
        ]
        weaknesses = [
            "在极端异常场景（如网络分区、节点宕机、主从延迟）下的容灾降级方案可进一步细化",
            "可补充更多量化数据（如压测 QPS、响应时间优化幅度）来增强说服力"
        ]
        missing = [
            "生产环境监控告警与故障自愈机制的设计思路",
            "方案的性能瓶颈分析与扩展容量规划"
        ]
        suggestions = [
            "面试时可主动对比不同方案的优劣取舍（如 Redis 分布式锁 vs Zookeeper 锁），展现技术选型思考",
            "建议补充线上实际踩过的坑与排查过程，真实故障案例比理论方案更有说服力",
            "可进一步学习该领域的前沿实践（如 Caffeine 多级缓存、Sentinel 限流降级）"
        ]

    elif len(matched_categories) >= 1 or word_count >= 80:
        # ---- 中等回答 ----
        prof = round(random.uniform(68.0, 78.0), 1)
        rel = round(random.uniform(70.0, 80.0), 1)
        comp = round(random.uniform(65.0, 74.0), 1)
        logic = round(random.uniform(68.0, 77.0), 1)
        depth = round(random.uniform(62.0, 72.0), 1)
        comm = round(random.uniform(72.0, 80.0), 1)
        total_score = round(prof * 0.30 + rel * 0.20 + comp * 0.15 + logic * 0.15 + depth * 0.15 + comm * 0.05, 1)
        action = "FOLLOW_UP" if seq < 5 else "FINISH"

        cats_str = "、".join(matched_categories[:2]) if matched_categories else "基础概念"
        evidence = [
            f"对【{cats_str}】有基本认知，能够回答出核心要点",
            f"回答篇幅 {word_count} 字，基本覆盖了题目的主要考察方向"
        ]
        weaknesses = [
            "回答偏向基础用法介绍，对底层原理与高并发边界条件探讨较浅",
            ("缺少量化数据支撑，建议结合具体项目中的实际效果展开" if not has_numbers else "量化数据较少，可补充更多具体指标")
        ]
        missing = [
            "技术方案的底层实现原理与工作机制",
            "生产环境中的异常处理与降级兜底方案",
            "不同技术方案的对比选型与适用场景"
        ]
        suggestions = [
            "建议结合自己项目中的真实场景展开，用 STAR 法则（情境-任务-行动-结果）组织回答",
            "深挖一个核心技术点的源码实现，而不是泛泛了解多个技术的表面用法",
            "面试前准备 2-3 个自己主导的项目案例，每个都能讲清楚遇到的难点与解决过程"
        ]

    else:
        # ---- 偏短/一般回答 ----
        prof = round(random.uniform(55.0, 65.0), 1)
        rel = round(random.uniform(58.0, 68.0), 1)
        comp = round(random.uniform(50.0, 60.0), 1)
        logic = round(random.uniform(55.0, 65.0), 1)
        depth = round(random.uniform(45.0, 55.0), 1)
        comm = round(random.uniform(60.0, 70.0), 1)
        total_score = round(prof * 0.30 + rel * 0.20 + comp * 0.15 + logic * 0.15 + depth * 0.15 + comm * 0.05, 1)
        action = "BASIC"

        evidence = [
            f"回答篇幅 {word_count} 字，内容较为简略，覆盖知识点有限",
            "基本理解题意，但回答深度与广度均有明显提升空间"
        ]
        weaknesses = [
            "回答不够结构化，缺乏清晰的逻辑层次",
            "技术细节不足，未能展开说明核心原理"
        ]
        missing = [
            "题目的核心考察点与标准答案框架",
            "至少 2-3 个具体的技术实现细节",
            "结合实际项目的案例与数据支撑"
        ]
        suggestions = [
            "练习用「总-分-总」结构答题：先给结论，再分点展开，最后总结",
            "针对本题涉及的技术点，整理一份包含「原理 + 应用 + 优缺点」的学习笔记",
            "多做模拟面试练习，提升临场组织语言的能力"
        ]

    return {
        "score": total_score,
        "dimensions": {
            "professional": prof,
            "relevance": rel,
            "completeness": comp,
            "logic": logic,
            "depth": depth,
            "communication": comm
        },
        "evidence": evidence,
        "weaknesses": weaknesses,
        "missing_knowledge": missing,
        "suggestions": suggestions,
        "next_action": action
    }

def generate_adaptive_mock_question(
    job_title: str, seq: int = 1, last_question: str = None, last_answer: str = None,
    last_score: float = None, used_texts: List[str] = None
) -> Dict[str, Any]:
    """按岗位大类选题的 Mock 出题引擎。

    先识别 job_title 所属大类（技术/非技术均覆盖），再从对应出题池取题：
    - 首题（seq==1）：取该大类基础题；
    - 答得差（消极/过短/低分）：降难取 EASY 题（基础诊断）；
    - 答得好（高分/有深度）：升难取 HARD 题（深度探究）；
    - 其余：按 seq 轮转取下一道题。
    始终优先避开本场已用题干。
    """
    category = detect_job_category(job_title)
    used = list(used_texts or [])
    if last_question:
        used.append(last_question)

    def pick(prefer_difficulty=None):
        q = dict(_pick_category_question(category, seq, used_texts=used, prefer_difficulty=prefer_difficulty))
        q["hints"] = q.get("hints") or "回答时请结合真实经历，先给结论再分点展开，尽量给出可量化的结果"
        return q

    if seq == 1 or not last_question or not last_answer:
        return pick(prefer_difficulty="MEDIUM")

    ans = (last_answer or "").strip()
    negative_patterns = ["不知道", "没用过", "随便", "不会", "不懂", "不清楚", "没接触过", "跳过", "没做过"]
    is_negative = any(p in ans for p in negative_patterns)
    is_poor = is_negative or len(ans) < 12 or (last_score is not None and last_score < 65)
    is_strong = (last_score is not None and last_score >= 80) or len(ans) >= 150

    if is_poor:
        q = pick(prefer_difficulty="EASY")
        if q["stage"] not in ("综合素养", "压力应对"):
            q["stage"] = "基础诊断"
        return q
    if is_strong:
        return pick(prefer_difficulty="HARD")
    return pick()

def generate_mock_report(interview_id: int, total_questions: int, scores: List[float] = None,
                         qa_pairs: List[Dict[str, Any]] = None, job_title: str = None) -> Dict[str, Any]:
    # 严格基于实际答题得分计算，不瞎编
    if scores and len(scores) > 0:
        avg_score = round(sum(scores) / len(scores), 1)
    else:
        avg_score = 40.0  # 没答题就给低分

    # 表现等级
    if avg_score >= 85:
        perf = "表现优异"
    elif avg_score >= 75:
        perf = "表现良好"
    elif avg_score >= 60:
        perf = "基本达标"
    elif avg_score >= 45:
        perf = "有待提升"
    else:
        perf = "基础薄弱"

    # 雷达维度名按岗位类型自适应：非技术岗用"业务理解"替代"系统设计"
    dim_names = report_dimension_names(job_title or "")
    w = _report_wording(job_title or "")
    jitter = [(-4, 4), (-5, 5), (-6, 4), (-3, 5), (-4, 4)]
    dim_scores = {
        name: round(max(20, min(98, avg_score + random.uniform(lo, hi))), 1)
        for name, (lo, hi) in zip(dim_names, jitter)
    }

    # 根据分数分档生成反馈内容（措辞随岗位类型切换）
    if avg_score >= 80:
        strengths = [
            f"{w['core_label']}基础扎实：核心概念理解准确，能结合实际项目场景展开说明",
            "回答逻辑清晰：分点阐述有条理，能主动说明方案的取舍与边界",
            "具备全局思维：不仅讲做法，还能联系真实业务场景中的实际问题"
        ]
        weaknesses = [
            w["high_extra"],
            "量化数据（如业务指标、提升幅度）可更具体"
        ]
        suggestions = [w["high_sugg"]]
        summary = f"综合评分 {avg_score} 分，整体表现优异。{w['summary_hi']}"

    elif avg_score >= 65:
        strengths = [
            f"对核心{w['core_label']}概念有基本认知，能回答出主要要点",
            "回答围绕题目展开，相关性较好"
        ]
        weaknesses = [
            w["mid_weak"],
            "缺少项目实战案例与量化数据支撑"
        ]
        suggestions = [
            w["mid_sugg"],
            "用 STAR 法则组织回答：情境-任务-行动-结果，增强说服力"
        ]
        summary = f"综合评分 {avg_score} 分，整体表现中等。{w['summary_mid']}建议针对薄弱环节进行系统性补强。"

    elif avg_score >= 50:
        strengths = [
            "基本理解题意，能给出部分相关回答"
        ]
        weaknesses = [
            f"回答内容较浅，缺乏{w['core_label']}细节与原理说明",
            "结构不够清晰，知识点覆盖不全"
        ]
        suggestions = [
            "先夯实基础概念，再深入进阶内容，循序渐进",
            "多做模拟面试练习，提升临场组织语言的能力"
        ]
        summary = f"综合评分 {avg_score} 分，基础有待加强。{w['summary_low']}"

    else:
        strengths = [
            "态度认真，能尝试回答问题"
        ]
        weaknesses = [
            f"对题目考察的核心{w['core_label']}点缺乏基本认知",
            "回答内容过于简略，未能展开说明"
        ]
        suggestions = [
            w["low_sugg"],
            "面试中遇到不会的问题，可以先说明已知的相关背景，展现思考过程",
            f"推荐：针对目标岗位的核心要求，制定分阶段学习计划"
        ]
        summary = f"综合评分 {avg_score} 分，目前基础较薄弱。{w['summary_low']}"

    return {
        "total_score": avg_score,
        "performance_level": perf,
        "dimension_scores": dim_scores,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "suggestions": suggestions,
        "summary": summary
    }

def generate_mock_learning_tasks() -> List[Dict[str, Any]]:
    return [
        {
            "title": "夯实 Java 并发与 JVM 底层基础",
            "competency_name": "Java",
            "stage": "第一阶段 · 基础夯实",
            "priority": "HIGH",
            "reason": "面试高频考察 JMM、锁机制与 GC 调优，是岗位 JD 的核心要求",
            "action_type": "READING"
        },
        {
            "title": "精读 Redis 分布式锁与 Redisson 源码实现",
            "competency_name": "Redis",
            "stage": "第一阶段 · 基础夯实",
            "priority": "HIGH",
            "reason": "在面试中针对缓存击穿与分布式锁细节仍有提升空间",
            "action_type": "INTERVIEW_PRACTICE"
        },
        {
            "title": "MySQL 深入调优：慢查询日志排查与执行计划全解",
            "competency_name": "MySQL",
            "stage": "第二阶段 · 专项强化",
            "priority": "HIGH",
            "reason": "岗位要求熟练掌握 B+ 树索引覆盖与聚集索引调优",
            "action_type": "INTERVIEW_PRACTICE"
        },
        {
            "title": "完成 1 次 Redis/MySQL 专项模拟面试并复盘",
            "competency_name": "综合表达",
            "stage": "第二阶段 · 专项强化",
            "priority": "MEDIUM",
            "reason": "通过定向模拟检验专项强化成果，形成可量化的提升证据",
            "action_type": "INTERVIEW_PRACTICE"
        },
        {
            "title": "分布式系统高可用设计：发号器与防重幂等设计演练",
            "competency_name": "系统设计",
            "stage": "第三阶段 · 架构进阶",
            "priority": "MEDIUM",
            "reason": "强化面对架构深挖题的结构化设计与表达输出",
            "action_type": "PROJECT"
        },
        {
            "title": "高并发系统设计模拟面试冲刺",
            "competency_name": "系统设计",
            "stage": "第三阶段 · 架构进阶",
            "priority": "MEDIUM",
            "reason": "综合检验架构进阶成果，冲刺目标岗位终面",
            "action_type": "INTERVIEW_PRACTICE"
        }
    ]
