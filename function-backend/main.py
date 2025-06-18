import os
import re
import functions_framework
from flask import jsonify
from google.cloud import language_v2

# 初始化用戶端
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
        final_response = {
            "keywords": list(keywords.keys())
        }
        return jsonify(final_response), 200, headers

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"後端分析服務發生錯誤: {e}"}), 500, headers

def clean_chat_log(text: str) -> str:
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
    user_lines = [line.replace(f"{user_name} ", "", 1) for line in full_log.split('\n') if line.startswith(user_name + " ")]
    if not user_lines: return {}
    my_text_only = "\n".join(user_lines)
    document = language_v2.Document(content=my_text_only, type_=language_v2.Document.Type.PLAIN_TEXT)
    response = language_client.analyze_entities(document=document)
    return {entity.name: entity.importance for entity in response.entities[:30]}