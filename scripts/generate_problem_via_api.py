import os
import sys
from dotenv import load_dotenv
import requests

load_dotenv()
API_KEY = os.getenv("MY_API_KEY")
if not API_KEY:
    raise RuntimeError("MY_API_KEY not set. Please set it in your .env file or environment.")

# Example: Use OpenAI API to generate a LaTeX problem (replace with your API endpoint as needed)
def generate_problem(prompt, bank_dir, problem_number):
    # Example API call (replace with your actual API usage)
    headers = {"Authorization": f"Bearer {API_KEY}"}
    data = {
        "model": "gpt-3.5-turbo-instruct",  # REQUIRED for OpenAI API
        "prompt": prompt,
        "max_tokens": 150
    }
    response = requests.post("https://api.openai.com/v1/completions", headers=headers, json=data)
    if response.status_code != 200:
        print(f"API error: {response.status_code} {response.text}")
        return False
    result = response.json()
    # Extract the generated LaTeX (customize as needed)
    latex_content = result.get("choices", [{}])[0].get("text", "")
    if not latex_content.strip():
        print("No content generated.")
        return False
    # Write to the appropriate problem file
    os.makedirs(bank_dir, exist_ok=True)
    fname = os.path.join(bank_dir, f"problem{problem_number}.tex")
    with open(fname, "w") as f:
        f.write(latex_content.strip())
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
