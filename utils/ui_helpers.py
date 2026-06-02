"""
通用 UI 辅助组件
"""
from __future__ import annotations

import hashlib

import streamlit as st


def render_copyable_ai_output(result: str, key_prefix: str, filename_prefix: str = "AI分析结果"):
    """展示 AI Markdown 结果，并提供稳定可复制的纯文本区域。"""
    st.markdown(result)

    digest = hashlib.md5(result.encode("utf-8")).hexdigest()[:10]
    with st.expander("复制原文 / 下载结果"):
        st.caption("如果页面正文无法用 Ctrl+C 复制，请点击下方文本框后使用 Ctrl+A / Ctrl+C。")
        st.text_area(
            "可复制文本",
            value=result,
            height=280,
            key=f"{key_prefix}_copy_{digest}",
            label_visibility="collapsed",
        )
        st.download_button(
            label="下载为 Markdown",
            data=result,
            file_name=f"{filename_prefix}_{digest}.md",
            mime="text/markdown",
            use_container_width=True,
            key=f"{key_prefix}_download_{digest}",
        )
