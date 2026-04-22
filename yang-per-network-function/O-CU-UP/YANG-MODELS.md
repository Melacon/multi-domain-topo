# O-CU-UP — YANG Models

The **O-RAN Central Unit User Plane (O-CU-UP)** implements the PDCP-U and SDAP protocols
for the user-plane data path. It connects to the O-CU-CP via the E1 interface, to O-DUs via
F1-U, and to the UPF via the N3 interface. Its O1 management interface aligns with the 3GPP
SA5 NR NRM: the `GNBCUUPFunction` object is the primary managed function, hanging beneath a
`ManagedElement`. Unlike the O-CU-CP, there are no O-RAN WG5 functional augmentation modules
specific to the UP; the O-CU-UP NRM objects are defined entirely by 3GPP with WG10 O1 NRM
overlays for SMO integration. The 3GPP NRM module `_3gpp-common-managed-element` is the
YANG tree entry point.

## YANG Tree Entry Points

| Module | Role |
|--------|------|
| `_3gpp-common-managed-element` | 🌳 **Root** — 3GPP `ManagedElement` list; top-level O1 anchor for all NRM objects including `GNBCUUPFunction` |
| `_3gpp-common-subnetwork` | 🌳 **Root** — 3GPP `SubNetwork` list; O1 topology grouping |
| `ietf-yang-schema-mount` | 🌳 **Root** — RFC 8528 schema mount declarations |

## O-RAN WG10 O1 NRM Modules

These modules augment the 3GPP NRM subtree with O1 management objects for the SMO interface.

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `o-ran-o1-managed-application` | 2025-07-02 | 📦 Groupings | Common O1 managed application groupings (vendor info, restart notifications) |
| `o-ran-o1-subscription-control` | 2025-07-02 | 📦 Groupings | O1 performance/alarm subscription control groupings |
| `o-ran-o1-subscription-control-me` | 2025-07-02 | 🔀 Augment | Augments `ManagedElement` with O1 subscription control instance |
| `o-ran-o1-subscription-control-subnetwork` | 2025-07-02 | 🔀 Augment | Augments `SubNetwork` with O1 subscription control |
| `o-ran-o1-EPE2` | 2024-07-11 | 🔀 Augment | Augments `ManagedElement` with Energy and Power Efficiency (EPE) O1 management objects |
| `o-ran-o1-NearRTRIC` | 2024-07-11 | 🔀 Augment | Augments `ManagedElement` with Near-RT RIC connectivity state for E2 interface management |

## 3GPP NR NRM Modules

### NRM Root Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `_3gpp-common-managed-element` | 2025-03-24 | 🌳 **Root** | 3GPP TS 28.623 — `ManagedElement` list; top-level O1 NRM anchor |
| `_3gpp-common-subnetwork` | 2025-03-24 | 🌳 **Root** | 3GPP TS 28.623 — `SubNetwork` list; logical NE grouping |

### 3GPP NR NRM CU-UP Augmentation Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `_3gpp-nr-nrm-gnbcuupfunction` | 2024-05-24 | 🔀 Augment | Augments `ManagedElement` with `GNBCUUPFunction` list: CU-UP identity, PLMN, E1 and N3 endpoints, served SNSSAI list |
| `_3gpp-nr-nrm-gnbcucpfunction` | 2024-08-12 | 🔀 Augment | Augments `ManagedElement` with `GNBCUCPFunction` (transitive dep via ep/rrmpolicy modules) |
| `_3gpp-nr-nrm-gnbdufunction` | 2024-02-24 | 🔀 Augment | Augments `ManagedElement` with `GNBDUFunction` (transitive dep via rrmpolicy) |
| `_3gpp-nr-nrm-nrcellcu` | 2023-09-18 | 🔀 Augment | Augments `GNBCUCPFunction` with `NRCellCU` list (transitive dep) |
| `_3gpp-nr-nrm-nrcelldu` | 2024-05-24 | 🔀 Augment | Augments `GNBDUFunction` with `NRCellDU` list (transitive dep) |
| `_3gpp-nr-nrm-rrmpolicy` | 2023-09-18 | 🔀 Augment | Augments multiple NRM objects with `RRMPolicy` for radio resource allocation |
| `_3gpp-nr-nrm-ep` | 2025-05-06 | 🔀 Augment | Augments NRM objects with E1, F1, Xn, X2 endpoint objects |
| `_3gpp-nr-nrm-externalgnbcuupfunction` | 2025-04-25 | 🔀 Augment | Augments `SubNetwork` with external gNB-CU-UP references |
| `_3gpp-nr-nrm-nrnetwork` | 2025-04-25 | 🔀 Augment | Augments `SubNetwork` with NR network topology |
| `_3gpp-nr-nrm-ecmappingrule` | 2025-05-06 | 📦 Groupings | ECM rule groupings used by ep module |

### 3GPP Common Framework Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `_3gpp-common-managed-function` | 2025-08-06 | 📦 Groupings | Base grouping for all 3GPP managed NF objects |
| `_3gpp-common-top` | 2023-09-18 | 📦 Groupings | Top-level list key (`id`) grouping |
| `_3gpp-common-ep-rp` | 2023-09-18 | 📦 Groupings | Endpoint and reference point base groupings |
| `_3gpp-common-fm` | 2026-01-24 | 📦 Groupings | Fault management alarm groupings |
| `_3gpp-common-trace` | 2025-08-06 | 📦 Groupings | 3GPP trace configuration groupings |
| `_3gpp-common-measurements` | 2025-08-06 | 📦 Groupings | PM measurement configuration groupings |
| `_3gpp-common-subscription-control` | 2025-11-06 | 📦 Groupings | O1 event subscription control groupings |
| `_3gpp-common-files` | 2025-07-01 | 📦 Groupings | File management groupings |
| `_3gpp-common-yang-types` | 2025-11-06 | 📦 Types | 3GPP common YANG types (Dnprefix, Mcc, Mnc, CellIdentity) |
| `_3gpp-common-yang-extensions` | 2025-02-06 | 📦 Types | 3GPP YANG extension statements |
| `_3gpp-5g-common-yang-types` | 2025-08-18 | 📦 Types | 5G-specific YANG types (SNSSAI, PLMN-ID, NSSAI) |
| `_3gpp-5gc-nrm-configurable5qiset` | 2023-09-18 | 📦 Groupings | Configurable 5QI set groupings |
| `_3gpp-5gc-nrm-ecmconnectioninfo` | 2024-01-29 | 📦 Groupings | ECM connection info groupings |

## IETF Base Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-yang-schema-mount` | 2019-01-14 | 🌳 Root | RFC 8528 — `schema-mounts` container; schema mount point declarations |
| `ietf-inet-types` | 2025-12-22 | 📦 Types | RFC 6991 — IP address and prefix types |
| `ietf-yang-types` | 2025-12-22 | 📦 Types | RFC 6991 — base YANG types |

## YANG Tree Generation

Run from the project root:

```bash
./generate-yang-tree.sh yang-per-network-function/O-CU-UP
```

Output is written to `yang-tree.txt` in this folder. The tree starts at three entry points:
`ManagedElement` (with `GNBCUUPFunction` and all augmentations folded in), `SubNetwork`,
and `schema-mounts`. The absence of WG5 CU-UP-specific augmentation modules reflects the
fact that O-CU-UP management is fully expressed through the 3GPP NRM `GNBCUUPFunction` object.
