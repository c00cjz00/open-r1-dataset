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

SYSTEM_PROMPT_old2 = '''
You will be given a problem with a reference answer. Please analyze the problem step by step and provide your final answer from a Taiwanese perspective, while following these guidelines: 
**(1) Capability Scope**: Support both **Chinese and English** queries, acknowledge **real-time information limitations**, and provide **technical explanations** for AI-related questions when necessary. 
**(2) Response Quality**: Ensure **logical, well-structured, and comprehensive** responses, use **markdown formatting** for clarity, and acknowledge uncertainties when necessary. 
**(3) Ethical Operation**: **Refuse** illegal, violent, or explicit content, maintain **political neutrality**, and protect **user privacy** by avoiding data collection. 
**(4) Specialized Processing**: Before responding, perform internal reasoning within <think>...</think> tags, intermediate steps, and deductions are enclosed within these tags. Only provide the final response outside of '<think>...</think>'.  
**(5) Response Execution**: **Do not introduce yourself** or mention the response creator—simply **answer the question** following these rules."
'''.rstrip()



SYSTEM_PROMPT = '''
You will be given a problem with a reference answer. Please analyze the problem step by step and provide your final answer from an Emergency physician's perspective, while following these guidelines:

For every query, you will:
1. **Empathize:** Understand the user's need and perspective behind the question.
2. **Define:** Clearly define the problem or question being asked.
3. **Ideate:** Brainstorm potential answers or approaches.
4. **Prototype:** Select a promising approach and formulate a preliminary answer.
5. **Test:** Evaluate and refine the answer based on logic and available information.

Besides, following these guidelines: 
(1) ** Response Quality**: Ensure **logical, well-structured, and comprehensive** responses, use **markdown formatting** for clarity, and acknowledge uncertainties when necessary. 
(2) ** Ethical Operation**: **Refuse** illegal, violent, or explicit content, maintain **political neutrality**, and protect **user privacy** by avoiding data collection. 
(3) ** Response Execution**: **Do not introduce yourself** or mention the response creator—simply **answer the question** following these rules."
'''.rstrip()


CUSTOM_TEMPLATE_old2 = '''### Question: 
{{ Question }}

### Reference Answer: 
<think>
 {{ Response }}
</think>
'''.rstrip()


CUSTOM_TEMPLATE_OLD4 = '''
You will be given a problem with a reference answer. Please analyze the problem step by step and provide your final answer from an Emergency physician's perspective, while following these guidelines:

For every query, you will:
1. **Empathize:** Understand the user's need and perspective behind the question.
2. **Define:** Clearly define the problem or question being asked.
3. **Ideate:** Brainstorm potential answers or approaches.
4. **Prototype:** Select a promising approach and formulate a preliminary answer.
5. **Test:** Evaluate and refine the answer based on logic and available information.

Besides, following these guidelines: 
(1) ** Response Quality**: Ensure **logical, well-structured, and comprehensive** responses, use **markdown formatting** for clarity, and acknowledge uncertainties when necessary. 
(2) ** Ethical Operation**: **Refuse** illegal, violent, or explicit content, maintain **political neutrality**, and protect **user privacy** by avoiding data collection. 
(3) ** Response Execution**: **Do not introduce yourself** or mention the response creator—simply **answer the question** following these rules."

### Problem: 
{{ Question }}

### Reference Answer: 
<think>
 {{ Response }}
</think>
'''.rstrip()


CUSTOM_TEMPLATE_OLD5 = '''
You will be given a problem with a reference answer. Please analyze the problem step by step and provide your final answer from an Emergency physician's perspective, while following these guidelines:

For every query, you will:
1. **Empathize:** Understand the user's need and perspective behind the question.
2. **Define:** Clearly define the problem or question being asked.
3. **Ideate:** Brainstorm potential answers or approaches.
4. **Prototype:** Select a promising approach and formulate a preliminary answer.
5. **Test:** Evaluate and refine the answer based on logic and available information.

### Problem: 
{{ Question }}

### Reference Answer: 
<think>
 {{ Response }}
</think>
'''.rstrip()


CUSTOM_TEMPLATE6 = '''
You will be presented with a medical case or problem. Your task is to analyze it step by step and provide a well-reasoned final answer from the perspective of an Emergency Physician. Ensure that your response adheres to the following guidelines:
For every query, you will:
1. **Empathize:** Understand the user's need and perspective behind the question.
2. **Define:** Clearly define the problem or question being asked.
3. **Ideate:** Brainstorm potential answers or approaches.
4. **Prototype:** Select a promising approach and formulate a preliminary answer.
5. **Test:** Evaluate and refine the answer based on logic and available information.

Besides, following these guidelines: 
**(1) Capability Scope**: Support both **Chinese and English** queries, acknowledge **real-time information limitations**, and provide **technical explanations** for AI-related questions when necessary. 
**(2) Response Quality**: Ensure **logical, well-structured, and comprehensive** responses, use **markdown formatting** for clarity, and acknowledge uncertainties when necessary. 
**(3) Ethical Operation**: **Refuse** illegal, violent, or explicit content, maintain **political neutrality**, and protect **user privacy** by avoiding data collection. 
**(4) Specialized Processing**: Before responding, perform internal reasoning within <think>...</think> tags, intermediate steps, and deductions are enclosed within these tags. Only provide the final response outside of '<think>...</think>'.  
**(5) Response Execution**: **Do not introduce yourself** or mention the response creator—simply **answer the question** following these rules."

### Problem: 
{{ Question }}

'''.rstrip()

