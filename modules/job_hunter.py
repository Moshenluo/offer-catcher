"""
模块四：岗位猎手 - 基于简历推荐方向 + 搜集最新岗位
"""
from datetime import datetime

import streamlit as st

from utils.job_search import (
    build_company_search_links,
    build_external_search_links,
    fetch_tencent_jobs,
    infer_job_keywords,
    infer_job_recommendations,
)


def render(resume_text: str, jd_text: str = ""):
    """渲染岗位猎手模块UI"""
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

    keywords = infer_job_keywords(resume_text, jd_text)
    recommendations = infer_job_recommendations(resume_text, jd_text)

    with tab1:
        st.markdown("### 🎯 推荐求职方向")
        st.markdown(
            '<div class="module-note note-jobs"><strong>根据简历自动推断：</strong>'
            '系统会从技能、项目和经历里提取适合搜索的岗位关键词。你也可以手动改关键词。</div>',
            unsafe_allow_html=True
        )

        if resume_text:
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
        else:
            st.warning("请先上传简历，或点击左侧「换一套示例材料」。")

        st.info("推荐使用方式：先选一个关键词搜岗位，再把感兴趣岗位的JD复制到左侧，进入「情报官」和「简历军师」。")

    with tab2:
        st.markdown("### 🔎 最新岗位搜集")
        st.markdown(
            '<div class="module-note note-jobs"><strong>数据来源：</strong>'
            '可实时展示腾讯招聘公开接口返回的岗位；同时提供字节、阿里、美团、百度、网易等官方入口和招聘平台入口，岗位实时性以原站为准。</div>',
            unsafe_allow_html=True
        )

        default_keyword = keywords[0] if keywords else "数据分析"
        keyword = st.text_input("岗位关键词", value=default_keyword, key="job_search_keyword")
        page_size = st.slider("展示岗位数量", 3, 12, 8, key="job_search_size")

        if st.button("搜集最新岗位", key="btn_fetch_jobs", use_container_width=True):
            if not keyword.strip():
                st.warning("请输入岗位关键词")
            else:
                with st.spinner("正在搜集最新岗位并整理岗位速览..."):
                    try:
                        result = fetch_tencent_jobs(keyword.strip(), page_size=page_size)
                    except Exception as e:
                        st.error(f"岗位搜集失败：{e}")
                        result = None

                if result:
                    st.success(
                        f"已搜集到 {result['count']} 条相关岗位，"
                        f"下方展示前 {len(result['posts'])} 条。更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"
                    )
                    for idx, post in enumerate(result["posts"], 1):
                        with st.container(border=True):
                            st.markdown(f"#### {idx}. {post.title}")
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
