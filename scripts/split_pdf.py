import os
import sys
import json
from pathlib import Path
from PyPDF2 import PdfReader, PdfWriter

def pad_page_number(page_num, total_pages):
    width = max(4, len(str(total_pages)))
    return str(page_num).zfill(width)

def split_pdf(input_pdf, output_dir):
    reader = PdfReader(input_pdf)
    total_pages = len(reader.pages)
    os.makedirs(output_dir, exist_ok=True)
    page_files = []
    for i in range(total_pages):
        writer = PdfWriter()
        writer.add_page(reader.pages[i])
        padded = pad_page_number(i+1, total_pages)
        out_path = os.path.join(output_dir, f"page_{padded}.pdf")
        with open(out_path, "wb") as f:
            writer.write(f)
        page_files.append(out_path)
    return page_files

def extract_outline(reader):
    # Recursively extract outline (bookmarks) as a tree with page numbers
    def walk(outline, parent=None):
        items = []
        for item in outline:
            if isinstance(item, list):
                # Nested list: subsection
                if items:
                    items[-1]['children'] = walk(item, items[-1])
            else:
                title = getattr(item, 'title', str(item))
                try:
                    page_num = reader.get_destination_page_number(item) + 1
                except Exception:
                    page_num = None
                items.append({'title': title, 'page': page_num, 'children': []})
        return items
    try:
        outline = reader.outline
    except Exception:
        outline = []
    return walk(outline)

def flatten_outline(outline):
    # Returns a dict: {section_title: [page_numbers]}
    result = {}
    def walk(node, path):
        title = node['title']
        page = node['page']
        key = ' > '.join(path + [title])
        if page is not None:
            result.setdefault(key, []).append(page)
        for child in node.get('children', []):
            walk(child, path + [title])
    for node in outline:
        walk(node, [])
    return result

def generate_index(reader, output_dir):
    outline = extract_outline(reader)
    flat = flatten_outline(outline)
    # For each section, also include the sorted list of unique pages (for reverse lookup)
    index = {k: sorted(set(v)) for k, v in flat.items()}
    # Add a special key for all pages
    total_pages = len(reader.pages)
    all_pages = list(range(1, total_pages + 1))
    index['__all_pages__'] = all_pages
    # NOTE: When processing split pages, ensure downstream GPT prompts include:
    # "Preserve all LaTeX-style math as inline (`$...$`) or block (`$$...$$`) where applicable.
    # Do not convert math to plain text. Reconstruct equations using standard LaTeX notation."
    with open(os.path.join(output_dir, "index.txt"), "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    return index

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 split_pdf.py <input.pdf> [output_dir]")
        sys.exit(1)
    input_pdf = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else Path(input_pdf).stem + "_pages"
    reader = PdfReader(input_pdf)
    split_pdf(input_pdf, output_dir)
    generate_index(reader, output_dir)
    print(f"Split complete. Output in {output_dir}/. Index written to index.txt.")

if __name__ == "__main__":
    main()
