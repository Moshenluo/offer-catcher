"""
Offer捕手 · 学生求职匹配智能体
主应用入口 - Streamlit（全中文界面）
"""
import streamlit as st
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.llm_client import LLMEngine
from utils.resume_parser import anonymize_resume_text, parse_resume
from modules import intel_officer, resume_advisor, interview_coach, job_hunter

SAMPLE_CASES = [
    {
        "name": "数据科学 / AI产品策略",
        "company": "腾讯",
        "jd": """腾讯校园招聘 - 数据科学/AI产品策略实习生

岗位职责：
1. 支持招聘业务的数据分析，构建候选人与岗位的匹配评估指标。
2. 参与AI工具在校园招聘场景中的需求分析、效果评估和产品迭代。
3. 结合业务数据输出可视化看板，帮助HR识别渠道质量、简历初筛效率和候选人转化问题。

岗位要求：
1. 数据科学、计算机、统计、信息管理等相关专业，本科及以上学历。
2. 熟悉Python、SQL、机器学习基础方法，能够完成数据清洗、建模和可视化。
3. 有NLP、推荐系统、AIGC产品、招聘/教育场景项目经验优先。
4. 具备良好的结构化表达、跨团队沟通和快速学习能力。""",
        "resume": """姓名：示例同学
教育背景：数据科学硕士在读，主修机器学习、数据挖掘、自然语言处理和商业分析。

项目经历：
1. 求职岗位匹配分析项目：使用Python清洗招聘JD和学生简历文本，基于关键词、TF-IDF和语义相似度构建岗位匹配评分，输出候选人能力差距报告。
2. 校园活动推荐系统：使用协同过滤和LightGBM构建推荐模型，完成特征工程、模型评估和可视化分析，帮助用户发现更相关的活动。
3. 社交媒体情绪分析：使用中文分词、情感词典和机器学习模型识别文本情绪倾向，并用Plotly制作交互式结果图表。

实习经历：
数据分析实习生，负责整理业务数据、制作周报看板、分析用户转化漏斗，并向产品和运营同学同步发现。

技能：Python、SQL、Pandas、Scikit-learn、Plotly、Streamlit、机器学习、NLP基础、数据可视化。""",
    },
    {
        "name": "AI算法工程 / NLP方向",
        "company": "腾讯",
        "jd": """腾讯校园招聘 - AI算法工程师（NLP方向）

岗位职责：
1. 参与搜索、推荐、对话系统等场景中的文本理解和语义匹配算法研发。
2. 负责数据清洗、特征构建、模型训练、离线评估和线上效果分析。
3. 跟进大语言模型、RAG、Embedding等技术在业务场景中的应用落地。

岗位要求：
1. 计算机、人工智能、数据科学等相关专业，硕士优先。
2. 熟悉Python、PyTorch或TensorFlow，理解Transformer、BERT、向量检索等基础方法。
3. 有NLP、推荐系统、信息检索、LLM应用项目经验优先。
4. 能清晰表达模型思路、实验设计和指标变化原因。""",
        "resume": """姓名：示例同学
教育背景：人工智能硕士在读，课程包括深度学习、自然语言处理、信息检索和机器学习系统。

项目经历：
1. 简历-JD语义匹配项目：使用Sentence-BERT生成文本向量，计算简历与岗位JD的语义相似度，并输出能力缺口标签。
2. RAG问答系统：构建文档切分、Embedding召回和LLM生成流程，支持基于企业知识库的问答检索。
3. 文本分类实验：基于BERT微调中文评论分类模型，比较不同学习率、batch size和文本截断策略对F1的影响。

实习经历：
算法实习生，参与模型评估数据整理、错误样本分析和实验记录沉淀，协助输出迭代报告。

技能：Python、PyTorch、Transformers、FAISS、Scikit-learn、NLP、Embedding、Git。""",
    },
    {
        "name": "产品运营 / 数据分析",
        "company": "腾讯",
        "jd": """腾讯校园招聘 - 产品运营数据分析实习生

岗位职责：
1. 跟踪校园招聘活动、内容触达和用户转化数据，发现增长机会。
2. 设计数据看板和分析报告，支持运营策略调整和活动复盘。
3. 与产品、运营、HR团队协作，推动AI工具在学生求职服务中的应用。

岗位要求：
1. 统计、商科、数据科学、信息管理等相关专业。
2. 熟悉Excel、SQL、Python或BI工具，能独立完成数据清洗和可视化。
3. 有校园活动、用户增长、内容运营或数据分析项目经验优先。
4. 具备用户洞察、结构化表达和跨团队沟通能力。""",
        "resume": """姓名：示例同学
教育背景：数据科学硕士在读，主修机器学习、数据挖掘、自然语言处理和商业分析。

项目经历：
1. 校园活动增长分析：整理活动报名、签到和反馈数据，分析不同渠道的转化差异，并提出内容投放建议。
2. 用户分层看板：用Python和Plotly制作交互式看板，展示学生年级、专业、兴趣标签和活动参与情况。
3. 求职内容运营复盘：分析公众号推文阅读、点击和收藏数据，总结高互动内容主题。

实习经历：
运营数据实习生，负责制作周报、整理用户反馈、跟进活动数据，并向产品和运营同学同步发现。

技能：Python、SQL、Excel、Pandas、Plotly、Streamlit、用户分析、数据可视化、运营复盘。""",
    },
]

