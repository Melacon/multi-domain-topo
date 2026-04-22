# O-DU — YANG Models

The **O-RAN Distributed Unit (O-DU)** implements the lower layers of the RAN protocol stack
(RLC, MAC, low-PHY) and manages the Open Fronthaul toward one or more O-RUs. Its O1 management
interface is defined by O-RAN WG5 and covers three areas: (1) direct O-DU management (scheduling,
QoS, synchronization, F1 transport), (2) aggregated M-Plane control of O-RUs proxied through the
O-DU, and (3) O1 NRM integration with the 3GPP SA5 NR Network Resource Model (NRM) for alignment
with the SMO/Non-RT RIC. The 3GPP NRM modules `_3gpp-common-managed-element` and
`_3gpp-common-subnetwork` are the primary YANG tree entry points; the O-RAN WG5 extension modules
`o-ran_3gpp-nr-nrm-gnbdufunction` and `o-ran_3gpp-nr-nrm-nrcelldu` further enrich the gNB-DU and
NR-Cell-DU objects with O-RAN-specific attributes.

## YANG Tree Entry Points

| Module | Role |
|--------|------|
| `_3gpp-common-managed-element` | 🌳 **Root** — 3GPP `ManagedElement` list; top-level anchor for all NRM objects |
| `_3gpp-common-subnetwork` | 🌳 **Root** — 3GPP `SubNetwork` list; O1 topology grouping |
| `o-ran_3gpp-nr-nrm-gnbdufunction` | 🌳 **Root** — O-RAN WG5 extension of `GNBDUFunction`; defines O-RAN-specific DU attributes |
| `o-ran_3gpp-nr-nrm-nrcelldu` | 🌳 **Root** — O-RAN WG5 extension of `NRCellDU`; defines O-RAN cell-level radio parameters |
| `o-ran-aggregation-base` | 🌳 **Root** — WG5 aggregated M-Plane anchor; mount point for proxied O-RU YANG modules |
| `o-ran-wg5-delay-management` | 🌳 **Root** — O-DU fronthaul transport delay configuration |
| `o-ran-synchronization` | 🌳 **Root** — O-DU synchronization state and configuration |
| `o-ran-dhcp` | 🌳 **Root** — DHCP client for management addressing |
| `o-ran-operations` | 🌳 **Root** — O-DU operational state and restart information |
| `o-ran-usermgmt` | 🌳 **Root** — Local user account management |
| `ietf-hardware` | 🌳 **Root** | RFC 8348 — hardware component inventory |
| `ietf-interfaces` | 🌳 **Root** | RFC 8343 — interface model |
| `ietf-netconf-acm` | 🌳 **Root** | RFC 8341 — NETCONF access control |
| `ietf-yang-schema-mount` | 🌳 **Root** | RFC 8528 — schema mount point declarations |

## O-RAN WG5 O-DU Core Functional Modules

### Aggregated M-Plane Anchor

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `o-ran-aggregation-base` | 2020-09-25 | 🌳 Root | Defines the aggregated M-Plane mount point through which the O-DU proxies NETCONF management of its connected O-RUs; each O-RU appears as a schema-mount instance |

### O-DU Radio and Transport Configuration

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `o-ran-wg5-delay-management` | 2020-09-25 | 🌳 Root | Fronthaul transport delay configuration on the O-DU side: T12/T34 budgets, transport delay profiles matching O-RU WG4 delay-management |
| `o-ran-c-plane-tnl` | 2020-09-25 | 📦 Groupings | C-Plane (control plane) fronthaul tunnel type definitions and groupings |
| `o-ran-u-plane-tnl` | 2020-09-25 | 📦 Groupings | U-Plane (user plane) fronthaul tunnel type definitions and groupings |
| `o-ran-du-f1-tnl` | 2020-09-25 | 🔀 Augment | Augments the gNB-DU NRM object with F1 interface transport tunnel endpoint configuration |
| `o-ran-qos` | 2020-09-25 | 🔀 Augment | Augments `GNBDUFunction` with QoS policy configuration (DSCP/PCP marking, scheduling weights) |
| `o-ran-rlc` | 2020-09-25 | 🔀 Augment | Augments `NRCellDU` with RLC (Radio Link Control) timer and configuration parameters |
| `o-ran-nr-u` | 2020-09-25 | 🔀 Augment | Augments `NRCellDU` with NR-U (NR over Unlicensed spectrum) channel access configuration |

