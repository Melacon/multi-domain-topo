# EPIC: Transport Inclusion — Network Topology Abstraction for SMO

| Field          | Value                                                        |
| -------------- | ------------------------------------------------------------ |
| **Epic ID**    | TI-EPIC-001                                                  |
| **Title**      | Unified Network Topology Model for RAN & Transport in SMO    |
| **Owner**      | TBD                                                          |
| **Priority**   | High                                                         |
| **Status**     | Draft                                                        |
| **Created**    | 2026-03-20                                                   |
| **Target Release** | TBD                                                      |

---

## 1  Problem Statement

Today, RAN and transport domains expose their topology through heterogeneous,
device-centric YANG models (e.g., O-RAN fronthaul, IETF microwave, OpenROADM).
The SMO Framework has no single, technology-agnostic view of the end-to-end
network that spans UE → O-RU → O-DU → O-CU → DWDM/ROADM ring → 5G Core →
Internet.

Without such a view, cross-domain path computation, fault correlation, and
lifecycle management require manual, per-technology integration — defeating the
purpose of a Service Management and Orchestration layer.

## 2  Goal

Implement a **unified network topology** inside the O-RAN SMO Framework that:

1. Ingests device-level models from every domain in the reference topology
   (RAN, Open Fronthaul, Wireless Transport, DWDM/ROADM, 5G Core).
2. Abstracts them into a **single, multi-layer network model** based on
   **RFC 8345 (ietf-network / ietf-network-topology)** and its augmentations.
3. Exposes the resulting topology via RESTCONF/NETCONF northbound so that
   rApps and other SMO consumers can query and subscribe to topology changes.

## 3  Reference Topology

The reference topology (see `usecase.svg`) contains:

```
Branch 1 (macro cell):
  UE-1/2 → O-RU-1 → O-DU-1 → O-CU-1 → ROADM-A1

Branch 2 (small cells via wireless transport):
  UE-3..8 → O-RU-2/3/4 → OFH-SW-1 → O-DU-2 → WT-2 ~~wireless~~ WT-1 → O-CU-2 → ROADM-C1

DWDM/ROADM Ring:
  ROADM-A1 — ROADM-B1 — ROADM-C1 — ROADM-A1  (optical ring)

Core:
  ROADM-B1 → 5GC-1 → NET-1 (Internet)
```

### Network layers (bottom → top)

| Layer               | IETF Network ID               | Nodes                                             |
| ------------------- | ----------------------------- | ------------------------------------------------- |
| Physical / optical  | `ietf-photonic-topology`      | ROADM-A1, ROADM-B1, ROADM-C1, fibre spans           |
| Wireless transport  | `ietf-microwave-topology`     | WT-1, WT-2                                        |
| Ethernet / IP       | `ietf-l2-topology` / `ietf-l3-unicast-topology` | OFH-SW-1, O-DU-*, O-CU-*, 5GC-1 |
| O-RAN RAN           | `o-ran-sc-ran-topology`       | O-RU-*, O-DU-*, O-CU-*                           |

Each layer references the one below via `supporting-network` and
`supporting-node` / `supporting-link` as defined in RFC 8345.

## 4  Scope & Features

### F-1 — Device Model Adapters (Southbound)

Create adapters that translate device-specific YANG models into normalised
internal representations consumed by the topology engine.

| Adapter               | Source Model(s)                             | Devices          |
| --------------------- | ------------------------------------------- | ---------------- |
| O-RAN Fronthaul       | `o-ran-hardware`, `o-ran-uplane-conf`       | O-RU-1..4        |
| O-RAN CU/DU           | `o-ran-sc-du-hello-world`, 3GPP NRM models  | O-DU-1/2, O-CU-1/2 |
| Open Fronthaul Switch | `ietf-interfaces`, `ieee802-dot1q-bridge`   | OFH-SW-1         |
| IETF Microwave        | `ietf-microwave-radio-link` (RFC 8561)      | WT-1, WT-2       |
| OpenROADM / DWDM      | `org-openroadm-device`, `org-openroadm-network` | ROADM-A1/2/3 |
| 5G Core               | 3GPP TS 28.541 NRM or vendor model          | 5GC-1            |

**Acceptance criteria:**

- Each adapter connects to its device via NETCONF/RESTCONF.
- Device capabilities are discovered dynamically (`hello` / capability exchange).
- Adapter emits `node-created`, `node-updated`, `node-deleted` events into the
  topology engine message bus.

### F-2 — Topology Abstraction Engine (Core)

Build the central service that maintains an in-memory, multi-layer graph and
persists it as RFC 8345 compliant YANG datastores.

**Key responsibilities:**

