#!/usr/bin/env python3
"""
Generate ietf-yang-library.json for NF instances (RFC 8525).

Usage:
  ./scripts/generate-ietf-yang-library.py                    # all instances
  ./scripts/generate-ietf-yang-library.py 5GC-1/AF-1         # one 5GC instance
  ./scripts/generate-ietf-yang-library.py O-CU-1/O-CU-CP-1   # one O-CU sub-NF
  ./scripts/generate-ietf-yang-library.py O-DU-1 WT-1        # multiple flat instances

NF instance path patterns:
  <parent>/<sub-NF>   for nested NFs: 5GC-N/<NF>-N  and  O-CU-N/<O-CU-CP|O-CU-UP>-N
  <inst>              for flat NFs: O-DU-N, O-RU-N, ROADM-N, WT-N, OFH-SW-N
"""

import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR  = REPO_ROOT / "data-models-per-network-function-instance"
YANG_NF   = REPO_ROOT / "yang-per-network-function"
RFC       = REPO_ROOT / "yang-repos/yang/standard/ietf/RFC"
EXP       = REPO_ROOT / "yang-repos/yang/experimental/ietf-extracted-YANG-modules"

# ── NF instance folder → yang-per-network-function type folder ────────────────

INSTANCE_TO_YANG_TYPE: dict[str, str] = {
    "O-DU-1": "O-DU",    "O-DU-2": "O-DU",
    "O-RU-1": "O-RU",    "O-RU-2": "O-RU",    "O-RU-3": "O-RU",    "O-RU-4": "O-RU",
    "OFH-SW-1": "OpenFronthaul-Switch",
    "ROADM-1": "ROADM",  "ROADM-2": "ROADM",  "ROADM-3": "ROADM",
    "WT-1":  "WirelessTransport", "WT-2":  "WirelessTransport",
}

# ── O-CU sub-NF name prefix → yang-per-network-function type folder ───────────
# O-CU-1/O-CU-CP-1 → "O-CU-CP",  O-CU-1/O-CU-UP-1 → "O-CU-UP"
O_CU_SUB_NF_TO_YANG_TYPE: dict[str, str] = {
    "O-CU-CP": "O-CU-CP",
    "O-CU-UP": "O-CU-UP",
}

# ── 5GC NF name prefix → 3GPP NRM module (without @revision) ─────────────────

NF_TO_NRM: dict[str, str] = {
    "AF":    "_3gpp-5gc-nrm-affunction",
    "AMF":   "_3gpp-5gc-nrm-amffunction",
    "AUSF":  "_3gpp-5gc-nrm-ausffunction",
    "LMF":   "_3gpp-5gc-nrm-lmffunction",
    "NEF":   "_3gpp-5gc-nrm-neffunction",
    "NGEIR": "_3gpp-5gc-nrm-ngeirfunction",
    "NRF":   "_3gpp-5gc-nrm-nrffunction",
    "NSSF":  "_3gpp-5gc-nrm-nssffunction",
    "PCF":   "_3gpp-5gc-nrm-pcffunction",
    "SEPP":  "_3gpp-5gc-nrm-seppfunction",
    "SMF":   "_3gpp-5gc-nrm-smffunction",
    "SMSF":  "_3gpp-5gc-nrm-smsffunction",
    "UDM":   "_3gpp-5gc-nrm-udmfunction",
    "UDSF":  "_3gpp-5gc-nrm-udsffunction",
    "UPF":   "_3gpp-5gc-nrm-upffunction",
}

# All 5GC NRM module names (used to exclude other NFs' modules per instance)
ALL_5GC_NRM = set(NF_TO_NRM.values())

# ── Modules that only define types / identities / extensions ──────────────────
# These have no top-level protocol-accessible data nodes → import-only.

