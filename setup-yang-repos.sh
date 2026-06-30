#!/usr/bin/env bash
# Populates the yang-repos/ folder with the YANG model repositories required
# by this project. Three repos are cloned automatically; five O-RAN Alliance
# spec packages must be downloaded manually (see instructions below).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
YANG_REPOS="$SCRIPT_DIR/yang-repos"
LOCK_FILE="${YANG_REPOS_LOCK:-$SCRIPT_DIR/yang-repos.lock}"

mkdir -p "$YANG_REPOS"

if [ -f "$LOCK_FILE" ]; then
  # shellcheck source=/dev/null
  . "$LOCK_FILE"
fi

YANG_MODELS_URL="${YANG_MODELS_URL:-https://github.com/YangModels/yang.git}"
YANG_MODELS_REF="${YANG_MODELS_REF:-8be95f275a7377828f5a6b34432d4ae1c816e53f}"
OPENROADM_URL="${OPENROADM_URL:-https://github.com/OpenROADM/OpenROADM_MSA_Public.git}"
OPENROADM_REF="${OPENROADM_REF:-011eec29711c46278aebc3c8a0583fc0f35f7395}"
MNS_URL="${MNS_URL:-https://forge.3gpp.org/rep/sa5/MnS.git}"
MNS_REF="${MNS_REF:-YANG-stage3-Corrections-Rel18-SA5-166}"
MNS_COMMIT="${MNS_COMMIT:-cb7960b625231af2bce35632fcbc89e21883efc2}"

resolve_ref() {
  local repo_dir="$1"
  local ref="$2"
  local candidate

  if [[ "$ref" =~ ^[0-9a-fA-F]{40}$ ]] && git -C "$repo_dir" cat-file -e "$ref^{commit}" 2>/dev/null; then
    echo "$ref"
    return 0
  fi

  for candidate in "refs/tags/$ref" "refs/remotes/origin/$ref" "refs/heads/$ref" "$ref"; do
    if git -C "$repo_dir" rev-parse --verify --quiet "$candidate^{commit}" >/dev/null; then
      echo "$candidate"
      return 0
    fi
  done

  return 1
}

checkout_ref() {
  local name="$1"
  local repo_dir="$2"
  local ref="$3"
  local override_var="$4"
  local expected_commit="${5:-}"
  local resolved_ref
  local resolved_commit

  if [ -n "$(git -C "$repo_dir" status --porcelain)" ]; then
    echo "[$name] ERROR: working tree has local changes. Commit, stash, or discard them before changing refs."
    exit 1
  fi

  echo "[$name] Fetching refs..."
  git -C "$repo_dir" fetch --tags --prune

  if ! resolved_ref="$(resolve_ref "$repo_dir" "$ref")"; then
    echo "[$name] ERROR: required ref '$ref' was not found."
    echo "[$name] Check the spelling or set $override_var to an available tag, branch, or commit."
    exit 1
  fi

  resolved_commit="$(git -C "$repo_dir" rev-parse "$resolved_ref^{commit}")"
  if [ -n "$expected_commit" ] && [ "$resolved_commit" != "$expected_commit" ]; then
    echo "[$name] ERROR: $ref resolves to $resolved_commit, expected $expected_commit."
    echo "[$name] Update yang-repos.lock only after confirming the new standards source is intended."
    exit 1
  fi

  echo "[$name] Checking out $ref ($resolved_ref -> $resolved_commit)..."
  git -C "$repo_dir" checkout --detach "${expected_commit:-$resolved_ref}"
}

# ---------------------------------------------------------------------------
# 1. YangModels/yang — comprehensive IETF/IEEE/vendor YANG model collection
# ---------------------------------------------------------------------------
if [ -d "$YANG_REPOS/yang/.git" ]; then
  echo "[yang] Already cloned."
else
  echo "[yang] Cloning YangModels/yang (this is ~4 GB, may take a while)..."
  git clone "$YANG_MODELS_URL" "$YANG_REPOS/yang"
fi
checkout_ref "yang" "$YANG_REPOS/yang" "$YANG_MODELS_REF" "YANG_MODELS_REF"

# ---------------------------------------------------------------------------
# 2. OpenROADM MSA Public — open DWDM/ROADM device and network models
# ---------------------------------------------------------------------------
if [ -d "$YANG_REPOS/OpenROADM_MSA_Public/.git" ]; then
  echo "[OpenROADM] Already cloned."
