import json
import sys
from pathlib import Path

def insert_nested(d, keys, pages):
    key = keys[0]
    if key not in d:
        d[key] = {"pages": [], "children": {}}
    if len(keys) == 1:
        d[key]["pages"].extend(pages)
        return
    insert_nested(d[key]["children"], keys[1:], pages)

def flat_to_nested(flat_index):
    nested = {}
    for k, v in flat_index.items():
        if k == "__all_pages__":
            continue
        keys = k.split(" > ")
        insert_nested(nested, keys, v)
    return nested

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 flat_to_nested.py <index.json> [output.json]")
        sys.exit(1)
    in_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else in_path.parent / "index_nested.json"
    with open(in_path) as f:
        flat = json.load(f)
    nested = flat_to_nested(flat)
    with open(out_path, "w") as f:
        json.dump(nested, f, indent=2)
    print(f"Nested index written to {out_path}")

if __name__ == "__main__":
    main()
