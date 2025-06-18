import functions_framework
from flask import jsonify

@functions_framework.http
def mbti_analyzer(request):
    """一個簡單的 HTTP 函式，只回傳成功訊息。"""
    
    # 設定 CORS 標頭，允許前端網頁呼叫
    headers = {
        "Access-Control-Allow-Origin": "*"
    }

    # 回傳一個固定的 JSON 物件
    response_data = {
        "message": "後端連接成功！歡迎來到雲端 AI 世界！"
    }
    
    return jsonify(response_data), 200, headers