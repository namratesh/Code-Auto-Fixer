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
    
# def get_modified_files():
#     """
#     Retrieves the list of modified Python files from the latest commit.
#     """
#     result = subprocess.run(["git", "diff", "--name-only", "HEAD~1"], capture_output=True, text=True)
#     files = result.stdout.strip().split("\n")
#     return [file for file in files if file.endswith(".py")]

def get_modified_files():
    """
    Retrieves the list of modified Python files in a PR.
    Dynamically detects the base branch for the PR.
    """
    base_branch = os.getenv("GITHUB_BASE_REF")  # Base branch of the PR (e.g., main, dev)
    if not base_branch:
        print("Error: GITHUB_BASE_REF is not set. Are you running in a PR context?")
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

    Args:
        code (str): The code snippet to be reviewed.
        language (str): The type of code ('python', 'docker', 'github_workflow').

    Returns:
        dict: JSON feedback from the LLM.
    """
    language = "python"
    system_prompt = f"""
    Analyze the following {language} code and provide structured feedback in JSON format in sort.

    Ensure the response follows this schema:
    - "overall_feedback": High-level summary of the review.
    - "detailed_feedback": A categorized breakdown of issues:
        - "code_quality": Issues related to readability, maintainability, and structure.
        - "performance": Inefficiencies, redundant computations, or better algorithms.
        - "security": Vulnerabilities such as unsafe imports, injection risks, or weak authentication.
        - "error_handling": Issues related to exception handling and robustness.
        - "best_practices": Violations of standard coding conventions.
        - "doc string and input output type defined": Doc string in every function with input and output function define
    - "suggestions": Actionable improvements for each issue category.

    Strictly return only valid JSON output.

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
        print(response)
        # print(response.choices[0].message.content)÷
        return response # Ensure valid JSON output
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Case: Running with specific file(s) as arguments
        modified_files = sys.argv[1:]
    else:
        # Case: Running in GitHub Actions (auto-detect modified files)
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

    print("LLM review completed.")
    for file, feedback in feedback_results.items():
        print(f"\n### Feedback for {file} ###\n{feedback}")
