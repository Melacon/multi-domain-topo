#!/usr/bin/env bash
# generate-yang-tree.sh — Generate a YANG tree for a network-function folder.
# Usage: ./generate-yang-tree.sh [<NF-folder>]
# Default NF folder: yang-per-network-function/ROADM
#
# The script loads ALL .yang files in the folder (which must already contain
# every transitive dependency as a symlink, just like validate-yang.sh expects).
# pyang -f tree is called with all files on the command line so that augment
# statements are folded into the augmented module's tree automatically.
#
# Modules that produce tree output (i.e. they define at least one top-level
# container or list) are reported as "root modules" — these are the canonical
# entry points for the YANG data tree of this NF.
#
# Output: yang-tree.txt written into the NF folder.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NF_DIR="${1:-$SCRIPT_DIR/yang-per-network-function/ROADM}"
NF_DIR="$(realpath "$NF_DIR")"

PYANG="${PYANG:-$(command -v pyang 2>/dev/null || echo "$HOME/.local/bin/pyang")}"

# ---------------------------------------------------------------------------
# Collect all .yang files in the NF folder (follow symlinks)
# ---------------------------------------------------------------------------
mapfile -t YANG_FILES < <(find "$NF_DIR" -maxdepth 1 -name "*.yang" | sort)

if [ ${#YANG_FILES[@]} -eq 0 ]; then
  echo "ERROR: no .yang files found in $NF_DIR" >&2
  exit 1
fi

PYANG_VER="$("$PYANG" --version 2>/dev/null)"
TREE_FILE="$NF_DIR/yang-tree.txt"
TS="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"

# ---------------------------------------------------------------------------
# Identify modules that define top-level data nodes (container/list at
# 2-space indent = direct child of the module statement, not inside an
# augment or grouping block).  These are the YANG tree root entry points.
# ---------------------------------------------------------------------------
declare -a ROOT_MODULES=()
for f in "${YANG_FILES[@]}"; do
  if grep -qP "^  (container|list) " "$f" 2>/dev/null; then
    ROOT_MODULES+=("$(basename "$f" .yang | sed 's/@[0-9-]*$//')")
  fi
done

ROOT_COUNT=${#ROOT_MODULES[@]}

# ---------------------------------------------------------------------------
# Print header (to both stdout and the tree file)
# ---------------------------------------------------------------------------
exec > >(sed "s|$NF_DIR/||g" | tee "$TREE_FILE") 2>&1

echo "=========================================================="
echo " NF folder      : $NF_DIR"
echo " tree file      : yang-tree.txt"
echo " timestamp      : $TS"
echo " YANG files     : ${#YANG_FILES[@]} total"
echo " root modules   : $ROOT_COUNT (define top-level container/list)"
echo " pyang          : $PYANG_VER"
echo "=========================================================="
echo ""
echo " Root modules (YANG tree entry points):"
for m in "${ROOT_MODULES[@]}"; do
  echo "   $m"
done
echo ""

# ---------------------------------------------------------------------------
# Generate YANG tree
# pyang receives ALL modules so that augment statements are automatically
# folded into the augmented module's tree.  Modules that define only
# groupings/typedefs produce no tree section in the output.
# ---------------------------------------------------------------------------
echo "--- YANG tree (pyang -f tree, line-length 120) ---"
echo ""

TREE_OUT="$("$PYANG" \
  -f tree \
  --tree-line-length 120 \
  -p "$NF_DIR" \
  "${YANG_FILES[@]}" 2>/dev/null || true)"

if [ -z "$TREE_OUT" ]; then
  echo "(pyang produced no tree output)"
else
  echo "$TREE_OUT"
fi

echo ""
echo "=========================================================="
echo " Tree written to: yang-tree.txt"
echo "=========================================================="
