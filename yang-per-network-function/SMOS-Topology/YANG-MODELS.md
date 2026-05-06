# YANG Models — SMO Topology (Northbound)

This folder contains the YANG modules for the **northbound topology model** exposed by the
SMO Topology Abstraction Service (see `topology/EPIC-transport-inclusion-topology.md`).

Unlike the per-NF folders in this directory, these modules do not describe device-level
configuration. They define the **SMO-side data model** that rApps and other consumers
query via RESTCONF/NETCONF.

## Module Set

| Module | Revision | RFC | Role |
|--------|----------|-----|------|
| `ietf-network` | 2018-02-26 | [RFC 8345](https://www.rfc-editor.org/rfc/rfc8345) | Core network and node model |
| `ietf-network-topology` | 2018-02-26 | [RFC 8345](https://www.rfc-editor.org/rfc/rfc8345) | Links and termination points |
| `ietf-sap-ntw` | 2023-06-20 | [RFC 9408](https://www.rfc-editor.org/rfc/rfc9408) | Service Attachment Points (SAPs) |
| `ietf-vpn-common` | 2022-02-11 | [RFC 9181](https://www.rfc-editor.org/rfc/rfc9181) | Service-type identities (dependency of ietf-sap-ntw) |
| `ietf-yang-types` | 2013-07-15 | [RFC 6991](https://www.rfc-editor.org/rfc/rfc6991) | Common types (dependency) |

## How ietf-sap-ntw Fits

`ietf-sap-ntw` augments `ietf-network` with a **Service Attachment Point (SAP)** list per node.
A SAP is an abstract reference point where a network service (network slice, L3VPN, etc.)
can be provisioned without exposing the internal topology to the service consumer.

```
ietf-network (RFC 8345)
  └── augmented by ietf-network-topology (RFC 8345)   — adds links + TPs
  └── augmented by ietf-sap-ntw (RFC 9408)            — adds SAP list per node
```

The augmentation applies only to networks whose `network-types` contains `sap:sap-network`.
In this project that is the `sap-network` network (see `topology/sap-topology.json`), which
references the underlying `transport-inclusion-reference` network via `supporting-network`.

## SAP Placement in the Reference Topology

| Node | SAP | Service Type | Description |
|------|-----|-------------|-------------|
| `urn:node:txp-1` | `sap:txp-1:o-cu-cp-1` | network-slice | Backhaul attachment for O-CU-CP-1 (Branch 1 CP) |
| `urn:node:txp-1` | `sap:txp-1:o-cu-up-1` | network-slice | Backhaul attachment for O-CU-UP-1 (Branch 1 UP) |
| `urn:node:txp-3` | `sap:txp-3:o-cu-cp-2` | network-slice | Backhaul attachment for O-CU-CP-2 (Branch 2 CP) |
| `urn:node:txp-3` | `sap:txp-3:o-cu-up-2` | network-slice | Backhaul attachment for O-CU-UP-2 (Branch 2 UP) |
| `urn:node:ip-rtr-1` | `sap:ip-rtr-1:to-5gc` | network-slice | Transport ↔ 5G Core boundary (N2/N3 traffic) |
| `urn:node:ip-rtr-1` | `sap:ip-rtr-1:to-5gc-basic` | basic-connectivity | Basic IP toward 5G Core |
| `urn:node:5gc-1` | `sap:5gc-1:to-internet` | basic-connectivity | Internet breakout (N6 interface) |

SAPs are placed at **inter-domain boundaries** (transponder client ports, IP router, 5GC),
not at device-level ports. The `peer-sap-id` leaf cross-references the peer endpoint so
the SMO can correlate SAPs when stitching an end-to-end service.

## YANG Tree (ietf-sap-ntw)

```
module: ietf-sap-ntw

  augment /nw:networks/nw:network/nw:network-types:
    +--rw sap-network!
       +--rw service-type*   identityref

  augment /nw:networks/nw:network/nw:node:
    +--rw service* [service-type]
       +--rw service-type    identityref
       +--rw sap* [sap-id]
          +--rw sap-id                   string
          +--rw description?             string
          +--rw parent-termination-point? nt:tp-id
          +--rw attachment-interface?    string
          +--rw interface-type?          identityref
          +--rw encapsulation-type?      identityref
          +--rw role?                    identityref
          +--rw allows-child-saps?       boolean
          +--rw peer-sap-id*             string
          +--ro sap-status
          |  ...
          +--rw service-status
             +--rw admin-status
             |  +--rw status?       identityref
             |  +--rw last-change?  yang:date-and-time
             +--ro oper-status
                ...
```
