# 5GCore / DN — YANG Models

Augments `ManagedElement` with `DNFunction`: represents an external data network (internet, operator services) reachable via the UPF N6 interface

This folder models a **disaggregated, containerized DN deployment**: only the DN managed
object and its direct dependencies are present. The combined view of all 5GC NFs (including
the `_3gpp-5gc-nrm-ep` hub that links all NF endpoints) is in the parent
[`5GCore/`](../YANG-MODELS.md) folder.

## YANG Tree Entry Points

| Module | Role |
|--------|------|
| `_3gpp-common-managed-element` | 🌳 **Root** — `ManagedElement` list; `DN`-specific objects hang beneath it |
| `_3gpp-common-subnetwork` | 🌳 **Root** — `SubNetwork` list; O1 topology grouping |
| `ietf-yang-schema-mount` | 🌳 **Root** — RFC 8528 schema mount declarations |

## 3GPP DN Function Module

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `_3gpp-5gc-nrm-dnfunction` | 2023-09-18 | 🔀 Augment | Augments `ManagedElement` with `DNFunction`: represents an external data network (internet, operator services) reachable via the UPF N6 interface |

## 3GPP Common Framework Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `_3gpp-common-managed-element` | 2025-03-24 | 🌳 **Root** | `ManagedElement` list — top-level O1 NRM anchor |
| `_3gpp-common-subnetwork` | 2025-03-24 | 🌳 **Root** | `SubNetwork` list — logical NE grouping |
| `_3gpp-common-managed-function` | 2025-08-06 | 📦 Groupings | Base grouping for all 3GPP managed NF objects |
| `_3gpp-common-top` | 2023-09-18 | 📦 Groupings | Top-level list key (`id`) grouping |
| `_3gpp-common-ep-rp` | 2023-09-18 | 📦 Groupings | Endpoint and reference point base groupings |
| `_3gpp-common-fm` | 2026-01-24 | 📦 Groupings | Fault management alarm groupings |
| `_3gpp-common-trace` | 2025-08-06 | 📦 Groupings | 3GPP trace configuration groupings |
| `_3gpp-common-measurements` | 2025-08-06 | 📦 Groupings | PM measurement configuration groupings |
| `_3gpp-common-subscription-control` | 2025-11-06 | 📦 Groupings | O1 event subscription control groupings |
| `_3gpp-common-files` | 2025-07-01 | 📦 Groupings | File management groupings |
| `_3gpp-common-yang-types` | 2025-11-06 | 📦 Types | 3GPP common YANG types (Mcc, Mnc, CellIdentity) |
| `_3gpp-common-yang-extensions` | 2025-02-06 | 📦 Types | 3GPP YANG extension statements |
| `_3gpp-5g-common-yang-types` | 2025-08-18 | 📦 Types | 5G types (SNSSAI, PLMN-ID, NSSAI, DNN) |
| `_3gpp-nr-nrm-ecmappingrule` | 2025-05-06 | 📦 Groupings | ECM rule groupings |

## O-RAN WG10 O1 NRM Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `o-ran-o1-managed-application` | 2025-07-02 | 📦 Groupings | Common O1 managed application groupings |
| `o-ran-o1-subscription-control` | 2025-07-02 | 📦 Groupings | O1 subscription control groupings |
| `o-ran-o1-subscription-control-me` | 2025-07-02 | 🔀 Augment | Augments `ManagedElement` with O1 subscription control |
| `o-ran-o1-subscription-control-subnetwork` | 2025-07-02 | 🔀 Augment | Augments `SubNetwork` with O1 subscription control |
| `o-ran-o1-EPE2` | 2024-07-11 | 🔀 Augment | Augments `ManagedElement` with Energy and Power Efficiency objects |
| `o-ran-o1-NearRTRIC` | 2024-07-11 | 🔀 Augment | Augments `ManagedElement` with Near-RT RIC E2 connectivity state |

## IETF Base Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-yang-schema-mount` | 2019-01-14 | 🌳 Root | RFC 8528 — `schema-mounts` container |
| `ietf-inet-types` | 2025-12-22 | 📦 Types | RFC 6991 — IP address and FQDN types |
| `ietf-yang-types` | 2025-12-22 | 📦 Types | RFC 6991 — base YANG types |

## YANG Tree Generation

```bash
./generate-yang-tree.sh yang-per-network-function/5GCore/DN
```

Output written to `yang-tree.txt`. The tree starts at `ManagedElement` with `DNFunction`
folded in, `SubNetwork`, and `schema-mounts`.
