import os
import sys
import requests
import time
import json
from dotenv import load_dotenv
import PyPDF2

load_dotenv()
API_KEY = os.getenv("MY_API_KEY")
if not API_KEY:
    raise RuntimeError("MY_API_KEY not set. Please set it in your .env file or environment.")

def pdf_page_to_text(pdf_path):
    try:
        reader = PyPDF2.PdfReader(pdf_path)
        if len(reader.pages) != 1:
            raise ValueError(f"{pdf_path} does not have exactly one page!")
        text = reader.pages[0].extract_text() or ""
        if not text.strip():
            print(f"[WARN] No text extracted from {pdf_path}")
        return text
    except Exception as e:
        print(f"[ERROR] Failed to extract text from {pdf_path}: {e}")
        return ""

def openai_pdf_to_obsidian(text, page_num):
    prompt = (
        "Convert the following PDF page text into clean, well-structured Obsidian Markdown.\n"
        "\n"
        "Use:\n"
        "- `##` and `###` for headings and logical sectioning\n"
        "- bullet points or numbered lists where appropriate\n"
        "- `> blockquotes` for author commentary or insights\n"
        "- `**bold**` for emphasis\n"
        "- backticks or triple backticks for code or technical terms\n"
        "- horizontal rules (`---`) to separate major segments if useful\n"
        "\n"
        "Preserve all LaTeX-style math as inline (`$...$`) or block (`$$...$$`) where applicable.\n"
        "Do not convert math to plain text. Reconstruct equations using standard LaTeX notation.\n"
        "\n"
        "If content seems list-oriented or enumerative, structure it that way.\n"
        "Do not hallucinate content or include explanations, extra commentary, or LaTeX artifacts.\n"
        "Output only valid Obsidian-compatible Markdown, with no YAML frontmatter.\n"
        "If the page is mostly blank or not useful, return an empty string.\n\n"
        f"Page {page_num} text:\n{text}\n\nMarkdown:"
    )
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that converts PDF page text to clean, valid Obsidian Markdown."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1800
    }
    for attempt in range(3):
        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
            if response.status_code == 200:
                result = response.json()
                usage = result.get("usage", {})
                print(f"  [INFO] Tokens used: prompt={usage.get('prompt_tokens')}, completion={usage.get('completion_tokens')}")
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                # Strip ```markdown and ``` wrappers if present
                if content.startswith('```markdown'):
                    content = content[len('```markdown'):].lstrip('\n')
                if content.startswith('```'):
                    content = content[len('```'):].lstrip('\n')
                if content.endswith('```'):
                    content = content[:-3].rstrip('\n')
                return content.strip()
            elif response.status_code >= 500:
                print(f"[WARN] API 5xx error on page {page_num}, attempt {attempt+1}: {response.text}")
                time.sleep(2 ** attempt)
            else:
                print(f"[ERROR] API error {response.status_code} on page {page_num}: {response.text}")
                break
        except Exception as e:
            print(f"[ERROR] Exception on page {page_num}, attempt {attempt+1}: {e}")
            time.sleep(2 ** attempt)
    return ""

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 convert_pdfs.py <folder_of_single_page_pdfs> [output_folder]")
        sys.exit(1)
    pdf_folder = sys.argv[1]
    output_folder = sys.argv[2] if len(sys.argv) > 2 else pdf_folder.rstrip("/") + "_md"
    os.makedirs(output_folder, exist_ok=True)
    pdf_files = sorted(f for f in os.listdir(pdf_folder) if f.endswith('.pdf'))
    for idx, pdf_file in enumerate(pdf_files):
        page_num = idx + 1
        pdf_path = os.path.join(pdf_folder, pdf_file)
        md_file = os.path.join(output_folder, os.path.splitext(pdf_file)[0] + ".md")
        if os.path.exists(md_file):
            print(f"  [SKIP] {md_file} already exists, skipping.")
            continue
        print(f"Processing {pdf_file} ...")
        text = pdf_page_to_text(pdf_path)
        if not text.strip():
            print("  (No text extracted, skipping)")
            continue
        md = openai_pdf_to_obsidian(text, page_num)
        if not md.strip():
            print("  (No markdown returned, skipping)")
            continue
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"  -> {md_file}")
        print("  ✓ Success")
        # Exponential backoff is handled in the API call

if __name__ == "__main__":
    main()