# ════════════════════════════════════════════════════════════
# 页面配置
# ════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Offer捕手 · 求职智脑",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ════════════════════════════════════════════════════════════
# 自定义CSS + 中文化文件上传组件
# ════════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* 品牌标题 */
    .brand-lockup {
        display: flex;
        align-items: center;
        gap: 16px;
        margin: 0.4rem 0 1.8rem;
    }
    .brand-mark {
        position: relative;
        width: 58px;
        height: 58px;
        flex: 0 0 58px;
        border-radius: 18px;
        background:
            radial-gradient(circle at 70% 28%, #ffffff 0 8px, transparent 9px),
            conic-gradient(from 210deg, #2dd4bf, #667eea, #7c5cff, #2dd4bf);
        box-shadow: 0 16px 34px rgba(102, 126, 234, 0.28);
    }
    .brand-mark::after {
        content: "";
        position: absolute;
        left: 16px;
        top: 17px;
        width: 23px;
        height: 23px;
        border-radius: 999px;
        border: 5px solid rgba(255,255,255,0.92);
        border-right-color: transparent;
        transform: rotate(-26deg);
    }
    .brand-title {
        margin: 0;
        font-size: clamp(2.15rem, 5vw, 3.35rem);
        line-height: 0.96;
        font-weight: 950;
        letter-spacing: 0;
        color: #25324b;
    }
    .brand-title span {
        color: #667eea;
    }
    .brand-subtitle {
        margin: 8px 0 0;
        color: #6c757d;
        font-size: 1rem;
        font-weight: 650;
    }
    .sidebar-brand {
        display: flex;
        align-items: center;
        gap: 11px;
        margin: 0.6rem 0 1.4rem;
    }
    .sidebar-brand .brand-mark {
        width: 44px;
        height: 44px;
        flex-basis: 44px;
        border-radius: 14px;
        box-shadow: 0 10px 22px rgba(102, 126, 234, 0.24);
    }
    .sidebar-brand .brand-mark::after {
        left: 12px;
        top: 13px;
        width: 17px;
        height: 17px;
        border-width: 4px;
    }
    .sidebar-brand strong {
        display: block;
        color: #25324b;
        font-size: 1.05rem;
        line-height: 1.1;
    }
    .sidebar-brand small {
        color: #7a8599;
        font-weight: 650;
    }

    /* 卡片样式 */
    .step-card {
        position: relative;
        overflow: hidden;
        background:
            linear-gradient(145deg, rgba(255,255,255,0.78) 0%, rgba(235,241,250,0.92) 100%);
        border-radius: 12px;
        padding: 24px 22px;
        margin: 10px 0;
        border: 1px solid rgba(102, 126, 234, 0.18);
        min-height: 220px;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.85), 0 18px 44px rgba(37, 50, 75, 0.08);
    }
    .step-card::before {
        content: "";
        position: absolute;
        width: 120px;
        height: 120px;
        right: -42px;
        top: -48px;
        border-radius: 999px;
        background: rgba(102,126,234,0.12);
    }
    .step-card h3 {
        margin: 0.65rem 0 0.4rem;
        font-size: 1.45rem;
        color: #25324b;
        line-height: 1.2;
    }
    .step-card .step-label {
        display: inline-block;
        color: #596579;
        font-size: 0.8rem;
        font-weight: 800;
    }
    .step-icon {
        display: inline-grid;
        place-items: center;
        width: 40px;
        height: 40px;
        margin-top: 18px;
        border-radius: 12px;
        background: #ffffff;
        color: #667eea;
        font-weight: 950;
        box-shadow: 0 10px 20px rgba(37, 50, 75, 0.10);
    }
    .step-card p {
        color: #3f4b5f;
        line-height: 1.65;
        margin-bottom: 0;
    }
    .welcome-panel {
        border-radius: 14px;
        padding: 24px 28px;
        margin-bottom: 1.25rem;
        background:
            radial-gradient(circle at 90% 18%, rgba(45, 212, 191, 0.18), transparent 28%),
            linear-gradient(135deg, #eef8ff 0%, #f6fbff 100%);
        border: 1px solid rgba(102,126,234,0.14);
        box-shadow: 0 18px 44px rgba(37, 50, 75, 0.06);
    }
    .welcome-panel h3 {
        margin: 0 0 12px;
        color: #25324b;
        font-size: 1.35rem;
    }
    .welcome-panel p {
        color: #17456b;
        line-height: 1.75;
        margin: 8px 0;
    }
    .metric-strip {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
        margin: -0.2rem 0 1.6rem;
    }
    .metric-tile {
        border-radius: 12px;
        padding: 14px 16px;
        background: #ffffff;
        border: 1px solid rgba(102,126,234,0.14);
        box-shadow: 0 12px 30px rgba(37, 50, 75, 0.06);
    }
    .metric-tile strong {
        display: block;
        color: #25324b;
        font-size: 1.35rem;
        line-height: 1.1;
    }
    .metric-tile span {
        display: block;
        margin-top: 5px;
        color: #667085;
        font-size: 0.86rem;
        font-weight: 650;
    }
    .demo-badge {
        border-radius: 10px;
        padding: 9px 11px;
        margin: 8px 0 10px;
        background: rgba(102,126,234,0.10);
        color: #25324b;
        font-size: 0.86rem;
        font-weight: 750;
        border: 1px solid rgba(102,126,234,0.16);
    }
    @media (max-width: 760px) {
        .brand-lockup {
            align-items: flex-start;
        }
        .metric-strip {
            grid-template-columns: 1fr;
        }
    }

    /* 模块差异化头部 */
    .module-hero {
        border-radius: 14px;
        padding: 22px 24px;
        margin: 0.5rem 0 1.2rem;
        border: 1px solid rgba(45, 52, 54, 0.08);
        box-shadow: 0 16px 36px rgba(31, 41, 55, 0.08);
    }
    .module-hero .eyebrow {
        display: inline-block;
        margin-bottom: 8px;
        font-size: 0.78rem;
        font-weight: 850;
        letter-spacing: 0.04em;
        color: rgba(29, 53, 87, 0.78);
    }
    .module-hero h2 {
        margin: 0 0 8px 0;
        padding: 0;
        border: none;
        color: #1f2937;
        font-size: 1.8rem;
        font-weight: 900;
    }
    .module-hero p {
        margin: 0;
        max-width: 68ch;
        color: #495057;
        line-height: 1.65;
    }
    .module-hero .chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 16px;
    }
    .module-hero .chip {
        border-radius: 999px;
        padding: 5px 10px;
        background: rgba(255,255,255,0.68);
        color: #2d3436;
        font-size: 0.82rem;
        font-weight: 700;
        border: 1px solid rgba(255,255,255,0.75);
    }
    .module-intel {
        background:
            radial-gradient(circle at 92% 18%, rgba(78, 205, 196, 0.28), transparent 32%),
            linear-gradient(135deg, #eef8fb 0%, #f8fbff 56%, #eef4ff 100%);
    }
    .module-jobs {
        background:
            radial-gradient(circle at 92% 18%, rgba(45, 212, 191, 0.22), transparent 32%),
            linear-gradient(135deg, #f1fff8 0%, #f5fbff 62%, #eef4ff 100%);
    }
    .module-resume {
        background:
            radial-gradient(circle at 88% 20%, rgba(255, 193, 7, 0.26), transparent 30%),
            linear-gradient(135deg, #f4fbf6 0%, #fffaf0 100%);
    }
    .module-interview {
        background:
            radial-gradient(circle at 88% 18%, rgba(214, 110, 129, 0.24), transparent 32%),
            linear-gradient(135deg, #fff5f6 0%, #f8f4ff 100%);
    }

    .module-note {
        border-radius: 10px;
        padding: 14px 16px;
        margin: 0.35rem 0 1rem;
        border-left: 5px solid #667eea;
        background: #f7f9ff;
        color: #344054;
        line-height: 1.6;
    }
    .module-note strong {
        color: #1d3557;
    }
    .note-intel {
        border-left-color: #168aad;
        background: #f0fbff;
    }
    .note-jobs {
        border-left-color: #12b886;
        background: #f0fff8;
    }
    .note-resume {
        border-left-color: #7a9a01;
        background: #fbfff0;
    }
    .note-interview {
        border-left-color: #c9184a;
        background: #fff5f7;
    }

    /* 进度条 */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
    }

    /* 侧边栏 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }

    /* 按钮 */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }

    /* Tab */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }

    /* AI输出重点强化：让评委和学生先看到结论 */
    [data-testid="stMarkdownContainer"] h2 {
        margin-top: 1.6rem;
        padding: 0.45rem 0 0.45rem 0.85rem;
        border-left: 5px solid #667eea;
        color: #2d3436;
        font-size: 1.65rem;
        font-weight: 850;
        line-height: 1.25;
    }
    [data-testid="stMarkdownContainer"] h3 {
        margin-top: 1.25rem;
        padding: 0.35rem 0 0.35rem 0.7rem;
        border-left: 4px solid #4ecdc4;
        color: #233142;
        font-size: 1.28rem;
        font-weight: 800;
        line-height: 1.3;
    }
    [data-testid="stMarkdownContainer"] h4 {
        color: #31445a;
        font-size: 1.08rem;
        font-weight: 760;
    }
    [data-testid="stMarkdownContainer"] strong {
        color: #1d3557;
        font-weight: 850;
    }
    [data-testid="stMarkdownContainer"] li::marker {
        color: #667eea;
        font-weight: 800;
    }
    [data-testid="stMarkdownContainer"] table {
        border-radius: 8px;
        overflow: hidden;
    }
    [data-testid="stMarkdownContainer"] th {
        background: #eef3ff;
        color: #1d3557;
        font-weight: 800;
    }

    /* 文件上传组件中文化：Streamlit未开放文案参数，用CSS稳定覆盖默认英文 */
    [data-testid="stFileUploaderDropzoneInstructions"] > div > span {
        font-size: 0;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] > div > span::after {
        content: "将文件拖放到此处";
        font-size: 0.92rem;
        color: #2d3436;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] small {
        font-size: 0;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] small::after {
        content: "单个文件不超过 10MB · 支持 PDF、TXT";
        font-size: 0.8rem;
        color: #6c757d;
    }
    [data-testid="stFileUploaderDropzone"] button[data-testid="stBaseButton-secondary"] {
        font-size: 0;
    }
    [data-testid="stFileUploaderDropzone"] button[data-testid="stBaseButton-secondary"]::after {
        content: "选择文件";
        font-size: 0.92rem;
    }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# 侧边栏：简历上传 + 配置
# ════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="brand-mark"></div>
        <div>
            <strong>Offer捕手</strong>
            <small>求职智脑</small>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("## 📥 输入中心")

    st.markdown("### 🚀 快速演示")
    if st.button("换一套示例材料", use_container_width=True):
        next_sample_index = (st.session_state.get("sample_case_index", -1) + 1) % len(SAMPLE_CASES)
        st.session_state.sample_case_index = next_sample_index
        sample_case = SAMPLE_CASES[next_sample_index]
        st.session_state.sample_refresh_id = st.session_state.get("sample_refresh_id", 0) + 1
        st.session_state.sample_jd_text = sample_case["jd"]
        st.session_state.sample_company_name = sample_case["company"]
        st.session_state.sample_resume_text = sample_case["resume"]
        st.session_state.sample_case_name = sample_case["name"]
        st.session_state.pop("radar_data", None)
        st.rerun()
    if st.session_state.get("sample_resume_text"):
        st.markdown(
            f'<div class="demo-badge">当前示例：{st.session_state.get("sample_case_name", "随机求职样例")}</div>',
            unsafe_allow_html=True
        )
        st.caption("上传真实简历后会自动替换示例。")
        if st.button("清空示例材料", use_container_width=True):
            st.session_state.sample_resume_text = ""
            st.session_state.sample_case_name = ""
            st.session_state.sample_jd_text = ""
            st.session_state.sample_company_name = ""
            st.session_state.sample_refresh_id = st.session_state.get("sample_refresh_id", 0) + 1
            st.session_state.pop("radar_data", None)
            st.rerun()

    with st.expander("3分钟演示路线"):
        st.markdown("""
        1. 点击 **换一套示例材料**
        2. 用 **情报官** 解码JD，展示关键结论
        3. 用 **简历军师** 做能力建模和雷达图
        4. 用 **一键重写** 展示可直接采纳的改写
        5. 用 **面试教练** 展示STAR或模拟反馈
        """)

    st.divider()

    # Step1: 上传简历
    st.markdown("### 1️⃣ 上传简历")
    st.markdown("支持 PDF / TXT 格式，最大 10MB")
    anonymize_resume = st.checkbox(
        "发送给 AI 前自动脱敏",
        value=True,
        help="自动替换手机号、邮箱、身份证号、微信/QQ等个人标识信息。"
    )
    st.caption("简历内容会发送给你配置的模型服务商，请勿上传不希望第三方处理的敏感材料。")

    uploaded_file = st.file_uploader(
        "上传简历文件",
        type=["pdf", "txt"],
        help="支持 PDF 或纯文本格式的简历文件",
        label_visibility="collapsed"
    )

    resume_text = ""
    if uploaded_file:
        try:
            filename, parsed_resume_text = parse_resume(uploaded_file)
            resume_text = (
                anonymize_resume_text(parsed_resume_text)
                if anonymize_resume
                else parsed_resume_text
            )
            st.success(f"✅ 已解析：{filename}")
            with st.expander("📄 预览简历内容"):
                st.text(resume_text[:2000] + ("..." if len(resume_text) > 2000 else ""))
        except Exception as e:
            st.error(f"简历解析失败：{e}")
    elif st.session_state.get("sample_resume_text"):
        resume_text = st.session_state.sample_resume_text
        st.success("✅ 已载入示例简历")
        with st.expander("📄 预览示例简历"):
            st.text(resume_text[:2000] + ("..." if len(resume_text) > 2000 else ""))

    st.divider()

    # Step2: 粘贴JD
    st.markdown("### 2️⃣ 粘贴岗位JD")
    sample_refresh_id = st.session_state.get("sample_refresh_id", 0)
    jd_text = st.text_area(
        "岗位JD",
        value=st.session_state.get("sample_jd_text", ""),
        placeholder="如：OPPO AI算法工程师\n\n岗位职责：\n1. 负责计算机视觉算法研发...\n\n岗位要求：\n1. 硕士及以上学历...",
        height=200,
        key=f"jd_input_{sample_refresh_id}",
        label_visibility="collapsed"
    )

    st.divider()

    # Step3: 公司名（可选）
    st.markdown("### 3️⃣ 公司名称（可选）")
    company_name = st.text_input(
        "公司名称",
        value=st.session_state.get("sample_company_name", ""),
        placeholder="如：OPPO",
        key=f"sidebar_company_{sample_refresh_id}",
        label_visibility="collapsed"
    )

    st.divider()

    # 状态显示
    st.markdown("---")
    jd_ready = len(jd_text.strip()) >= 20
    resume_ready = len(resume_text.strip()) >= 50

    st.markdown("### 📊 当前状态")
    st.progress(
        (0.5 if jd_ready else 0) + (0.5 if resume_ready else 0),
        text=f"JD {'✅' if jd_ready else '⚠️'} | 简历 {'✅' if resume_ready else '⚠️'}"
    )

    if not jd_ready:
        st.warning("请粘贴完整JD以使用情报官模块")
    if not resume_ready:
        st.warning("请上传简历以解锁全部功能")

# ════════════════════════════════════════════════════════════
# 主界面
# ════════════════════════════════════════════════════════════

# 标题区
st.markdown("""
<div class="brand-lockup">
    <div class="brand-mark"></div>
    <div>
        <h1 class="brand-title">Offer捕手<span> · 求职智脑</span></h1>
        <p class="brand-subtitle">四步求职赋能 | 岗位猎手 · 情报官 · 简历军师 · 面试教练</p>
    </div>
</div>
""", unsafe_allow_html=True)

# 快速入门指引
if not jd_ready and not resume_ready:
    st.markdown("""
    <div class="welcome-panel">
        <h3>欢迎来到 Offer捕手</h3>
        <p>我是一个帮你从「海投迷茫」到「精准命中心仪Offer」的 AI 求职参谋。</p>
        <p><strong>最快体验方式：</strong> 点击左侧「换一套示例材料」，即可直接跑完整流程。</p>
        <p><strong>真实使用方式：</strong> 上传简历 → 推荐岗位 → 粘贴目标JD → 按下面路径逐步分析。</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="metric-strip">
        <div class="metric-tile"><strong>3套</strong><span>可切换演示样例</span></div>
        <div class="metric-tile"><strong>5维</strong><span>能力差距诊断</span></div>
        <div class="metric-tile"><strong>1条链路</strong><span>岗位推荐 → 简历 → 面试</span></div>
    </div>
    """, unsafe_allow_html=True)

    # 功能卡片展示
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.markdown("""
        <div class="step-card">
        <span class="step-label">STEP 0 · 找岗位</span>
        <div class="step-icon">01</div>
        <h3>岗位猎手</h3>
        <p><strong>先找到值得投的岗位。</strong><br>
        根据简历推荐方向，分页搜集最新岗位，并提供多公司、多平台检索入口。</p>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div class="step-card">
        <span class="step-label">STEP 1 · 读懂岗位</span>
        <div class="step-icon">02</div>
        <h3>情报官</h3>
        <p><strong>先判断岗位真正要什么。</strong><br>
        解码JD潜台词，模拟HR初筛视角，找出简历里最该被看见的证据。</p>
        </div>
        """, unsafe_allow_html=True)
    with col_c:
        st.markdown("""
        <div class="step-card">
        <span class="step-label">STEP 2 · 诊断差距</span>
        <div class="step-icon">03</div>
        <h3>简历军师</h3>
        <p><strong>再决定简历怎么改。</strong><br>
        五维能力建模，生成差距雷达图，并把经历改写成更贴合JD的表达。</p>
        </div>
        """, unsafe_allow_html=True)
    with col_d:
        st.markdown("""
        <div class="step-card">
        <span class="step-label">STEP 3 · 准备面试</span>
        <div class="step-icon">04</div>
        <h3>面试教练</h3>
        <p><strong>最后把经历讲清楚。</strong><br>
        预测高频题，生成STAR回答框架，并对模拟回答给出改进反馈。</p>
        </div>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# 功能模块路由
# ════════════════════════════════════════════════════════════
if jd_ready or resume_ready:
    st.divider()

    # 模块选择
    if jd_ready and resume_ready:
        st.success("材料已就绪。推荐体验路径：岗位猎手搜集职位 → 情报官解码JD → 简历军师诊断差距 → 面试教练准备回答。")
    elif jd_ready:
        st.info("已识别到JD。可以先用「情报官」解码岗位；上传简历后可解锁岗位推荐与完整闭环。")
    elif resume_ready:
        st.info("已识别到简历。建议先用「岗位猎手」搜集合适岗位，再把目标JD粘贴到左侧。")

    module = st.pills(
        "选择一个模块开始分析：",
        ["🧭 岗位猎手", "🔍 情报官", "✍️ 简历军师", "🎤 面试教练"],
        default="🧭 岗位猎手",
        key="module_select"
    )

    st.divider()

    # 路由到对应模块（修复：函数参数用逗号分隔）
    if module == "🧭 岗位猎手":
        job_hunter.render(resume_text, jd_text)

    else:
        @st.cache_resource
        def init_engine():
            return LLMEngine()

        try:
            engine = init_engine()
        except Exception as e:
            st.error(f"""
            ⚠️ AI引擎初始化失败，请检查API配置

            **如果你在 Streamlit Cloud 部署：**
            请进入应用设置 `Settings` → `Secrets`，粘贴以下内容后保存并重新部署：

            ```toml
            LLM_API_KEY = "你的API密钥"
            LLM_BASE_URL = "https://api.deepseek.com"
            LLM_MODEL = "deepseek-v4-flash"
            ```

            **如果你在本地运行：**
            请在项目目录下创建 `.streamlit/secrets.toml`，内容格式同上。

            **低成本API推荐：**
            - DeepSeek：价格极低，中文效果优秀
            - Groq：提供免费额度，速度较快
            - 阿里百炼：通义千问，支持中文

            错误信息：{str(e)}
            """)
            st.stop()

        if module == "🔍 情报官":
            intel_officer.render(engine, jd_text, resume_text, company_name or "")

        elif module == "✍️ 简历军师":
            resume_advisor.render(engine, jd_text, resume_text)

        elif module == "🎤 面试教练":
            interview_coach.render(engine, jd_text, resume_text, company_name or "")
