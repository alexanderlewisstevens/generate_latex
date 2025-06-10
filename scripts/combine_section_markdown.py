import os
import json
from pathlib import Path
import sys
import shutil
import re

def load_index(index_path):
    with open(index_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_images_in_markdown(md_content):
    # Find all image links: ![alt](filename)
    return re.findall(r'!\[[^\]]*\]\(([^)]+)\)', md_content)

def combine_pages_and_collect_images(section, page_numbers, pages_dir):
    contents = []
    images = set()
    for page in page_numbers:
        page_file = pages_dir / f"page_{str(page).zfill(4)}.md"
        if page_file.exists():
            with open(page_file, 'r', encoding='utf-8') as f:
                md = f.read()
                contents.append(md)
                images.update(find_images_in_markdown(md))
        else:
            contents.append(f"<!-- Missing: {page_file.name} -->")
    return '\n\n'.join(contents), images

def copy_images(images, src_dir, dest_dir):
    for img in images:
        src = src_dir / img
        dest = dest_dir / img
        if src.exists():
            shutil.copy2(src, dest)

def write_section_md(section, page_numbers, out_dir, index_entry, images):
    out_path = out_dir / f"{section.replace('/', '_').replace(' ', '_')}.md"
    yaml_header = '---\n' + f'section: "{section}"\npages: {page_numbers}\n' + '---\n\n'
    content, found_images = combine_pages_and_collect_images(section, page_numbers, Path('book_pages_md'))
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(yaml_header)
        f.write(content)
    # Copy images for this section
    copy_images(found_images, Path('book_pages_md'), out_path.parent)

def main():
    index_path = Path('book_pages/index.json')
    pages_md_dir = Path('book_pages_md')
    out_dir = Path('book_sections_md')
    out_dir.mkdir(exist_ok=True)
    index = load_index(index_path)
    section_names = [k for k in index.keys() if k != '__all_pages__']
    for i, section in enumerate(section_names):
        pages = index[section]
        if not pages:
            continue
        # Add the first page of the next section if it exists and is not already included
        if i + 1 < len(section_names):
            next_section = section_names[i + 1]
            next_pages = index[next_section]
            if next_pages:
                next_first_page = next_pages[0]
                if next_first_page not in pages:
                    pages = pages + [next_first_page]
        # Combine pages and collect images, then write section and copy images
        content, images = combine_pages_and_collect_images(section, pages, pages_md_dir)
        write_section_md(section, pages, out_dir, index[section], images)
    print(f"Section markdown files and images written to {out_dir}/ (with overlap)")

if __name__ == "__main__":
    main()
