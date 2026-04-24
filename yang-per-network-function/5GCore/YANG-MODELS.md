# 5GCore — YANG Models

The **5G Core (5GC)** implements the service-based architecture (SBA) defined by 3GPP TS 23.501.
All 5GC NF managed objects follow the 3GPP SA5 NRM pattern: NF-specific objects (e.g.
`AMFFunction`, `SMFFunction`) augment the common `ManagedElement` list defined in
`_3gpp-common-managed-element`. O-RAN does not define extensions or augmentations for 5GC NFs;
the management model is purely 3GPP SA5 scope.

## Structure

```
5GCore/
├── yang-models/    ← canonical flat folder: 41 YANG symlinks (all 5GC modules)
├── AMF  →  yang-models/
├── SMF  →  yang-models/
├── UPF  →  yang-models/
└── ...  (17 NF directory symlinks total)
```

`yang-models/` contains the complete 5GC NRM module set including `_3gpp-5gc-nrm-ep` (the hub
module that defines all N-interface endpoints) and its dependencies. Each NF-named entry is a
directory symlink to `yang-models/` — all NFs share the same YANG module set because the 3GPP
5GC NRM is a single interconnected model.

For **sysrepo/netopeer2** deployment: point the YANG search path at `yang-models/` and install
only the NF-specific function module (e.g. `_3gpp-5gc-nrm-amffunction`); sysrepo resolves all
transitive dependencies from the search path automatically.

## NF Directory Symlinks

| NF | Symlink | 3GPP Function |
|----|---------|---------------|
| AMF | `AMF → yang-models/` | Access and Mobility Management |
| SMF | `SMF → yang-models/` | Session Management |
| UPF | `UPF → yang-models/` | User Plane Function |
| AUSF | `AUSF → yang-models/` | Authentication Server |
| UDM | `UDM → yang-models/` | Unified Data Management |
| UDSF | `UDSF → yang-models/` | Unstructured Data Storage |
| NRF | `NRF → yang-models/` | NF Repository |
| NSSF | `NSSF → yang-models/` | Network Slice Selection |
| PCF | `PCF → yang-models/` | Policy Control |
| NEF | `NEF → yang-models/` | Network Exposure |
| AF | `AF → yang-models/` | Application Function |
| DN | `DN → yang-models/` | Data Network |
| LMF | `LMF → yang-models/` | Location Management |
| N3IWF | `N3IWF → yang-models/` | Non-3GPP Interworking |
| NGEIR | `NGEIR → yang-models/` | Equipment Identity Register |
| SEPP | `SEPP → yang-models/` | Security Edge Protection Proxy |
| SMSF | `SMSF → yang-models/` | SMS Function |

## YANG Tree Entry Points

| Module | Role |
|--------|------|
| `_3gpp-common-managed-element` | 🌳 **Root** — `ManagedElement` list; all 17 NF objects augment it |
| `_3gpp-common-subnetwork` | 🌳 **Root** — `SubNetwork` list; O1 topology grouping |
| `ietf-yang-schema-mount` | 🌳 **Root** — RFC 8528 schema mount declarations |

## Validation and Tree Generation

```bash
# Validate and generate tree via yang-models/ directly
./validate-yang.sh yang-per-network-function/5GCore/yang-models
./generate-yang-tree.sh yang-per-network-function/5GCore/yang-models

# Or via any NF symlink (resolves to yang-models/ via realpath)
./validate-yang.sh yang-per-network-function/5GCore/AMF
```

## Module Set (41 modules — 3GPP only, no O-RAN WG10)

### 5GC NRM Function Modules (17)

