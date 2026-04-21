#!/usr/bin/env bash
# Populates the yang-repos/ folder with the YANG model repositories required
# by this project. Three repos are cloned automatically; five O-RAN Alliance
# spec packages must be downloaded manually (see instructions below).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
YANG_REPOS="$SCRIPT_DIR/yang-repos"

mkdir -p "$YANG_REPOS"

# ---------------------------------------------------------------------------
# 1. YangModels/yang — comprehensive IETF/IEEE/vendor YANG model collection
# ---------------------------------------------------------------------------
if [ -d "$YANG_REPOS/yang/.git" ]; then
  echo "[yang] Already cloned, pulling latest..."
  git -C "$YANG_REPOS/yang" pull --ff-only
else
  echo "[yang] Cloning YangModels/yang (this is ~4 GB, may take a while)..."
  git clone https://github.com/YangModels/yang.git "$YANG_REPOS/yang"
fi

# ---------------------------------------------------------------------------
# 2. OpenROADM MSA Public — open DWDM/ROADM device and network models
# ---------------------------------------------------------------------------
if [ -d "$YANG_REPOS/OpenROADM_MSA_Public/.git" ]; then
  echo "[OpenROADM] Already cloned, pulling latest..."
  git -C "$YANG_REPOS/OpenROADM_MSA_Public" pull --ff-only
else
  echo "[OpenROADM] Cloning OpenROADM/OpenROADM_MSA_Public..."
  git clone https://github.com/OpenROADM/OpenROADM_MSA_Public.git "$YANG_REPOS/OpenROADM_MSA_Public"
fi

# ---------------------------------------------------------------------------
# 3. 3GPP SA5 MnS — Management and Orchestration YANG models (Rel-16/17/18)
# ---------------------------------------------------------------------------
if [ -d "$YANG_REPOS/MnS/.git" ]; then
  echo "[MnS] Already cloned, pulling latest..."
  git -C "$YANG_REPOS/MnS" pull --ff-only
else
  echo "[MnS] Cloning 3GPP SA5 MnS repository..."
  git clone https://forge.3gpp.org/rep/sa5/MnS.git "$YANG_REPOS/MnS"
fi

# ---------------------------------------------------------------------------
# 4. O-RAN Alliance spec packages — MANUAL DOWNLOAD REQUIRED
# ---------------------------------------------------------------------------
# O-RAN Alliance specifications require registration at https://specifications.o-ran.org
# Download the following ZIP archives and extract them into yang-repos/:
#
#   Spec                                  | Target folder
#   --------------------------------------|--------------------------------------------------
#   O-RAN.WG4.TS.MP-YANGs-R005-v20.00   | yang-repos/O-RAN.WG4.TS.MP-YANGs-R005-v20.00/
#   O-RAN.WG4.CTI-TMP-YANG-v03.00        | yang-repos/O-RAN.WG4.CTI-TMP-YANG-v03.00/
#   O-RAN.WG5.O-DU-O1.1-R003-v09.00     | yang-repos/O-RAN.WG5.O-DU-O1.1-R003-v09.00/
#   O-RAN.WG5.O-CU-O1.1-R003-v07.00     | yang-repos/O-RAN.WG5.O-CU-O1.1-R003-v07.00/
#   O-RAN.WG9.XTRP-SYN.1-R004-v06.00    | yang-repos/O-RAN.WG9.XTRP-SYN.1-R004-v06.00_YANG/
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
  "O-RAN.WG9.XTRP-SYN.1-R004-v06.00_YANG"; do
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
