# 知識蒸餾 (Think) 生成   

## 安裝套件
```bash=
mkdir -p ~/uv
cd ~/uv
export PATH=$PATH:$HOME/.local/bin
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv openr1d --python 3.11 && source ~/uv/openr1d/bin/activate && uv pip install --upgrade pip
uv pip install distilabel python-dotenv openai opencc beautifulsoup4 Pillow huggingface-hub
```

## 下載套件
```bash=
mkdir -p ~/github/ 
cd ~/github
git clone https://github.com/c00cjz00/open-r1-dataset.git
```

## **編輯 .env 並登錄API KEY**
- https://build.nvidia.com/deepseek-ai/deepseek-r1 取得 nvidia-key
```bash
cd ~/github/open-r1-dataset
echo "OPENAI_API_KEY=sk-xxxx" >.env
```

## **編輯 登錄HF KEY**

```bash
source ~/uv/openr1d/bin/activate
huggingface-cli login
```

## **指令一: generate_cot_from_Q.py 指令說明**

```bash
python generate_cot_from_Q.py \
    --hf-dataset c00cjz00/ft_dataset_parquet \
    --hf-dataset-config b8.3-patch4_v1 \
    --hf-dataset-split train \
    --hf-output-dataset c00cjz00/b8.3-patch4_v1-save \
    --vllm-server-url https://integrate.api.nvidia.com/v1 \
    --model deepseek-ai/deepseek-r1 \
    --temperature 0.6 \
    --max-new-tokens 8192 \
    --num-generations 1 \
    --input-batch-size 4 \
    --page 1 \
    --page-size 64 \
    --client-replicas 2 \
    --timeout 600 \
    --retries 3 \
    --prompt-column prompt \
    --question-column-name input \
    --answer-column-name output \
    --answer-max-len 3072 \
    --prompt-template "You will be given a problem. Please analyze the problem step by step and provide your final answer in **Traditional Chinese (zh-TW) from a Taiwanese perspective** while following these guidelines:  {{ instruction }}"
```

**指令參數說明**

### **1. 數據集相關參數**
- `--hf-dataset c00cjz00/ft_dataset_parquet`
  - 指定要使用的 Hugging Face 數據集 (`c00cjz00/ft_dataset_parquet`)。
- `--hf-dataset-config b8.3-patch4_v1`
  - 指定數據集的配置版本 (`b8.3-patch4_v1`)。
- `--hf-dataset-split train`
  - 使用 `train` 切分的數據集。
- `--hf-output-dataset c00cjz00/b8.3-patch4_v1-save`
  - 生成的數據集將儲存至 Hugging Face Hub (`c00cjz00/b8.3-patch4_v1-save`)。

### **2. 模型與推理服務**
- `--vllm-server-url https://integrate.api.nvidia.com/v1`
  - 指定 vLLM 伺服器 API 端點 (`https://integrate.api.nvidia.com/v1`)。
- `--model deepseek-ai/deepseek-r1`
  - 使用 `DeepSeek-R1` 模型進行推理。

### **3. 生成相關參數**
- `--temperature 0.6`
  - 設定 `temperature`，值越高則生成內容越隨機，越低則結果更確定。
- `--max-new-tokens 8192`
  - 生成的最大新 token 數量（最多 8192 個 token）。
- `--num-generations 1`
  - 每個問題生成 `1` 個回答。

### **4. 批次與處理設定**
- `--input-batch-size 4`
  - 每批次處理 `4` 條數據。
- `--page 1`
  - 指定數據集的頁數（第 `1` 頁）。
- `--page-size 64`
  - 每頁處理 `64` 條數據。
- `--client-replicas 2`
  - 啟動 `2` 個客戶端副本來提高並行處理能力。
- `--timeout 600`
  - 設定請求的超時時間為 `600` 秒。
- `--retries 3`
  - 設定請求失敗後的最大重試次數為 `3` 次。

### **5. 數據集列名設定**
- `--prompt-column prompt`
  - 指定數據集中存放 Prompt（提示詞）的欄位名稱為 `prompt`。
- `--question-column-name input`
  - 指定問題所在的欄位名稱為 `input`。
- `--answer-column-name output`
  - 指定答案所在的欄位名稱為 `output`。
- `--answer-max-len 3072`
  - 設定答案的最大長度為 `3072` 個 token。

### **6. Prompt 設定**
- `--prompt-template "You will be given a problem..."`
  - 設定 Prompt 模板，引導模型提供 **繁體中文（台灣視角）** 的答案。
  - `{{ instruction }}` 是佔位符，會被動態填充為具體指令。

## **指令執行的步驟**
1. **從 Hugging Face 數據集中讀取數據**，選擇 `train` 切分並處理 `page 1`（64 條數據）。
2. **使用 DeepSeek-R1 模型** 透過 NVIDIA vLLM API 進行推理。
3. **使用 Chain-of-Thought (COT) 方法** 來生成 **繁體中文** 回答。
4. **將結果存入 Hugging Face Hub** (`c00cjz00/tw-instruct-500k-fix-save`)。
5. **支持錯誤重試**（最多 3 次）並允許多個客戶端 (`client-replicas=2`）併行處理。