| # | Capability                              | Detail |
|---|-----------------------------------------|--------|
| 1 | **Layer construction**                  | Create `ietf-network` instances for each technology layer (photonic, microwave, Ethernet/IP, RAN). |
| 2 | **Inter-layer stitching**               | Populate `supporting-network`, `supporting-node`, and `supporting-link` references to express vertical relationships (e.g., an O-CU-1 L3 node is supported by a ROADM-A1 photonic node). |
| 3 | **Intra-layer link discovery**          | Derive `ietf-network-topology:link` objects from adapter events (e.g., LLDP, OSPF-TE, OpenROADM XPDR-to-ROADM). |
| 4 | **Ring detection**                      | Identify and tag the ROADM ring as a `te:topology` with protection type `ring`. |
| 5 | **Change notification**                 | Publish YANG Push (`ietf-subscribed-notifications`) or SSE events when the topology changes. |

**Acceptance criteria:**

- Given the reference topology devices are onboarded, the engine produces
  a valid RFC 8345 datastore with all four layers, correct inter-layer links,
  and the ROADM ring.
- Adding or removing a device updates the topology within SLA (< 5 s).

### F-3 — RESTCONF / NETCONF Northbound API

Expose the abstracted topology to SMO consumers.

| Endpoint / RPC                                   | Purpose |
| ------------------------------------------------ | ------- |
| `GET /restconf/data/ietf-network:networks`       | Full multi-layer topology |
| `GET /restconf/data/ietf-network:networks/network={id}` | Single-layer view |
| `POST /restconf/operations/ietf-subscribed-notifications:establish-subscription` | Real-time topology change stream |

**Acceptance criteria:**

- Response payloads validate against the YANG schemas (RFC 8345, RFC 8795,
  augmentations).
- Pagination / filtering by network-id, node-id, link-id.
- OAuth2 / certificate-based access control.

### F-4 — SMO Integration (rApp / platform service)

Package the topology service so it runs within the O-RAN SMO platform.

- Deploy as a containerised micro-service (Helm chart for O-RAN-SC SMO / ONAP).
- Register as an **r1-interface** provider so rApps can discover it.
- Provide a Kubernetes `ServiceMonitor` for Prometheus scraping.

**Acceptance criteria:**

- Service starts, onboards all reference topology devices, and answers
  northbound queries in an SMO-SC integration test environment.
- rApp sample can read the topology, find the shortest optical path between
  two O-CUs, and render it.

### F-5 — Mapping Specification & Documentation

Produce a formal, reviewable mapping from each device model to the target
RFC 8345 structures.

| Deliverable                | Format |
| -------------------------- | ------ |
| Device → Topology mapping tables | Markdown / AsciiDoc |
| YANG augmentation modules (if any) | `.yang` files |
| Architecture & data-flow diagram  | SVG / draw.io |
| API guide with curl examples      | OpenAPI + Markdown |

---

## 5  YANG Model Stack

```
                ┌─────────────────────────────────────────┐
                │        Northbound (RESTCONF / NETCONF)  │
                └────────────────┬────────────────────────┘
                                 │
   ┌─────────────────────────────┼─────────────────────────────┐
   │                ietf-network (RFC 8345)                    │
   │       ietf-network-topology (RFC 8345)                    │
   ├───────────────────────────────────────────────────────────┤
   │  ietf-te-topology (RFC 8795)   – TE extensions            │
   │  ietf-l3-unicast-topology      – IP layer                 │
   │  ietf-l2-topology              – Ethernet layer           │
   │  ietf-microwave-topology       – Microwave WT links       │
   │  org-openroadm-network-topology – ROADM photonic layer    │
   │  o-ran-sc-topology (custom)    – RAN O-CU/O-DU/O-RU      │
   └───────────────────────────────────────────────────────────┘
```

### Core RFC 8345 structures used

```yang
module: ietf-network
  +--rw networks
     +--rw network* [network-id]
        +--rw network-id       network-id
        +--rw supporting-network* [network-ref]
        +--rw node* [node-id]
           +--rw node-id             node-id
           +--rw supporting-node* [network-ref node-ref]
           +--rw nt:termination-point* [tp-id]
              +--rw nt:supporting-termination-point*

module: ietf-network-topology (augments ietf-network)
  augment /nw:networks/nw:network:
     +--rw link* [link-id]
        +--rw source      (node-ref, tp-ref)
        +--rw destination (node-ref, tp-ref)
        +--rw supporting-link* [network-ref link-ref]
```

## 6  Stories (suggested breakdown)

