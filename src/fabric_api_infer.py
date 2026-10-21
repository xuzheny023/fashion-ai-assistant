# -*- coding: utf-8 -*-
"""
Cloud VLM Fashion Analysis Engine | 云端视觉语言模型时尚分析引擎
========================================================================

English:
---------
Core inference engine for AI-powered fashion design analysis using Alibaba Cloud's
DashScope API (Qwen-VL-Max model). Provides structured production recommendations
for fabrics, prints, and construction details.

Key Components:
- Unified JSON schema for consistent output format
- Bilingual prompt templates (Chinese/English)
- Context-aware analysis (budget, use case, constraints)
- Robust JSON extraction from model responses
- Multi-task support (fabric/print/construction)

Functions:
- cloud_infer(): Main inference function
- make_prompt(): Dynamic prompt generation
- try_parse_json(): Robust JSON parsing with fallback strategies
- image_to_base64_datauri(): Image encoding for API calls

中文：
------
基于阿里云灵积 API（Qwen-VL-Max 模型）的 AI 驱动时尚设计分析核心推理引擎。
为面料、印花和工艺细节提供结构化的生产建议。

核心组件：
- 统一 JSON 模式确保输出格式一致
- 双语提示词模板（中文/英文）
- 场景化分析（预算、使用场景、约束条件）
- 鲁棒的 JSON 提取机制
- 多任务支持（面料/印花/工艺）

主要函数：
- cloud_infer()：主推理函数
- make_prompt()：动态提示词生成
- try_parse_json()：鲁棒 JSON 解析，支持多种回退策略
- image_to_base64_datauri()：API 调用的图像编码

Technical Details:
- Model: qwen-vl-max
- Input: PIL Image objects
- Output: Structured JSON with task-specific details
- Error Handling: Comprehensive fallback mechanisms
- Performance: ~3-10 seconds per inference

技术细节：
- 模型：qwen-vl-max
- 输入：PIL Image 对象
- 输出：包含任务特定细节的结构化 JSON
- 错误处理：全面的回退机制
- 性能：每次推理约 3-10 秒

Author: AI Fashion Tech Team
Version: 2.0
Last Updated: 2025-10
"""

from typing import Dict, List, Optional
from PIL import Image
import io
import base64
import os
import json
import re

try:
    import dashscope
    from dashscope import MultiModalConversation
except Exception:
    dashscope = None
    MultiModalConversation = None

# ==================== 模型映射 ====================
MODEL_MAP = {
    "qwen-vl": "qwen-vl-max",
    "qwen-vl-plus": "qwen-vl-max",
    "qwen-vl-max": "qwen-vl-max",
}

# ==================== 统一 JSON Schema ====================
UNIFIED_SCHEMA_ZH = """{
  "task": "fabric|print|construction",
  "summary": "一句话核心结论",
  "details": {
    "fabric": {
      "material": "材质名称",
      "weave_or_knit": "组织结构(satin/twill/plain/jacquard/rib/jersey等)",
      "weight_gsm": [最低克重, 最高克重],
      "finish": ["后整理工艺数组"],
      "stretch": "none|one-way|two-way|four-way",
      "gloss": "low|medium|high",
      "handfeel": "soft|crisp|drapey|dry|bouncy",
      "alternatives": ["替代面料1", "替代面料2", "替代面料3"]
    },
    "print": {
      "type": "工艺类型(reactive|disperse|pigment|sublimation|plastisol|foil|flock|discharge)",
      "colors": 套色数量,
      "resolution_dpi": 分辨率要求,
      "repeat": "重复尺寸(如32cm x 32cm)",
      "base_fabric_suggestion": ["推荐底布1", "推荐底布2"],
      "workflow": ["工序步骤1", "工序步骤2", "..."],
      "risks": ["风险点1", "风险点2"]
    },
    "construction": {
      "stitch": "针型(如lockstitch 301)",
      "needle_thread": "针号与线号(如75/11, tex40)",
      "seam": "缝型(如SSa-1)",
      "edge_finish": "边缝处理",
      "interlining": "衬料规格",
      "tolerance": "公差要求"
    }
  },
  "recommendations": {
    "budget_low": "低成本方案描述",
    "budget_mid": "中等价位方案描述", 
    "budget_high": "高端方案描述",
    "suppliers_or_process": ["采购/工艺建议1", "建议2"]
  },
  "dfm_risks": ["可生产性风险点1", "风险点2"],
  "next_actions": ["下一步行动1", "行动2"]
}"""