### O-DU Performance and Shared Resources

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `o-ran-du-performance-management` | 2020-09-25 | 🔀 Augment | Augments `GNBDUFunction` with O-DU-specific PM measurement job and counter definitions |
| `o-ran-o-du-shared-o-ru` | 2023-03-17 | 🔀 Augment | Augments `GNBDUFunction` with shared O-RU configuration: defines which O-RUs are shared among multiple O-DUs |

### O-DU System Management

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `o-ran-synchronization` | 2020-09-25 | 🌳 Root | O-DU synchronization: PTP grandmaster clock tracking, SyncE, air-interface timing state |
| `o-ran-dhcp` | 2020-09-25 | 🌳 Root | DHCP client configuration for O-DU management-plane IP addressing |
| `o-ran-operations` | 2025-12-22 | 🌳 Root | Operational state: restart cause, re-call-home timer, load status |
| `o-ran-usermgmt` | 2024-08-12 | 🌳 Root | Local user accounts, password policy, and SUDO rules for NETCONF access |
| `o-ran-hardware` | 2025-04-14 | 🔀 Augment | Augments `ietf-hardware` with O-RAN hardware labels, product codes, and O-DU-specific component labels |
| `o-ran-interfaces` | 2025-12-22 | 🔀 Augment | Augments `ietf-interfaces` with O-RAN fronthaul port VLAN, MAC-learning, and M-Plane bindings |

## O-RAN WG5 Aggregated M-Plane Modules

These modules proxy the O-RAN WG4 M-Plane interface from the O-DU toward managed O-RUs.
Each `o-ran-agg-*` module augments the corresponding WG4 module within the schema-mount
instance defined by `o-ran-aggregation-base`, adding O-DU-aggregation-specific attributes
or context. pyang folds them into the aggregated subtree automatically.

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `o-ran-agg-ald-port` | 2020-09-25 | 🔀 Augment | Proxied ALD (Antenna Line Device) port management |
| `o-ran-agg-ald` | 2020-09-25 | 🔀 Augment | Proxied ALD device communication RPCs |
| `o-ran-agg-antenna-calibration` | 2020-09-25 | 🔀 Augment | Proxied antenna calibration procedure control |
| `o-ran-agg-beamforming` | 2020-09-25 | 🔀 Augment | Proxied beamforming weight configuration |
| `o-ran-agg-dhcp` | 2020-09-25 | 🔀 Augment | Proxied O-RU DHCP state readback |
| `o-ran-agg-ecpri-delay` | 2020-09-25 | 🔀 Augment | Proxied eCPRI one-way delay measurement |
| `o-ran-agg-ethernet-forwarding` | 2020-09-25 | 🔀 Augment | Proxied O-RU Ethernet bridge configuration |
| `o-ran-agg-externalio` | 2020-09-25 | 🔀 Augment | Proxied O-RU external GPIO management |
| `o-ran-agg-fan` | 2020-09-25 | 🔀 Augment | Proxied O-RU fan tray state |
| `o-ran-agg-hardware` | 2020-09-25 | 🔀 Augment | Proxied O-RAN hardware inventory extensions |
| `o-ran-agg-ietf-hardware` | 2020-09-25 | 🔀 Augment | Proxied `ietf-hardware` component tree readback |
| `o-ran-agg-ietf-interfaces` | 2020-09-25 | 🔀 Augment | Proxied `ietf-interfaces` interface list |
| `o-ran-agg-ietf-ip` | 2020-09-25 | 🔀 Augment | Proxied IPv4/IPv6 address configuration |
| `o-ran-agg-ietf-netconf-acm` | 2020-09-25 | 🔀 Augment | Proxied NETCONF access control (NACM) |
| `o-ran-agg-interfaces` | 2020-09-25 | 🔀 Augment | Proxied O-RAN interface attributes |
| `o-ran-agg-laa` | 2020-09-25 | 🔀 Augment | Proxied LAA (Licensed Assisted Access) configuration |
| `o-ran-agg-laa-operations` | 2020-09-25 | 🔀 Augment | Proxied LAA channel access procedures |
| `o-ran-agg-lbm` | 2020-09-25 | 🔀 Augment | Proxied Loopback Measurement domain data |
| `o-ran-agg-module-cap` | 2020-09-25 | 🔀 Augment | Proxied O-RU module capabilities readback |
| `o-ran-agg-mplane-int` | 2020-09-25 | 🔀 Augment | Proxied M-Plane interface configuration readback |
| `o-ran-agg-operations` | 2020-09-25 | 🔀 Augment | Proxied O-RU operational state |
| `o-ran-agg-performance-management` | 2020-09-25 | 🔀 Augment | Proxied O-RU PM job configuration and results |
| `o-ran-agg-processing-element` | 2020-09-25 | 🔀 Augment | Proxied transport endpoint mapping |
| `o-ran-agg-shared-cell` | 2020-09-25 | 🔀 Augment | Proxied shared cell (cascaded O-RU) configuration |
| `o-ran-agg-software-management` | 2020-09-25 | 🔀 Augment | Proxied O-RU software inventory and activation |
| `o-ran-agg-supervision` | 2020-09-25 | 🔀 Augment | Proxied O-RU supervision watchdog configuration |
| `o-ran-agg-transceiver` | 2020-09-25 | 🔀 Augment | Proxied SFP/QSFP transceiver inventory and state |
| `o-ran-agg-udp-echo` | 2020-09-25 | 🔀 Augment | Proxied UDP echo server configuration |
| `o-ran-agg-uplane-conf` | 2020-09-25 | 🔀 Augment | Proxied U-Plane (carrier termination) configuration |
| `o-ran-agg-usermgmt` | 2020-09-25 | 🔀 Augment | Proxied O-RU user account management |