IMPORT_ONLY: set[str] = {
    # IETF typedef / identity / extension-only modules
    "ietf-yang-types",
    "ietf-inet-types",
    "ietf-datastores",
    "ietf-yang-metadata",
    "ietf-yang-patch",
    "ietf-routing-types",
    "ietf-te-types",
    "ietf-microwave-types",
    "iana-hardware",
    "iana-if-type",
    "iana-crypt-hash",
    "ietf-dhcpv6-types",
    "ietf-dhcpv6-common",
    "ietf-x509-cert-to-name",
    # IETF grouping-only modules (no top-level data, only reusable groupings)
    "ietf-crypto-types",
    "ietf-ssh-common",
    "ietf-tls-common",
    "ietf-tcp-common",
    # 3GPP typedef / extension / grouping-only modules
    "_3gpp-common-yang-types",
    "_3gpp-common-yang-extensions",
    "_3gpp-5g-common-yang-types",
    "_3gpp-common-ep-rp",
}

# ── YANG file parsing ─────────────────────────────────────────────────────────

def module_info(symlink: Path) -> dict | None:
    """
    Return name, revision, namespace, features from a .yang file.
    Returns None if the file is a submodule (no standalone namespace).
    """
    filename = symlink.name                            # e.g. ietf-system@2014-08-06.yang
    name = re.sub(r"@[\d-]+\.yang$|\.yang$", "", filename)

    m = re.search(r"@(\d{4}-\d{2}-\d{2})\.yang$", filename)
    revision_from_name = m.group(1) if m else None

    real = symlink.resolve()
    try:
        text = real.read_text(errors="replace")
    except OSError:
        return {"name": name, "revision": revision_from_name or "", "namespace": "", "features": []}

    # Detect submodule: the very first module/submodule keyword in the file
    decl = re.search(r"^\s*(module|submodule)\s+\S", text, re.MULTILINE)
    if decl and decl.group(1) == "submodule":
        return None   # submodules have no namespace; skip them

    # namespace: quoted ("urn:...") or unquoted (urn:...;)
    ns_m = re.search(r'^\s*namespace\s+"([^"]+)"', text, re.MULTILINE)
    if not ns_m:
        ns_m = re.search(r"^\s*namespace\s+(\S+?)\s*;", text, re.MULTILINE)
    namespace = ns_m.group(1) if ns_m else ""

    # revision: prefer file name, fall back to first revision stmt in file
    if revision_from_name:
        revision = revision_from_name
    else:
        rv_m = re.search(r"^\s*revision\s+(\d{4}-\d{2}-\d{2})", text, re.MULTILINE)
        revision = rv_m.group(1) if rv_m else ""

    features = re.findall(r"^\s*feature\s+([A-Za-z_][A-Za-z0-9_-]*)", text, re.MULTILINE)
    return {"name": name, "revision": revision, "namespace": namespace, "features": features}


# ── Instance → yang directory resolution ─────────────────────────────────────

def yang_dir_for(instance_rel: str) -> tuple[Path | None, str | None, bool]:
    """
    Return (yang_dir, nrm_module_name_or_None, is_5gc).

    For 5GC instances (e.g. '5GC-1/AF-1') the nrm_module is the one
    specific 3GPP NRM module that this NF type implements.
    """
    parts = instance_rel.replace("\\", "/").split("/")

    if len(parts) == 2 and parts[0].startswith("5GC"):
        yang_dir = YANG_NF / "5GCore" / "yang-models"
        nf_prefix = re.sub(r"-\d+$", "", parts[1])   # "AF-1" → "AF"
        return yang_dir, NF_TO_NRM.get(nf_prefix), True

    # O-CU is split into O-CU-CP and O-CU-UP sub-NFs under each O-CU-N parent.
    # path: "O-CU-1/O-CU-CP-1" → strip trailing -N from parts[1] → "O-CU-CP"
    if len(parts) == 2 and parts[0].startswith("O-CU"):
        sub_type = re.sub(r"-\d+$", "", parts[1])   # "O-CU-CP-1" → "O-CU-CP"
        yang_type = O_CU_SUB_NF_TO_YANG_TYPE.get(sub_type)
        if not yang_type:
            return None, None, False
        return YANG_NF / yang_type, None, False

    inst_name = parts[0]
    yang_type = INSTANCE_TO_YANG_TYPE.get(inst_name)
    if not yang_type:
        return None, None, False
    return YANG_NF / yang_type, None, False


