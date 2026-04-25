#!/usr/bin/env bash
# Validate all YANG-modeled JSON files in data-models-per-network-function-instance/.
#
# Usage:
#   ./scripts/validate-yang-data.sh              # validate everything
#   ./scripts/validate-yang-data.sh 5GC-1/AF-1  # one instance
#   ./scripts/validate-yang-data.sh O-DU-1 WT-1 # multiple instances
#
# Exit code: 0 = all passed, 1 = one or more failures.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="$REPO_ROOT/data-models-per-network-function-instance"
RFC="$REPO_ROOT/yang-repos/yang/standard/ietf/RFC"
EXP="$REPO_ROOT/yang-repos/yang/experimental/ietf-extracted-YANG-modules"

# ── Prerequisite check ────────────────────────────────────────────────────────

if ! command -v yanglint &>/dev/null; then
    echo "ERROR: yanglint not found in PATH. Install libyang to continue." >&2
    exit 2
fi

# ── Schema registry ───────────────────────────────────────────────────────────
# Each entry maps a JSON filename to:
#   SCHEMA   — path to the primary YANG schema file (relative to REPO_ROOT)
#   TYPE     — "config" (default datastore) or "get" (operational / state data)
#   EXTRA    — optional additional YANG files to load (space-separated, relative to REPO_ROOT)
#
# Add a new row here whenever a new YANG model is introduced.

declare -A SCHEMA TYPE EXTRA

SCHEMA["ietf-system.json"]="yang-repos/yang/standard/ietf/RFC/ietf-system.yang"
TYPE["ietf-system.json"]="config"
EXTRA["ietf-system.json"]=""

SCHEMA["ietf-yang-library.json"]="yang-repos/yang/standard/ietf/RFC/ietf-yang-library@2019-01-04.yang"
TYPE["ietf-yang-library.json"]="get"
EXTRA["ietf-yang-library.json"]="yang-repos/yang/standard/ietf/RFC/ietf-datastores.yang"

# ── Validation logic ──────────────────────────────────────────────────────────

ok=0; fail=0; skip=0

validate_file() {
    local json_file="$1"
    local json_name
    json_name="$(basename "$json_file")"
    local rel
    rel="$(realpath --relative-to="$DATA_DIR" "$json_file")"

    local schema="${SCHEMA[$json_name]:-}"
    if [[ -z "$schema" ]]; then
        printf "  SKIP  %s — no schema registered\n" "$rel"
        (( skip++ )) || true
        return
    fi

    local schema_path="$REPO_ROOT/$schema"
    local vtype="${TYPE[$json_name]:-config}"
    local extra_raw="${EXTRA[$json_name]:-}"

    # Build yanglint argument list
    local args=(-p "$RFC" -p "$EXP")
    [[ "$vtype" == "get" ]] && args+=(-t get)

    # Load any extra YANG files required by this schema
    if [[ -n "$extra_raw" ]]; then
        for extra in $extra_raw; do
            args+=("$REPO_ROOT/$extra")
        done
    fi

    args+=("$schema_path" "$json_file")

    local stderr_output
    stderr_output="$(yanglint "${args[@]}" 2>&1)" && rc=0 || rc=$?

    if [[ $rc -eq 0 ]]; then
        printf "  OK    %s\n" "$rel"
        (( ok++ )) || true
    else
        printf "  FAIL  %s\n" "$rel"
        while IFS= read -r line; do
            printf "        %s\n" "$line"
        done <<< "$stderr_output"
        (( fail++ )) || true
    fi
}

# ── Collect files to validate ─────────────────────────────────────────────────

mapfile -t json_files < <(
    if [[ $# -gt 0 ]]; then
        for arg in "$@"; do
            find "$DATA_DIR/$arg" -name "*.json" 2>/dev/null | sort
        done
    else
        find "$DATA_DIR" -name "*.json" | sort
    fi
)

if [[ ${#json_files[@]} -eq 0 ]]; then
    echo "No JSON files found."
    exit 0
fi

printf "Validating %d JSON file(s)...\n\n" "${#json_files[@]}"

for f in "${json_files[@]}"; do
    validate_file "$f"
done

# ── Summary ───────────────────────────────────────────────────────────────────

printf "\nResults:  %d OK  |  %d FAIL  |  %d SKIPPED\n" "$ok" "$fail" "$skip"
[[ $fail -eq 0 ]]