UNIFIED_SCHEMA_EN = """{
  "task": "fabric|print|construction",
  "summary": "One-sentence core conclusion in English",
  "details": {
    "fabric": {
      "material": "Material name in English (e.g. silk, cotton, polyester)",
      "weave_or_knit": "Structure in English (satin/twill/plain/jacquard/rib/jersey)",
      "weight_gsm": [min_weight, max_weight],
      "finish": ["Finishing process array in English"],
      "stretch": "none|one-way|two-way|four-way",
      "gloss": "low|medium|high",
      "handfeel": "soft|crisp|drapey|dry|bouncy",
      "alternatives": ["Alternative fabric 1 in English", "Alternative 2", "Alternative 3"]
    },
    "print": {
      "type": "Process type in English (reactive/disperse/pigment/sublimation/plastisol/foil/flock/discharge)",
      "colors": color_count_number,
      "resolution_dpi": resolution_requirement,
      "repeat": "Repeat size in English (e.g. 32cm x 32cm)",
      "base_fabric_suggestion": ["Recommended base fabric 1 in English", "Base fabric 2"],
      "workflow": ["Workflow step 1 in English", "Step 2", "..."],
      "risks": ["Risk point 1 in English", "Risk 2"]
    },
    "construction": {
      "stitch": "Stitch type in English (e.g. lockstitch 301)",
      "needle_thread": "Needle and thread specs in English (e.g. 75/11 needle, tex40 thread)",
      "seam": "Seam type in English (e.g. SSa-1)",
      "edge_finish": "Edge finishing method in English",
      "interlining": "Interlining specification in English",
      "tolerance": "Tolerance requirement in English"
    }
  },
  "recommendations": {
    "budget_low": "Low-cost option description in English",
    "budget_mid": "Mid-range option description in English", 
    "budget_high": "High-end option description in English",
    "suppliers_or_process": ["Sourcing/process recommendation 1 in English", "Recommendation 2"]
  },
  "dfm_risks": ["DFM risk point 1 in English", "Risk 2"],
  "next_actions": ["Next action 1 in English", "Action 2"]
}"""

# ==================== 专业提示词模板 ====================
PROMPT_FABRIC_ZH = """你是纺织面料与成衣工艺专家。只输出JSON，不要多余文字。**所有字段值必须用中文表达**。

分析图片中**裁剪框ROI**的面料特征：
- 材质/组织（如：真丝/棉/粘胶/涤纶/锦纶/氨纶等，组织如：缎纹/斜纹/平纹/提花/罗纹/针织等）
- 克重范围（gsm，根据视觉厚度和垂坠感估算）
- 光泽度（低/中等/高）
- 弹性（无/单向弹/双向弹/四向弹）
- 手感（柔软/挺括/垂坠/干爽/弹性）
- 可能的后整理工艺（压光/涂层/丝光/磨毛/预缩等）
- 可替代的同类面料（同价位/更低价/更高价各给1-2个）

**重要**：material、weave_or_knit、stretch、gloss、handfeel 等字段的值必须用中文，如：
- material: "涤纶" (不是 polyester)
- weave_or_knit: "斜纹" (不是 twill)
- stretch: "无弹性" (不是 none)
- gloss: "中等" (不是 medium)
- handfeel: "挺括" (不是 crisp)

结合上下文：预算档位={budget}，使用场景={scene}，约束条件={constraints}

按此JSON模板输出（task字段填"fabric"）：
{schema}"""

PROMPT_PRINT_ZH = """你是印花与分色工程专家。只输出JSON，不要多余文字。**所有字段值必须用中文表达**。

分析图片中**裁剪框ROI**的印花/图案特征：
- 判断工艺类型（如：反应染料印花/分散染料印花/涂料印花/热升华印花/胶浆印花/烫金/植绒/拔染等）
- 估算套色数量（通过色彩复杂度判断）
- 分辨率要求（dpi，根据图案精细度）
- 重复尺寸/花型大小
- 推荐底布类型（棉/涤纶/混纺等及其组织）
- 完整工艺流程（含预处理/印花/固色/后处理）
- 风险点（对位公差/色牢度/渗色/缩水/套色偏差等）
- 小批量与大货的不同工艺路线

**重要**：type 字段值必须用中文工艺名称。

结合上下文：预算={budget}，场景={scene}，约束={constraints}

按此JSON模板输出（task字段填"print"）：
{schema}"""

