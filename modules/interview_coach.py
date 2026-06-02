"""
模块三：面试教练 - 高频题预测 + STAR答案 + 模拟面试
"""
import streamlit as st
from utils.ui_helpers import render_copyable_ai_output


def _show_ai_error(error: Exception):
    st.error(f"生成失败：{error}")


def render(engine, jd_text: str, resume_text: str, company_name: str = ""):
    """渲染面试教练模块UI"""
    st.markdown("""
    <div class="module-hero module-interview">
        <span class="eyebrow">STEP 3 · 面试表达训练</span>
        <h2>🎤 面试教练</h2>
        <p>把简历经历转换成能讲出口的答案：先预测高频题，再搭STAR框架，最后用模拟反馈打磨表达。</p>
        <div class="chips">
            <span class="chip">题目预测</span>
            <span class="chip">STAR答案</span>
            <span class="chip">模拟反馈</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🔮 高频题预测", "📋 STAR模板", "🎭 模拟面试"])

    # ── Tab 1: 高频题预测 ──
    with tab1:
        st.markdown("### 🔮 面试题预测")
        st.markdown(
            '<div class="module-note note-interview"><strong>先确定题库：</strong>'
            '根据JD、公司和你的简历，预测最可能被深挖的问题。</div>',
            unsafe_allow_html=True
        )
        with st.expander("建议补充"):
            st.markdown("填写公司名称，并在JD中保留技术栈、业务方向和岗位级别；上传简历后可生成更贴近个人经历的问题。")

        company = company_name or st.text_input(
            "公司名称（用于定制面试题）",
            placeholder="如：OPPO、腾讯、字节跳动",
            key="interview_company"
        )

        if st.button("🔮 预测面试题", key="btn_questions",
                    use_container_width=True):
            if not company:
                st.warning("请输入公司名称")
            else:
                with st.spinner("正在分析并生成面试题..."):
                    try:
                        resume_brief = resume_text[:800] if resume_text else "未提供简历"
                        result = engine.generate_questions(jd_text, company, resume_brief)
                        render_copyable_ai_output(result, "interview_questions", "面试题预测")
                        st.success("下一步：挑一道最高频或最难的问题，切到「STAR模板」生成回答框架。")
                    except Exception as e:
                        _show_ai_error(e)

    # ── Tab 2: STAR答案模板 ──
    with tab2:
        st.markdown("### 📋 STAR答案生成器")
        st.markdown(
            '<div class="module-note note-interview"><strong>再搭回答框架：</strong>'
            '把真实经历拆成背景、任务、行动、结果，避免回答散、泛、短。</div>',
            unsafe_allow_html=True
        )
        with st.expander("适合输入的问题类型"):
            st.markdown("项目深挖、失败复盘、冲突协作、技术挑战、为什么投递该岗位、职业规划。")

        if st.button("填入示例面试题", key="btn_sample_star", use_container_width=True):
            st.session_state.star_question = "请介绍一个你用数据分析或AI方法解决真实问题的项目，你具体负责了什么？"
            st.rerun()

        question = st.text_area(
            "输入面试题",
            placeholder="如：请介绍一下你在实习中遇到的最大技术挑战，你是如何解决的？",
            key="star_question",
            height=100
        )

        if st.button("🎯 生成STAR答案", key="btn_star",
                    use_container_width=True):
            if not question:
                st.warning("请输入面试题")
            elif not resume_text:
                st.warning("请先在侧边栏上传简历，才能基于你的经历生成答案")
            else:
                with st.spinner("正在基于你的经历生成STAR答案..."):
                    try:
                        result = engine.generate_star_answer(question, resume_text, jd_text)
                        render_copyable_ai_output(result, "star_answer", "STAR回答模板")
                        st.success("下一步：把STAR模板改成自己的口语版，再切到「模拟面试」让AI面试官打分。")
                    except Exception as e:
                        _show_ai_error(e)

    # ── Tab 3: 模拟面试 ──
    with tab3:
        st.markdown("### 🎭 模拟面试练习")
        st.markdown(
            '<div class="module-note note-interview"><strong>最后反复练：</strong>'
            '输入你的口语版回答，系统会指出亮点、漏洞和下一版该怎么改。</div>',
            unsafe_allow_html=True
        )
        with st.expander("回答建议"):
            st.markdown("尽量按背景、任务、行动、结果来写；如果回答很短，系统会重点指出信息缺口。")

        if st.button("填入示例回答", key="btn_sample_mock", use_container_width=True):
            st.session_state.mock_question = "请介绍一个你用数据分析或AI方法解决真实问题的项目。"
            st.session_state.mock_answer = (
                "我做过一个求职岗位匹配分析项目，目标是帮助学生判断简历和JD的匹配度。"
                "我负责清洗JD和简历文本，提取技能关键词，并用相似度方法生成匹配评分。"
                "最后我把结果做成可视化报告，用来提示学生优先优化哪些经历。"
            )
            st.rerun()

        mock_q = st.text_area(
            "面试题目",
            placeholder="输入面试官问的问题...",
            key="mock_question",
            height=80
        )

        mock_a = st.text_area(
            "你的回答",
            placeholder="写下你的回答（语音转文字或打字输入）...",
            key="mock_answer",
            height=150
        )

        if st.button("📊 评估我的回答", key="btn_mock",
                    use_container_width=True):
            if not mock_q or not mock_a:
                st.warning("请输入面试题和你的回答")
            else:
                with st.spinner("面试官正在评估..."):
                    try:
                        resume_brief = resume_text[:500] if resume_text else "未提供简历"
                        result = engine.mock_interview(mock_q, mock_a,
                                                       resume_brief, jd_text)
                        render_copyable_ai_output(result, "mock_interview", "模拟面试反馈")
                        st.success("下一步：根据反馈重写回答，再评估一次，直到评分和表达都稳定。")
                    except Exception as e:
                        _show_ai_error(e)