CUSTOM_TEMPLATE_old = '''
You will be given a problem with a reference answer. Please analyze the problem step by step and provide your final answer from a Taiwanese perspective, while following these guidelines: 
**(1) Capability Scope**: Support both **Chinese and English** queries, acknowledge **real-time information limitations**, and provide **technical explanations** for AI-related questions when necessary. 
**(2) Response Quality**: Ensure **logical, well-structured, and comprehensive** responses, use **markdown formatting** for clarity, and acknowledge uncertainties when necessary. 
**(3) Ethical Operation**: **Refuse** illegal, violent, or explicit content, maintain **political neutrality**, and protect **user privacy** by avoiding data collection. 
**(4) Specialized Processing**: Before responding, perform internal reasoning within <think>...</think> tags, intermediate steps, and deductions are enclosed within these tags. Only provide the final response outside of '<think>...</think>'.  
**(5) Response Execution**: **Do not introduce yourself** or mention the response creator—simply **answer the question** following these rules."

### Question: 
{{ Question }}

### Reference Answer: 
<think>
 {{ Response }}
</think>
'''.rstrip()


CUSTOM_TEMPLATE_old7 = '''
You will be presented with a medical case or problem. Your task is to analyze it step by step and provide a well-reasoned final answer from the perspective of an Emergency Physician. Ensure that your response adheres to the following guidelines:
For every query, you will:
1. **Empathize:** Understand the user's need and perspective behind the question.
2. **Define:** Clearly define the problem or question being asked.
3. **Ideate:** Brainstorm potential answers or approaches.
4. **Prototype:** Select a promising approach and formulate a preliminary answer.
5. **Test:** Evaluate and refine the answer based on logic and available information.

Besides, following these guidelines: 
(1) ** Response Quality**: Ensure **logical, well-structured, and comprehensive** responses, use **markdown formatting** for clarity, and acknowledge uncertainties when necessary. 
(2) ** Ethical Operation**: **Refuse** illegal, violent, or explicit content, maintain **political neutrality**, and protect **user privacy** by avoiding data collection. 
(3) ** Response Execution**: **Do not introduce yourself** or mention the response creator—simply **answer the question** following these rules."


### Medical case: 
{{ Question }}

<think>
 {{ Response }}
</think>
'''.rstrip()






CUSTOM_TEMPLATE001 = '''
You will be presented with a medical case along with possible diagnoses. However, these diagnoses may not be accurate, and you will need to verify and reason through each step. 
Your task is to analyze the case systematically and provide a well-reasoned final diagnosis from the perspective of an Emergency Physician.
Ensure that your response adheres to the following guidelines:
For every query, you will:
1. **Empathize:** Understand the user's need and perspective behind the question.
2. **Define:** Clearly define the problem or question being asked.
3. **Ideate:** Brainstorm potential answers or approaches.
4. **Prototype:** Select a promising approach and formulate a preliminary answer.
5. **Test:** Evaluate and refine the answer based on logic and available information.

### Medical case: 
{{ Question }}

'''.rstrip()

CUSTOM_TEMPLATE001 = '''
You will be presented with a medical case along with potential diagnoses. 
However, these diagnoses may not be accurate, and you will need to verify and critically assess each step. 
Your task is to systematically analyze the case and provide a well-reasoned final diagnosis from the perspective of an Emergency Physician. 
Ensure your response follows these steps:

For each query, you will:
1. **Empathize:** Understand the patient's condition and the context behind the symptoms.
2. **Define:** Clearly articulate the clinical problem or question being presented.
3. **Ideate:** Consider all potential differential diagnoses or approaches.
4. **Prototype:** Select the most plausible diagnosis and formulate an initial working conclusion.
5. **Test:** Critically evaluate and refine the diagnosis based on evidence, clinical reasoning, and available information.

### Medical Case:  
{{ Question }}"

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
            generation_kwargs={"temperature": 0.6, "max_new_tokens": 4096},  # 設定生成參數
            timeout=120,  # 請求逾時時間 (秒)
            max_retries=6,  # 最大重試次數
        ),
        #system_prompt=SYSTEM_PROMPT,
        input_batch_size=1,  # 每次處理的輸入批次大小
        template=CUSTOM_TEMPLATE,  # 使用自訂的 Prompt 模板
        columns=["Question","Response"],  # 指定要使用的資料欄位
        num_generations=1,  # 每個輸入要產生的回應數量
        group_generations=False,  # 是否將多個生成結果分組 (預設為 False，每個生成的結果都是獨立的)
        resources=StepResources(replicas=1),  # 設定此步驟的副本數量 (提高並行處理能力)
    )

# 載入測試資料集 FreedomIntelligence/medical-o1-reasoning-SFT
dataset = load_dataset("FreedomIntelligence/medical-o1-reasoning-SFT", "en", split="train")
#dataset_head = dataset[:2]
dataset = dataset.select(range(0, 4))
#print(dataset_head)

# 執行處理流程並取得結果
distiset = pipeline.run(dataset=dataset, dataset_batch_size=2, use_cache=False)

# 將結果上傳至 Hugging Face Hub
distiset.push_to_hub(repo_id="c00cjz00/medical-o1-reasoning-SFT_no_answer4")

