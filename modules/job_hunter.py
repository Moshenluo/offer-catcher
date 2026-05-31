"""
模块四：岗位猎手 - 基于简历推荐方向 + 搜集最新岗位
"""
import json
import math
import re
from datetime import datetime

import streamlit as st

from utils.llm_client import LLMEngine
from utils.job_search import (
    build_company_search_links,
    build_external_search_links,
    fetch_tencent_jobs,
    infer_job_keywords,
    infer_job_recommendations,
)


def _init_job_engine():
    return LLMEngine()


def render(resume_text: str, jd_text: str = ""):
    """渲染岗位猎手模块UI"""
    source_signature = str(hash((resume_text, jd_text)))
    if st.session_state.get("job_recommend_source") != source_signature:
        st.session_state["job_recommend_source"] = source_signature
        st.session_state.pop("ai_job_recommendations", None)
        st.session_state.pop("ai_job_error", None)

    st.markdown("""
    <div class="module-hero module-jobs">
        <span class="eyebrow">STEP 0 · 先找到值得投的岗位</span>
        <h2>🧭 岗位猎手</h2>
        <p>根据你的简历提取求职方向，展示岗位画像，并连接企业官网与招聘平台。先找到合适岗位，再进入JD解码、简历诊断和面试准备。</p>
        <div class="chips">
            <span class="chip">岗位画像</span>
            <span class="chip">实时职位</span>
            <span class="chip">多公司入口</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🎯 智能推荐", "🔎 最新岗位搜集"])

    fallback_keywords = infer_job_keywords(resume_text, jd_text)
    fallback_recommendations = infer_job_recommendations(resume_text, jd_text)

    with tab1:
        st.markdown("### 🎯 推荐求职方向")
        st.markdown(
            '<div class="module-note note-jobs"><strong>根据简历自动推断：</strong>'
            '优先调用 AI 读取简历，生成更细分的岗位方向；如果 API 不可用，会回退到本地规则推荐。</div>',
            unsafe_allow_html=True
        )

        if resume_text:
            if st.button("AI 深度分析岗位方向", key="btn_ai_job_recommend", use_container_width=True):
                with st.spinner("正在调用 AI 阅读简历并生成细分岗位方向..."):
                    try:
                        engine = _init_job_engine()
                        raw = engine.recommend_jobs(resume_text, jd_text)
                        ai_items = _parse_ai_recommendations(raw)
                        st.session_state["ai_job_recommendations"] = ai_items
                        st.session_state.pop("ai_job_error", None)
                        first_keyword = _recommended_search_keywords(ai_items, fallback_keywords)[0]
                        if first_keyword:
                            st.session_state["job_search_keyword"] = first_keyword
                            st.session_state["job_page"] = 1
                    except Exception as exc:
                        st.session_state["ai_job_error"] = str(exc)

            ai_recommendations = st.session_state.get("ai_job_recommendations")
            if ai_recommendations:
                st.success("已基于简历生成细分岗位推荐。")
                _render_ai_recommendations(ai_recommendations)
            else:
                if st.session_state.get("ai_job_error"):
                    st.warning(f"AI 推荐暂不可用，已展示本地备用推荐。原因：{st.session_state['ai_job_error']}")
                    _render_rule_recommendations(fallback_recommendations)
                else:
                    st.info("上传简历后，点击上方按钮才会开始分析岗位方向；这里不会在未确认前自动生成推荐。")
        else:
            st.warning("请先上传简历，或点击左侧「换一套示例材料」。")

        st.info("推荐使用方式：先选一个关键词搜岗位，再把感兴趣岗位的JD复制到左侧，进入「情报官」和「简历军师」。")

    with tab2:
        st.markdown("### 🔎 最新岗位搜集")
        st.markdown(
            '<div class="module-note note-jobs"><strong>数据来源：</strong>'
            '当前可分页实时展示的是腾讯招聘公开接口；字节、阿里、美团、百度、网易等放在官方入口区，点击后在原站查看最新岗位。</div>',
            unsafe_allow_html=True
        )

        keyword_options = _recommended_search_keywords(
            st.session_state.get("ai_job_recommendations") or [],
            fallback_keywords,
        )
        selected_keyword = st.selectbox(
            "推荐关键词",
            keyword_options,
            index=0,
            key="job_keyword_choice",
            help="优先使用短关键词搜索，避免过窄的岗位名搜不到结果。你也可以在下方手动微调。",
        )
        default_keyword = _default_search_keyword(keyword_options)
        current_keyword = st.session_state.get("job_search_keyword", default_keyword)
        if selected_keyword and selected_keyword != current_keyword and st.button("使用该推荐关键词", use_container_width=True):
            st.session_state["job_search_keyword"] = selected_keyword
            st.session_state.pop("job_query", None)
            st.session_state.pop("job_match_results", None)
            st.session_state.pop("job_match_source", None)
            st.rerun()
        keyword = st.text_input("岗位关键词", value=default_keyword, key="job_search_keyword")
        page_size = st.slider("展示岗位数量", 3, 12, 8, key="job_search_size")

        if st.button("搜集最新岗位", key="btn_fetch_jobs", use_container_width=True):
            if not keyword.strip():
                st.warning("请输入岗位关键词")
            else:
                st.session_state["job_query"] = keyword.strip()
                st.session_state["job_page"] = 1
                st.session_state.pop("job_match_results", None)
                st.session_state.pop("job_match_source", None)

        if st.session_state.get("job_query"):
            query = st.session_state["job_query"]
            page_size = int(page_size)
            current_page = int(st.session_state.get("job_page", 1))
            with st.spinner("正在搜集最新岗位并整理岗位速览..."):
                try:
                    result = fetch_tencent_jobs(query, page_size=page_size, page_index=current_page)
                except Exception as e:
                    st.error(f"岗位搜集失败：{e}")
                    result = None

            if result:
                total = int(result["count"] or 0)
                total_pages = max(1, math.ceil(total / page_size))
                current_page = min(current_page, total_pages)
                st.session_state["job_page"] = current_page
                start_no = (current_page - 1) * page_size + 1
                end_no = start_no + len(result["posts"]) - 1
                range_text = f"{start_no}-{end_no} 条" if result["posts"] else "暂无结果"

                st.success(
                    f"腾讯招聘已搜集到 {total} 条「{query}」相关岗位，"
                    f"当前展示第 {current_page}/{total_pages} 页（{range_text}）。"
                    f"更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )

                if not result["posts"]:
                    st.warning("当前关键词没有搜到腾讯岗位，建议换成更短的关键词，或点击下方公司/平台入口继续检索。")
                    st.caption(f"接口来源：{result['source_url']}")
                else:
                    nav_left, nav_mid, nav_right = st.columns([1, 2, 1])
                    with nav_left:
                        if st.button("上一页", disabled=current_page <= 1, use_container_width=True):
                            st.session_state["job_page"] = current_page - 1
                            st.rerun()
                    with nav_mid:
                        selected_page = st.number_input(
                            "跳转页码",
                            min_value=1,
                            max_value=total_pages,
                            value=current_page,
                            step=1,
                            key="job_page_input",
                        )
                        if int(selected_page) != current_page:
                            st.session_state["job_page"] = int(selected_page)
                            st.rerun()
                    with nav_right:
                        if st.button("下一页", disabled=current_page >= total_pages, use_container_width=True):
                            st.session_state["job_page"] = current_page + 1
                            st.rerun()

                    page_match_source = _match_source_key(query, current_page, result["posts"])
                    if resume_text:
                        st.markdown("#### AI 岗位匹配排序")
                        st.caption("点击后会根据你的简历给当前页岗位打分，并把高匹配岗位排在前面。")
                        if st.button("AI 评估当前页岗位匹配度", key="btn_rank_current_jobs", use_container_width=True):
                            with st.spinner("正在根据你的简历给当前页岗位排序..."):
                                try:
                                    engine = _init_job_engine()
                                    if not hasattr(engine, "rank_job_matches"):
                                        raise RuntimeError("AI引擎版本仍是旧缓存，请在 Streamlit Cloud 点击 Reboot app 后重试。")
                                    job_payload = [_post_to_payload(post) for post in result["posts"]]
                                    raw = engine.rank_job_matches(resume_text, query, job_payload)
                                    st.session_state["job_match_source"] = page_match_source
                                    st.session_state["job_match_results"] = _parse_match_results(raw)
                                    st.rerun()
                                except Exception as exc:
                                    st.error(f"岗位匹配评估失败：{exc}")
                    else:
                        st.info("上传简历后，可以让 AI 对当前页岗位做匹配度排序。")

                    display_posts = _sort_posts_by_match(result["posts"], page_match_source)
                    for offset, post in enumerate(display_posts, start_no):
                        match = _match_for_post(post.post_id, page_match_source)
                        with st.container(border=True):
                            st.markdown(f"#### {offset}. {post.title}")
                            if match:
                                _render_match_summary(match)
                            else:
                                st.caption("还未评估匹配度。点击上方「AI 评估当前页岗位匹配度」后，这里会显示匹配分。")
                            c1, c2, c3 = st.columns(3)
                            c1.markdown(f"**公司/来源**：{post.company} · {post.source}")
                            c2.markdown(f"**地点**：{post.location}")
                            c3.markdown(f"**更新**：{post.update_time}")
                            st.markdown(f"**部门/事业群**：{post.business_group}")
                            st.markdown(f"**岗位类别**：{post.category}")
                            st.markdown(f"**职位速览**：{post.description}")
                            st.link_button("打开腾讯招聘详情", post.detail_url, use_container_width=True)

                    st.caption(f"接口来源：{result['source_url']}")

        st.markdown("#### 更多公司官方入口")
        st.caption("这些入口会带着当前关键词跳转到各公司官网，由原站展示最新岗位。")
        company_links = build_company_search_links(keyword or default_keyword)
        for row_start in range(0, len(company_links), 3):
            link_cols = st.columns(3)
            for col, (label, url) in zip(link_cols, list(company_links.items())[row_start:row_start + 3]):
                with col:
                    st.link_button(label, url, use_container_width=True)

        st.markdown("#### 更多招聘平台检索")
        platform_links = build_external_search_links(keyword or default_keyword)
        link_cols = st.columns(len(platform_links))
        for col, (label, url) in zip(link_cols, platform_links.items()):
            with col:
                st.link_button(label, url, use_container_width=True)


def _parse_ai_recommendations(raw: str):
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError("AI 未返回可解析的 JSON")
    data = json.loads(match.group(0))
    items = data.get("recommendations", [])
    if not isinstance(items, list) or not items:
        raise ValueError("AI 推荐结果为空")
    return items[:7]


def _parse_match_results(raw: str):
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if not match:
        raise ValueError("AI 未返回可解析的 JSON")
    data = json.loads(match.group(0))
    items = data.get("matches", [])
    if not isinstance(items, list):
        raise ValueError("AI 匹配结果格式异常")
    normalized = {}
    for item in items:
        if not isinstance(item, dict) or not item.get("post_id"):
            continue
        normalized[str(item["post_id"])] = {
            "score": _normalize_match_score(item.get("score")),
            "decision": str(item.get("decision") or "可以尝试"),
            "reason": str(item.get("reason") or "需要结合岗位详情进一步判断。"),
            "resume_angle": str(item.get("resume_angle") or "突出与岗位职责最相关的项目证据。"),
            "risk": str(item.get("risk") or "证据缺口待确认。"),
        }
    return normalized


def _normalize_match_score(value):
    try:
        return max(0, min(100, int(round(float(value)))))
    except (TypeError, ValueError):
        return 60


def _recommended_search_keywords(recommendations, fallback_keywords):
    candidates = []
    for rec in recommendations:
        candidates.extend(rec.get("search_keywords") or [])
        candidates.append(rec.get("keyword"))
        candidates.append(rec.get("title"))
    candidates.extend(fallback_keywords)

    keywords = []
    for item in candidates:
        cleaned = _normalize_search_keyword(item)
        if cleaned and cleaned not in keywords:
            keywords.append(cleaned)
    return keywords[:8] or ["数据分析"]


def _normalize_search_keyword(value):
    if not value:
        return ""
    text = str(value).strip()
    for noise in ["招聘", "急招", "诚聘", "寻找", "招募"]:
        text = text.replace(noise, "")
    for suffix in ["实习生", "实习", "校招", "岗位", "职位", "工程师", "经理", "专员"]:
        text = text.replace(suffix, "")
    text = re.sub(r"[，,、/|]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > 10:
        compact_patterns = [
            "数据分析", "AI产品", "推荐算法", "推荐系统", "产品运营",
            "NLP", "自然语言处理", "机器学习", "算法", "用户研究",
            "商业分析", "数据科学", "游戏数据", "增长运营",
        ]
        for pattern in compact_patterns:
            if pattern.lower() in text.lower():
                return pattern
    return text[:12]


def _default_search_keyword(keyword_options):
    if st.session_state.get("job_search_keyword"):
        return st.session_state["job_search_keyword"]
    return keyword_options[0] if keyword_options else "数据分析"


def _post_to_payload(post):
    return {
        "post_id": post.post_id,
        "title": post.title,
        "company": post.company,
        "location": post.location,
        "business_group": post.business_group,
        "category": post.category,
        "description": post.description,
    }


def _match_source_key(query, page, posts):
    post_ids = ",".join(post.post_id for post in posts)
    return f"{query}:{page}:{post_ids}"


def _match_for_post(post_id, source_key):
    if st.session_state.get("job_match_source") != source_key:
        return None
    return (st.session_state.get("job_match_results") or {}).get(str(post_id))


def _sort_posts_by_match(posts, source_key):
    if st.session_state.get("job_match_source") != source_key:
        return posts
    matches = st.session_state.get("job_match_results") or {}
    return sorted(
        posts,
        key=lambda post: matches.get(str(post.post_id), {}).get("score", -1),
        reverse=True,
    )


def _render_match_summary(match):
    score = match.get("score", 60)
    decision = match.get("decision", "可以尝试")
    color = "#12b886" if score >= 80 else "#f59f00" if score >= 65 else "#f03e3e"
    st.markdown(f"""
    <div style="border:1px solid rgba(0,0,0,.08); border-radius:8px; padding:12px; margin:10px 0; background:#fbfffd;">
        <div style="display:flex; align-items:center; gap:12px; justify-content:space-between;">
            <div>
                <div style="font-size:13px; color:#475569;">AI匹配分</div>
                <div style="font-size:30px; font-weight:800; color:{color}; line-height:1;">{score}<span style="font-size:14px;">/100</span></div>
            </div>
            <div style="padding:6px 10px; border-radius:999px; background:{color}18; color:{color}; font-weight:700;">{decision}</div>
        </div>
        <div style="height:8px; background:#e9ecef; border-radius:999px; margin:10px 0 8px;">
            <div style="width:{score}%; height:8px; background:{color}; border-radius:999px;"></div>
        </div>
        <div style="font-size:14px; line-height:1.65;">
            <strong>匹配理由：</strong>{match.get('reason')}<br>
            <strong>简历主打角度：</strong>{match.get('resume_angle')}<br>
            <strong>风险提醒：</strong>{match.get('risk')}
        </div>
    </div>
    """, unsafe_allow_html=True)


def _render_ai_recommendations(recommendations):
    for row_start in range(0, len(recommendations), 2):
        cols = st.columns(2)
        for col, rec in zip(cols, recommendations[row_start:row_start + 2]):
            title = rec.get("title") or rec.get("keyword") or "推荐岗位"
            keyword = rec.get("keyword") or title
            with col:
                with st.container(border=True):
                    st.markdown(f"#### {title}")
                    st.markdown(f"**匹配度**：{rec.get('match_level', '待确认')}")
                    st.markdown(f"**推荐理由**：{rec.get('why', '证据不足，需要补充')}")
                    st.markdown(f"**岗位简介**：{rec.get('job_intro', '岗位职责需结合具体 JD 确认。')}")
                    tasks = rec.get("typical_tasks") or []
                    if tasks:
                        st.markdown("**典型工作**：" + "；".join(str(item) for item in tasks[:3]))
                    st.markdown(f"**简历补强点**：{rec.get('resume_gap', '建议结合目标 JD 再校准。')}")
                    search_terms = rec.get("search_keywords") or [keyword]
                    st.caption("建议搜索词：" + " / ".join(str(item) for item in search_terms[:4]))
                    links = build_company_search_links(str(keyword))
                    link_cols = st.columns(3)
                    for link_col, (label, url) in zip(link_cols, list(links.items())[:3]):
                        with link_col:
                            st.link_button(label, url, use_container_width=True)


def _render_rule_recommendations(recommendations):
    for row_start in range(0, len(recommendations), 2):
        cols = st.columns(2)
        for col, rec in zip(cols, recommendations[row_start:row_start + 2]):
            with col:
                with st.container(border=True):
                    st.markdown(f"#### {rec['keyword']}")
                    st.markdown(f"**岗位简介**：{rec['intro']}")
                    st.markdown(f"**适合你因为**：{rec['evidence']}")
                    st.markdown(f"**典型匹配画像**：{rec['fit']}")
                    st.markdown(f"**下一步准备**：{rec['prep']}")
                    links = build_company_search_links(rec["keyword"])
                    link_cols = st.columns(3)
                    for link_col, (label, url) in zip(link_cols, list(links.items())[:3]):
                        with link_col:
                            st.link_button(label, url, use_container_width=True)
