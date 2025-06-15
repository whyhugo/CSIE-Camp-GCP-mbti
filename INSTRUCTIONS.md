# 雲端 AI 應用部署指令

## 步驟零：啟用必要的 API 服務
請在 GCP 控制台頂端的搜尋列，依序搜尋並啟用以下 5 個 API：
1. Cloud Functions API
2. Cloud Run API
3. Vertex AI API
4. Cloud Storage API
5. Cloud Natural Language API

## 步驟一：下載專案程式碼
# 在 Cloud Shell 中執行以下指令
git clone https://github.com/whyhugo/[您的倉庫名稱].git
cd [您的倉庫名稱]

## 步驟二：部署後端 AI 函式
# 進入後端程式碼資料夾
cd function-backend

# 執行部署指令 (此過程約需 3-5 分鐘)
gcloud functions deploy mbti-analyzer --gen2 --runtime python311 --region=asia-east1 --trigger-http --allow-unauthenticated

# 部署成功後，系統會顯示一個 https://... 的 `uri`。請務必將此網址完整複製下來！

## 步驟三：部署前端網站
# 回到上一層，並進入前端程式碼資料夾
cd ../webapp-frontend

# 在執行下方指令前，請先手動將 <貼上你複製的函式網址> 替換成你上一步複製的網址
gcloud run deploy personal-mbti-app --source . --region=asia-east1 --allow-unauthenticated --update-env-vars=FUNCTION_URL=<貼上你複製的函式網址>

# 部署成功後，系統會提供一個 Service URL。這就是你個人專屬應用的網址！