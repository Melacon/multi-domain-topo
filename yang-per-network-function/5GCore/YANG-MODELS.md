# 5GCore — YANG Models

The **5G Core (5GC)** implements the service-based architecture (SBA) defined by 3GPP TS 23.501,
comprising a suite of network functions (NFs) each responsible for a specific domain of control-plane
and user-plane processing. The 3GPP SA5 5GC NRM (TS 28.541) provides YANG models for all core NFs,
following the same `ManagedElement`-anchored O1 pattern as the RAN NRM. The `_3gpp-5gc-nrm-ep`
module is the pivotal hub: it imports all 17 5GC function modules so that all endpoint (N-interface)
objects are defined in a single module, which causes the full 5GC NRM to be transitively required.
O-RAN WG10 O1NRM overlays provide SMO integration for subscription control, EPE, and Near-RT RIC.

## YANG Tree Entry Points

| Module | Role |
|--------|------|
| `_3gpp-common-managed-element` | 🌳 **Root** — 3GPP `ManagedElement` list; top-level anchor for all 5GC NRM objects |
| `_3gpp-common-subnetwork` | 🌳 **Root** — 3GPP `SubNetwork` list; O1 topology grouping |
| `ietf-yang-schema-mount` | 🌳 **Root** — RFC 8528 schema mount declarations |

## O-RAN WG10 O1 NRM Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `o-ran-o1-managed-application` | 2025-07-02 | 📦 Groupings | Common O1 managed application groupings (vendor info, restart notifications) |
| `o-ran-o1-subscription-control` | 2025-07-02 | 📦 Groupings | O1 performance/alarm subscription control groupings |
| `o-ran-o1-subscription-control-me` | 2025-07-02 | 🔀 Augment | Augments `ManagedElement` with O1 subscription control instance |
| `o-ran-o1-subscription-control-subnetwork` | 2025-07-02 | 🔀 Augment | Augments `SubNetwork` with O1 subscription control |
| `o-ran-o1-EPE2` | 2024-07-11 | 🔀 Augment | Augments `ManagedElement` with Energy and Power Efficiency (EPE) O1 management objects |
| `o-ran-o1-NearRTRIC` | 2024-07-11 | 🔀 Augment | Augments `ManagedElement` with Near-RT RIC connectivity state for E2 interface management |

## 3GPP 5GC NRM Function Modules

Each NF module augments `ManagedElement` with an NF-specific managed object list.
All NF modules are transitively required because `_3gpp-5gc-nrm-ep` imports every
function module to model the corresponding N-interface endpoint objects.

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `_3gpp-5gc-nrm-amffunction` | 2025-11-06 | 🔀 Augment | `AMFFunction` — Access and Mobility Management Function: UE registration, mobility, and authentication management via N1/N2 interfaces |
| `_3gpp-5gc-nrm-smffunction` | 2025-11-06 | 🔀 Augment | `SMFFunction` — Session Management Function: PDU session establishment, IP allocation, N4 UPF selection |
| `_3gpp-5gc-nrm-upffunction` | 2025-11-06 | 🔀 Augment | `UPFFunction` — User Plane Function: data packet routing/forwarding on N3/N6/N9 interfaces |
| `_3gpp-5gc-nrm-ausffunction` | 2025-11-06 | 🔀 Augment | `AUSFFunction` — Authentication Server Function: UE authentication via Uu/5G-AKA/EAP-AKA' |
| `_3gpp-5gc-nrm-udmfunction` | 2025-11-06 | 🔀 Augment | `UDMFunction` — Unified Data Management: subscriber data repository, authentication credential generation |
| `_3gpp-5gc-nrm-udsffunction` | 2025-11-06 | 🔀 Augment | `UDSFFunction` — Unstructured Data Storage Function: stores NF-specific state as unstructured data |
| `_3gpp-5gc-nrm-nrffunction` | 2025-08-18 | 🔀 Augment | `NRFFunction` — NF Repository Function: NF registration, discovery, and heartbeat management |
| `_3gpp-5gc-nrm-nssffunction` | 2025-11-06 | 🔀 Augment | `NSSFFunction` — Network Slice Selection Function: NSSAI-based slice selection for UE sessions |
| `_3gpp-5gc-nrm-pcffunction` | 2025-11-06 | 🔀 Augment | `PCFFunction` — Policy Control Function: dynamic QoS and charging policy provisioning |
| `_3gpp-5gc-nrm-neffunction` | 2025-11-06 | 🔀 Augment | `NEFFunction` — Network Exposure Function: exposes 5GC capabilities to AF via northbound APIs |
| `_3gpp-5gc-nrm-affunction` | 2023-09-18 | 🔀 Augment | `AFFunction` — Application Function: 3GPP-trusted application influencing traffic routing or QoS |
| `_3gpp-5gc-nrm-dnfunction` | 2023-09-18 | 🔀 Augment | `DNFunction` — Data Network Function: represents an external data network connection point |
| `_3gpp-5gc-nrm-lmffunction` | 2025-11-06 | 🔀 Augment | `LMFFunction` — Location Management Function: UE positioning and location services |
| `_3gpp-5gc-nrm-n3iwffunction` | 2023-09-18 | 🔀 Augment | `N3IWFFunction` — Non-3GPP Interworking Function: connects untrusted non-3GPP access (Wi-Fi) to 5GC |
| `_3gpp-5gc-nrm-ngeirfunction` | 2025-11-06 | 🔀 Augment | `NGEIRFunction` — Next Generation Equipment Identity Register: device blacklist/whitelist enforcement |
| `_3gpp-5gc-nrm-seppfunction` | 2023-09-18 | 🔀 Augment | `SEPPFunction` — Security Edge Protection Proxy: inter-PLMN N32 interface security |
| `_3gpp-5gc-nrm-smsffunction` | 2025-11-06 | 🔀 Augment | `SMSFFunction` — SMS Function: SMS over NAS delivery for 5GC subscribers |

