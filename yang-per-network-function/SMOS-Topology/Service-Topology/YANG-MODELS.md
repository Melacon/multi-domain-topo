# Service-Topology — YANG Models

The **Service Topology** layer models **Service Attachment Points (SAPs)** per IETF RFC 9408
(`ietf-sap-ntw`). A SAP is the point where a customer service attaches to the network; the
SAP network augments the RFC 8345 base topology to mark specific nodes as service endpoints
and describe what services (L2/L3 VPNs) are available at each point. VPN common attributes
are shared from RFC 9181 (`ietf-vpn-common`). The SMO uses this topology layer to expose
end-to-end service connectivity across all technology domains.

## YANG Tree Entry Points

| Module | Role |
|--------|------|
| `ietf-network` | 🌳 **Root** — RFC 8345 `networks` container; SAP service attributes folded in via augmentation |
| `ietf-netconf-acm` | 🌳 **Root** — RFC 8341 `nacm` container; included as transitive dependency of `ietf-vpn-common` for access control rule definitions |

## SAP Topology Module

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-sap-ntw` | 2023-06-20 | 🔀 Augment | RFC 9408 — augments `ietf-network` to introduce a `sap-network` type and extend network nodes with SAP entries, each describing the service type, VPN attachment point, and associated bearer information |

## VPN and Type Dependency Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-vpn-common` | 2022-02-11 | 📦 Groupings | RFC 9181 — common VPN type definitions and groupings (service type, address family, encapsulation, QoS) referenced by `ietf-sap-ntw` |
| `ietf-routing-types` | 2017-12-04 | 📦 Types | RFC 8294 — routing address family and protocol type definitions used by `ietf-vpn-common` |
| `ietf-packet-fields` | 2019-03-04 | 📦 Types | RFC 8519 — packet field match definitions (IP, Ethernet, port ranges) used by `ietf-vpn-common` for traffic classification |
| `ietf-netconf-acm` | 2018-02-14 | 🌳 Root | RFC 8341 — NETCONF access control module; defines `nacm` container; included as transitive dependency of `ietf-vpn-common` |
| `ietf-ethertypes` | 2019-03-04 | 📦 Types | RFC 8519 — Ethertype identity definitions used by `ietf-packet-fields` |

## IETF Network Topology Base Modules

These modules define the base topology that `ietf-sap-ntw` augments.

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-network` | 2018-02-26 | 🌳 **Root** | RFC 8345 — `networks` container; the base topology entry point |
| `ietf-network-topology` | 2018-02-26 | 🔀 Augment | RFC 8345 — adds `link` and `termination-point` to `ietf-network`; imported by `ietf-sap-ntw` for termination-point references |

## IETF Type Dependency Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-yang-types` | 2013-07-15 | 📦 Types | RFC 6991 — `yang:date-and-time`, `yang:mac-address`, and other base types |
| `ietf-inet-types` | 2013-07-15 | 📦 Types | RFC 6991 — IP address, prefix, and port-number types |

## YANG Tree Generation

Run from the project root:

```bash
./generate-yang-tree.sh yang-per-network-function/SMOS-Topology/Service-Topology
```

Output is written to `yang-tree.txt` in this folder. The tree covers two entry points:
`/networks` (ietf-network with SAP augmentation) and `/nacm` (ietf-netconf-acm, pulled
in as a transitive dependency of ietf-vpn-common).
