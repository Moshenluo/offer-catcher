"""
模块一：情报官 - JD深度解码 + HR视角模拟 + 公司洞察
"""
import streamlit as st


def _show_ai_error(error: Exception):
    st.error(f"分析失败：{error}")


def render(engine, jd_text: str, resume_text: str, company_name: str = ""):
    """渲染情报官模块UI"""
    st.markdown("""
    <div class="module-hero module-intel">
        <span class="eyebrow">STEP 1 · 岗位情报扫描</span>
        <h2>🔍 情报官</h2>
        <p>先把JD翻译成人话：识别岗位真正考查的能力、HR初筛时会抓住的证据，以及面试前必须核验的公司信息。</p>
        <div class="chips">
            <span class="chip">JD潜台词</span>
            <span class="chip">HR 6秒扫描</span>
            <span class="chip">公司认知话题</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📋 JD深度解码", "👁️ HR视角模拟", "🏢 公司情报"])

    # ── Tab 1: JD深度解码 ──
    with tab1:
        st.markdown("### 📋 JD深度解码")
        st.markdown(
            '<div class="module-note note-intel"><strong>适合先做：</strong>'
            '每一条岗位要求背后都有筛选逻辑，本模块会把JD拆成能力、证据和行动优先级。</div>',
            unsafe_allow_html=True
        )
        with st.expander("建议粘贴的JD信息"):
            st.markdown(
                "岗位职责、任职要求、加分项、岗位地点、招聘对象、业务方向。"
                "信息越完整，解码出的能力优先级越稳定。"
            )

        if st.button("🔍 开始解码", key="btn_jd_decode", use_container_width=True):
            with st.spinner("正在深度解读JD..."):
                try:
                    result = engine.analyze_jd(jd_text)
                    st.markdown(result)
                    if resume_text:
                        st.success("下一步：切到「HR视角模拟」查看这份简历能否通过初筛，或进入「简历军师」做能力差距诊断。")
                    else:
                        st.info("下一步：上传简历后，可继续开启HR视角模拟和简历差距诊断。")
                except Exception as e:
                    _show_ai_error(e)

    # ── Tab 2: HR视角模拟 ──
    with tab2:
        st.markdown("### 👁️ HR视角模拟")
        st.markdown(
            '<div class="module-note note-intel"><strong>适合上传简历后做：</strong>'
            '模拟HR初筛，直接指出哪些信息会被看见、跳过或质疑。</div>',
            unsafe_allow_html=True
        )
        with st.expander("输出会重点检查什么"):
            st.markdown("学历/专业门槛、相关项目证据、技能关键词、量化成果、与JD无关的信息噪音。")

        if resume_text:
            if st.button("👀 开启HR视角", key="btn_hr_view", use_container_width=True):
                with st.spinner("正在模拟HR筛选视角..."):
                    try:
                        result = engine.hr_perspective(jd_text, resume_text)
                        st.markdown(result)
                        st.success("下一步：进入「简历军师」做能力建模，并把高风险经历改写成更贴合JD的表达。")
                    except Exception as e:
                        _show_ai_error(e)
        else:
            st.warning("⚠️ 请先在侧边栏上传简历，才能使用HR视角模拟")

    # ── Tab 3: 公司情报 ──
    with tab3:
        st.markdown("### 🏢 公司/行业情报")
        st.markdown(
            '<div class="module-note note-intel"><strong>适合面试前做：</strong>'
            '把公司认知整理成可核验、可表达、可用于反问的面试素材。</div>',
            unsafe_allow_html=True
        )
        with st.expander("使用提示"):
            st.markdown("本模块不联网核验新闻，会把不确定事实标记为待核验；面试前请用官网、招聘页、财报或公众号补证据。")

        if company_name and "company_name" not in st.session_state:
            st.session_state.company_name = company_name
        company_name = st.text_input("公司名称", placeholder="如：腾讯、字节跳动、OPPO",
                                     key="company_name")

        if st.button("📡 获取情报", key="btn_company", use_container_width=True):
            if not company_name:
                st.warning("请先输入公司名称")
            else:
                with st.spinner(f"正在分析 {company_name} 相关信息..."):
                    try:
                        result = engine.company_insight(jd_text, company_name)
                        st.markdown(result)
                        st.success("下一步：把其中标注为「待核验」的信息补证据，再放进面试自我介绍或反问环节。")
                    except Exception as e:
                        _show_ai_error(e)