## 3GPP 5GC NRM Supporting Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `_3gpp-5gc-nrm-ep` | (not in folder) | 🔀 Augment | Hub module that imports all 17 NF modules and augments NRM objects with N1–N9 endpoint objects; drives the full 5GC NRM dependency closure |
| `_3gpp-5gc-nrm-nfprofile` | 2025-08-25 | 📦 Groupings | NF profile grouping (NF type, PLMN, capacity, FQDN) used by NRF and all NF modules |
| `_3gpp-5gc-nrm-managed-nfprofile` | 2025-11-06 | 📦 Groupings | Managed NF profile extending the base NF profile with O1 management attributes |
| `_3gpp-5gc-nrm-nfservice` | 2025-08-18 | 📦 Groupings | NF service instance grouping (service name, version, endpoints) |
| `_3gpp-5gc-nrm-configurable5qiset` | 2023-09-18 | 📦 Groupings | Configurable 5QI (5G QoS Identifier) set for operator-defined QoS profiles |
| `_3gpp-5gc-nrm-ecmconnectioninfo` | 2024-01-29 | 📦 Groupings | ECM (Error Correction Mapping) connection information groupings |

## 3GPP NR NRM Dependency Module

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `_3gpp-nr-nrm-gnbcuupfunction` | 2024-05-24 | 🔀 Augment | Transitive dependency: `AMFFunction` directly imports `GNBCUUPFunction` for modeling UE session handover tracking between AMF and the CU-UP |
| `_3gpp-nr-nrm-ecmappingrule` | 2025-05-06 | 📦 Groupings | ECM rule groupings |

## 3GPP Common Framework Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `_3gpp-common-managed-element` | 2025-03-24 | 🌳 **Root** | 3GPP TS 28.623 — `ManagedElement` list; top-level O1 NRM anchor |
| `_3gpp-common-subnetwork` | 2025-03-24 | 🌳 **Root** | 3GPP TS 28.623 — `SubNetwork` list; logical NE grouping |
| `_3gpp-common-managed-function` | 2025-08-06 | 📦 Groupings | Base grouping for all 3GPP managed NF objects |
| `_3gpp-common-top` | 2023-09-18 | 📦 Groupings | Top-level list key (`id`) grouping |
| `_3gpp-common-ep-rp` | 2023-09-18 | 📦 Groupings | Endpoint and reference point base groupings |
| `_3gpp-common-fm` | 2026-01-24 | 📦 Groupings | Fault management alarm groupings |
| `_3gpp-common-trace` | 2025-08-06 | 📦 Groupings | 3GPP trace configuration groupings |
| `_3gpp-common-measurements` | 2025-08-06 | 📦 Groupings | PM measurement configuration groupings |
| `_3gpp-common-subscription-control` | 2025-11-06 | 📦 Groupings | O1 event subscription control groupings |
| `_3gpp-common-files` | 2025-07-01 | 📦 Groupings | File management groupings |
| `_3gpp-common-yang-types` | 2025-11-06 | 📦 Types | 3GPP common YANG types (Dnprefix, Mcc, Mnc) |
| `_3gpp-common-yang-extensions` | 2025-02-06 | 📦 Types | 3GPP YANG extension statements |
| `_3gpp-5g-common-yang-types` | 2025-08-18 | 📦 Types | 5G-specific YANG types (SNSSAI, PLMN-ID, NSSAI, DNN) |

## IETF Base Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-yang-schema-mount` | 2019-01-14 | 🌳 Root | RFC 8528 — `schema-mounts` container |
| `ietf-inet-types` | 2025-12-22 | 📦 Types | RFC 6991 — IP address and FQDN types |
| `ietf-yang-types` | 2025-12-22 | 📦 Types | RFC 6991 — base YANG types |

## YANG Tree Generation

Run from the project root:

```bash
./generate-yang-tree.sh yang-per-network-function/5GCore
```

Output is written to `yang-tree.txt` in this folder. The tree starts at three entry points:
`ManagedElement` (all 17 5GC NF objects folded in as child lists), `SubNetwork`, and
`schema-mounts`. The WG10 O1NRM augmentations are automatically folded into the tree by pyang
when all modules are loaded together.
