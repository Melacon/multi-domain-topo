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

#!/usr/bin/env python3
"""
Detect telecommunication Network Function Types from an ietf-yang-library JSON file.

Key behavior:
- Uses module-set[*].module by default.
- Ignores module-set[*].import-only-module by default.
- Uses conservative, exact module-name matching for O-RU to avoid false positives from
  common O-RAN WG4 / O-DU / aggregation modules.
- Suppresses 3GPP gNB-* aliases when O-RAN modules are detected, unless disabled.

Example:
    python3 detect_nf_types.py ietf-yang-library.json
    python3 detect_nf_types.py ietf-yang-library.json --format table
    python3 detect_nf_types.py ietf-yang-library.json --keep-3gpp-ran-aliases
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable, Literal

Confidence = Literal["weak", "medium", "strong"]

NETWORK_FUNCTION_TYPES = [
    "gNB-CU-CP",
    "gNB-CU-UP",
    "gNB-DU",
    "O-CU-CP",
    "O-CU-UP",
    "O-DU",
    "O-RU",
    "OFH-Switch",
    "Transponder",
    "ROADM",
    "WirelessTransport",
    "AF",
    "AMF",
    "AUSF",
    "LMF",
    "NEF",
    "NGEIR",
    "NRF",
    "NSSF",
    "PCF",
    "SEPP",
    "SMF",
    "SMSF",
    "UDM",
    "UDSF",
    "UPF",
]


@dataclass(frozen=True)
class YangModule:
    name: str
    namespace: str | None = None
    revision: str | None = None
    features: tuple[str, ...] = ()
    import_only: bool = False


@dataclass(frozen=True)
class MatchResult:
    network_function_type: str
    confidence: Confidence
    score: int
    matched_rules: list[str]
    matched_modules: list[str]


@dataclass(frozen=True)
class DetectionRule:
    nf_type: str
    score: int
    description: str
    module_names_any: tuple[str, ...] = ()
    module_prefixes_any: tuple[str, ...] = ()
    namespace_substrings_any: tuple[str, ...] = ()

    def match(self, modules: list[YangModule]) -> tuple[bool, list[str]]:
        matched: set[str] = set()
        wanted_names = {n.lower() for n in self.module_names_any}
        wanted_prefixes = tuple(p.lower() for p in self.module_prefixes_any)
        wanted_ns_parts = tuple(s.lower() for s in self.namespace_substrings_any)

        for module in modules:
            module_name = module.name.lower()
            namespace = (module.namespace or "").lower()

            if module_name in wanted_names:
                matched.add(module.name)
            if wanted_prefixes and module_name.startswith(wanted_prefixes):
                matched.add(module.name)
            if wanted_ns_parts and any(s in namespace for s in wanted_ns_parts):
                matched.add(module.name)

        return bool(matched), sorted(matched)


# Important rule design:
# - O-RU detection is intentionally strict and exact-name based.
# - Do not use generic O-RAN modules such as o-ran-wg4-features, o-ran-interfaces,
#   o-ran-hardware, o-ran-operations, o-ran-synchronization, o-ran-supervision,
#   o-ran-software-management, or o-ran-performance-management as O-RU identifiers.
# - Do not use o-ran-agg-* modules as O-RU identifiers; those can describe aggregation profiles.
DETECTION_RULES: list[DetectionRule] = [
    # 3GPP NR RAN functions
    DetectionRule(
        nf_type="gNB-DU",
        score=80,
        description="3GPP GNBDUFunction module implemented",
        module_names_any=("_3gpp-nr-nrm-gnbdufunction",),
    ),
    DetectionRule(
        nf_type="gNB-CU-CP",
        score=80,
        description="3GPP GNBCUCPFunction module implemented",
        module_names_any=("_3gpp-nr-nrm-gnbcucpfunction",),
    ),
    DetectionRule(
        nf_type="gNB-CU-UP",
        score=80,
        description="3GPP GNBCUUPFunction module implemented",
        module_names_any=("_3gpp-nr-nrm-gnbcuupfunction",),
    ),

    # O-RAN RAN functions
    DetectionRule(
        nf_type="O-DU",
        score=90,
        description="O-RAN O-DU or 3GPP GNBDUFunction modules implemented in an O-RAN module set",
        module_names_any=(
            "_3gpp-nr-nrm-gnbdufunction",
            "o-ran_3gpp-nr-nrm-gnbdufunction",
            "o-ran-o1-ctiOdu",
            "o-ran-o1-odu-nespolicy",
            "o-ran-o1-odu-nespolicyrelation",
            "o-ran-o1-odu-rballoc",
            "o-ran-du-performance-management",
            "o-ran-du-f1-tnl",
        ),
    ),
    DetectionRule(
        nf_type="O-CU-CP",
        score=90,
        description="O-RAN O-CU-CP or 3GPP GNBCUCPFunction modules implemented in an O-RAN module set",
        module_names_any=(
            "_3gpp-nr-nrm-gnbcucpfunction",
            "o-ran_3gpp-nr-nrm-gnbcucpfunction",
        ),
    ),
    DetectionRule(
        nf_type="O-CU-UP",
        score=90,
        description="O-RAN O-CU-UP or 3GPP GNBCUUPFunction modules implemented in an O-RAN module set",
        module_names_any=(
            "_3gpp-nr-nrm-gnbcuupfunction",
            "o-ran_3gpp-nr-nrm-gnbcuupfunction",
        ),
    ),
    DetectionRule(
        nf_type="O-RU",
        score=90,
        description="O-RAN O-RU specific Open Fronthaul M-Plane modules implemented",
        module_names_any=(
            "o-ran-uplane-conf",
            "o-ran-module-cap",
            "o-ran-transceiver",
            "o-ran-beamforming",
            "o-ran-ald",
            "o-ran-ald-port",
            "o-ran-processing-element",
            "o-ran-laa",
            "o-ran-laa-operations",
            "o-ran-shared-cell",
        ),
    ),
    DetectionRule(
        nf_type="OFH-Switch",
        score=70,
        description="Open Fronthaul switch or Ethernet bridge modules implemented",
        module_names_any=(
            "o-ran-ethernet-forwarding",
            "ieee802-dot1q-bridge",
            "ieee802-dot1ab-lldp",
        ),
    ),

    # Transport functions. These may need refinement for your exact transport model set.
    DetectionRule(
        nf_type="ROADM",
        score=90,
        description="OpenROADM ROADM/device modules implemented",
        module_prefixes_any=("org-openroadm",),
        namespace_substrings_any=("openroadm",),
    ),
    DetectionRule(
        nf_type="Transponder",
        score=80,
        description="Optical transponder / terminal device modules implemented",
        module_names_any=(
            "ietf-layer0-types",
            "ietf-optical-impairment-topology",
        ),
        namespace_substrings_any=("transponder", "terminal-device", "otsi", "otn"),
    ),
    DetectionRule(
        nf_type="WirelessTransport",
        score=80,
        description="Wireless transport / microwave modules implemented",
        namespace_substrings_any=("wireless", "microwave"),
    ),

    # 5G Core managed functions according to common 3GPP 5GC NRM module naming.
    DetectionRule("AF", 90, "3GPP 5GC AFFunction module implemented", module_names_any=("_3gpp-5gc-nrm-affunction",)),
    DetectionRule("AMF", 90, "3GPP 5GC AMFFunction module implemented", module_names_any=("_3gpp-5gc-nrm-amffunction",)),
    DetectionRule("AUSF", 90, "3GPP 5GC AUSFFunction module implemented", module_names_any=("_3gpp-5gc-nrm-ausffunction",)),
    DetectionRule("LMF", 90, "3GPP 5GC LMFFunction module implemented", module_names_any=("_3gpp-5gc-nrm-lmffunction",)),
    DetectionRule("NEF", 90, "3GPP 5GC NEFFunction module implemented", module_names_any=("_3gpp-5gc-nrm-neffunction",)),
    DetectionRule("NGEIR", 90, "3GPP 5GC NGEIRFunction module implemented", module_names_any=("_3gpp-5gc-nrm-ngeirfunction",)),
    DetectionRule("NRF", 90, "3GPP 5GC NRFFunction module implemented", module_names_any=("_3gpp-5gc-nrm-nrffunction",)),
    DetectionRule("NSSF", 90, "3GPP 5GC NSSFFunction module implemented", module_names_any=("_3gpp-5gc-nrm-nssffunction",)),
    DetectionRule("PCF", 90, "3GPP 5GC PCFFunction module implemented", module_names_any=("_3gpp-5gc-nrm-pcffunction",)),
    DetectionRule("SEPP", 90, "3GPP 5GC SEPPFunction module implemented", module_names_any=("_3gpp-5gc-nrm-seppfunction",)),
    DetectionRule("SMF", 90, "3GPP 5GC SMFFunction module implemented", module_names_any=("_3gpp-5gc-nrm-smffunction",)),
    DetectionRule("SMSF", 90, "3GPP 5GC SMSFFunction module implemented", module_names_any=("_3gpp-5gc-nrm-smsffunction",)),
    DetectionRule("UDM", 90, "3GPP 5GC UDMFunction module implemented", module_names_any=("_3gpp-5gc-nrm-udmfunction",)),
    DetectionRule("UDSF", 90, "3GPP 5GC UDSFFunction module implemented", module_names_any=("_3gpp-5gc-nrm-udsffunction",)),
    DetectionRule("UPF", 90, "3GPP 5GC UPFFunction module implemented", module_names_any=("_3gpp-5gc-nrm-upffunction",)),
]


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise SystemExit(f"ERROR: File not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: Invalid JSON in {path}: {exc}")
    if not isinstance(data, dict):
        raise SystemExit("ERROR: JSON root must be an object.")
    return data


def find_key_recursively(value: Any, key: str) -> Any | None:
    if isinstance(value, dict):
        if key in value:
            return value[key]
        for child in value.values():
            result = find_key_recursively(child, key)
            if result is not None:
                return result
    elif isinstance(value, list):
        for child in value:
            result = find_key_recursively(child, key)
            if result is not None:
                return result
    return None


def get_yang_library_root(data: dict[str, Any]) -> dict[str, Any]:
    for key in ("ietf-yang-library:yang-library", "yang-library"):
        value = data.get(key)
        if isinstance(value, dict):
            return value
    found = find_key_recursively(data, "ietf-yang-library:yang-library")
    if isinstance(found, dict):
        return found
    raise SystemExit("ERROR: Could not find ietf-yang-library:yang-library in the JSON file.")


def parse_single_module(raw_module: Any, import_only: bool) -> YangModule | None:
    if not isinstance(raw_module, dict):
        return None
    name = raw_module.get("name")
    if not isinstance(name, str) or not name.strip():
        return None
    features_raw = raw_module.get("feature", []) or []
    features = tuple(str(f) for f in features_raw) if isinstance(features_raw, list) else ()
    namespace = raw_module.get("namespace")
    revision = raw_module.get("revision")
    return YangModule(
        name=name.strip(),
        namespace=namespace if isinstance(namespace, str) else None,
        revision=revision if isinstance(revision, str) else None,
        features=features,
        import_only=import_only,
    )


def parse_modules(data: dict[str, Any], include_import_only: bool = False) -> list[YangModule]:
    root = get_yang_library_root(data)
    module_sets = root.get("module-set", [])
    if not isinstance(module_sets, list):
        raise SystemExit("ERROR: yang-library/module-set must be a list.")

    modules: list[YangModule] = []
    seen: set[tuple[str, str | None, bool]] = set()

    for module_set in module_sets:
        if not isinstance(module_set, dict):
            continue

        for raw_module in module_set.get("module", []) or []:
            module = parse_single_module(raw_module, import_only=False)
            if module:
                key = (module.name, module.revision, module.import_only)
                if key not in seen:
                    modules.append(module)
                    seen.add(key)

        if include_import_only:
            for raw_module in module_set.get("import-only-module", []) or []:
                module = parse_single_module(raw_module, import_only=True)
                if module:
                    key = (module.name, module.revision, module.import_only)
                    if key not in seen:
                        modules.append(module)
                        seen.add(key)

    return modules


def confidence_from_score(score: int) -> Confidence:
    if score >= 80:
        return "strong"
    if score >= 50:
        return "medium"
    return "weak"


def confidence_rank(confidence: Confidence) -> int:
    return {"weak": 1, "medium": 2, "strong": 3}[confidence]


def has_oran_modules(modules: list[YangModule]) -> bool:
    return any(
        m.name.lower().startswith("o-ran") or (m.namespace or "").lower().startswith("urn:o-ran:")
        for m in modules
        if not m.import_only
    )


def normalize_results(
    results: list[MatchResult],
    modules: list[YangModule],
    keep_3gpp_ran_aliases: bool = False,
) -> list[MatchResult]:
    if keep_3gpp_ran_aliases:
        return results

    # If O-RAN modules are present, report O-RAN RAN function names only.
    # Example: an O-DU normally implements 3GPP GNBDUFunction, but the NF type
    # exposed to O-RAN architecture should be O-DU, not gNB-DU.
    if has_oran_modules(modules):
        suppressed = {"gNB-DU", "gNB-CU-CP", "gNB-CU-UP"}
        return [r for r in results if r.network_function_type not in suppressed]

    return results


def detect_network_function_types(
    modules: list[YangModule],
    min_confidence: Confidence = "weak",
    keep_3gpp_ran_aliases: bool = False,
) -> list[MatchResult]:
    by_nf: dict[str, dict[str, Any]] = {}

    for rule in DETECTION_RULES:
        did_match, matched_modules = rule.match(modules)
        if not did_match:
            continue

        current = by_nf.setdefault(
            rule.nf_type,
            {"score": 0, "matched_rules": [], "matched_modules": set()},
        )
        current["score"] += rule.score
        current["matched_rules"].append(rule.description)
        current["matched_modules"].update(matched_modules)

    results: list[MatchResult] = []
    for nf_type in NETWORK_FUNCTION_TYPES:
        item = by_nf.get(nf_type)
        if not item:
            continue
        score = int(item["score"])
        confidence = confidence_from_score(score)
        if confidence_rank(confidence) < confidence_rank(min_confidence):
            continue
        results.append(
            MatchResult(
                network_function_type=nf_type,
                confidence=confidence,
                score=score,
                matched_rules=sorted(item["matched_rules"]),
                matched_modules=sorted(item["matched_modules"]),
            )
        )

    return normalize_results(results, modules, keep_3gpp_ran_aliases=keep_3gpp_ran_aliases)


def output_json(results: list[MatchResult], modules: list[YangModule], args: argparse.Namespace) -> None:
    payload = {
        "input": str(args.yang_library_json),
        "include_import_only": args.include_import_only,
        "min_confidence": args.min_confidence,
        "keep_3gpp_ran_aliases": args.keep_3gpp_ran_aliases,
        "oran_modules_detected": has_oran_modules(modules),
        "implemented_module_count": len([m for m in modules if not m.import_only]),
        "import_only_module_count": len([m for m in modules if m.import_only]),
        "detected_network_function_types": [asdict(r) for r in results],
    }
    print(json.dumps(payload, indent=2, sort_keys=False))


def output_table(results: list[MatchResult]) -> None:
    if not results:
        print("No network function types detected.")
        return

    rows = [
        (
            r.network_function_type,
            r.confidence,
            str(r.score),
            ", ".join(r.matched_modules),
        )
        for r in results
    ]
    headers = ("Network Function Type", "Confidence", "Score", "Matched Modules")
    widths = [len(h) for h in headers]
    for row in rows:
        widths = [max(widths[i], len(row[i])) for i in range(len(headers))]

    def fmt(row: Iterable[str]) -> str:
        values = list(row)
        return " | ".join(values[i].ljust(widths[i]) for i in range(len(values)))

    print(fmt(headers))
    print("-+-".join("-" * w for w in widths))
    for row in rows:
        print(fmt(row))


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Detect Network Function Types from an ietf-yang-library JSON file."
    )
    parser.add_argument("yang_library_json", type=Path, help="Path to the ietf-yang-library JSON file.")
    parser.add_argument(
        "--include-import-only",
        action="store_true",
        help="Also evaluate import-only-module entries. Default: false.",
    )
    parser.add_argument(
        "--min-confidence",
        choices=("weak", "medium", "strong"),
        default="weak",
        help="Minimum confidence level to output. Default: weak.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "table"),
        default="json",
        help="Output format. Default: json.",
    )
    parser.add_argument(
        "--list-modules",
        action="store_true",
        help="Print parsed modules and exit. Useful for debugging rules.",
    )
    parser.add_argument(
        "--keep-3gpp-ran-aliases",
        action="store_true",
        help="Keep gNB-DU/gNB-CU-* results even when O-RAN modules are detected. Default: false.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    data = load_json(args.yang_library_json)
    modules = parse_modules(data, include_import_only=args.include_import_only)

    if args.list_modules:
        for module in modules:
            marker = "import-only" if module.import_only else "implemented"
            print(f"{module.name}\t{module.revision or '-'}\t{marker}")
        return 0

    results = detect_network_function_types(
        modules,
        min_confidence=args.min_confidence,
        keep_3gpp_ran_aliases=args.keep_3gpp_ran_aliases,
    )

    if args.format == "table":
        output_table(results)
    else:
        output_json(results, modules, args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
