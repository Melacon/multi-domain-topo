#!/usr/bin/env bash
# Copyright 2026 demx8as6
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/env bash
set -euo pipefail

# scan-yang-libraries.sh
#
# Recursively searches for files named "ietf-yang-library.json" and creates
# a Markdown table with one row per file:
#
# | File | NF types |
#
# Prerequisite:
#   The Python detector script from the previous step must be available,
#   for example as ./detect_nf_types.py
#
# Usage:
#   ./scan-yang-libraries.sh
#   ./scan-yang-libraries.sh -r ./data -d ./detect_nf_types.py -o nf-types.md
#   ./scan-yang-libraries.sh --include-import-only --min-confidence strong

ROOT_DIR="./data-models-per-network-function-instance"
DETECTOR="./scripts/detect_nf_types.py"
OUTPUT="network-function-types.md"
MIN_CONFIDENCE="strong"
INCLUDE_IMPORT_ONLY=false



usage() {
  cat <<'EOF'
Usage: scan-yang-libraries.sh [OPTIONS]

Options:
  -r, --root DIR              Root directory to search. Default: .
  -d, --detector FILE         Path to detect_nf_types.py. Default: ./detect_nf_types.py
  -o, --output FILE           Markdown output file. Default: network-function-types.md
      --min-confidence LEVEL  weak, medium, or strong. Default: weak
      --include-import-only   Also evaluate import-only-module entries
  -h, --help                  Show this help

Example:
  ./scan-yang-libraries.sh \
    --root ./yang-library-dumps \
    --detector ./detect_nf_types.py \
    --output nf-types.md \
    --min-confidence strong
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -r|--root)
      ROOT_DIR="$2"
      shift 2
      ;;
    -d|--detector)
      DETECTOR="$2"
      shift 2
      ;;
    -o|--output)
      OUTPUT="$2"
      shift 2
      ;;
    --min-confidence)
      MIN_CONFIDENCE="$2"
      shift 2
      ;;
    --include-import-only)
      INCLUDE_IMPORT_ONLY=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ ! -d "$ROOT_DIR" ]]; then
  echo "ERROR: Root directory does not exist: $ROOT_DIR" >&2
  exit 1
fi

if [[ ! -f "$DETECTOR" ]]; then
  echo "ERROR: Detector script not found: $DETECTOR" >&2
  exit 1
fi

if [[ "$MIN_CONFIDENCE" != "weak" && "$MIN_CONFIDENCE" != "medium" && "$MIN_CONFIDENCE" != "strong" ]]; then
  echo "ERROR: --min-confidence must be one of: weak, medium, strong" >&2
  exit 1
fi

# Escape characters that are special inside Markdown table cells.
markdown_escape() {
  local value="$1"
  value="${value//\\/\\\\}"
  value="${value//|/\\|}"
  value="${value//$'\n'/<br>}"
  printf '%s' "$value"
}

# Extract nf-types from detector JSON output.
# This uses Python so we do not depend on jq being installed.
extract_nf_types() {
  python3 -c '
import json
import sys
try:
    data = json.load(sys.stdin)
except Exception as exc:
    print(f"ERROR: could not parse detector output: {exc}", file=sys.stderr)
    sys.exit(2)
items = data.get("detected_network_function_types", [])
names = [item.get("network_function_type", "") for item in items if item.get("network_function_type")]
print(", ".join(names) if names else "-")
'
}

DETECTOR_ARGS=("--min-confidence" "$MIN_CONFIDENCE" "--format" "json")
if [[ "$INCLUDE_IMPORT_ONLY" == true ]]; then
  DETECTOR_ARGS+=("--include-import-only")
fi

{
  echo "| path | nf-types |"
  echo "|---|---|"

  # Use -print0 to handle spaces and special characters in file paths.
  while IFS= read -r -d '' yanglib_file; do
    detector_output=""
    nf_types=""

    if detector_output="$(python3 "$DETECTOR" "$yanglib_file" "${DETECTOR_ARGS[@]}" 2>&1)"; then
      nf_types="$(printf '%s' "$detector_output" | extract_nf_types)"
    else
      nf_types="ERROR: detector failed"
      echo "WARNING: Detector failed for: $yanglib_file" >&2
      echo "$detector_output" >&2
    fi

    # Show the path relative to ROOT_DIR in the Markdown output.
    # Example: if ROOT_DIR=./dumps and the file is ./dumps/o-du/ietf-yang-library.json,
    # the table will show o-du/ietf-yang-library.json.
    relative_path="${yanglib_file#"$ROOT_DIR"/}"
    relative_path="${relative_path#./}"

    escaped_path="$(markdown_escape "$relative_path")"
    escaped_nf_types="$(markdown_escape "$nf_types")"
    echo "| $escaped_path | $escaped_nf_types |"
  done < <(find "$ROOT_DIR" -type f -name 'ietf-yang-library.json' -print0 | sort -z)
} > "$OUTPUT"

echo "Wrote Markdown summary to: $OUTPUT"
