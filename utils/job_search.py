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


@dataclass
class JobPost:
    title: str
    location: str
    business_group: str
    category: str
    update_time: str
    post_id: str
    detail_url: str


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


def fetch_tencent_jobs(keyword: str, page_size: int = 8) -> Dict[str, object]:
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
        "pageIndex": "1",
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
            title=item.get("RecruitPostName") or "未命名岗位",
            location=item.get("LocationName") or "地点待确认",
            business_group=item.get("BGName") or "BG待确认",
            category=item.get("CategoryName") or "类别待确认",
            update_time=item.get("LastUpdateTime") or "更新时间待确认",
            post_id=post_id,
            detail_url=TENCENT_DETAIL_URL.format(post_id=post_id),
        ))
    return {
        "count": data.get("Count", 0),
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
