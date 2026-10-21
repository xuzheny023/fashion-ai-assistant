# Contributing / 贡献指南

Thank you for contributing to AI Fashion Fabric Analyst. This repository aims to help fashion designers explore the translation from visual concepts into **preliminary** production-oriented suggestions.

感谢参与 AI 设计落地助手。本项目面向服装设计图到**初步**生产建议的探索，欢迎可复现的修复、测试、文档完善与合适的新功能。

## Getting started / 本地运行

1. Fork the repository and create a descriptive branch.
2. Install Python 3.11 and dependencies: `python -m pip install -r requirements.txt`.
3. Set `DASHSCOPE_API_KEY` as an environment variable or in an untracked `.streamlit/secrets.toml`.
4. Run `python -m streamlit run app_new.py`.
5. Run offline tests before opening a PR: `python -m unittest discover -s tests -v`.

## Pull requests / 提交 PR

- Describe the user-facing problem, intended change, and how you tested it.
- Include example inputs/outputs where relevant, with sensitive data removed.
- Keep changes scoped; avoid unrelated dependency upgrades.
- Never commit real API keys, proprietary design images, or identifying personal information.
- If changing a model provider, implement and test the actual backend before exposing it in the UI.
- Describe what is verified versus estimated. Material content, GSM, durability and production feasibility cannot be confirmed from an image alone.

## Issues / 问题反馈

Please provide the platform, Python version, steps to reproduce, expected versus actual behavior, and a redacted traceback where possible. Do not publish API keys.

请尽量提供系统、Python 版本、复现步骤、预期及实际结果，并对日志和截图中的密钥、个人信息脱敏。

## Scope / 项目范围

The current supported inference backend is Alibaba Cloud DashScope (Qwen-VL-Max). The project does **not** currently implement OpenAI/Gemini inference or connect optional web-search utilities to the analysis pipeline. Contributions adding providers or retrieval should include tests, usage documentation, and provider-specific key handling.
