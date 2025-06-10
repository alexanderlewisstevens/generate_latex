import os
import json
from pathlib import Path
import sys

def load_index(index_path):
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def combine_pages(section, page_numbers, pages_dir):
    contents = []
    for page in page_numbers:
        page_file = pages_dir / f"page_{str(page).zfill(4)}.md"
        if page_file.exists():
            with open(page_file, 'r', encoding='utf-8') as f:
                contents.append(f.read())
        else:
            contents.append(f"<!-- Missing: {page_file.name} -->")
    return '\n\n'.join(contents)

def write_section_md(section, page_numbers, out_dir, index_entry):
    out_path = out_dir / f"{section.replace('/', '_').replace(' ', '_')}.md"
    yaml_header = '---\n' + f'section: "{section}"\npages: {page_numbers}\n' + '---\n\n'
    content = combine_pages(section, page_numbers, Path('book_pages_md'))
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(yaml_header)
        f.write(content)

def main():
    index_path = Path('book_pages/index.json')
    pages_md_dir = Path('book_pages_md')
    out_dir = Path('book_sections_md')
    out_dir.mkdir(exist_ok=True)
    index = load_index(index_path)
    for section, pages in index.items():
        if section == '__all_pages__':
            continue
        if not pages:
            continue
        write_section_md(section, pages, out_dir, index[section])
    print(f"Section markdown files written to {out_dir}/")

if __name__ == "__main__":
    main()