PROMPT_CONSTRUCTION_ZH = """你是版师与缝制工艺专家。只输出JSON，不要多余文字。**所有字段值必须用中文表达**。

分析图片中**裁剪框ROI**的结构与做法：
- 推荐针型（如：平缝（301）/链缝（401）/包缝（504）等）
- 线号与针号（如tex40配75/11针）
- 缝型代码（如SSa-1, LSc-2等ISO标准，需附中文说明）
- 边缝处理方式（包缝/滚边/贴边/包边等）
- 衬料规格（梭织/针织/无纺布，克重，粘合温度）
- 公差要求（±多少mm）
- 特殊工序（打褶/压线/嵌条/贴袋等）
- 生产注意事项与避坑指南

**重要**：stitch、seam、edge_finish 等字段值要包含中文说明。

结合上下文：预算={budget}，场景={scene}，约束={constraints}

按此JSON模板输出（task字段填"construction"）：
{schema}"""

# 英文版本
PROMPT_FABRIC_EN = """You are a textile and garment manufacturing expert. 

**CRITICAL REQUIREMENT: Output ONLY JSON in ENGLISH. EVERY SINGLE field value, description, and text MUST be in English. NO Chinese characters allowed.**

Analyze the fabric in the cropped ROI region:
- Material/construction (silk/cotton/viscose/polyester/nylon/spandex + satin/twill/plain/jacquard/jersey/rib)
- Weight range in gsm (estimate from visual drape and thickness)
- Gloss level (low/medium/high)
- Stretch (none/one-way/two-way/four-way)
- Handfeel (soft/crisp/drapey/dry/bouncy)
- Finishing processes (calendering/coating/mercerizing/brushing/pre-shrinking)
- Alternative fabrics (same/lower/higher price points)

Context: budget={budget}, use case={scene}, constraints={constraints}

**IMPORTANT: Use English for ALL field values - material names, process descriptions, recommendations, risks, actions - EVERYTHING must be in English.**

Output JSON following this schema (task="fabric"):
{schema}"""

PROMPT_PRINT_EN = """You are a print and color separation expert. 

**CRITICAL REQUIREMENT: Output ONLY JSON in ENGLISH. EVERY SINGLE field value, description, and text MUST be in English. NO Chinese characters allowed.**

Analyze the print/pattern in the cropped ROI region:
- Process type (reactive/disperse/pigment/sublimation/plastisol/foil/flock/discharge)
- Color count (estimate from complexity)
- Resolution requirement (dpi, based on detail level)
- Repeat size/pattern dimensions
- Recommended base fabrics
- Complete workflow (pre-treatment/printing/fixing/post-processing)
- Risks (registration/color fastness/bleeding/shrinkage)
- Small batch vs bulk production approaches

Context: budget={budget}, scene={scene}, constraints={constraints}

**IMPORTANT: Use English for ALL field values - process names, workflow steps, recommendations, risks, actions - EVERYTHING must be in English.**

Output JSON following this schema (task="print"):
{schema}"""

PROMPT_CONSTRUCTION_EN = """You are a pattern making and sewing expert. 

**CRITICAL REQUIREMENT: Output ONLY JSON in ENGLISH. EVERY SINGLE field value, description, and text MUST be in English. NO Chinese characters allowed.**

Analyze the construction details in the cropped ROI region:
- Stitch type (lockstitch 301/chainstitch 401/overlock 504)
- Thread & needle specs (e.g. tex40 with 75/11 needle)
- Seam class (SSa-1, LSc-2, ISO standards)
- Edge finishing method
- Interlining specifications
- Tolerance requirements (±mm)
- Special operations (pleating/topstitching/piping/pockets)
- Production tips and pitfalls

Context: budget={budget}, scene={scene}, constraints={constraints}

**IMPORTANT: Use English for ALL field values - stitch types, specifications, recommendations, risks, actions - EVERYTHING must be in English.**

Output JSON following this schema (task="construction"):
{schema}"""

# 旧提示词已移除，使用上面的专业模板系统

# ==================== 辅助函数 ====================
def image_to_base64_datauri(img: Image.Image) -> str:
    """将 PIL Image 转换为 DashScope 接受的 base64 data URI"""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_bytes = buf.getvalue()
    b64_str = base64.b64encode(img_bytes).decode('utf-8')
    return f"data:image/png;base64,{b64_str}"

