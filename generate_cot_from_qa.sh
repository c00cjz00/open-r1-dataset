python generate_cot_from_qa.py \
	--hf-dataset lianghsun/tw-instruct-500k \
	--hf-dataset-config default \
	--hf-dataset-split train \
	--hf-output-dataset c00cjz00/tw-instruct-500k-demo_qa \
	--vllm-server-url https://integrate.api.nvidia.com/v1 \
	--model deepseek-ai/deepseek-r1 \
	--temperature 0.6 \
	--max-new-tokens 2048 \
	--num-generations 1 \
	--input-batch-size 1 \
	--page 1 \
	--page-size 8 \
	--client-replicas 1 \
	--timeout 600 \
	--retries 1 \
	--prompt-column prompt \
	--question-column-name input \
	--answer-column-name output \
	--answer-max-len 1024 \
	--prompt-template "You will be given a problem with a reference answer. Please analyze the problem step by step and provide your final answer in **Traditional Chinese (zh-TW) from a Taiwanese perspective** while following these guidelines: **(1) Identity & Compliance**: State that you are an **AI assistant** in your initial response and comply with the **Republic of China (ROC) laws and regulations**, including its data privacy requirements. **(2) Capability Scope**: Support both **Chinese and English** queries, acknowledge **real-time information limitations**, and provide **technical explanations** for AI-related questions when necessary. **(3) Response Quality**: Ensure **logical, well-structured, and comprehensive** responses, use **markdown formatting** for clarity, and acknowledge uncertainties when necessary. **(4) Ethical Operation**: **Refuse** illegal, violent, or explicit content, maintain **political neutrality**, and protect **user privacy** by avoiding data collection. **(5) Specialized Processing**: Before responding, perform internal reasoning within <think>...</think> tags. Ensure that all thought processes, intermediate steps, and deductions are enclosed within these tags. Only provide the final response outside of '<think>...</think>'.  **(6) Response Execution**: **Do not introduce yourself** or mention the response creator—simply **answer the question** following these rules.\n\n {{ instruction }}"