| Module | Revision | Description |
|--------|----------|-------------|
| `_3gpp-5gc-nrm-amffunction` | 2025-11-06 | `AMFFunction` — UE registration, mobility, authentication (N1/N2) |
| `_3gpp-5gc-nrm-smffunction` | 2025-11-06 | `SMFFunction` — PDU session, IP allocation, UPF selection (N4/N11) |
| `_3gpp-5gc-nrm-upffunction` | 2025-11-06 | `UPFFunction` — User-plane forwarding (N3/N6/N9) |
| `_3gpp-5gc-nrm-ausffunction` | 2025-11-06 | `AUSFFunction` — UE authentication (5G-AKA/EAP-AKA') |
| `_3gpp-5gc-nrm-udmfunction` | 2025-11-06 | `UDMFunction` — Subscriber data management |
| `_3gpp-5gc-nrm-udsffunction` | 2025-11-06 | `UDSFFunction` — Unstructured NF state storage |
| `_3gpp-5gc-nrm-nrffunction` | 2025-08-18 | `NRFFunction` — NF registration and discovery |
| `_3gpp-5gc-nrm-nssffunction` | 2025-11-06 | `NSSFFunction` — Network slice selection |
| `_3gpp-5gc-nrm-pcffunction` | 2025-11-06 | `PCFFunction` — QoS and charging policy (N7/N15) |
| `_3gpp-5gc-nrm-neffunction` | 2025-11-06 | `NEFFunction` — Network capability exposure |
| `_3gpp-5gc-nrm-affunction` | 2023-09-18 | `AFFunction` — Trusted application function |
| `_3gpp-5gc-nrm-dnfunction` | 2023-09-18 | `DNFunction` — External data network point |
| `_3gpp-5gc-nrm-lmffunction` | 2025-11-06 | `LMFFunction` — UE location/positioning |
| `_3gpp-5gc-nrm-n3iwffunction` | 2023-09-18 | `N3IWFFunction` — Non-3GPP access interworking |
| `_3gpp-5gc-nrm-ngeirfunction` | 2025-11-06 | `NGEIRFunction` — Device identity register |
| `_3gpp-5gc-nrm-seppfunction` | 2023-09-18 | `SEPPFunction` — Inter-PLMN security proxy (N32) |
| `_3gpp-5gc-nrm-smsffunction` | 2025-11-06 | `SMSFFunction` — SMS over NAS |

### 5GC NRM Supporting Modules (6)

| Module | Revision | Description |
|--------|----------|-------------|
| `_3gpp-5gc-nrm-ep` | 2023-09-18 | Hub module: imports all 17 NF modules; defines all N-interface endpoint objects |
| `_3gpp-5gc-nrm-configurable5qiset` | 2023-09-18 | Configurable 5QI set (operator-defined QoS profiles) |
| `_3gpp-5gc-nrm-ecmconnectioninfo` | 2024-01-29 | ECM connection information groupings |
| `_3gpp-5gc-nrm-nfservice` | 2025-08-18 | NF service instance (name, version, endpoints) |
| `_3gpp-5gc-nrm-nfprofile` | 2025-08-25 | NF profile (type, PLMN, capacity, FQDN) |
| `_3gpp-5gc-nrm-managed-nfprofile` | 2025-11-06 | Managed NF profile with O1 management attributes |

### 3GPP Common Framework (15)

| Module | Revision | Description |
|--------|----------|-------------|
| `_3gpp-common-managed-element` | 2025-03-24 | 🌳 `ManagedElement` list |
| `_3gpp-common-subnetwork` | 2025-03-24 | 🌳 `SubNetwork` list |
| `_3gpp-common-managed-function` | 2025-08-06 | Base NF object grouping |
| `_3gpp-common-top` | 2023-09-18 | List key (`id`) grouping |
| `_3gpp-common-ep-rp` | 2023-09-18 | Endpoint/reference-point base |
| `_3gpp-common-fm` | 2026-01-24 | Fault management groupings |
| `_3gpp-common-trace` | 2025-08-06 | Trace configuration |
| `_3gpp-common-measurements` | 2025-08-06 | PM measurement configuration |
| `_3gpp-common-subscription-control` | 2025-11-06 | O1 event subscription control |
| `_3gpp-common-files` | 2025-07-01 | File management groupings |
| `_3gpp-common-yang-types` | 2025-11-06 | 3GPP common types (Mcc, Mnc, CellIdentity) |
| `_3gpp-common-yang-extensions` | 2025-02-06 | 3GPP YANG extension statements |
| `_3gpp-5g-common-yang-types` | 2025-08-18 | 5G types (SNSSAI, PLMN-ID, NSSAI, DNN) |
| `_3gpp-nr-nrm-gnbcuupfunction` | 2024-05-24 | Transitive dep: AMF imports GNBCUUPFunction |
| `_3gpp-nr-nrm-ecmappingrule` | 2025-05-06 | ECM rule groupings |

### IETF Base (3)

| Module | Revision | Description |
|--------|----------|-------------|
| `ietf-yang-schema-mount` | 2019-01-14 | 🌳 RFC 8528 schema mount |
| `ietf-inet-types` | 2025-12-22 | RFC 6991 IP address / FQDN types |
| `ietf-yang-types` | 2025-12-22 | RFC 6991 base YANG types |