## O-RAN WG10 O1 NRM Modules

These modules augment the 3GPP NRM `ManagedElement` subtree with O-DU-specific O1 management
objects for the SMO interface.

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `o-ran-o1-managed-application` | 2025-07-02 | 📦 Groupings | Common O1 managed application groupings (vendor info, restart notifications) |
| `o-ran-o1-subscription-control` | 2025-07-02 | 📦 Groupings | O1 performance/alarm subscription control groupings |
| `o-ran-o1-subscription-control-me` | 2025-07-02 | 🔀 Augment | Augments `ManagedElement` with O1 subscription control instance |
| `o-ran-o1-subscription-control-subnetwork` | 2025-07-02 | 🔀 Augment | Augments `SubNetwork` with O1 subscription control for the O-DU domain |
| `o-ran-o1-EPE2` | 2024-07-11 | 🔀 Augment | Augments `ManagedElement` with Energy and Power Efficiency (EPE) O1 management objects |
| `o-ran-o1-NearRTRIC` | 2024-07-11 | 🔀 Augment | Augments `ManagedElement` with Near-RT RIC connectivity state for E2 interface management |
| `o-ran-o1-ctiOdu` | 2023-03-17 | 🔀 Augment | Augments `GNBDUFunction` with Centralized Unit–DU Topology Interface (CTI) O-DU attributes |
| `o-ran-o1-odu-nespolicy` | 2025-07-02 | 🔀 Augment | Augments `GNBDUFunction` with NES (Network Energy Saving) policy configuration |
| `o-ran-o1-odu-nespolicyrelation` | 2025-07-02 | 🔀 Augment | Augments `GNBDUFunction` with NES policy–cell relation mapping |
| `o-ran-o1-odu-rballoc` | 2025-07-02 | 🔀 Augment | Augments `GNBDUFunction` with resource-block allocation policy objects |
| `o-ran-cti-common` | 2023-03-17 | 📦 Types | CTI (Centralized–DU topology interface) common type definitions |