# ── Module set builder ────────────────────────────────────────────────────────

def build_module_sets(yang_dir: Path, nrm_module: str | None, is_5gc: bool):
    """
    Return (implemented, import_only) as lists of dicts ready for JSON.
    """
    implemented: list[dict] = []
    import_only_list: list[dict] = []

    for sym in sorted(yang_dir.glob("*.yang")):
        info = module_info(sym)
        if info is None:
            continue   # skip submodules
        name = info["name"]

        # 5GC: skip NRM modules belonging to other NF types
        if is_5gc and name in ALL_5GC_NRM and name != nrm_module:
            continue

        entry: dict = {"name": name}
        if info["revision"]:
            entry["revision"] = info["revision"]
        entry["namespace"] = info["namespace"]

        if name in IMPORT_ONLY:
            import_only_list.append(entry)
        else:
            if info["features"]:
                entry["feature"] = info["features"]
            implemented.append(entry)

    return implemented, import_only_list


# ── JSON generation ───────────────────────────────────────────────────────────

def generate(inst_dir: Path, inst_rel: str) -> bool:
    yang_dir, nrm_module, is_5gc = yang_dir_for(inst_rel)

    if yang_dir is None or not yang_dir.exists():
        print(f"  SKIP  {inst_rel} — yang folder not found")
        return True   # not a failure

    hostname        = inst_dir.name.lower()           # "af-1"
    module_set_name = f"{hostname}-modules"
    schema_name     = f"{hostname}-schema"
    content_id      = f"{hostname}-yanglib-{date.today().isoformat()}"

    implemented, import_only_list = build_module_sets(yang_dir, nrm_module, is_5gc)

    doc = {
        "ietf-yang-library:yang-library": {
            "module-set": [
                {
                    "name": module_set_name,
                    "module": implemented,
                    "import-only-module": import_only_list,
                }
            ],
            "schema": [
                {"name": schema_name, "module-set": [module_set_name]}
            ],
            "datastore": [
                {"name": "ietf-datastores:running",     "schema": schema_name},
                {"name": "ietf-datastores:startup",     "schema": schema_name},
                {"name": "ietf-datastores:candidate",   "schema": schema_name},
                {"name": "ietf-datastores:operational", "schema": schema_name},
            ],
            "content-id": content_id,
        }
    }

    out = inst_dir / "ietf-yang-library.json"
    out.write_text(json.dumps(doc, indent=2) + "\n")

    # Validate with yanglint
    result = subprocess.run(
        [
            "yanglint", "-t", "get",
            "-p", str(RFC), "-p", str(EXP),
            str(RFC / "ietf-datastores.yang"),
            str(RFC / "ietf-yang-library@2019-01-04.yang"),
            str(out),
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print(f"  OK    {inst_rel}  "
              f"({len(implemented)} implemented, {len(import_only_list)} import-only)")
        return True

    print(f"  FAIL  {inst_rel}")
    for line in (result.stderr or result.stdout).strip().splitlines():
        print(f"        {line}")
    return False


# ── Instance discovery ────────────────────────────────────────────────────────

def all_instances() -> list[tuple[Path, str]]:
    """Find all leaf NF instance directories (those containing ietf-system.json)."""
    found = []
    for p in sorted(DATA_DIR.rglob("ietf-system.json")):
        inst_dir = p.parent
        inst_rel = str(inst_dir.relative_to(DATA_DIR))
        found.append((inst_dir, inst_rel))
    return found


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    if sys.argv[1:]:
        targets = [(DATA_DIR / t, t) for t in sys.argv[1:]]
    else:
        targets = all_instances()

    if not targets:
        print("No instances found.")
        sys.exit(0)

    print(f"Generating ietf-yang-library.json for {len(targets)} instance(s)...\n")
    ok = fail = 0
    for inst_dir, inst_rel in targets:
        if not inst_dir.is_dir():
            print(f"  SKIP  {inst_rel} — directory does not exist")
            continue
        if generate(inst_dir, inst_rel):
            ok += 1
        else:
            fail += 1

    print(f"\nDone: {ok} generated  |  {fail} failed")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
