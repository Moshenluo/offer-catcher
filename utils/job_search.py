"""
岗位搜索工具 - 基于简历关键词拉取公开招聘信息
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, List
from urllib.parse import quote_plus

import requests


TENCENT_QUERY_URL = "https://careers.tencent.com/tencentcareer/api/post/Query"
TENCENT_DETAIL_URL = "https://careers.tencent.com/jobdesc.html?postId={post_id}"


KEYWORD_RULES = [
    ("NLP", ["NLP", "自然语言处理", "BERT", "Transformer", "LLM", "Embedding", "RAG", "文本"]),
    ("算法工程", ["机器学习", "深度学习", "PyTorch", "TensorFlow", "模型", "推荐系统", "算法"]),
    ("数据分析", ["数据分析", "SQL", "Pandas", "可视化", "看板", "转化", "漏斗"]),
    ("AI产品", ["AIGC", "AI产品", "需求分析", "产品", "用户", "策略"]),
    ("产品运营", ["运营", "活动", "增长", "内容", "渠道", "复盘"]),
    ("推荐系统", ["推荐", "协同过滤", "召回", "排序", "LightGBM"]),
]

ROLE_PROFILES = {
    "数据分析": {
        "intro": "面向业务增长、用户行为、商业化或游戏场景，把数据转成业务判断和策略建议。",
        "fit": "适合有 SQL、Python、指标体系、A/B 测试、可视化或业务分析经历的同学。",
        "prep": "重点补强指标拆解、实验设计、业务复盘和数据结论表达。",
    },
    "AI产品": {
        "intro": "围绕 AI 能力设计产品方案，把模型能力、用户需求和落地场景连接起来。",
        "fit": "适合既懂用户/需求分析，又有 AIGC、LLM、数据或技术项目经历的同学。",
        "prep": "重点补强需求文档、竞品分析、Prompt/Agent 方案和效果评估方法。",
    },
    "NLP": {
        "intro": "处理文本理解、生成、检索、问答、RAG、对话系统等自然语言相关任务。",
        "fit": "适合有 LLM、Transformer、Embedding、RAG、文本分类或信息抽取项目的同学。",
        "prep": "重点补强模型原理、数据构造、评测指标和工程部署表达。",
    },
    "产品运营": {
        "intro": "围绕用户增长、内容生态、活动策略和留存转化，持续推动产品目标达成。",
        "fit": "适合有社群、活动、内容、增长、用户研究或数据复盘经历的同学。",
        "prep": "重点补强目标拆解、用户分层、活动复盘和可量化结果。",
    },
    "推荐系统": {
        "intro": "负责内容、商品、广告或社交场景下的召回、排序、特征和效果优化。",
        "fit": "适合有机器学习、排序模型、召回策略、特征工程或推荐项目经历的同学。",
        "prep": "重点补强推荐链路、离线/在线指标、实验设计和模型迭代叙述。",
    },
    "算法工程": {
        "intro": "围绕机器学习、深度学习或业务算法问题，完成建模、训练、评估和上线优化。",
        "fit": "适合有 PyTorch/TensorFlow、机器学习竞赛、科研或工程项目经历的同学。",
        "prep": "重点补强算法选择理由、数据处理、指标提升和工程实现细节。",
    },
}


@dataclass
class JobPost:
    company: str
    source: str
    title: str
    location: str
    business_group: str
    category: str
    update_time: str
    post_id: str
    detail_url: str
    description: str = ""


def infer_job_keywords(resume_text: str, jd_text: str = "", limit: int = 5) -> List[str]:
    """从简历和JD中推断适合检索的岗位关键词。"""
    combined = f"{resume_text}\n{jd_text}".lower()
    scored = []
    for keyword, signals in KEYWORD_RULES:
        score = sum(1 for signal in signals if signal.lower() in combined)
        if score:
            scored.append((score, keyword))
    scored.sort(key=lambda item: (-item[0], item[1]))

    keywords = [keyword for _, keyword in scored]
    for fallback in ["数据分析", "AI产品", "算法工程", "产品运营", "NLP"]:
        if fallback not in keywords:
            keywords.append(fallback)
    return keywords[:limit]


def infer_job_recommendations(resume_text: str, jd_text: str = "", limit: int = 5) -> List[Dict[str, str]]:
    """生成带简介的岗位方向推荐，避免把关键词展示成分数。"""
    keywords = infer_job_keywords(resume_text, jd_text, limit=limit)
    recommendations = []
    combined = f"{resume_text}\n{jd_text}".lower()
    for keyword in keywords:
        profile = ROLE_PROFILES.get(keyword, ROLE_PROFILES["数据分析"])
        signals = [
            signal for role, role_signals in KEYWORD_RULES
            if role == keyword
            for signal in role_signals
            if signal.lower() in combined
        ]
        recommendations.append({
            "keyword": keyword,
            "intro": profile["intro"],
            "fit": profile["fit"],
            "prep": profile["prep"],
            "evidence": "、".join(signals[:4]) if signals else "根据通用求职路径推荐，可结合目标 JD 再校准",
        })
    return recommendations


def fetch_tencent_jobs(keyword: str, page_size: int = 8, page_index: int = 1) -> Dict[str, object]:
    """调用腾讯招聘公开岗位查询接口。"""
    params = {
        "timestamp": str(int(time.time() * 1000)),
        "countryId": "",
        "cityId": "",
        "bgIds": "",
        "productId": "",
        "categoryId": "",
        "parentCategoryId": "",
        "attrId": "",
        "keyword": keyword,
        "pageIndex": str(page_index),
        "pageSize": str(page_size),
        "language": "zh-cn",
        "area": "cn",
    }
    response = requests.get(
        TENCENT_QUERY_URL,
        params=params,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=12,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("Code") != 200:
        raise RuntimeError(f"腾讯招聘接口返回异常：{payload.get('Message') or payload.get('Code')}")

    data = payload.get("Data", {})
    posts = []
    for item in data.get("Posts", []):
        post_id = str(item.get("PostId") or "")
        posts.append(JobPost(
            company="腾讯",
            source="腾讯招聘",
            title=item.get("RecruitPostName") or "未命名岗位",
            location=item.get("LocationName") or "地点待确认",
            business_group=item.get("BGName") or "BG待确认",
            category=item.get("CategoryName") or "类别待确认",
            update_time=item.get("LastUpdateTime") or "更新时间待确认",
            post_id=post_id,
            detail_url=item.get("PostURL") or TENCENT_DETAIL_URL.format(post_id=post_id),
            description=_clean_description(item.get("Responsibility") or ""),
        ))
    return {
        "count": data.get("Count", 0),
        "page_index": page_index,
        "page_size": page_size,
        "posts": posts,
        "source_url": response.url,
    }


def build_external_search_links(keyword: str) -> Dict[str, str]:
    encoded = quote_plus(keyword)
    return {
        "腾讯招聘": f"https://careers.tencent.com/search.html?keyword={encoded}",
        "牛客校招": f"https://www.nowcoder.com/jobs/school?query={encoded}",
        "实习僧": f"https://www.shixiseng.com/interns?keyword={encoded}",
        "BOSS直聘": f"https://www.zhipin.com/web/geek/job?query={encoded}",
        "猎聘校园": f"https://campus.liepin.com/xycompany/?key={encoded}",
    }


def build_company_search_links(keyword: str) -> Dict[str, str]:
    encoded = quote_plus(keyword)
    return {
        "腾讯": f"https://careers.tencent.com/search.html?keyword={encoded}",
        "字节跳动": f"https://jobs.bytedance.com/campus/position?keywords={encoded}",
        "阿里巴巴": f"https://talent.alibaba.com/?keyword={encoded}",
        "美团": f"https://zhaopin.meituan.com/web/campus?keyword={encoded}",
        "百度": f"https://talent.baidu.com/jobs/list?search={encoded}",
        "网易": f"https://hr.163.com/job-list.html?keyword={encoded}",
    }


def _clean_description(text: str, limit: int = 180) -> str:
    cleaned = " ".join(part.strip() for part in text.replace("\r", "\n").splitlines() if part.strip())
    if len(cleaned) > limit:
        return f"{cleaned[:limit]}..."
    return cleaned or "岗位职责待在详情页确认。"
