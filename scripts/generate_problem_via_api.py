import os
import sys
from dotenv import load_dotenv
import requests

load_dotenv()
API_KEY = os.getenv("MY_API_KEY")
if not API_KEY:
    raise RuntimeError("MY_API_KEY not set. Please set it in your .env file or environment.")

# Example: Use OpenAI API to generate a LaTeX problem (replace with your API endpoint as needed)
def extract_question_and_solution(latex_content):
    # Try to split the content into question and solution parts
    # Look for 'Solution:' or similar as a separator
    if '\\begin{solution}' in latex_content:
        parts = latex_content.split('\\begin{solution}', 1)
        question = parts[0].strip()
        solution = parts[1].replace('\\end{solution}', '').strip()
    elif 'Solution:' in latex_content:
        parts = latex_content.split('Solution:', 1)
        question = parts[0].strip()
        solution = parts[1].strip()
    else:
        question = latex_content.strip()
        solution = '<solution here>'
    return question, solution

def generate_problem(prompt, bank_dir, problem_number):
    headers = {"Authorization": f"Bearer {API_KEY}"}
    data = {
        "model": "gpt-3.5-turbo-instruct",
        "prompt": prompt,
        "max_tokens": 500
    }
    response = requests.post("https://api.openai.com/v1/completions", headers=headers, json=data)
    if response.status_code != 200:
        print(f"API error: {response.status_code} {response.text}")
        return False
    result = response.json()
    latex_content = result.get("choices", [{}])[0].get("text", "").strip()
    if not latex_content:
        print("No content generated.")
        return False
    # Extract question and solution
    question, solution = extract_question_and_solution(latex_content)
    # Remove any point allocation like [10] from the start of the question
    import re
    if question.startswith('\\question'):
        # Remove [number] after \question (e.g., \question[10])
        question = re.sub(r'^\\question\s*\[[^\]]*\]', r'\\question', question)
    formatted = f"% Example problem {problem_number}\n"
    if not question.startswith('\\question'):
        formatted += "\\question "
    formatted += question.strip() + "\n"
    formatted += "\\begin{solution}\n" + solution.strip() + "\n\\end{solution}\n"
    formatted = formatted.strip() + "\n"
    os.makedirs(bank_dir, exist_ok=True)
    fname = os.path.join(bank_dir, f"problem{problem_number}.tex")
    with open(fname, "w") as f:
        f.write(formatted)
    print(f"Generated {fname}")
    return True

def get_next_problem_number(bank_dir):
    files = [f for f in os.listdir(bank_dir) if f.startswith('problem') and f.endswith('.tex')]
    nums = [int(f[len('problem'):-len('.tex')]) for f in files if f[len('problem'):-len('.tex')].isdigit()]
    return max(nums, default=0) + 1

def generate_prompts_for_folder(folder_path):
    import glob
    import re
    BANKS = ["Bank1", "Bank2"]
    files = sorted([f for f in glob.glob(os.path.join(folder_path, '*')) if os.path.isfile(f)])
    for file_path in files:
        print(f"\n=== {os.path.basename(file_path)} ===")
        with open(file_path, 'r', encoding='utf-8') as f:
            section_content = f.read()
        try:
            n = int(input(f"How many problems to create for '{os.path.basename(file_path)}'? "))
        except Exception:
            print("Invalid input, skipping file.")
            continue
        if n < 1:
            print("Skipping (n < 1)")
            continue
        print("Available banks:")
        for idx, bank in enumerate(BANKS, 1):
            print(f"  {idx}. {bank}")
        while True:
            try:
                bank_choice = int(input(f"Select a bank for these prompts (1-{len(BANKS)}): "))
                if 1 <= bank_choice <= len(BANKS):
                    break
            except Exception:
                pass
            print("Invalid choice. Try again.")
        bank = BANKS[bank_choice - 1]
        bank_dir = os.path.join("src/banks", bank)
        prompt = (
            f"Given the following section of text, generate a numbered list of {n} distinct, high-quality LaTeX exam problem prompts (not full problems, just prompts) inspired by the content. "
            f"Do NOT include solutions or LaTeX markup, just the prompts.\n\nSection:\n{section_content}\n\nList of {n} distinct problem prompts:"
        )
        headers = {"Authorization": f"Bearer {API_KEY}"}
        data = {
            "model": "gpt-3.5-turbo-instruct",
            "prompt": prompt,
            "max_tokens": 500,
            "temperature": 0.7
        }
        response = requests.post("https://api.openai.com/v1/completions", headers=headers, json=data)
        if response.status_code != 200:
            print(f"API error: {response.status_code} {response.text}")
            continue
        result = response.json()
        text = result.get("choices", [{}])[0].get("text", "").strip()
        print(f"\nSuggested prompts for {os.path.basename(file_path)}:")
        print(text)
        # Parse the numbered list of prompts
        prompts = []
        for line in text.splitlines():
            m = re.match(r"\s*\d+\.\s*(.*)", line)
            if m:
                prompts.append(m.group(1).strip())
        if not prompts:
            print("No prompts parsed from API output.")
            continue
        # For each prompt, ask user if it should be used
        for prompt_text in prompts:
            print(f"\nPrompt: {prompt_text}")
            use = input("Use this prompt to generate a problem? (y/n): ").strip().lower()
            if use == 'y':
                problem_number = get_next_problem_number(bank_dir)
                print(f"Generating problem {problem_number} in {bank}...")
                generate_problem(prompt_text, bank_dir, problem_number)
            else:
                print("Skipped.")

def main():
    if len(sys.argv) >= 3 and sys.argv[1] == '--batch-prompts':
        folder = sys.argv[2]
        generate_prompts_for_folder(folder)
        return
    if len(sys.argv) < 4:
        print("Usage: python3 scripts/generate_problem_with_api.py <Bank1|Bank2> <problem_number> <prompt>")
        sys.exit(1)
    bank = sys.argv[1]
    problem_number = sys.argv[2]
    prompt = sys.argv[3]
    bank_dir = os.path.join("src/banks", bank)
    generate_problem(prompt, bank_dir, problem_number)

if __name__ == "__main__":
    main()
