# 部署检查清单

## GitHub 推送前

- 确认 `.streamlit/secrets.toml` 没有被提交。
- 确认 `.streamlit/secrets.toml.template` 保留在仓库中。
- 确认入口文件是 `app.py`。
- 确认依赖文件是 `requirements.txt`。
- 确认方案说明文件是 `docs/submission_statement.md`。

## Streamlit Cloud 配置

1. 打开 `https://share.streamlit.io`。
2. 连接 GitHub 仓库。
3. 选择本项目仓库和分支。
4. Main file path 填写 `app.py`。
5. 在 Secrets 中粘贴本地 `.streamlit/secrets.toml` 的内容。
6. 点击 Deploy。

## 提交作业时

- 提交公网 Demo 链接：`https://xxx.streamlit.app`
- 提交方案说明：`docs/submission_statement.md` 导出为 DOC 或 PDF
- 演示视频可不提交