## 3GPP NR NRM Modules

### NRM Root Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `_3gpp-common-managed-element` | 2025-03-24 | 🌳 **Root** | 3GPP TS 28.623 — `ManagedElement` list; the primary O1 NRM anchor; all NF-specific objects hang beneath it |
| `_3gpp-common-subnetwork` | 2025-03-24 | 🌳 **Root** | 3GPP TS 28.623 — `SubNetwork` list; logical grouping of managed elements |

### O-RAN WG5 NRM Extension Roots

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `o-ran_3gpp-nr-nrm-gnbdufunction` | 2020-09-25 | 🌳 **Root** | O-RAN WG5 extension of `_3gpp-nr-nrm-gnbdufunction`; adds fronthaul and O-DU-specific operational attributes to `GNBDUFunction` |
| `o-ran_3gpp-nr-nrm-nrcelldu` | 2020-09-25 | 🌳 **Root** | O-RAN WG5 extension of `_3gpp-nr-nrm-nrcelldu`; adds O-RAN cell-level parameters (carrier aggregation config, TDD pattern) to `NRCellDU` |
| `o-ran_3gpp-nr-nrm-rrmpolicy` | 2021-10-31 | 🔀 Augment | O-RAN WG5 extension of `_3gpp-nr-nrm-rrmpolicy`; adds O-RAN policy attributes |

### 3GPP NR NRM Augmentation Modules

These modules augment `_3gpp-common-managed-element` to add NR-specific managed objects.

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `_3gpp-nr-nrm-gnbdufunction` | 2024-02-24 | 🔀 Augment | Augments `ManagedElement` with `GNBDUFunction` list: DU identity, F1 interface, cell counts |
| `_3gpp-nr-nrm-nrcelldu` | 2024-05-24 | 🔀 Augment | Augments `GNBDUFunction` with `NRCellDU` list: ARFCN, NCI, bandwidth, TDD config |
| `_3gpp-nr-nrm-gnbcucpfunction` | 2024-08-12 | 🔀 Augment | Augments `ManagedElement` with `GNBCUCPFunction` (transitive dep via rrmpolicy) |
| `_3gpp-nr-nrm-gnbcuupfunction` | 2024-05-24 | 🔀 Augment | Augments `ManagedElement` with `GNBCUUPFunction` (transitive dep) |
| `_3gpp-nr-nrm-nrcellcu` | 2023-09-18 | 🔀 Augment | Augments `GNBCUCPFunction` with `NRCellCU` list |
| `_3gpp-nr-nrm-rrmpolicy` | 2023-09-18 | 🔀 Augment | Augments multiple NRM objects with `RRMPolicy` for radio resource allocation |
| `_3gpp-nr-nrm-ep` | 2025-05-06 | 🔀 Augment | Augments NRM objects with endpoint (E1, F1, Xn, X2) objects |
| `_3gpp-nr-nrm-externalgnbcucpfunction` | 2025-04-25 | 🔀 Augment | Augments `SubNetwork` with external gNB-CU-CP references |
| `_3gpp-nr-nrm-externalgnbdufunction` | 2025-04-25 | 🔀 Augment | Augments `SubNetwork` with external gNB-DU references |
| `_3gpp-nr-nrm-externalnrcellcu` | 2025-04-25 | 🔀 Augment | Augments external gNB references with NRCellCU entries |
| `_3gpp-nr-nrm-nrnetwork` | 2025-04-25 | 🔀 Augment | Augments `SubNetwork` with NR network topology objects |
| `_3gpp-nr-nrm-ecmappingrule` | 2025-05-06 | 📦 Groupings | ECM (Error Correction Mapping) rule groupings |

