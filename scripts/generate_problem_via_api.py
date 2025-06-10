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
<<<<<<< HEAD
        "model": "gpt-3.5-turbo-instruct",
        "prompt": prompt,
        "max_tokens": 500
=======
        "model": "gpt-3.5-turbo-instruct",  # REQUIRED for OpenAI API
        "prompt": prompt,
        "max_tokens": 150
>>>>>>> 820f8e7 (Update API call in generate_problem_via_api.py to include model specification; add problem99.tex with quadratic equation problem and solution.)
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
    # Ensure the LaTeX content is wrapped in the standard format
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

def main():
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
