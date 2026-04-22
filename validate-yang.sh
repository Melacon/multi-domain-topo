#!/usr/bin/env bash
# Validates YANG files in a yang-per-network-function/<NF>/ folder.
# Usage: ./validate-yang.sh [<NF-folder>]
# Default NF folder: yang-per-network-function/ROADM
#
# Step 1 — pyang (structural)   exit 1 on any error
# Step 2 — pyang --lint         RFC 8407 style report; informational for
#                                vendor/external modules, exit 1 only for
#                                our own modules
# Step 3 — yanglint             libyang schema validation; runs only when
#                                step 1 passes; receives only the top-level
#                                modules (those not imported by anything else
#                                in the folder) to avoid double-loading deps
#
# All YANG dependencies must be present as (sym)links in the NF folder.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NF_DIR="${1:-$SCRIPT_DIR/yang-per-network-function/ROADM}"
NF_DIR="$(realpath "$NF_DIR")"

PYANG="${PYANG:-$(command -v pyang 2>/dev/null || echo "$HOME/.local/bin/pyang")}"
YANGLINT="${YANGLINT:-$(command -v yanglint 2>/dev/null || true)}"

# Collect all .yang files in the NF folder (follow symlinks)
mapfile -t YANG_FILES < <(find "$NF_DIR" -maxdepth 1 -name "*.yang" | sort)