### 3GPP Common Framework Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `_3gpp-common-managed-function` | 2025-08-06 | 📦 Groupings | Base grouping for all 3GPP managed NF objects (vendor info, operational state) |
| `_3gpp-common-top` | 2023-09-18 | 📦 Groupings | Top-level list key (`id`) grouping used by all NRM lists |
| `_3gpp-common-ep-rp` | 2023-09-18 | 📦 Groupings | Endpoint and reference point base groupings |
| `_3gpp-common-fm` | 2026-01-24 | 📦 Groupings | Fault management alarm groupings |
| `_3gpp-common-trace` | 2025-08-06 | 📦 Groupings | 3GPP trace configuration groupings |
| `_3gpp-common-measurements` | 2025-08-06 | 📦 Groupings | PM measurement configuration groupings |
| `_3gpp-common-subscription-control` | 2025-11-06 | 📦 Groupings | O1 event subscription control groupings |
| `_3gpp-common-files` | 2025-07-01 | 📦 Groupings | File management groupings (log upload, config transfer) |
| `_3gpp-common-yang-types` | 2025-11-06 | 📦 Types | 3GPP common YANG types (Dnprefix, Mcc, Mnc, CellIdentity, etc.) |
| `_3gpp-common-yang-extensions` | 2025-02-06 | 📦 Types | 3GPP YANG extension statements (`inVariant`, `notNotified`) |
| `_3gpp-5g-common-yang-types` | 2025-08-18 | 📦 Types | 5G-specific YANG types (SNSSAI, PLMN-ID, NSSAI) |
| `_3gpp-5gc-nrm-configurable5qiset` | 2023-09-18 | 📦 Groupings | Configurable 5QI (QoS Indicator) set groupings |
| `_3gpp-5gc-nrm-ecmconnectioninfo` | 2024-01-29 | 📦 Groupings | ECM (Error Correction Mapping) connection info groupings |

## IETF/IANA Base Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-hardware` | 2018-03-13 | 🌳 Root | RFC 8348 — `hardware` container; physical inventory |
| `ietf-interfaces` | 2018-02-20 | 🌳 Root | RFC 8343 — `interfaces` container; fronthaul Ethernet ports |
| `ietf-ip` | 2018-02-22 | 🔀 Augment | RFC 8344 — augments `ietf-interfaces` with IPv4/IPv6 |
| `ietf-netconf-acm` | 2018-02-14 | 🌳 Root | RFC 8341 — `nacm` container; NETCONF access control |
| `ietf-yang-schema-mount` | 2019-01-14 | 🌳 Root | RFC 8528 — schema mount declarations for aggregated M-Plane |
| `ietf-crypto-types` | 2024-10-10 | 📦 Types | RFC 9640 — cryptographic algorithm types |
| `ietf-dhcpv6-types` | 2018-09-04 | 📦 Types | DHCPv6 base types |
| `ietf-inet-types` | 2025-12-22 | 📦 Types | RFC 6991 — IP address types |
| `ietf-yang-types` | 2025-12-22 | 📦 Types | RFC 6991 — base YANG types |
| `iana-hardware` | 2018-03-13 | 📦 Types | IANA hardware component type identities |
| `iana-if-type` | 2014-05-08 | 📦 Types | IANA interface type registry |

## O-RAN Common Type Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `o-ran-common-yang-types` | 2025-07-02 | 📦 Types | O-RAN common types (frequencies, SCS, slot indices) |
| `o-ran-common-identity-refs` | 2025-07-02 | 📦 Types | O-RAN identity references (interface types, hardware classes) |
| `o-ran-wg4-features` | 2025-12-22 | 📦 Types | WG4 feature identities (used in `if-feature` guards) |
| `o-ran-wg5-features` | 2022-03-14 | 📦 Types | WG5 feature identities for O-DU capability declarations |

## YANG Tree Generation

Run from the project root:

```bash
./generate-yang-tree.sh yang-per-network-function/O-DU
```

Output is written to `yang-tree.txt` in this folder. The tree covers 14 root module entry points.
The 3GPP NRM augmentation modules are folded into `_3gpp-common-managed-element`, and the WG5
aggregated M-Plane `o-ran-agg-*` modules are folded into the `o-ran-aggregation-base` subtree
automatically by pyang when all modules are loaded together.
