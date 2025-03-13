from datasets import load_dataset

from distilabel.models import OpenAILLM
from distilabel.pipeline import Pipeline
from distilabel.steps.tasks import TextGeneration
from distilabel.steps import StepResources

# 匯入 API 金鑰
import os
from dotenv import load_dotenv
load_dotenv()  # 載入環境變數
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# 自訂的 Prompt 模板 strip(), lstrip(), rstrip()
SYSTEM_PROMPT_old = '''You will be given a problem with a reference answer. Please analyze the problem step by step and provide your final answer from a Taiwanese perspective, while following these guidelines: 
**(1) Capability Scope**: Support both **Chinese and English** queries, acknowledge **real-time information limitations**, and provide **technical explanations** for AI-related questions when necessary. 
**(2) Response Quality**: Ensure **logical, well-structured, and comprehensive** responses, use **markdown formatting** for clarity, and acknowledge uncertainties when necessary. 
**(3) Ethical Operation**: **Refuse** illegal, violent, or explicit content, maintain **political neutrality**, and protect **user privacy** by avoiding data collection. 
**(4) Specialized Processing**: Before responding, perform internal reasoning within <think>...</think> tags, intermediate steps, and deductions are enclosed within these tags. Only provide the final response outside of '<think>...</think>'.  
**(5) Response Execution**: **Do not introduce yourself** or mention the response creator—simply **answer the question** following these rules."
'''.rstrip()

SYSTEM_PROMPT = '''
You will be given a problem with a reference answer. Please analyze the problem step by step and provide your final answer from a Taiwanese perspective, while following these guidelines: 
**(1) Capability Scope**: Support both **Chinese and English** queries, acknowledge **real-time information limitations**, and provide **technical explanations** for AI-related questions when necessary. 
**(2) Response Quality**: Ensure **logical, well-structured, and comprehensive** responses, use **markdown formatting** for clarity, and acknowledge uncertainties when necessary. 
**(3) Ethical Operation**: **Refuse** illegal, violent, or explicit content, maintain **political neutrality**, and protect **user privacy** by avoiding data collection. 
**(4) Specialized Processing**: Before responding, perform internal reasoning within <think>...</think> tags, intermediate steps, and deductions are enclosed within these tags. Only provide the final response outside of '<think>...</think>'.  
**(5) Response Execution**: **Do not introduce yourself** or mention the response creator—simply **answer the question** following these rules."
'''.rstrip()

CUSTOM_TEMPLATE = '''### Question: 
{{ Question }}

### Reference Answer: 
<think>
 {{ Response }}
</think>
'''.rstrip()


# 建立處理流程 (Pipeline)
with Pipeline() as pipeline:
    TextGeneration(
        llm=OpenAILLM(
            base_url="https://integrate.api.nvidia.com/v1",  # OpenAI LLM 服務的基礎 URL
            api_key=OPENAI_API_KEY,  # 使用環境變數讀取 API 金鑰
            model="deepseek-ai/deepseek-r1",  # 指定要使用的語言模型
            generation_kwargs={"temperature": 0.7, "max_new_tokens": 2048},  # 設定生成參數
            timeout=120,  # 請求逾時時間 (秒)
            max_retries=6,  # 最大重試次數
        ),
        system_prompt=SYSTEM_PROMPT,
        input_batch_size=2,  # 每次處理的輸入批次大小
        template=CUSTOM_TEMPLATE,  # 使用自訂的 Prompt 模板
        columns=["Question","Response"],  # 指定要使用的資料欄位
        num_generations=2,  # 每個輸入要產生的回應數量
        group_generations=False,  # 是否將多個生成結果分組 (預設為 False，每個生成的結果都是獨立的)
        resources=StepResources(replicas=2),  # 設定此步驟的副本數量 (提高並行處理能力)
    )

# 載入測試資料集 FreedomIntelligence/medical-o1-reasoning-SFT
dataset = load_dataset("FreedomIntelligence/medical-o1-reasoning-SFT", "en", split="train")
dataset_head = dataset[:10]
#print(dataset_head)

# 執行處理流程並取得結果
distiset = pipeline.run(dataset=dataset, dataset_batch_size=10,use_cache=True)

# 將結果上傳至 Hugging Face Hub
distiset.push_to_hub(repo_id="c00cjz00/medical-o1-reasoning-SFT")

