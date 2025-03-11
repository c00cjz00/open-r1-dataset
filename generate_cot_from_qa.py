# Create COT from Q+A

# - INSTALL package
# sudo apt install git-lfs
# curl -LsSf https://astral.sh/uv/install.sh | sh
# sudo cp /home/ubuntu/.local/bin/* /usr/local/bin/
# sudo apt install git-lfs
# uv venv openr1 --python 3.11 && source openr1/bin/activate && uv pip install --upgrade pip
# uv pip install distilabel python-dotenv openai opencc beautifulsoup4 Pillow
# - KEY
# echo "OPENAI_API_KEY=sk-xxxx" >.env
# - HF (writting key)
# huggingface-cli login

# - Example
# python generate_cot_from_qa.py \
	# --hf-dataset lianghsun/tw-instruct-500k \
	# --hf-dataset-config default \
	# --hf-dataset-split train \
	# --hf-output-dataset c00cjz00/tw-instruct-500k-demo_qa \
	# --vllm-server-url https://integrate.api.nvidia.com/v1 \
	# --model deepseek-ai/deepseek-r1 \
	# --temperature 0.6 \
	# --max-new-tokens 2048 \
	# --num-generations 1 \
	# --input-batch-size 1 \
	# --page 1 \
	# --page-size 8 \
	# --client-replicas 1 \
	# --timeout 600 \
	# --retries 1 \
	# --prompt-column prompt \
	# --question-column-name input \
	# --answer-column-name output \
	# --answer-max-len 1024 \
	# --prompt-template "You will be given a problem with a reference answer. Please analyze the problem step by step and provide your final answer in **Traditional Chinese (zh-TW) from a Taiwanese perspective** while following these guidelines: **(1) Identity & Compliance**: State that you are an **AI assistant** in your initial response and comply with the **Republic of China (ROC) laws and regulations**, including its data privacy requirements. **(2) Capability Scope**: Support both **Chinese and English** queries, acknowledge **real-time information limitations**, and provide **technical explanations** for AI-related questions when necessary. **(3) Response Quality**: Ensure **logical, well-structured, and comprehensive** responses, use **markdown formatting** for clarity, and acknowledge uncertainties when necessary. **(4) Ethical Operation**: **Refuse** illegal, violent, or explicit content, maintain **political neutrality**, and protect **user privacy** by avoiding data collection. **(5) Specialized Processing**: Before responding, perform internal reasoning within <think>...</think> tags. Ensure that all thought processes, intermediate steps, and deductions are enclosed within these tags. Only provide the final response outside of '<think>...</think>'.  **(6) Response Execution**: **Do not introduce yourself** or mention the response creator—simply **answer the question** following these rules.\n\n {{ instruction }}"

from typing import Optional
from distilabel.models import OpenAILLM
from distilabel.pipeline import Pipeline
from distilabel.steps import StepResources
from distilabel.steps.tasks import TextGeneration
from dotenv import load_dotenv
import os

# api key
load_dotenv() # Load the environment variables
OPENAI_API_KEY=os.getenv('OPENAI_API_KEY')

# Page num
def get_page_data(dataset, page, page_size=64):
    start = (page - 1) * page_size
    end = min(start + page_size, len(dataset))  # 如果 end 超過了 dataset 的長度，設定為最後一筆
    return dataset.select(range(start, end))

# QA combination
def replace_input_with_combined_data(dataset, question_column_name, answer_column_name, answer_max_len):
    answer_max_len = int(answer_max_len)
    dataset = dataset.map(lambda x: {
        **x,
        "prompt": f"""
### Question:  
{x[question_column_name]}

<think>
{str(x.get(answer_column_name, ""))[:answer_max_len]}  
</think>
"""
    })
    return dataset

def build_distilabel_pipeline(
    model: str,
    base_url: str = "http://localhost:8000/v1",
    prompt_column: Optional[str] = None,
    prompt_template: str = "{{ instruction }}",
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    max_new_tokens: int = 8192,
    num_generations: int = 1,
    input_batch_size: int = 64,
    client_replicas: int = 1,
    timeout: int = 900,
    retries: int = 0,
) -> Pipeline:
    generation_kwargs = {"max_new_tokens": max_new_tokens}

    if temperature is not None:
        generation_kwargs["temperature"] = temperature

    if top_p is not None:
        generation_kwargs["top_p"] = top_p

    #with Pipeline().ray() as pipeline:
    #pipeline_id=args.hf_dataset_config + "_" +  str(args.page)
    pipeline_id = args.hf_output_dataset.split("/")[-1] + "_" +  str(args.page)
    with Pipeline(name=pipeline_id) as pipeline:
        TextGeneration(
            llm=OpenAILLM(
                base_url=base_url,
                api_key=OPENAI_API_KEY,
                model=model,
                timeout=timeout,
                max_retries=retries,
                generation_kwargs=generation_kwargs,
            ),
            template=prompt_template,
            input_mappings={"instruction": prompt_column} if prompt_column is not None else {},
            input_batch_size=input_batch_size,
            num_generations=num_generations,
            group_generations=True,
            resources=StepResources(replicas=client_replicas),
        )

    return pipeline


