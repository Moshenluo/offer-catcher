"""
简历解析工具 - 支持PDF和纯文本
"""
import io
import re
from typing import Tuple
import pdfplumber


def parse_resume(uploaded_file) -> Tuple[str, str]:
    """
    解析简历文件，返回 (文件名, 文本内容)
    支持 PDF (.pdf) 和纯文本 (.txt)
    """
    filename = uploaded_file.name
    file_bytes = uploaded_file.getvalue()

    if filename.lower().endswith('.pdf'):
        return filename, _parse_pdf(file_bytes)
    elif filename.lower().endswith('.txt'):
        return filename, file_bytes.decode('utf-8', errors='replace')
    else:
        # 尝试作为文本读取
        try:
            return filename, file_bytes.decode('utf-8', errors='replace')
        except:
            raise ValueError(f"不支持的文件格式: {filename}，请上传PDF或TXT文件")


def _parse_pdf(file_bytes: bytes) -> str:
    """解析PDF文件中的文本"""
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    if not text_parts:
        raise ValueError("PDF文件中未检测到文本内容，请确保PDF包含可提取的文字")
    return "\n\n".join(text_parts)


def anonymize_resume_text(text: str) -> str:
    """
    对发送给LLM的简历文本做基础脱敏。
    仅替换常见个人标识信息，不改变项目、经历、技能等求职判断内容。
    """
    patterns = [
        (r'[\w.+-]+@[\w-]+(?:\.[\w-]+)+', '[邮箱已脱敏]'),
        (r'(?<!\d)1[3-9]\d{9}(?!\d)', '[手机号已脱敏]'),
        (r'(?<!\d)\d{17}[\dXx](?!\d)', '[身份证号已脱敏]'),
        (r'(微信|WeChat|wechat|QQ)[:：\s]*[A-Za-z0-9_-]{5,}', r'\1：[账号已脱敏]'),
    ]
    anonymized = text
    for pattern, replacement in patterns:
        anonymized = re.sub(pattern, replacement, anonymized)
    return anonymized
