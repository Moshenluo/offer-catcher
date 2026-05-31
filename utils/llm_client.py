"""
LLM客户端 - 支持OpenAI兼容接口（Groq/DeepSeek/通义等）
配置优先级：streamlit secrets > 环境变量
"""
import os
import streamlit as st
from openai import OpenAI, OpenAIError


def get_llm_client():
    """获取LLM客户端，优先从streamlit secrets读取配置"""
    # 默认使用Groq免费API
    api_key = st.secrets.get("LLM_API_KEY", None) or os.getenv("LLM_API_KEY")
    base_url = (
        st.secrets.get("LLM_BASE_URL", None)
        or os.getenv("LLM_BASE_URL")
        or "https://api.groq.com/openai/v1"
    )
    model = (
        st.secrets.get("LLM_MODEL", None)
        or os.getenv("LLM_MODEL")
        or "llama-3.1-70b-versatile"
    )

    if not api_key:
        raise ValueError("请在 Streamlit Secrets 或环境变量中配置 LLM_API_KEY")

    return OpenAI(api_key=api_key, base_url=base_url, timeout=60), model


class LLMEngine:
    """LLM调用引擎，统一管理所有AI分析请求"""

    def __init__(self):
        self.client, self.model = get_llm_client()

    def chat(self, system_prompt: str, user_prompt: str,
             temperature: float = 0.7, max_tokens: int = 4096) -> str:
        """基础对话接口"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )
        except OpenAIError as exc:
            raise RuntimeError(
                "AI 服务调用失败。请检查 API Key、模型名称、余额配额和网络连接后重试。"
            ) from exc

        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("AI 服务返回为空，请稍后重试或更换模型。")
        return content

    def analyze_jd(self, jd_text: str) -> str:
        """情报官 - JD深度解码"""
        from utils.prompts import JD_DECODE_SYSTEM, jd_decode_prompt
        return self.chat(JD_DECODE_SYSTEM, jd_decode_prompt(jd_text))

    def hr_perspective(self, jd_text: str, resume_text: str) -> str:
        """情报官 - HR视角模拟"""
        from utils.prompts import HR_VIEW_SYSTEM, hr_view_prompt
        return self.chat(HR_VIEW_SYSTEM, hr_view_prompt(jd_text, resume_text))

    def company_insight(self, jd_text: str, company_name: str) -> str:
        """情报官 - 公司近期动态分析"""
        from utils.prompts import COMPANY_INSIGHT_SYSTEM, company_insight_prompt
        return self.chat(COMPANY_INSIGHT_SYSTEM,
                        company_insight_prompt(company_name, jd_text))

    def build_capability_model(self, jd_text: str, resume_text: str) -> str:
        """简历军师 - 逆向能力建模"""
        from utils.prompts import CAPABILITY_MODEL_SYSTEM, capability_model_prompt
        return self.chat(CAPABILITY_MODEL_SYSTEM,
                        capability_model_prompt(jd_text, resume_text))

    def rewrite_resume(self, jd_text: str, resume_text: str, target_part: str = "full") -> str:
        """简历军师 - 一键重写简历"""
        from utils.prompts import REWRITE_SYSTEM, rewrite_prompt
        return self.chat(REWRITE_SYSTEM,
                        rewrite_prompt(jd_text, resume_text, target_part))

    def generate_questions(self, jd_text: str, company_name: str, resume_text: str) -> str:
        """面试教练 - 高频面试题预测"""
        from utils.prompts import QUESTIONS_SYSTEM, questions_prompt
        return self.chat(QUESTIONS_SYSTEM,
                        questions_prompt(jd_text, company_name, resume_text))

    def generate_star_answer(self, question: str, resume_text: str, jd_text: str) -> str:
        """面试教练 - STAR答案生成"""
        from utils.prompts import STAR_SYSTEM, star_prompt
        return self.chat(STAR_SYSTEM,
                        star_prompt(question, resume_text, jd_text))

    def mock_interview(self, question: str, user_answer: str, resume_text: str,
                       jd_text: str) -> str:
        """面试教练 - 模拟面试反馈"""
        from utils.prompts import MOCK_INTERVIEW_SYSTEM, mock_interview_prompt
        return self.chat(MOCK_INTERVIEW_SYSTEM,
                        mock_interview_prompt(question, user_answer, resume_text, jd_text))

    def recommend_jobs(self, resume_text: str, jd_text: str = "") -> str:
        """岗位猎手 - 基于简历生成细分岗位推荐"""
        from utils.prompts import JOB_RECOMMEND_SYSTEM, job_recommend_prompt
        return self.chat(
            JOB_RECOMMEND_SYSTEM,
            job_recommend_prompt(resume_text, jd_text),
            temperature=0.35,
            max_tokens=2200,
        )
