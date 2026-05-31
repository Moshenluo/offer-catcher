# 🎯 Offer捕手 · 学生求职匹配智能体

> 腾讯校园招聘 Demo 课题作业 · 作业一「Offer捕手」

## 项目简介

**Offer捕手** 是一个面向高校学生的AI求职参谋系统，突破传统"简历打分器"的局限，打造三位一体的求职赋能工具：

本项目对应 Demo 课题 **作业一：「Offer捕手」学生求职匹配智能体**，核心目标是帮助学生有效匹配心仪岗位，并提升简历初筛命中率。

| 模块 | 功能 | 创新点 |
|------|------|--------|
| 🔍 **情报官** | JD深度解码 + HR视角模拟 + 公司情报 | 揭示JD潜台词，模拟HR 6秒扫描内幕 |
| ✍️ **简历军师** | 逆向能力建模 + 差距雷达图 + 一键重写 | 从JD反推能力模型，量化差距，直接产出优化简历 |
| 🎤 **面试教练** | 高频题预测 + STAR模板 + 模拟面试 | 不只给题，还给答题框架和实时反馈 |

## 截图预览

```
┌─────────────────────────────────────────────────┐
│          Offer捕手 · 求职智脑                    │
├──────────┬──────────┬────────┬────────────────┤
│ 🔍 情报官  │ ✍️ 简历军师│🎤 面试教练│
├──────────┼──────────┼────────┼────────────────┤
│JD深度解码 │逆向能力建模│高频题预测│ 30天时间线 │
│HR视角模拟 │差距雷达图  │STAR生成  │模拟对话    │
│公司近期动态│一键重写   │模拟面试  │申请进度板  │
└──────────┴──────────┴────────┴────────────────┘
```

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/你的用户名/offer-catcher.git
cd offer-catcher
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置 LLM API Key

复制配置模板并填入你的API Key：
```bash
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# 编辑 .streamlit/secrets.toml，填入API Key
```

**推荐免费/低价方案：**
- 🚀 [Groq Cloud](https://console.groq.com) - 提供免费额度，速度快
- 💰 [DeepSeek](https://platform.deepseek.com) - 中文友好，价格极低
- ☁️ [阿里百炼](https://bailian.console.aliyun.com) - 通义千问，支持中文

### 4. 本地运行
```bash
streamlit run app.py
```

访问 `http://localhost:8501` 即可使用。

## 隐私与使用提示

- 简历内容会发送给你配置的模型服务商，请勿上传不希望第三方处理的敏感材料。
- 系统默认在发送给 AI 前脱敏手机号、邮箱、身份证号和常见社交账号。
- 简历改写不会主动编造经历；缺少量化结果时会用 `[请补充真实数字]` 提醒你自行核实补全。
- 公司情报模块不联网核验实时新闻，输出中的待核验事实需要在官网、招聘页、财报或公众号中补证据。

## 部署到 Streamlit Cloud（公网访问）

1. 将 `offer-catcher` 文件夹推送到你的 GitHub 仓库
2. 访问 [share.streamlit.io](https://share.streamlit.io)
3. 连接 GitHub，选择此仓库
4. 在 `Advanced settings` → `Secrets` 中粘贴本地 `.streamlit/secrets.toml` 的内容
5. 点击 Deploy，获得 `https://xxx.streamlit.app` 公网链接

部署注意：
- 不要把 `.streamlit/secrets.toml` 推送到 GitHub；本项目已在 `.gitignore` 中排除该文件。
- GitHub 仓库中需要保留 `.streamlit/secrets.toml.template`，方便说明配置格式。
- Streamlit Cloud 的主入口文件选择 `app.py`。

## 技术架构

```
offer-catcher/
├── app.py                    # 主应用入口（Streamlit）
├── requirements.txt          # Python依赖
├── .streamlit/
│   ├── config.toml          # Streamlit主题配置
│   └── secrets.toml.template # API Key配置模板
├── utils/
│   ├── __init__.py
│   ├── llm_client.py        # LLM调用引擎
│   ├── prompts.py           # 全部Prompt模板
│   └── resume_parser.py     # PDF/文本简历解析
└── modules/
    ├── __init__.py
    ├── intel_officer.py     # 情报官模块
    ├── resume_advisor.py    # 简历军师模块
    └── interview_coach.py    # 面试教练模块
```

### 技术栈
- **前端**：Streamlit 1.40+
- **LLM**：OpenAI 兼容接口（支持 Groq/DeepSeek/通义等）
- **简历解析**：pdfplumber
- **图表**：Plotly（雷达图）
- **文档导出**：python-docx

## 方案说明（1000字摘要）

### 问题诊断
学生求职面临三个核心痛点：(1)海量岗位中精准匹配耗时；(2)不清楚简历与岗位的匹配度；(3)不知道如何优化简历以提升初筛通过率。现有工具要么只做关键词匹配，要么只给改简历建议，缺乏全链路赋能。

### 方案设计
Offer捕手以**逆向求职**为核心思路——不是"我的简历能匹配什么"，而是"我想去哪里，现在差什么，怎么弥补"。三大模块形成闭环：情报官帮助学生读懂JD本质，简历军师量化差距并直接产出优化简历，面试教练提供从预测题到模拟面试的完整准备。

### AI工具选型
- **LLM引擎**：采用 OpenAI 兼容接口，支持 Groq、DeepSeek、通义千问等多平台切换，兼顾成本与效果
- **Prompt工程**：每个模块独立设计 System Prompt，明确角色设定、输出格式、评分标准
- **解析方案**：pdfplumber 做PDF文本提取，LLM做结构化抽取，避免传统规则解析的脆弱性

### 创新点
1. **HR视角模拟**：业内首创，模拟HR看简历时的真实内心OS，6秒扫描→细读→初筛决策全流程
2. **JD潜台词解码**：逐条翻译JD字面要求背后的真实考查意图
3. **逆向能力建模**：从JD反推五维能力雷达图，量化差距
4. **一键重写简历**：不是给建议，是直接产出可下载的优化版简历

### 交付物
- ✅ 可运行的 Web Demo（Streamlit Cloud 公网部署）
- ✅ 方案说明：[docs/submission_statement.md](docs/submission_statement.md)
- 演示视频为可选项，本项目不作为必要交付提交。

## 作者

香港城市大学（东莞）· 数据科学硕士在读

## 许可

MIT License
