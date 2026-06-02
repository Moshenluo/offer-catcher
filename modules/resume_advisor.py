"""
模块二：简历军师 - 逆向能力建模 + 差距雷达图 + 一键重写简历
"""
import streamlit as st
import plotly.graph_objects as go
import json
import re
from datetime import datetime
from utils.ui_helpers import render_copyable_ai_output

RADAR_DIMENSIONS = ["技术硬实力", "项目经验", "学历背景", "实习经历", "软技能"]


def _show_ai_error(error: Exception):
    st.error(f"分析失败：{error}")


def render(engine, jd_text: str, resume_text: str):
    """渲染简历军师模块UI"""
    st.markdown("""
    <div class="module-hero module-resume">
        <span class="eyebrow">STEP 2 · 简历诊断与改写</span>
        <h2>✍️ 简历军师</h2>
        <p>把“感觉不匹配”变成可解释的差距：先建能力模型，再看雷达图，最后把经历改成更容易过初筛的表达。</p>
        <div class="chips">
            <span class="chip">五维能力模型</span>
            <span class="chip">差距优先级</span>
            <span class="chip">针对JD重写</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🎯 能力建模", "📊 差距雷达图", "📝 一键重写"])

    # ── Tab 1: 逆向能力建模 ──
    with tab1:
        st.markdown("### 🎯 逆向能力建模")
        st.markdown(
            '<div class="module-note note-resume"><strong>先诊断，再改写：</strong>'
            '从JD反推岗位能力模型，并判断你的简历证据够不够支撑这些能力。</div>',
            unsafe_allow_html=True
        )
        with st.expander("建议输入"):
            st.markdown("请上传包含教育背景、项目经历、实习经历、技能栈和成果数据的简历；JD中最好保留加分项和岗位职责。")

        if resume_text:
            if st.button("🧠 开始建模分析", key="btn_capability",
                        use_container_width=True):
                with st.spinner("正在构建能力模型..."):
                    try:
                        result = engine.build_capability_model(jd_text, resume_text)
                        render_copyable_ai_output(result, "capability_model", "能力建模分析")

                        # 尝试提取JSON雷达图数据，存储到session
                        if not _extract_radar_data(result):
                            st.info("未识别到标准雷达图数据。请查看上方文字分析，或重新生成一次能力模型。")
                        else:
                            st.success("下一步：切到「差距雷达图」查看优先补强维度，再到「一键重写」优化对应经历。")
                    except Exception as e:
                        _show_ai_error(e)
        else:
            st.warning("⚠️ 请先在侧边栏上传简历")

    # ── Tab 2: 差距雷达图 ──
    with tab2:
        st.markdown("### 📊 差距雷达图")
        st.markdown(
            '<div class="module-note note-resume"><strong>看优先级：</strong>'
            '只展示AI建模后的雷达图，帮助你判断先补哪一类证据，不平均用力。</div>',
            unsafe_allow_html=True
        )

        # 尝试从session中加载AI分析的数据
        if "radar_data" in st.session_state and st.session_state.radar_data:
            radar_data = st.session_state.radar_data
            _plot_radar(radar_data)

            # 差距总结
            gaps = [(d["维度"], d["JD要求"] - d["你的当前"]) for d in radar_data]
            gaps.sort(key=lambda x: x[1], reverse=True)
            st.markdown("#### 🔴 差距优先级排序")
            for dim, gap in gaps:
                if gap > 0:
                    color = "🔴" if gap >= 3 else "🟠" if gap >= 2 else "🟡"
                    st.markdown(f"{color} **{dim}**：差 {gap} 分 → 优先补足")
            if all(gap <= 0 for _, gap in gaps):
                st.success("当前五个维度均达到或超过JD要求，建议重点打磨表达和面试故事。")
            else:
                st.info("下一步：优先改写差距最大的1-2个维度对应经历，不必平均用力。")
        else:
            st.info("请先在「能力建模」中点击 **开始建模分析**，系统会自动生成雷达图。")

    # ── Tab 3: 一键重写 ──
    with tab3:
        st.markdown("### 📝 一键重写简历")
        st.markdown(
            '<div class="module-note note-resume"><strong>改成可投递表达：</strong>'
            '围绕JD关键词、STAR结构和真实量化证据，重写最影响初筛的部分。</div>',
            unsafe_allow_html=True
        )
        with st.expander("改写原则"):
            st.markdown("只优化表达，不编造经历；缺失的量化结果会用 `[请补充真实数字]` 标出，便于你后续核实补全。")

        rewrite_target = st.selectbox(
            "选择要优化的部分",
            ["整份简历", "实习/工作经历", "项目经历", "技能/证书"],
            format_func=lambda x: {
                "整份简历": "📄 整份简历",
                "实习/工作经历": "💼 实习/工作经历",
                "项目经历": "🚀 项目经历",
                "技能/证书": "🔧 技能/证书",
            }[x],
            key="rewrite_target"
        )

        if resume_text:
            if st.button("✨ 开始优化重写", key="btn_rewrite",
                        use_container_width=True):
                with st.spinner("正在针对JD优化简历..."):
                    try:
                        result = engine.rewrite_resume(jd_text, resume_text, rewrite_target)
                        render_copyable_ai_output(result, "rewrite_resume", "优化简历")

                        # 导出按钮
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        st.download_button(
                            label="📥 下载优化后的简历（Markdown格式）",
                            data=result,
                            file_name=f"优化简历_{timestamp}.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                        st.success("下一步：复制优化后的关键经历，进入「面试教练」生成STAR回答并练习追问。")
                    except Exception as e:
                        _show_ai_error(e)
        else:
            st.warning("⚠️ 请先在侧边栏上传简历")


def _extract_radar_data(text: str) -> bool:
    """从AI输出中提取雷达图JSON数据"""
    try:
        # 尝试匹配JSON块
        json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if not json_match:
            json_match = re.search(r'\{.*"skills_radar".*\}', text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(1) if json_match.lastindex else json_match.group(0))
            if "skills_radar" in data:
                st.session_state.radar_data = _normalize_radar_data(data["skills_radar"])
                return True
    except (json.JSONDecodeError, TypeError, ValueError):
        return False
    return False


def _normalize_score(value, default: int) -> int:
    try:
        score = int(round(float(value)))
    except (TypeError, ValueError):
        score = default
    return min(10, max(1, score))


def _normalize_radar_data(data: list) -> list:
    if not isinstance(data, list):
        raise ValueError("radar data must be a list")

    by_dimension = {
        item.get("维度"): item
        for item in data
        if isinstance(item, dict) and item.get("维度") in RADAR_DIMENSIONS
    }
    normalized = []
    for dimension in RADAR_DIMENSIONS:
        item = by_dimension.get(dimension, {})
        normalized.append({
            "维度": dimension,
            "JD要求": _normalize_score(item.get("JD要求"), 7),
            "你的当前": _normalize_score(item.get("你的当前"), 5),
        })
    return normalized


def _plot_radar(data: list):
    """绘制五维能力雷达图"""
    categories = [d["维度"] for d in data]
    jd_values = [d["JD要求"] for d in data]
    me_values = [d["你的当前"] for d in data]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=jd_values + [jd_values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='JD要求',
        line=dict(color='#FF6B6B', width=2),
        fillcolor='rgba(255, 107, 107, 0.15)'
    ))

    fig.add_trace(go.Scatterpolar(
        r=me_values + [me_values[0]],
        theta=categories + [categories[0]],
        fill='toself',
        name='你的当前',
        line=dict(color='#4ECDC4', width=2),
        fillcolor='rgba(78, 205, 196, 0.25)'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickvals=[2, 4, 6, 8, 10],
                gridcolor='rgba(128,128,128,0.15)'
            ),
            angularaxis=dict(
                gridcolor='rgba(128,128,128,0.15)'
            )
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=60, r=60, t=40, b=80),
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )

    st.plotly_chart(fig, use_container_width=True)
