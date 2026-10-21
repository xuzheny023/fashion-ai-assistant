# AI Fashion Fabric Analyst · AI 设计落地助手

**Open-source fashion design-to-production assistant / 开源服装设计到生产建议辅助工具**

[English](#english) · [中文](#中文) · [Contributing / 贡献指南](CONTRIBUTING.md) · [MIT License](LICENSE)

This Python + Streamlit project uses **Alibaba Cloud DashScope (Qwen-VL-Max)** to inspect a selected area of a fashion design image and suggest possible fabrics, print processes and garment construction methods. It translates visual ideas into **preliminary manufacturing discussion points**, not verified technical specifications.

本项目基于 **Python、Streamlit 与阿里云 DashScope（Qwen-VL-Max）**，分析服装效果图中的选定区域，提出面料、印花与缝制工艺的初步建议，帮助设计师与生产团队沟通。**模型输出是推测性建议，不是经过检验的生产规格。**

> **Accuracy / 准确性提醒：** A photograph or rendering cannot reliably establish fiber composition, fabric weight (GSM), colorfastness, stretch, shrinkage or the feasibility of a sewing process. Validate suggestions using samples, material specifications, physical tests and manufacturing expertise before production. / 单凭图片无法可靠确定纤维成分、克重、色牢度、弹性、缩水率或工艺可生产性，投产前必须通过样布、检测与实际打样验证。

<a id="english"></a>
## English

### Current capabilities

- **Fabric analysis:** estimates possible material, weave/knit, drape, sheen and alternatives.
- **Print analysis:** suggests print approaches, repeat/resolution considerations, base fabrics and process risks.
- **Construction analysis:** proposes stitch/seam/edge-finishing approaches and manufacturing considerations.
- **Production context:** budget tier, garment use case and constraint selections.
- **Region selection:** interactive crop via `streamlit-cropper`, with manual coordinate fallback.
- **Bilingual interface:** Chinese and English prompts and result presentation.
- **Structured responses:** attempts to parse the model's JSON into task-specific result panels.

**Implemented inference provider:** Alibaba Cloud DashScope Qwen-VL-Max. OpenAI/Gemini are **not implemented**. An optional web-search helper is present in the codebase, but **web search is not connected to the current inference path**. Selecting a task explicitly (Fabric, Print, Construction) is recommended; automatic category classification is not part of the current UI.

### Setup

**Requirements:** Python 3.11 recommended; a DashScope API key for live inference; Windows, macOS or Linux.

```bash
git clone https://github.com/xuzheny023/fashion-ai-assistant.git
cd fashion-ai-assistant
python -m venv .venv
```

Activate the environment, then install dependencies:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

```bash
# macOS / Linux
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Configure `DASHSCOPE_API_KEY` as an environment variable, or create an **untracked** `.streamlit/secrets.toml` file:

```toml
DASHSCOPE_API_KEY = "replace-with-your-own-key"
```

The application also supports entering a DashScope key in the sidebar for the current session. **Never commit a real API key.** The `.gitignore` excludes `.streamlit/secrets.toml`.

Run on any platform:

```bash
python -m streamlit run app_new.py
```

Open the Streamlit URL (normally `http://localhost:8501`). On Windows you may instead run `./scripts/ensure_venv.ps1` to prepare a virtual environment and `./run.ps1` to start the app on port 9000. The PowerShell scripts do not change global pip settings.

### How to use

1. Upload a PNG/JPEG fashion drawing, concept image or photograph.
2. Choose **Fabric**, **Print** or **Construction**; set the budget, use case and constraints.
3. Select a relevant region with the cropper, or enter coordinates if the cropper is unavailable.
4. Click **Analyze Selected Region**; a valid DashScope key and connectivity are required.
5. Review the suggested details, alternatives, risks and next actions. Independently verify technical claims.

### Project structure

```text
fashion-ai-assistant/
├── app_new.py                 # Streamlit interface and result rendering
├── src/fabric_api_infer.py    # Prompting, DashScope call and JSON parsing
├── src/aug/web_search.py      # Optional utilities (not wired into inference)
├── src/utils/logger.py       # Logging helper
├── scripts/ensure_venv.ps1   # Optional Windows environment setup
├── run.ps1                   # Optional Windows launcher
├── tests/                    # Offline unit tests
├── .github/workflows/        # Pull-request checks
├── requirements.txt
└── CONTRIBUTING.md
```

### Offline quality checks

```bash
python -m unittest discover -s tests -v
python -m compileall -q app_new.py src tests
```

Tests cover prompt construction, JSON parsing, image upscaling and per-request API key forwarding via a mocked model response. **They do not validate real model accuracy, service availability or manufacturing correctness.** Pull requests run these checks automatically in GitHub Actions.

### Contribution and limitations

See [CONTRIBUTING.md](CONTRIBUTING.md) for a local setup, reproducible bug reports and PR guidance. Suitable contributions include tests, error handling, actual provider integrations, validated examples, accessibility and documentation. Please avoid committing proprietary design assets, real API credentials, or personal information.

<a id="中文"></a>
## 中文

### 已实现的功能

- **面料分析：** 估计可能的材质、组织结构、光泽、悬垂表现与替代方案。
- **印花分析：** 提供印花方式、分辨率与花型重复的建议，并提示工艺风险。
- **工艺分析：** 提供针型、缝型、边缘处理、衬料及公差的初步建议。
- **生产上下文：** 预算档位、服装使用场景及约束条件。
- **局部裁剪：** 支持图像交互式选区，失败时可以通过坐标手动裁剪。
- **中英文界面：** 双语操作与结果展示。
- **结构化输出：** 对模型返回的 JSON 进行解析并分区展示。

**目前唯一接通的推理服务是阿里云 DashScope Qwen-VL-Max。** OpenAI 和 Gemini 尚未接入。仓库包含辅助联网检索代码，但尚未连接到当前分析流程，因此界面不再显示无法生效的联网选项。分析类型需要手动选择；暂不承诺自动识别分类。

### 快速安装

推荐 Python 3.11，并准备 [阿里云 DashScope API Key](https://dashscope.aliyun.com/)。

```bash
git clone https://github.com/xuzheny023/fashion-ai-assistant.git
cd fashion-ai-assistant
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS / Linux:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

设置环境变量 `DASHSCOPE_API_KEY`，或者在本地新建**不提交到 GitHub** 的 `.streamlit/secrets.toml`：

```toml
DASHSCOPE_API_KEY = "填入你自己的密钥"
```

也可以直接在侧边栏临时填写 API Key。**不要把密钥上传到公开仓库。**

启动程序：

```bash
python -m streamlit run app_new.py
```

默认打开 `http://localhost:8501`。Windows 也可以使用 `./scripts/ensure_venv.ps1` 准备环境，再执行 `./run.ps1`（端口 9000）。脚本不会更改全局 pip 镜像配置。

### 使用流程

1. 上传服装款式图、效果图或照片（PNG / JPEG）。
2. 选择面料、印花或工艺分析，填写预算、场景与约束条件。
3. 框选需要分析的区域；如组件无法运行，使用坐标选区。
4. 点击“AI 分析选中区域”，并确保有有效的 DashScope API Key。
5. 查看建议、风险和下一步行动。生产决策前须进行实际验证。

### 开源维护与测试

运行 `python -m unittest discover -s tests -v` 可执行**无需真实 API 密钥**的离线单元测试；GitHub Pull Request 也会运行这些检查。测试不代表模型识别准确率或生产质量验证。问题反馈及贡献方式详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

**当前限制：** 图像识别无法直接替代纤维检测、克重检测、物性测试、成本核算与打样；联网检索功能尚未接入推理流程，OpenAI/Gemini 推理未实现。本项目不宣称已经拥有特定数量的真实用户或已验证的产业采用规模。

---

Licensed under the [MIT License](LICENSE). Powered by open-source tooling and Alibaba Cloud's DashScope model API; API service use and billing follow the provider's terms.
