# save as folder_tree.py
from pathlib import Path
import sys

def print_tree(dir_path: Path, prefix: str = ""):
    dirs = sorted([p for p in dir_path.iterdir() if p.is_dir()], key=lambda x: x.name.lower())
    for i, d in enumerate(dirs):
        last = (i == len(dirs) - 1)
        connector = "└── " if last else "├── "
        print(prefix + connector + d.name)
        print_tree(d, prefix + ("    " if last else "│   "))

if __name__ == "__main__":
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    print(root.resolve().name)
    print_tree(root.resolve())