def make_prompt(task_type: str, lang: str, budget: str, scene: str, constraints: str) -> str:
    """根据任务类型、语言和上下文生成提示词"""
    # 选择对应语言的 Schema
    schema = UNIFIED_SCHEMA_ZH if lang == "zh" else UNIFIED_SCHEMA_EN
    
    # 选择对应的提示词模板
    if lang == "zh":
        if task_type == "fabric":
            template = PROMPT_FABRIC_ZH
        elif task_type == "print":
            template = PROMPT_PRINT_ZH
        elif task_type == "construction":
            template = PROMPT_CONSTRUCTION_ZH
        else:  # auto - 让模型自己判断
            template = PROMPT_FABRIC_ZH  # 默认用fabric作为兜底
    else:
        if task_type == "fabric":
            template = PROMPT_FABRIC_EN
        elif task_type == "print":
            template = PROMPT_PRINT_EN
        elif task_type == "construction":
            template = PROMPT_CONSTRUCTION_EN
        else:
            template = PROMPT_FABRIC_EN
    
    # 填充上下文参数
    prompt = template.format(
        budget=budget,
        scene=scene,
        constraints=constraints,
        schema=schema
    )
    
    return prompt

def try_parse_json(text: str) -> dict:
    """
    简单 JSON 抽取（从大段文字里找首个 {...}）
    
    尝试策略：
    1. 直接 json.loads
    2. 提取 markdown 代码块
    3. 正则提取第一个 JSON 对象
    4. 尝试修复常见的 JSON 格式问题
    """
    if not text or not isinstance(text, str):
        return {}
    
    # 策略1: 直接解析
    try:
        return json.loads(text.strip())
    except Exception:
        pass
    
    # 策略2: 提取 markdown 代码块
    if "```json" in text:
        try:
            json_text = text.split("```json")[1].split("```")[0].strip()
            return json.loads(json_text)
        except Exception:
            pass
    
    if "```" in text:
        try:
            json_text = text.split("```")[1].split("```")[0].strip()
            return json.loads(json_text)
        except Exception:
            pass
    
    # 策略3: 正则提取第一个完整的 JSON 对象
    # 找到第一个 { 和最后一个匹配的 }
    try:
        first_brace = text.find('{')
        if first_brace >= 0:
            # 从第一个 { 开始，找到匹配的 }
            depth = 0
            for i in range(first_brace, len(text)):
                if text[i] == '{':
                    depth += 1
                elif text[i] == '}':
                    depth -= 1
                    if depth == 0:
                        json_text = text[first_brace:i+1]
                        return json.loads(json_text)
    except Exception:
        pass
    
    # 策略4: 正则提取（兜底）
    match = re.search(r'\{.*\}', text, flags=re.S)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    
    return {}

def ensure_min_size(pil_img: Image.Image, tgt: int = 640) -> Image.Image:
    """保证传云端的图片最短边≥tgt，避免太小导致识别失败"""
    w, h = pil_img.size
    if min(w, h) >= tgt:
        return pil_img
    scale = tgt / min(w, h)
    nw, nh = int(w * scale), int(h * scale)
    return pil_img.resize((nw, nh), Image.BICUBIC)

