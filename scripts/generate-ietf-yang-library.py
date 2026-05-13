#!/usr/bin/env python3
"""
Generate ietf-yang-library.json for NF types (RFC 8525).

Files are written to yang-per-network-function/<NF-type>/ — one per NF type,
not per NF instance.  The yang library depends only on the YANG model set that
defines the type, so it lives beside the models in yang-per-network-function.

Usage:
  ./scripts/generate-ietf-yang-library.py                    # all NF types
  ./scripts/generate-ietf-yang-library.py 5GCore/AF          # one 5GC NF type
  ./scripts/generate-ietf-yang-library.py O-CU-CP            # one type directly
  ./scripts/generate-ietf-yang-library.py O-DU ROADM         # multiple types

  # Instance paths are also accepted and resolved to their NF-type folder:
  ./scripts/generate-ietf-yang-library.py 5GC-1/AF-1         # → yang-per-network-function/5GCore/AF
  ./scripts/generate-ietf-yang-library.py O-CU-1/O-CU-CP-1   # → yang-per-network-function/O-CU-CP
  ./scripts/generate-ietf-yang-library.py O-DU-1 WT-1        # → O-DU, WirelessTransport
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
YANG_NF   = REPO_ROOT / "yang-per-network-function"
RFC       = REPO_ROOT / "yang-repos/yang/standard/ietf/RFC"
EXP       = REPO_ROOT / "yang-repos/yang/experimental/ietf-extracted-YANG-modules"

# ── NF instance folder → yang-per-network-function type folder ────────────────
# Used when the caller passes an instance path such as "O-DU-1" or "ROADM-B1".

INSTANCE_TO_YANG_TYPE: dict[str, str] = {
    "IP-RTR-1": "IP-Router",
    "O-DU-1": "O-DU",    "O-DU-2": "O-DU",
    "O-RU-1": "O-RU",    "O-RU-2": "O-RU",    "O-RU-3": "O-RU",    "O-RU-4": "O-RU",
    "OFH-SW-1": "OpenFronthaul-Switch",
    "ROADM-A1": "ROADM",  "ROADM-B1": "ROADM",  "ROADM-C1": "ROADM",
    "TXP-1": "Xponder",  "TXP-2": "Xponder",  "TXP-3": "Xponder",
    "WT-1":  "WirelessTransport", "WT-2":  "WirelessTransport",
}

# ── O-CU sub-NF name prefix → yang-per-network-function type folder ───────────
# O-CU-1/O-CU-CP-1 → "O-CU-CP",  O-CU-1/O-CU-UP-1 → "O-CU-UP"
O_CU_SUB_NF_TO_YANG_TYPE: dict[str, str] = {
    "O-CU-CP": "O-CU-CP",
    "O-CU-UP": "O-CU-UP",
}

# ── yang-per-network-function type → primary 3GPP NRM module ──────────────────
YANG_TYPE_TO_NRM: dict[str, str] = {
    "O-CU-CP": "_3gpp-nr-nrm-gnbcucpfunction",
    "O-CU-UP": "_3gpp-nr-nrm-gnbcuupfunction",
    "O-DU":    "_3gpp-nr-nrm-gnbdufunction",
}

# ── yang-per-network-function type → module-set / schema name token ───────────
# Used to build the identifiers in the generated JSON.
# Defaults to yang_dir.name.lower() when not listed here.
YANG_TYPE_TO_TOKEN: dict[str, str] = {
    "WirelessTransport": "wireless-transport",
}

# ── Per-primary-NRM additional name-token exclusions ─────────────────────────
_NRM_EXCLUDE_NAME_TOKENS: dict[str, set[str]] = {
    "_3gpp-nr-nrm-gnbdufunction": {"gnbcucp", "gnbcuup"},
}

# ── Per-primary-NRM implemented overrides ────────────────────────────────────
_NRM_OVERRIDE_IMPLEMENTED: dict[str, set[str]] = {
    "_3gpp-nr-nrm-gnbdufunction": {"_3gpp-nr-nrm-nrcelldu"},
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

# ── Modules that only define types / identities / extensions ──────────────────

IMPORT_ONLY: set[str] = {
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
    "ietf-crypto-types",
    "ietf-ssh-common",
    "ietf-tls-common",
    "ietf-tcp-common",
    "ietf-bfd-types",
    "ietf-segment-routing-common",
    "_3gpp-common-yang-types",
    "_3gpp-common-yang-extensions",
    "_3gpp-5g-common-yang-types",
    "_3gpp-common-ep-rp",
    "_3gpp-nr-nrm-nrcelldu",
    "_3gpp-5gc-nrm-ecmconnectioninfo",
}

# ── EP import-only classification ─────────────────────────────────────────────

_EP_ALWAYS_PATTERNS = [
    re.compile(r"_3gpp-\w+-nrm-ecmappingrule"),
]


def is_ep_import_only(name: str, primary_nrm: str | None) -> bool:
    for pat in _EP_ALWAYS_PATTERNS:
        if pat.fullmatch(name):
            return True

    if primary_nrm and name != primary_nrm:
        if re.fullmatch(r"_3gpp-\w+-nrm-(?!external)\w+function", name):
            return True

    if primary_nrm:
        for token in _NRM_EXCLUDE_NAME_TOKENS.get(primary_nrm, set()):
            if token in name:
                return True

    return False


def filter_ep_features(features: list[str], primary_nrm: str | None) -> list[str]:
    if not primary_nrm or not features:
        return features

    m = re.search(r"-nrm-(\w+function)$", primary_nrm, re.IGNORECASE)
    if not m:
        return features

    primary_func = m.group(1).upper()

    result = []
    for feat in features:
        ep_m = re.fullmatch(r"EPClassesUnder(\w+)", feat, re.IGNORECASE)
        if ep_m and ep_m.group(1).upper() != primary_func:
            continue
        result.append(feat)
    return result


# ── YANG file parsing ─────────────────────────────────────────────────────────

def module_info(symlink: Path) -> dict | None:
    filename = symlink.name
    name = re.sub(r"@[\d-]+\.yang$|\.yang$", "", filename)

    m = re.search(r"@(\d{4}-\d{2}-\d{2})\.yang$", filename)
    revision_from_name = m.group(1) if m else None

    real = symlink.resolve()
    try:
        text = real.read_text(errors="replace")
    except OSError:
        return {"name": name, "revision": revision_from_name or "", "namespace": "", "features": []}

    decl = re.search(r"^\s*(module|submodule)\s+\S", text, re.MULTILINE)
    if decl and decl.group(1) == "submodule":
        return None

    ns_m = re.search(r'^\s*namespace\s+"([^"]+)"', text, re.MULTILINE)
    if not ns_m:
        ns_m = re.search(r"^\s*namespace\s+(\S+?)\s*;", text, re.MULTILINE)
    namespace = ns_m.group(1) if ns_m else ""

    if revision_from_name:
        revision = revision_from_name
    else:
        rv_m = re.search(r"^\s*revision\s+(\d{4}-\d{2}-\d{2})", text, re.MULTILINE)
        revision = rv_m.group(1) if rv_m else ""

    features = re.findall(r"^\s*feature\s+([A-Za-z_][A-Za-z0-9_-]*)", text, re.MULTILINE)
    return {"name": name, "revision": revision, "namespace": namespace, "features": features}


# ── Target resolution ─────────────────────────────────────────────────────────

def resolve_target(arg: str) -> tuple[Path, str | None, str] | None:
    """
    Resolve a CLI argument to (yang_dir, nrm_module, label).

    Accepts:
      - NF type paths:     "O-DU", "5GCore/AF", "O-CU-CP"
      - NF instance paths: "O-DU-1", "5GC-1/AF-1", "O-CU-1/O-CU-CP-1"
    """
    parts = arg.replace("\\", "/").split("/")

    # ── Direct type path: "5GCore/AF" ──
    if len(parts) == 2 and parts[0] == "5GCore":
        nf_prefix = parts[1]
        yang_dir = YANG_NF / "5GCore" / nf_prefix
        if yang_dir.is_dir():
            return yang_dir, NF_TO_NRM.get(nf_prefix), arg
        return None

    # ── Direct type path: "O-DU", "O-CU-CP", "ROADM", … ──
    if len(parts) == 1:
        yang_dir = YANG_NF / arg
        if yang_dir.is_dir() and yang_dir.name != "5GCore":
            nrm = YANG_TYPE_TO_NRM.get(arg)
            return yang_dir, nrm, arg

    # ── Instance path: "5GC-1/AF-1" ──
    if len(parts) == 2 and parts[0].startswith("5GC"):
        nf_prefix = re.sub(r"-\d+$", "", parts[1])   # "AF-1" → "AF"
        yang_dir = YANG_NF / "5GCore" / nf_prefix
        if yang_dir.is_dir():
            return yang_dir, NF_TO_NRM.get(nf_prefix), f"5GCore/{nf_prefix}"
        return None

    # ── Instance path: "O-CU-1/O-CU-CP-1" ──
    if len(parts) == 2 and parts[0].startswith("O-CU"):
        sub_type = re.sub(r"-\d+$", "", parts[1])   # "O-CU-CP-1" → "O-CU-CP"
        yang_type = O_CU_SUB_NF_TO_YANG_TYPE.get(sub_type)
        if yang_type:
            yang_dir = YANG_NF / yang_type
            return yang_dir, YANG_TYPE_TO_NRM.get(yang_type), yang_type
        return None

    # ── Flat instance path: "O-DU-1", "ROADM-A1", … ──
    if len(parts) == 1:
        yang_type = INSTANCE_TO_YANG_TYPE.get(arg)
        if yang_type:
            yang_dir = YANG_NF / yang_type
            return yang_dir, YANG_TYPE_TO_NRM.get(yang_type), yang_type

    return None


# ── Module set builder ────────────────────────────────────────────────────────

def build_module_sets(yang_dir: Path, nrm_module: str | None):
    implemented: list[dict] = []
    import_only_list: list[dict] = []

    override_implemented = _NRM_OVERRIDE_IMPLEMENTED.get(nrm_module or "", set())

    for sym in sorted(yang_dir.glob("*.yang")):
        info = module_info(sym)
        if info is None:
            continue
        name = info["name"]

        entry: dict = {"name": name}
        if info["revision"]:
            entry["revision"] = info["revision"]
        entry["namespace"] = info["namespace"]

        if name in override_implemented:
            features = filter_ep_features(info["features"], nrm_module)
            if features:
                entry["feature"] = features
            implemented.append(entry)
        elif name in IMPORT_ONLY or is_ep_import_only(name, nrm_module):
            import_only_list.append(entry)
        else:
            features = filter_ep_features(info["features"], nrm_module)
            if features:
                entry["feature"] = features
            implemented.append(entry)

    return implemented, import_only_list


# ── JSON generation ───────────────────────────────────────────────────────────

def generate(yang_dir: Path, nrm_module: str | None, label: str) -> bool:
    if not yang_dir.exists():
        print(f"  SKIP  {label} — yang folder not found")
        return True

    type_token      = YANG_TYPE_TO_TOKEN.get(yang_dir.name, yang_dir.name.lower())
    module_set_name = f"{type_token}-modules"
    schema_name     = f"{type_token}-schema"
    content_id      = f"{type_token}-yanglib-{date.today().isoformat()}"

    implemented, import_only_list = build_module_sets(yang_dir, nrm_module)

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

    out = yang_dir / "ietf-yang-library.json"
    out.write_text(json.dumps(doc, indent=2) + "\n")

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
        print(f"  OK    {label}  "
              f"({len(implemented)} implemented, {len(import_only_list)} import-only)")
        return True

    print(f"  FAIL  {label}")
    for line in (result.stderr or result.stdout).strip().splitlines():
        print(f"        {line}")
    return False


# ── NF type discovery ─────────────────────────────────────────────────────────

def all_nf_types() -> list[tuple[Path, str | None, str]]:
    """Enumerate all NF type directories as (yang_dir, nrm_module, label) tuples."""
    results = []

    skip = {"5GCore", "SMOS-Topology"}
    for d in sorted(YANG_NF.iterdir()):
        if not d.is_dir() or d.name in skip:
            continue
        nrm = YANG_TYPE_TO_NRM.get(d.name)
        results.append((d, nrm, d.name))

    fgcore = YANG_NF / "5GCore"
    if fgcore.is_dir():
        for d in sorted(fgcore.iterdir()):
            if d.is_dir() and d.name != "yang-models":
                nrm = NF_TO_NRM.get(d.name)
                results.append((d, nrm, f"5GCore/{d.name}"))

    return results


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    if sys.argv[1:]:
        targets: list[tuple[Path, str | None, str]] = []
        for arg in sys.argv[1:]:
            resolved = resolve_target(arg)
            if resolved:
                targets.append(resolved)
            else:
                print(f"  SKIP  {arg} — unknown NF type or instance path")
    else:
        targets = all_nf_types()

    if not targets:
        print("No NF types found.")
        sys.exit(0)

    print(f"Generating ietf-yang-library.json for {len(targets)} NF type(s)...\n")
    ok = fail = 0
    for yang_dir, nrm_module, label in targets:
        if generate(yang_dir, nrm_module, label):
            ok += 1
        else:
            fail += 1

    print(f"\nDone: {ok} generated  |  {fail} failed")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
