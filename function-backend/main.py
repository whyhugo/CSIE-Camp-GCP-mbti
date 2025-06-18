import os
import re
import json
import traceback

import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

import functions_framework
from flask import jsonify
from google.cloud import language_v2
import google.auth

# --- 全域設定 ---
try:
    _, default_project = google.auth.default()
except (google.auth.exceptions.DefaultCredentialsError):
    default_project = None

PROJECT_ID = os.getenv("GCP_PROJECT", default_project)
LOCATION = os.getenv("GCP_LOCATION", "us-central1")
GEMINI_MODEL_NAME = "gemini-pro"

# 初始化用戶端
vertexai.init(project=PROJECT_ID, location=LOCATION)
language_client = language_v2.LanguageServiceClient()

@functions_framework.http
def mbti_analyzer(request):
    headers = {
        "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "POST",
        "Access-Control-Allow-Headers": "Content-Type",
    }
    if request.method == "OPTIONS": return "", 204, headers
    if request.method != "POST": return "僅接受 POST 請求", 405, headers

    request_json = request.get_json(silent=True)
    if not request_json or "text" not in request_json or "user_name" not in request_json:
        return jsonify({"error": "請求中缺少文字內容或使用者暱稱"}), 400, headers

    raw_text = request_json["text"]
    user_name = request_json["user_name"]
    
    cleaned_log = clean_chat_log(raw_text)
    if not cleaned_log:
        return jsonify({"error": "清理後無有效對話內容"}), 400, headers

    try:
        keywords = analyze_text_entities(cleaned_log, user_name)
        gemini_result = analyze_mbti_text_only(cleaned_log, user_name)

        final_response = {
            "mbtiResult": gemini_result,
            "keywords": ", ".join(keywords.keys())
        }
        return jsonify(final_response), 200, headers

    except Exception as e:
        print(f"發生嚴重錯誤: {e}")
        traceback.print_exc()
        return jsonify({"error": f"後端分析服務發生錯誤: {e}"}), 500, headers

def analyze_mbti_text_only(full_log: str, user_name: str) -> dict:
    """只進行文字分析的 Gemini 函式。"""
    model = GenerativeModel(GEMINI_MODEL_NAME)
    prompt = f"""
    ROLE: 你是一位結合了心理學專業的AI。
    TASK: 請依據下方提供的對話紀錄，針對使用者「{user_name}」，完成性格分析。
    ---
    任務：
    1.  根據「{user_name}」的發言，推斷出其最可能的 MBTI 人格類型。
    2.  從對話中找出 3 個最關鍵的證據來支持你的判斷。
    3.  用溫暖且鼓勵的中文語氣，給予「{user_name}」一句個人化建議。
    ---
    OUTPUT FORMAT: 你必須嚴格按照以下 JSON 格式回傳，不得包含任何 JSON 結構外的文字。
    ```json
    {{
      "mbti_type": "string",
      "evidence": ["string", "string", "string"],
      "suggestion": "string"
    }}
    ```
    ---
    對話紀錄:
    ```
    {full_log}
    ```
    """
    generation_config = GenerationConfig(
        temperature=0.7, max_output_tokens=2048, response_mime_type="application/json",
    )
    response = model.generate_content(prompt, generation_config=generation_config)
    return json.loads(response.text)

def clean_chat_log(text: str) -> str:
    # (此函式與版本 2 相同)
    lines = text.strip().split('\n')
    cleaned_lines = []
    skip_patterns = [
        re.compile(r"^\d{4}\.\d{2}\.\d{2}\s\w+$"), re.compile(r"^(Stickers|Photos|Videos)$"),
        re.compile(r"^https?://\S+$"), re.compile(r"^[\+\=\-\s]*$"),
    ]
    for line in lines:
        line = line.strip()
        if not line or any(pattern.match(line) for pattern in skip_patterns): continue
        cleaned_line = re.sub(r"^\d{2}:\d{2}\s", "", line)
        cleaned_line = re.sub(r"@\S+", "", cleaned_line).strip()
        if ' ' in cleaned_line: cleaned_lines.append(cleaned_line)
    return "\n".join(cleaned_lines)

def analyze_text_entities(full_log: str, user_name: str) -> dict:
    # (此函式與版本 2 相同)
    user_lines = [line.replace(f"{user_name} ", "", 1) for line in full_log.split('\n') if line.startswith(user_name + " ")]
    if not user_lines: return {}
    my_text_only = "\n".join(user_lines)
    document = language_v2.Document(content=my_text_only, type_=language_v2.Document.Type.PLAIN_TEXT)
    response = language_client.analyze_entities(document=document)
    return {entity.name: entity.importance for entity in response.entities[:30]}