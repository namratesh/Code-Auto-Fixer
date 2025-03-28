from openai import OpenAI
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json
import subprocess
import sys

load_dotenv()

class ReviewCode:
    review_comment: str

def get_llm_client():
    """
    Initializes and returns an OpenAI client for structured output.
    """
    return ChatOpenAI(
        model="deepseek/deepseek-chat-v3-0324",  # Or "gpt-3.5-turbo-0125"
        temperature=0,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1"
    ).with_structured_output(ReviewCode)

def get_modified_files():
    """
    Retrieves the list of modified Python files in a PR.
    """
    base_branch = os.getenv("GITHUB_BASE_REF")  # Base branch of the PR
    if not base_branch:
        print("Error: GITHUB_BASE_REF is not set. Are you running in a PR context?")
        sys.exit(1)

    result = subprocess.run(["git", "fetch", "origin", base_branch], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Git fetch failed: {result.stderr}")
        sys.exit(1)

    result = subprocess.run(["git", "diff", "--name-only", f"origin/{base_branch}...HEAD"], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Git command failed: {result.stderr}")
        sys.exit(1)

    files = result.stdout.strip().split("\n")
    return [file for file in files if file.endswith(".py")]

def read_file_content(file_path):
    """
    Reads the content of a given file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def review_code_with_llm(code: str):
    """
    Calls an LLM to review the given code and returns feedback.
    """
    language = "python"
    system_prompt = f"""
    Analyze the following {language} code and provide structured feedback in JSON format.

    Schema:
    - "overall_feedback": Summary of the review.
    - "detailed_feedback": Categorized breakdown of issues:
        - "code_quality": Readability and maintainability.
        - "performance": Inefficiencies or redundant computations.
        - "security": Vulnerabilities like unsafe imports or injections.
        - "error_handling": Exception handling and robustness.
        - "best_practices": Standard coding conventions.
        - "doc_strings": Presence of docstrings and input/output types.

    Only return valid JSON.

    Code:
    ```{language}
    {code}```
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt)
    ])
    
    client = get_llm_client()
    chain = prompt | client
    
    try:
        response = chain.invoke({"code": code})
        return response
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    modified_files = get_modified_files()

    if not modified_files:
        print("No modified Python files found.")
        sys.exit(0)

    feedback_results = {}
    for file in modified_files:
        if not os.path.exists(file):
            print(f"Error: File '{file}' not found.")
            continue

        code_content = read_file_content(file)
        feedback_results[file] = review_code_with_llm(code_content)

    with open("llm_output.json", "w") as f:
        json.dump(feedback_results, f, indent=4)

    print("LLM review completed. Output saved to llm_output.json.")