if __name__ == "__main__":
    import argparse

    from datasets import load_dataset

    parser = argparse.ArgumentParser(description="Run distilabel pipeline for generating responses with DeepSeek R1")
    parser.add_argument(
        "--hf-dataset",
        type=str,
        required=True,
        help="HuggingFace dataset to load",
    )
    parser.add_argument(
        "--hf-dataset-config",
        type=str,
        required=False,
        help="Dataset config to use",
    )
    parser.add_argument(
        "--hf-dataset-split",
        type=str,
        default="train",
        help="Dataset split to use",
    )
    parser.add_argument(
        "--prompt-column",
        type=str,
        default="prompt",
    )
    parser.add_argument(
        "--prompt-template",
        type=str,
        default="{{ instruction }}",
        help="Template string for formatting prompts.",
    )
    parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="Model name to use for generation",
    )
    parser.add_argument(
        "--vllm-server-url",
        type=str,
        default="http://localhost:8000/v1",
        help="URL of the vLLM server",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        help="Temperature for generation",
    )
    parser.add_argument(
        "--top-p",
        type=float,
        help="Top-p value for generation",
    )
    parser.add_argument(
        "--max-new-tokens",
        type=int,
        default=8192,
        help="Maximum number of new tokens to generate",
    )
    parser.add_argument(
        "--num-generations",
        type=int,
        default=1,
        help="Number of generations per problem",
    )
    parser.add_argument(
        "--input-batch-size",
        type=int,
        default=64,
        help="Batch size for input processing",
    )
    parser.add_argument(
        "--client-replicas",
        type=int,
        default=1,
        help="Number of client replicas for parallel processing",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="Request timeout in seconds (default: 600)",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=0,
        help="Number of retries for failed requests (default: 0)",
    )
    parser.add_argument(
        "--hf-output-dataset",
        type=str,
        required=False,
        help="HuggingFace repo to push results to",
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Whether to make the output dataset private when pushing to HF Hub",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=64,
        help="Page size (default: 64)",
    )
    parser.add_argument(
        "--page",
        type=int,
        default=0,
        help="page (default: 0)",
    )    
    parser.add_argument(
        "--question-column-name",
        type=str,
        default="input",
        help="HF dataset question column",
    )
    parser.add_argument(
        "--answer-column-name",
        type=str,
        default="output",
        help="HF dataset answer column",
    )
    parser.add_argument(
        "--answer-max-len",
        type=str,
        default="output",
        help="HF dataset answer max length",
    )         
    args = parser.parse_args()

    print("\nRunning with arguments:")
    for arg, value in vars(args).items():
        print(f"  {arg}: {value}")
    print()

    print(f"Loading '{args.hf_dataset}' (config: {args.hf_dataset_config}, split: {args.hf_dataset_split}) dataset...")
    dataset = load_dataset(args.hf_dataset, args.hf_dataset_config, split=args.hf_dataset_split)
    dataset = get_page_data(dataset, page=args.page, page_size=args.page_size)
    datasets_combination = replace_input_with_combined_data(dataset, args.question_column_name, args.answer_column_name, args.answer_max_len) 
    print("Dataset loaded!")

    pipeline = build_distilabel_pipeline(
        model=args.model,
        base_url=args.vllm_server_url,
        prompt_template=args.prompt_template,
        prompt_column=args.prompt_column,
        temperature=args.temperature,
        top_p=args.top_p,
        max_new_tokens=args.max_new_tokens,
        num_generations=args.num_generations,
        input_batch_size=args.input_batch_size,
        client_replicas=args.client_replicas,
        timeout=args.timeout,
        retries=args.retries,
    )

    print("Running generation pipeline...")
    distiset = pipeline.run(
        dataset=datasets_combination,
        #dataset_batch_size=args.input_batch_size * 1000,
        dataset_batch_size=args.page_size,
        use_cache=True,
    )
    print("Generation pipeline finished!")
        
    #if args.hf_output_dataset:
    #    print(f"Pushing resulting dataset to '{args.hf_output_dataset}'...")
    #    distiset.push_to_hub(args.hf_output_dataset, private=args.private)
    #    print("Dataset pushed!")