| ID        | Story                                                                 | Feature | Est. |
| --------- | --------------------------------------------------------------------- | ------- | ---- |
| TI-001    | As a developer, I can deploy the topology service in a local SMO-SC env | F-4   | 5 SP |
| TI-002    | As a developer, I can onboard an OpenROADM device and see it as an `ietf-network` node | F-1, F-2 | 8 SP |
| TI-003    | As a developer, I can onboard an O-RU via O-RAN fronthaul and see it in the RAN topology layer | F-1, F-2 | 8 SP |
| TI-004    | As a developer, I can onboard O-DU / O-CU and the engine auto-creates midhaul/backhaul links | F-1, F-2 | 5 SP |
| TI-005    | As a developer, I can onboard WT-1/WT-2 and see a microwave link in the topology | F-1, F-2 | 5 SP |
| TI-006    | As a developer, I can onboard OFH-SW-1 and see fronthaul links to O-RUs | F-1, F-2 | 5 SP |
| TI-007    | As a developer, the engine stitches supporting-node references across layers | F-2 | 8 SP |
| TI-008    | As a developer, the ROADM ring is detected and tagged with protection type | F-2 | 3 SP |
| TI-009    | As a consumer, I can query the full topology via RESTCONF `GET /networks` | F-3 | 5 SP |
| TI-010    | As a consumer, I can subscribe to topology-change notifications via YANG Push | F-3 | 5 SP |
| TI-011    | As a developer, I have mapping tables for every device model to RFC 8345 | F-5 | 5 SP |
| TI-012    | As a developer, the topology service publishes Prometheus metrics | F-4 | 3 SP |
| TI-013    | As an rApp developer, a sample rApp reads the topology and computes an optical path | F-4 | 5 SP |
| TI-014    | As a developer, 5GC-1 is onboarded and the core layer connects to ROADM-B1 | F-1, F-2 | 5 SP |

## 7  Architecture Overview

```
 ┌──────────────────────────────────────────────────────────────┐
 │                        SMO Framework                         │
 │  ┌────────────────────────────────────────────────────────┐  │
 │  │              Topology Abstraction Service               │  │
 │  │                                                        │  │
 │  │  ┌──────────┐  ┌──────────────┐  ┌─────────────────┐  │  │
 │  │  │ Adapters │→ │ Topo Engine  │→ │ RESTCONF / NB   │  │  │
 │  │  │ (SB)     │  │ (multi-layer │  │ (RFC 8040)      │  │  │
 │  │  │          │  │  graph +     │  │                  │  │  │
 │  │  │ OpenROADM│  │  RFC 8345    │  └─────────────────┘  │  │
 │  │  │ O-RAN FH │  │  datastore)  │                       │  │
 │  │  │ 3GPP NRM │  │              │  ┌─────────────────┐  │  │
 │  │  │ MW (8561)│  │              │→ │ YANG Push /     │  │  │
 │  │  │ IEEE 802 │  │              │  │ Notifications   │  │  │
 │  │  └──────────┘  └──────────────┘  └─────────────────┘  │  │
 │  └────────────────────────────────────────────────────────┘  │
 │         ▲                                    │               │
 │    NETCONF/RESTCONF                    r1-interface          │
 │         │                                    ▼               │
 │  ┌──────┴──────┐                     ┌──────────────┐        │
 │  │ Network     │                     │ rApps        │        │
 │  │ Devices     │                     │ (consumers)  │        │
 │  └─────────────┘                     └──────────────┘        │
 └──────────────────────────────────────────────────────────────┘
```

## 8  Assumptions & Risks

| #  | Item | Type | Mitigation |
|----|------|------|------------|
| 1  | All devices expose NETCONF/RESTCONF with standard YANG models | Assumption | Validate in lab; fall back to vendor-specific adapters where needed |
| 2  | No existing RFC 8345 topology service in SMO-SC covers transport | Assumption | Review latest O-RAN-SC repos before starting |
| 3  | OpenROADM and O-RAN models may evolve during development | Risk | Pin to specific model versions; design adapters for version negotiation |
| 4  | YANG Push support varies across NETCONF servers | Risk | Provide polling fallback in adapters |
| 5  | Inter-layer stitching heuristics may not cover all edge cases | Risk | Start with explicit configuration; evolve to auto-discovery |

## 9  Definition of Done

- [ ] All reference topology devices are onboarded and represented in the
      RFC 8345 datastore with correct multi-layer relationships.
- [ ] RESTCONF northbound returns valid, schema-compliant JSON/XML for every
      layer.
- [ ] Topology change notifications are delivered within 5 seconds of a device
      state change.
- [ ] The service runs in the O-RAN-SC SMO integration test environment.
- [ ] Mapping documentation and YANG augmentation modules are reviewed and
      merged.
- [ ] A sample rApp successfully queries and renders the topology.