# ==================== 云端推理 ====================
def cloud_infer(
    pil_image: Image.Image,
    engine: str,
    lang: str = "zh",
    enable_web: bool = False,
    k_per_query: int = 4,
    task_type: str = "auto",
    budget: str = "mid",
    scene: str = "casual",
    constraints: str = "无特殊约束",
    api_key: Optional[str] = None
) -> Dict:
    """
    云端生产分析 - 专业版
    
    Args:
        pil_image: PIL Image 对象（ROI裁剪区域）
        engine: 模型引擎 ("qwen-vl", "qwen-vl-plus")
        lang: 语言 ("zh", "en")
        enable_web: 是否启用联网检索
        k_per_query: 每个候选检索条数
        task_type: 任务类型 ("fabric"|"print"|"construction"|"auto")
        budget: 预算档位 ("low"|"mid"|"high")
        scene: 使用场景 (如"casual"|"evening"|"activewear"|"home")
        constraints: 约束条件 (如"环保,可水洗,四向弹")
        api_key: Optional explicit DashScope API key (e.g. entered in the UI)
    
    Returns:
        统一JSON Schema包含：
        - task, summary, details, recommendations, dfm_risks, next_actions
    """
    # Do not silently route unsupported engines (e.g. OpenAI/Gemini) to Qwen.
    if engine not in MODEL_MAP:
        return {
            "labels": [],
            "confidences": [],
            "reasoning": f"Unsupported model engine: {engine}. Supported: {', '.join(MODEL_MAP)}",
            "raw": "",
            "model": engine,
            "engine": "error",
        }

    # 检查依赖
    if dashscope is None or MultiModalConversation is None:
        return {
            "labels": [],
            "confidences": [],
            "reasoning": "DashScope SDK 未安装。请运行: pip install dashscope",
            "raw": "",
            "model": engine,
            "engine": "error"
        }
    
    # 获取 API Key
    api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        # 尝试从 streamlit secrets 读取
        try:
            import streamlit as st
            api_key = st.secrets.get("DASHSCOPE_API_KEY")
        except Exception:
            pass
    
    if not api_key:
        return {
            "labels": [],
            "confidences": [],
            "reasoning": "缺少 DASHSCOPE_API_KEY。请在 .streamlit/secrets.toml 或环境变量中配置。",
            "raw": "",
            "model": engine,
            "engine": "error"
        }
    
    # Pass credentials per request; do not mutate process-global SDK state.
    # 选择模型
    model = MODEL_MAP.get(engine, "qwen-vl-plus")
    
    # 确保图片尺寸足够
    pil_image = ensure_min_size(pil_image, 640)
    
    # 转换为 base64 data URI
    img_datauri = image_to_base64_datauri(pil_image)
    
    # 构建消息 - 使用新的提示词系统
    system_prompt = make_prompt(task_type, lang, budget, scene, constraints)
    
    # 用户消息根据任务类型调整
    if lang == "zh":
        if task_type == "fabric":
            user_text = "分析这个裁剪区域的面料特征"
        elif task_type == "print":
            user_text = "分析这个裁剪区域的印花/图案特征"
        elif task_type == "construction":
            user_text = "分析这个裁剪区域的结构与做法"
        else:
            user_text = "分析这个裁剪区域（面料/印花/工艺结构）"
    else:
        # 英文模式 - 强制要求英文输出
        if task_type == "fabric":
            user_text = "Analyze the fabric characteristics in this cropped region. OUTPUT EVERYTHING IN ENGLISH ONLY."
        elif task_type == "print":
            user_text = "Analyze the print/pattern characteristics in this cropped region. OUTPUT EVERYTHING IN ENGLISH ONLY."
        elif task_type == "construction":
            user_text = "Analyze the construction details in this cropped region. OUTPUT EVERYTHING IN ENGLISH ONLY."
        else:
            user_text = "Analyze this cropped region (fabric/print/construction). OUTPUT EVERYTHING IN ENGLISH ONLY."
    
    messages = [
        {
            "role": "system",
            "content": [{"text": system_prompt}]
        },
        {
            "role": "user",
            "content": [
                {"image": img_datauri},
                {"text": user_text}
            ]
        }
    ]
    
    # 调用 API
    try:
        response = MultiModalConversation.call(
            api_key=api_key,
            model=model,
            messages=messages,
            top_p=0.7,
            temperature=0.2,
        )
        
        # 提取响应文本 - 兼容 DashScope 多种响应格式
        raw_text = ""
        extraction_path = "unknown"  # 调试：记录提取路径
        
        if hasattr(response, 'output'):
            output = response.output
            
            # 情况1：output 是列表 [{'text': '...'}]
            if isinstance(output, list) and len(output) > 0:
                extraction_path = "list_branch"
                first_item = output[0]
                if isinstance(first_item, dict):
                    raw_text = first_item.get('text', '') or first_item.get('content', '') or str(first_item)
                    extraction_path = "list_dict_branch"
                else:
                    raw_text = str(first_item)
                    extraction_path = "list_str_branch"
            
            # 情况2：output 是字典 {'choices': [...]}
            elif isinstance(output, dict):
                extraction_path = "dict_branch"
                # 尝试从 choices 提取
                choices = output.get('choices', [])
                if choices and len(choices) > 0:
                    message = choices[0].get('message', {})
                    content = message.get('content', '')
                    
                    # content 可能又是列表 [{'text': '...'}]
                    if isinstance(content, list) and len(content) > 0:
                        first_content = content[0]
                        if isinstance(first_content, dict):
                            raw_text = first_content.get('text', '') or first_content.get('content', '')
                            extraction_path = "dict_choices_list_branch"
                        else:
                            raw_text = str(first_content)
                            extraction_path = "dict_choices_list_str_branch"
                    elif isinstance(content, str):
                        raw_text = content
                        extraction_path = "dict_choices_str_branch"
                    else:
                        raw_text = str(content)
                        extraction_path = "dict_choices_fallback"
                
                # 兜底：直接提取 text 或 content 字段
                if not raw_text:
                    raw_text = output.get('text', '') or output.get('content', '')
                    extraction_path = "dict_text_branch"
            
            # 情况3：output 是字符串
            elif isinstance(output, str):
                raw_text = output
                extraction_path = "str_branch"
            
            # 最终兜底
            if not raw_text:
                raw_text = str(output)
                extraction_path = "fallback_str"
        else:
            raw_text = str(response)
            extraction_path = "no_output"
        
        # === 调试信息 ===
        # print(f"DEBUG: raw_text type = {type(raw_text)}")
        # print(f"DEBUG: raw_text[:200] = {raw_text[:200]}")
        
        # 解析 JSON
        data = try_parse_json(raw_text)
        
        # print(f"DEBUG: parsed data keys = {list(data.keys()) if data else 'empty'}")
        
        if not data:
            # 解析失败，返回原始文本
            return {
                "labels": [],
                "confidences": [],
                "reasoning": raw_text[:500] if raw_text else "模型返回为空",
                "raw": raw_text,
                "model": model,
                "engine": "cloud",
                "_debug": {
                    "extraction_path": extraction_path,
                    "raw_text_type": str(type(raw_text)),
                    "raw_text_len": len(raw_text) if raw_text else 0,
                    "raw_text_preview": str(raw_text)[:500] if raw_text else "empty",
                    "output_type": str(type(response.output)) if hasattr(response, 'output') else "no output",
                    "output_preview": str(response.output)[:500] if hasattr(response, 'output') else "no output"
                }
            }
        
        # 如果解析成功，检查是否是新的统一格式（包含task字段）
        if "task" in data:
            # 新统一格式，直接返回解析后的JSON（附加meta信息）
            data["_meta"] = {
                "model": model,
                "engine": "cloud",
                "raw": raw_text
            }
            return data
        
        # 旧格式兼容逻辑
        labels = data.get("labels", [])
        confidences = data.get("confidences", [])
        reasoning = data.get("reasoning", raw_text)
        
        # 对齐 labels 和 confidences
        if len(confidences) < len(labels):
            remaining = 1.0 - sum(confidences)
            avg_conf = remaining / max(1, len(labels) - len(confidences))
            confidences.extend([avg_conf] * (len(labels) - len(confidences)))
        elif len(confidences) > len(labels):
            confidences = confidences[:len(labels)]
        
        # 归一化置信度
        total_conf = sum(confidences) if confidences else 1.0
        if total_conf > 0:
            confidences = [c / total_conf for c in confidences]
        
        return {
            "labels": labels,
            "confidences": confidences,
            "reasoning": reasoning,
            "raw": raw_text,
            "model": model,
            "engine": "cloud"
        }
    
    except Exception as e:
        return {
            "labels": [],
            "confidences": [],
            "reasoning": f"调用失败: {type(e).__name__}: {str(e)}",
            "raw": "",
            "model": model,
            "engine": "error"
        }