else
  echo "[OpenROADM] Cloning OpenROADM/OpenROADM_MSA_Public..."
  git clone "$OPENROADM_URL" "$YANG_REPOS/OpenROADM_MSA_Public"
fi
checkout_ref "OpenROADM" "$YANG_REPOS/OpenROADM_MSA_Public" "$OPENROADM_REF" "OPENROADM_REF"

# ---------------------------------------------------------------------------
# 3. 3GPP SA5 MnS — Management and Orchestration YANG models (Rel-16/17/18)
# ---------------------------------------------------------------------------
if [ -d "$YANG_REPOS/MnS/.git" ]; then
  echo "[MnS] Already cloned."
else
  echo "[MnS] Cloning 3GPP SA5 MnS repository..."
  git clone "$MNS_URL" "$YANG_REPOS/MnS"
fi
checkout_ref "MnS" "$YANG_REPOS/MnS" "$MNS_REF" "MNS_REF" "$MNS_COMMIT"

# ---------------------------------------------------------------------------
# 4. O-RAN Alliance spec packages — MANUAL DOWNLOAD REQUIRED
# ---------------------------------------------------------------------------
# O-RAN Alliance specifications require registration at https://specifications.o-ran.org
# Download the following ZIP archives and extract them into yang-repos/:
#
#   Spec                                                          | Target folder
#   --------------------------------------------------------------|----------------------------------------------------------------------
#   O-RAN.WG4.TS.MP-YANGs-R005-v20.00                           | yang-repos/O-RAN.WG4.TS.MP-YANGs-R005-v20.00/
#   O-RAN.WG4.CTI-TMP-YANG-v03.00                                | yang-repos/O-RAN.WG4.CTI-TMP-YANG-v03.00/
#   O-RAN.WG5.O-DU-O1.1-R003-v09.00                             | yang-repos/O-RAN.WG5.O-DU-O1.1-R003-v09.00/
#   O-RAN.WG5.O-CU-O1.1-R003-v07.00                             | yang-repos/O-RAN.WG5.O-CU-O1.1-R003-v07.00/
#   O-RAN.WG9.XTRP-SYN.1-R004-v06.00                            | yang-repos/O-RAN.WG9.XTRP-SYN.1-R004-v06.00_YANG/
#   O-RAN.WG10.TS.Information Model and Data Models.1-R005-v13.00 | yang-repos/O-RAN.WG10.TS.Information Model and Data Models.1-R005-v13.00/
#   O-RAN.WG10.TS.O1NRM.1-R004-v04.00                           | yang-repos/O-RAN.WG10.TS.O1NRM.1-R004-v04.00/
#
# Steps:
#   1. Go to https://specifications.o-ran.org
#   2. Search for each spec name listed above
#   3. Download the YANG model ZIP attachment
#   4. Extract into the corresponding target folder under yang-repos/
#
MISSING_ORAN=()
for dir in \
  "O-RAN.WG4.TS.MP-YANGs-R005-v20.00" \
  "O-RAN.WG4.CTI-TMP-YANG-v03.00" \
  "O-RAN.WG5.O-DU-O1.1-R003-v09.00" \
  "O-RAN.WG5.O-CU-O1.1-R003-v07.00" \
  "O-RAN.WG9.XTRP-SYN.1-R004-v06.00_YANG" \
  "O-RAN.WG10.TS.Information Model and Data Models.1-R005-v13.00" \
  "O-RAN.WG10.TS.O1NRM.1-R004-v04.00"; do
  if [ ! -d "$YANG_REPOS/$dir" ]; then
    MISSING_ORAN+=("$dir")
  fi
done

if [ ${#MISSING_ORAN[@]} -gt 0 ]; then
  echo ""
  echo "================================================================"
  echo " ACTION REQUIRED: missing O-RAN Alliance spec packages"
  echo "================================================================"
  echo " The following folders must be populated manually."
  echo " Download the YANG ZIP archives from https://specifications.o-ran.org"
  echo " and extract them into yang-repos/:"
  echo ""
  for dir in "${MISSING_ORAN[@]}"; do
    echo "   - $dir"
  done
  echo "================================================================"
  echo ""
else
  echo "[O-RAN] All O-RAN spec packages are present."
fi

echo ""
echo "Done. yang-repos/ is ready."
