# 5GCore — YANG Models

The **5G Core (5GC)** implements the service-based architecture (SBA) defined by 3GPP TS 23.501.
Each NF is modeled as a disaggregated, containerized unit with its own independent YANG module set.
The 3GPP SA5 5GC NRM (TS 28.541) anchors all NF managed objects beneath a common `ManagedElement`
list; O-RAN WG10 O1NRM overlays add SMO subscription control, EPE, and Near-RT RIC management.

> **Note on `_3gpp-5gc-nrm-ep`:** This hub module imports all 17 NF function modules to define
> N-interface endpoint objects. Including it in any per-NF folder would drag in all other NFs,
> defeating disaggregation. It is intentionally absent from the subfolders below.

## NF Subfolders

Each subfolder is self-contained: YANG symlinks, `validation.log`, `yang-tree.txt`, and
`YANG-MODELS.md`. All 17 pass pyang structural, pyang --lint, and yanglint validation.

| NF | Folder | Function | Modules | Tree lines |
|----|--------|----------|---------|------------|
| AMF | [AMF/](AMF/YANG-MODELS.md) | Access and Mobility Management | 28 | ~1,800 |
| SMF | [SMF/](SMF/YANG-MODELS.md) | Session Management | 27 | ~1,320 |
| UPF | [UPF/](UPF/YANG-MODELS.md) | User Plane Function | 27 | ~1,310 |
| AUSF | [AUSF/](AUSF/YANG-MODELS.md) | Authentication Server | 27 | ~1,330 |
| UDM | [UDM/](UDM/YANG-MODELS.md) | Unified Data Management | 27 | ~1,320 |
| UDSF | [UDSF/](UDSF/YANG-MODELS.md) | Unstructured Data Storage | 27 | ~1,310 |
| NRF | [NRF/](NRF/YANG-MODELS.md) | NF Repository | 26 | ~1,510 |
| NSSF | [NSSF/](NSSF/YANG-MODELS.md) | Network Slice Selection | 27 | ~1,310 |
| PCF | [PCF/](PCF/YANG-MODELS.md) | Policy Control | 27 | ~1,320 |
| NEF | [NEF/](NEF/YANG-MODELS.md) | Network Exposure | 27 | ~1,360 |
| AF | [AF/](AF/YANG-MODELS.md) | Application Function | 24 | ~1,260 |
| DN | [DN/](DN/YANG-MODELS.md) | Data Network | 24 | ~1,260 |
| LMF | [LMF/](LMF/YANG-MODELS.md) | Location Management | 27 | ~1,310 |
| N3IWF | [N3IWF/](N3IWF/YANG-MODELS.md) | Non-3GPP Interworking | 24 | ~1,270 |
| NGEIR | [NGEIR/](NGEIR/YANG-MODELS.md) | Equipment Identity Register | 27 | ~1,310 |
| SEPP | [SEPP/](SEPP/YANG-MODELS.md) | Security Edge Protection Proxy | 24 | ~1,280 |
| SMSF | [SMSF/](SMSF/YANG-MODELS.md) | SMS Function | 27 | ~1,310 |

## Common Module Set

All 17 NF subfolders share the same 23-module base (14 × 3GPP common + 6 × O-RAN WG10 O1NRM
+ 3 × IETF). NF-specific additions are documented in each subfolder's `YANG-MODELS.md`.

### 3GPP Common Framework

| Module | Revision | Description |
|--------|----------|-------------|
| `_3gpp-common-managed-element` | 2025-03-24 | `ManagedElement` list — top-level O1 NRM anchor |
| `_3gpp-common-subnetwork` | 2025-03-24 | `SubNetwork` list — logical NE grouping |
| `_3gpp-common-managed-function` | 2025-08-06 | Base grouping for all 3GPP managed NF objects |
| `_3gpp-common-top` | 2023-09-18 | Top-level list key (`id`) grouping |
| `_3gpp-common-ep-rp` | 2023-09-18 | Endpoint and reference point base groupings |
| `_3gpp-common-fm` | 2026-01-24 | Fault management alarm groupings |
| `_3gpp-common-trace` | 2025-08-06 | 3GPP trace configuration groupings |
| `_3gpp-common-measurements` | 2025-08-06 | PM measurement configuration groupings |
| `_3gpp-common-subscription-control` | 2025-11-06 | O1 event subscription control groupings |
| `_3gpp-common-files` | 2025-07-01 | File management groupings |
| `_3gpp-common-yang-types` | 2025-11-06 | 3GPP common YANG types (Mcc, Mnc, CellIdentity) |
| `_3gpp-common-yang-extensions` | 2025-02-06 | 3GPP YANG extension statements |
| `_3gpp-5g-common-yang-types` | 2025-08-18 | 5G types (SNSSAI, PLMN-ID, NSSAI, DNN) |
| `_3gpp-nr-nrm-ecmappingrule` | 2025-05-06 | ECM rule groupings |

### O-RAN WG10 O1 NRM

| Module | Revision | Description |
|--------|----------|-------------|
| `o-ran-o1-managed-application` | 2025-07-02 | Common O1 managed application groupings |
| `o-ran-o1-subscription-control` | 2025-07-02 | O1 subscription control groupings |
| `o-ran-o1-subscription-control-me` | 2025-07-02 | Augments `ManagedElement` with O1 subscription control |
| `o-ran-o1-subscription-control-subnetwork` | 2025-07-02 | Augments `SubNetwork` with O1 subscription control |
| `o-ran-o1-EPE2` | 2024-07-11 | Augments `ManagedElement` with Energy and Power Efficiency objects |
| `o-ran-o1-NearRTRIC` | 2024-07-11 | Augments `ManagedElement` with Near-RT RIC E2 connectivity state |

### IETF Base

| Module | Revision | Description |
|--------|----------|-------------|
| `ietf-yang-schema-mount` | 2019-01-14 | RFC 8528 — `schema-mounts` container |
| `ietf-inet-types` | 2025-12-22 | RFC 6991 — IP address and FQDN types |
| `ietf-yang-types` | 2025-12-22 | RFC 6991 — base YANG types |
