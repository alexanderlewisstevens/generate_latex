import os
import re
import json
from pathlib import Path

def check_markdown_formatting(md_text, filename):
    issues = []
    # Check for unclosed code blocks
    code_blocks = re.findall(r'```', md_text)
    if len(code_blocks) % 2 != 0:
        issues.append({
            'file': filename,
            'type': 'unclosed_code_block',
            'message': 'Odd number of triple backticks (```), possible unclosed code block.'
        })
    # Check for unclosed YAML frontmatter
    if md_text.strip().startswith('---'):
        yaml_count = len(re.findall(r'^---$', md_text, re.MULTILINE))
        if yaml_count % 2 != 0:
            issues.append({
                'file': filename,
                'type': 'unclosed_yaml',
                'message': 'Odd number of YAML frontmatter delimiters (---), possible unclosed YAML.'
            })
    # Check for broken image links
    for match in re.finditer(r'!\[[^\]]*\]\(([^)]+)\)', md_text):
        img_path = match.group(1)
        if not Path(img_path).exists():
            issues.append({
                'file': filename,
                'type': 'missing_image',
                'message': f'Image file not found: {img_path}'
            })
    # Check for tables with inconsistent columns
    for table in re.findall(r'(\|.+\|\n(?:\|.+\|\n)+)', md_text):
        rows = [row for row in table.strip().split('\n') if row.strip()]
        if len(rows) > 1:
            col_counts = [row.count('|') for row in rows]
            if len(set(col_counts)) > 1:
                issues.append({
                    'file': filename,
                    'type': 'table_column_mismatch',
                    'message': 'Table rows have inconsistent number of columns.'
                })
    return issues

def main():
    section_dir = Path('book_sections_md')
    all_issues = []
    for md_file in section_dir.glob('*.md'):
        with open(md_file, 'r', encoding='utf-8') as f:
            text = f.read()
        issues = check_markdown_formatting(text, md_file.name)
        all_issues.extend(issues)
    with open('issues.json', 'w', encoding='utf-8') as f:
        json.dump(all_issues, f, indent=2)
    print(f"Checked {len(list(section_dir.glob('*.md')))} files. Issues written to issues.json.")

if __name__ == '__main__':
    main()