# ==================== 兼容接口 ====================
def analyze_image(
    image: Image.Image,
    api_key: str = None,
    lang: str = "zh",
    engine: str = "qwen-vl",
    enable_web: bool = False,
    k_per_query: int = 4
) -> Dict:
    """
    分析图片 - 兼容旧接口
    
    Args:
        image: PIL Image 对象
        api_key: API Key（可选，会自动从环境变量或 secrets 读取）
        lang: 语言
        engine: 模型引擎
        enable_web: 是否启用联网检索
        k_per_query: 每个候选检索条数
    
    Returns:
        {
            "result": {
                "labels": [...],
                "confidences": [...],
                "reasoning": "...",
                "raw": "..."
            },
            "meta": {
                "engine": "cloud",
                "model": "qwen-vl-plus"
            }
        }
    """
    # 如果提供了 api_key，设置到环境变量
    if api_key:
        os.environ["DASHSCOPE_API_KEY"] = api_key
    
    # 调用云端推理
    result = cloud_infer(
        pil_image=image,
        engine=engine,
        lang=lang,
        enable_web=enable_web,
        k_per_query=k_per_query
    )
    
    # 提取 meta 信息
    model = result.pop("model", engine)
    engine_status = result.pop("engine", "cloud")
    
    return {
        "result": result,
        "meta": {
            "engine": engine_status,
            "model": model
        }
    }
