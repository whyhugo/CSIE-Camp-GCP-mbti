# 雲端 AI 鏡像分析：從零到一完整部署指南

歡迎來到「The Mirror in Your Words」實作工作坊！本指南將帶領你從一個全新的 GCP 專案開始，親手建構一個功能強大的 AI 性格分析應用。

## 課前準備：建立你的雲端工作室

在開始部署應用程式之前，我們需要先設定好 GCP 環境。

### 步驟一：登入與環境準備

1.  **登入 GCP**：使用老師提供的帳號或您自己的帳號登入 [Google Cloud Console](https://console.cloud.google.com/)。
2.  **選取專案**：確認頂端顯示的是您要操作的 GCP 專案。
3.  **啟動 Cloud Shell**：點擊控制台右上角的 `>_` 圖示，啟動 Cloud Shell 指令列環境。後續所有指令都將在此處執行。

### 步驟二：啟用所有必要的 API

在 Cloud Shell 中，逐一執行以下指令，來開啟我們專案所需的所有服務。

```bash
# 啟用 Vertex AI, Cloud Run, Cloud Functions, Cloud Build, Natural Language, Storage, IAM 等核心服務
gcloud services enable aiplatform.googleapis.com \
run.googleapis.com \
functions.googleapis.com \
cloudbuild.googleapis.com \
language.googleapis.com \
storage-component.googleapis.com \
iam.googleapis.com \
cloudresourcemanager.googleapis.com
```

### 步驟三：設定權限 (最關鍵的一步)

我們的程式需要一個「身份」去呼叫 AI 服務。我們將為預設的服務帳戶授予必要的權限。

1.  **找到你的服務帳戶 Email**：

      * 執行 `gcloud projects describe $(gcloud config get-value project)` 指令，找到你的「專案編號 (projectNumber)」。
      * 你的預設服務帳戶 Email 就是：`[你的專案編號]-compute@developer.gserviceaccount.com`。

2.  **授予權限** (請將 `[你的服務帳戶Email]` 替換成上一步得到的完整 Email)：

    ```bash
    # 授予 Vertex AI 使用者權限
    gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
      --member="serviceAccount:[你的服務帳戶Email]" \
      --role="roles/aiplatform.user"

    # 授予 Natural Language AI 使用者權限
    gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
      --member="serviceAccount:[你的服務帳戶Email]" \
      --role="roles/language.user"

    # 授予 Cloud Storage 物件管理員權限
    gcloud projects add-iam-policy-binding $(gcloud config get-value project) \
      --member="serviceAccount:[你的服務帳戶Email]" \
      --role="roles/storage.objectAdmin"
    ```

### 步驟四：建立雲端儲存桶

我們需要一個地方來存放 AI 生成的圖片。

1.  **建立儲存桶** (Bucket)
    ```bash
    # 我們將儲存桶命名為 專案ID-mbti-images，確保名稱獨一無二
    gsutil mb -p $(gcloud config get-value project) -l us-central1 gs://$(gcloud config get-value project)-mbti-images
    ```
2.  **設定公開讀取權限**
    ```bash
    gsutil iam ch allUsers:objectViewer gs://$(gcloud config get-value project)-mbti-images
    ```
3.  **修改後端程式碼中的儲存桶名稱**
      * 在 Cloud Shell 左側的檔案瀏覽器中，打開 `function-backend/main.py`。
      * 找到 `BUCKET_NAME = ...` 那一行，將其修改為指向我們剛剛建立的儲存桶。
    <!-- end list -->
    ```python
    # 修改前:
    # BUCKET_NAME = os.getenv("GCP_BUCKET", "csiecamp-mbti-test-us-central1")

    # 修改後 (請將 [你的專案ID] 換成你自己的專案 ID):
    BUCKET_NAME = "[你的專案ID]-mbti-images"
    ```
      * 儲存檔案。

-----

## 循序漸進的應用部署

現在，環境已準備就緒！讓我們開始分步驟建構我們的應用。

### 第一步：基礎部署 (Hello World)

1.  **獲取程式碼**：在 Cloud Shell 中，下載並進入第一版的程式碼。
    ```bash
    git clone https://github.com/whyhugo/csie-camp-gcp-mbti.git
    cd csie-camp-gcp-mbti
    git checkout step1 
    ```
2.  **部署後端**：`cd function-backend` 並執行：
    ```bash
    gcloud functions deploy mbti-analyzer --gen2 --runtime python311 --region=us-central1 --trigger-http --allow-unauthenticated --entry-point mbti_analyzer --memory=1Gi
    ```
      * 部署成功後，複製 `uri:` 後面的網址。
3.  **部署前端**：`cd ../webapp-frontend` 並執行 (記得替換 URL)：
    ```bash
    gcloud run deploy personal-mbti-app --source . --region=us-central1 --allow-unauthenticated --update-env-vars=FUNCTION_URL=<貼上後端網址>
    ```
4.  **驗證**：打開前端的 `Service URL`，點擊按鈕，確認看到成功訊息。

### 第二步：加入 Natural Language API

1.  **獲取程式碼**：`git checkout step2`
2.  **重新部署後端**：`cd ../function-backend` 並執行部署指令。
3.  **重新部署前端**：`cd ../webapp-frontend` 並執行部署指令。
4.  **驗證**：打開前端網址，輸入文字，確認看到分析出的關鍵詞。

### 第三步：加入 Gemini Pro

1.  **獲取程式碼**：`git checkout step3`
2.  **重新部署後端**。
3.  **重新部署前端**。
4.  **驗證**：打開前端網址，輸入文字，確認看到完整的 MBTI 文字分析。

### 第四步：加入 Imagen (最終版)

1.  **獲取程式碼**：`git checkout main` (或 `step4`)
2.  **重新部署後端**。
3.  **重新部署前端**。
4.  **驗證**：打開前端網址，輸入文字，確認看到所有分析結果與圖片。

-----

## (重要) 課程結束後 - 資源卸除

為了避免產生額外費用，請務必在課程結束後清理所有資源。

### 方法一：逐一刪除服務

在 Cloud Shell 中執行以下指令：

```bash
# 刪除前端服務
gcloud run services delete personal-mbti-app --region=us-central1

# 刪除後端服務
gcloud functions delete mbti-analyzer --region=us-central1

# 刪除儲存桶 (這會刪除裡面所有圖片)
gsutil rm -r gs://$(gcloud config get-value project)-mbti-images
```

### 方法二：關閉整個專案 (最保險)

如果您使用的是自己的專案，這是最徹底乾淨的方法。

1.  前往 GCP 控制台。
2.  點擊左上角導覽選單 \> 「IAM 與管理」 \> 「設定」。
3.  在頁面頂端，點擊「**關閉**」。
4.  依照指示輸入專案 ID 以確認關閉。專案將在 30 天后被永久刪除。