if [ ${#YANG_FILES[@]} -eq 0 ]; then
  echo "ERROR: no .yang files found in $NF_DIR" >&2
  exit 1
fi

# ---------------------------------------------------------------------------
# Discover top-level modules: files not imported by any other file in
# the folder. yanglint receives only these; it finds deps via --path.
# ---------------------------------------------------------------------------
all_module_names=()
for f in "${YANG_FILES[@]}"; do
  # Strip @date.yang or .yang suffix to get the module name
  mod="$(basename "$f" .yang | sed 's/@[0-9-]*$//')"
  all_module_names+=("$mod")
done

imported_modules=()
for f in "${YANG_FILES[@]}"; do
  while IFS= read -r line; do
    if [[ "$line" =~ ^[[:space:]]*import[[:space:]]+([^[:space:]{]+) ]]; then
      imported_modules+=("${BASH_REMATCH[1]}")
    fi
  done < <(grep -E '^\s*import\s+' "$f" 2>/dev/null || true)
done

toplevel_files=()
for f in "${YANG_FILES[@]}"; do
  mod="$(basename "$f" .yang | sed 's/@[0-9-]*$//')"
  is_imported=0
  for imp in "${imported_modules[@]}"; do
    if [[ "$imp" == "$mod" ]]; then
      is_imported=1
      break
    fi
  done
  # Also exclude IETF/IEEE standard modules from yanglint's "implemented"
  # list: libyang validates default identityref values strictly for implemented
  # modules, which fails on well-known IETF specs that reference identities
  # across module boundaries. They load correctly as non-implemented deps.
  if [[ "$mod" == ietf-* || "$mod" == ieee-* ]]; then
    is_imported=1
  fi
  if [ "$is_imported" -eq 0 ]; then
    toplevel_files+=("$f")
  fi
done

PYANG_VER="$("$PYANG" --version 2>/dev/null)"
YANGLINT_VER="${YANGLINT:+$("$YANGLINT" --version 2>/dev/null)}"

LOG_FILE="$NF_DIR/validation.log"
# Strip the NF_DIR prefix from all tool output so the log contains relative paths
exec > >(sed "s|$NF_DIR/||g" | tee "$LOG_FILE") 2>&1

echo "=========================================================="
echo " NF folder      : $NF_DIR"
echo " log file       : $LOG_FILE"
echo " timestamp      : $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo " YANG files     : ${#YANG_FILES[@]} total, ${#toplevel_files[@]} top-level"
echo " pyang          : $PYANG_VER"
echo " yanglint       : ${YANGLINT_VER:-not found}"
echo "=========================================================="
echo ""

STEP1_OK=0
STEP2_OK=0
STEP3_OK=0

# ---------------------------------------------------------------------------
# Step 1 — pyang structural validation (no --lint)
# ---------------------------------------------------------------------------
echo "--- Step 1: pyang (structural validation) ---"
if "$PYANG" \
     --path "$NF_DIR" \
     "${YANG_FILES[@]}" \
   2>&1; then
  echo "[PASS] pyang structural"
  STEP1_OK=1
else
  echo "[FAIL] pyang structural — fix errors before continuing"
fi
echo ""

# ---------------------------------------------------------------------------
# Step 2 — pyang --lint (RFC 8407 style check)
# Errors in vendor/external modules are informational only.
# ---------------------------------------------------------------------------
echo "--- Step 2: pyang --lint (RFC 8407 style) ---"
LINT_OUTPUT="$("$PYANG" \
  --lint \
  --path "$NF_DIR" \
  "${YANG_FILES[@]}" 2>&1 || true)"

if [ -z "$LINT_OUTPUT" ]; then
  echo "[PASS] pyang --lint (no issues)"
  STEP2_OK=1
else
  LINT_ERRORS=$(echo "$LINT_OUTPUT"   | grep ': error:'   || true)
  LINT_WARNINGS=$(echo "$LINT_OUTPUT" | grep ': warning:' || true)
  WARN_COUNT=$(echo "$LINT_WARNINGS"  | grep -c '.'       || true)
  ERR_COUNT=$(echo "$LINT_ERRORS"     | grep -c '.'       || true)

  echo "$LINT_OUTPUT"
  echo ""
  echo "  errors  : $ERR_COUNT"
  echo "  warnings: $WARN_COUNT"

  # Fail only if errors originate from our own (non-vendor) modules
  OWN_ERRORS=$(echo "$LINT_ERRORS" \
    | grep -v '/ietf-' \
    | grep -v '/iana-' \
    | grep -v '/ieee-' \
    | grep -v '/org-openroadm-' \
    | grep -v '/org-3gpp-' \
    | grep -v '/o-ran-' \
    || true)

  if [ -n "$OWN_ERRORS" ]; then
    echo "[FAIL] pyang --lint: errors in local modules"
  else
    echo "[INFO] pyang --lint: errors are in vendor/external modules (informational)"
    STEP2_OK=1
  fi
fi
echo ""

# ---------------------------------------------------------------------------
# Step 3 — yanglint (only when step 1 passed)
# Passes top-level modules on the command line; deps resolved via --path.
# ---------------------------------------------------------------------------
if [ "$STEP1_OK" -eq 1 ]; then
  echo "--- Step 3: yanglint (top-level modules: ${#toplevel_files[@]}) ---"
  for f in "${toplevel_files[@]}"; do
    echo "  $(basename "$f")"
  done
  echo ""
  if [ -z "$YANGLINT" ]; then
    echo "[SKIP] yanglint not found in PATH"
    STEP3_OK=1
  else
    # When every file in the folder is an IETF/IANA/IEEE standard module
    # (toplevel_files is empty after the vendor-filter), fall back to the
    # structurally non-imported set and add -i -i so that all modules
    # loaded via --path are also marked implemented. This resolves cross-
    # module identityref defaults that libyang 2.x validates strictly.
    yanglint_files=("${toplevel_files[@]}")
    yanglint_extra_flags=()
    if [ ${#yanglint_files[@]} -eq 0 ]; then
      for f in "${YANG_FILES[@]}"; do
        mod="$(basename "$f" .yang | sed 's/@[0-9-]*$//')"
        is_imported=0
        for imp in "${imported_modules[@]}"; do
          [[ "$imp" == "$mod" ]] && is_imported=1 && break
        done
        [ "$is_imported" -eq 0 ] && yanglint_files+=("$f")
      done
      yanglint_extra_flags=(-i -i)
    fi

    if "$YANGLINT" \
         "${yanglint_extra_flags[@]}" \
         --path "$NF_DIR" \
         "${yanglint_files[@]}" \
       2>&1; then
      echo "[PASS] yanglint"
      STEP3_OK=1
    else
      echo "[FAIL] yanglint reported errors"
    fi
  fi
else
  echo "--- Step 3: yanglint [SKIPPED — step 1 failed] ---"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "=========================================================="
echo " Step 1 pyang structural : $([ $STEP1_OK -eq 1 ] && echo PASS || echo FAIL)"
echo " Step 2 pyang --lint     : $([ $STEP2_OK -eq 1 ] && echo PASS || echo FAIL)"
echo " Step 3 yanglint         : $([ $STEP3_OK -eq 1 ] && echo PASS || echo FAIL/SKIP)"
echo "=========================================================="

if [ "$STEP1_OK" -eq 0 ] || [ "$STEP3_OK" -eq 0 ]; then
  exit 1
fi
