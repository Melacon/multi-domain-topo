#!/usr/bin/env python3
import os, re, sys

# Robust patterns (no anchors, no braces required)
MODULE_PATTERN = re.compile(r'module\s+([a-zA-Z_][a-zA-Z0-9\-_.]*)')
IMPORT_PATTERN = re.compile(r'import\s+([a-zA-Z_][a-zA-Z0-9\-_.]*)')

def get_module_name(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    m = MODULE_PATTERN.search(content)
    if m:
        return m.group(1)
    raise ValueError(f"No module declaration in {file_path}")

def get_imports(file_path: str) -> list:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    imports = []
    for m in IMPORT_PATTERN.finditer(content):
        name = m.group(1)
        if '@' in name:
            name = name.split('@')[0]
        imports.append(name)
    return imports

def find_module_file(directory: str, module_name: str) -> str:
    candidates = []
    for fname in os.listdir(directory):
        if not fname.endswith('.yang'):
            continue
        base = fname[:-5]
        if '@' in base:
            base = base.split('@')[0]
        if base == module_name:
            candidates.append(fname)
    if not candidates:
        raise FileNotFoundError(f"No .yang file for '{module_name}' in {directory}")
    def rev_key(f):
        base = f[:-5]
        return base.split('@')[1] if '@' in base else '0000-00-00'
    candidates.sort(key=rev_key, reverse=True)
    return os.path.join(directory, candidates[0])

# === MAIN ===
if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <yang-file.yang>")
    sys.exit(1)

input_file = sys.argv[1]
search_dir = os.path.dirname(os.path.abspath(input_file)) or '.'

try:
    root_name = get_module_name(input_file)
except Exception as e:
    print(f"Error parsing root module: {e}", file=sys.stderr)
    sys.exit(1)

# Build module map
yang_map = {}
for fname in os.listdir(search_dir):
    if not fname.endswith('.yang'):
        continue
    fpath = os.path.join(search_dir, fname)
    try:
        mod_name = get_module_name(fpath)
        real_path = find_module_file(search_dir, mod_name)
        yang_map[mod_name] = real_path
    except Exception as e:
        print(f"Skipping {fname}: {e}", file=sys.stderr)

print(f"Loaded {len(yang_map)} modules from {search_dir}\n")

# DFS
tree = {}
visited = set()
rec_stack = set()

def dfs(module):
    if module in rec_stack or module in visited:
        return
    visited.add(module)
    rec_stack.add(module)
    
    try:
        file_path = yang_map[module]
    except KeyError:
        print(f"Missing module: '{module}'", file=sys.stderr)
        tree[module] = []
        return
    
    imports = get_imports(file_path)
    tree[module] = imports
    
    for imp in imports:
        if imp not in visited:
            dfs(imp)
    
    rec_stack.remove(module)

dfs(root_name)

# === PYANG-STYLE TREE OUTPUT ===
def print_pyang_tree(module, prefix="", is_last=True, seen=None):
    if seen is None:
        seen = set()
    
    if module in seen:
        connector = "│   " if prefix else ""
        print(f"{connector}└── {module} (circular)")
        return
    seen.add(module)
    
    # Print current node
    connector = "└── " if is_last else "├── "
    print(f"{prefix}{connector}{module}")
    
    # Prepare prefix for children
    child_prefix = prefix + ("    " if is_last else "│   ")
    
    # Get children (imports), sorted for stability
    children = sorted(set(tree.get(module, [])))
    
    # Print each child
    for i, child in enumerate(children):
        is_last_child = (i == len(children) - 1)
        print_pyang_tree(child, child_prefix, is_last_child, seen.copy())

print(f"Import hierarchy for: {root_name}\n")
print_pyang_tree(root_name)
