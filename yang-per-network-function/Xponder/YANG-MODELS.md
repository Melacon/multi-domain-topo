# ROADM — YANG Models

A **Reconfigurable Optical Add-Drop Multiplexer (ROADM)** is a core optical networking element
that dynamically switches, routes, and amplifies wavelengths in a DWDM (Dense Wavelength-Division
Multiplexing) network. The OpenROADM Multi-Source Agreement (MSA) defines an open, vendor-neutral
YANG data model for ROADM topology, covering node types (ROADMs, transponders, amplifiers), degrees,
Shared Risk Groups (SRGs), and OTN overlays. All ROADM-specific attributes are modeled as
augmentations of the IETF RFC 8345 network topology base, making `ietf-network` the single
YANG tree entry point.

## YANG Tree Entry Point

| Module | Role |
|--------|------|
| `ietf-network` | 🌳 **Root** — RFC 8345 `networks` container; all ROADM topology is folded in via augmentation |

## OpenROADM Topology Augmentation Modules

These modules extend the IETF network topology model with ROADM-specific attributes.
pyang folds them into the `ietf-network` tree automatically when all modules are loaded together.

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `org-openroadm-network` | 2025-12-12 | 🔀 Augment | Adds ROADM node types (ROADM, transponder, regen, extplug) to `ietf-network` network and node objects |
| `org-openroadm-network-topology` | 2025-12-12 | 🔀 Augment | Adds link properties (amplified links, OMS/OTS span data), port mappings, and ROADM-specific termination points |
| `org-openroadm-common-network` | 2025-12-12 | 🔀 Augment | Adds shared attributes to nodes and links (operational mode, planning information) |
| `org-openroadm-clli-network` | 2019-11-29 | 🔀 Augment | Adds Common Language Location Identifiers (CLLI) to network sites for operator OSS correlation |
| `org-openroadm-otn-network-topology` | 2025-12-12 | 🔀 Augment | Adds OTN (Optical Transport Network) client/line side topology for ODU cross-connect management |
| `ietf-network-topology` | 2018-02-26 | 🔀 Augment | RFC 8345 — extends `ietf-network` with `link` and `termination-point` (required by all topology augmenters) |
| `ietf-te-topology` | 2020-08-06 | 🔀 Augment | RFC 8795 — adds Traffic Engineering attributes (bandwidth, SRLG, switching capability) to links and nodes |

## OpenROADM Hardware Component Modules

These modules define groupings representing physical ROADM sub-components, referenced by the
topology augmentation modules above.

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `org-openroadm-roadm` | 2019-11-29 | 📦 Groupings | ROADM node structure: add/drop ports, pass-through channels, ROADMPort grouping |
| `org-openroadm-degree` | 2025-12-12 | 📦 Groupings | Degree (directional amplified port group) configuration groupings |
| `org-openroadm-srg` | 2025-12-12 | 📦 Groupings | Shared Risk Group (SRG) — groups add/drop ports that share failure risk |
| `org-openroadm-amplifier` | 2025-03-28 | 📦 Groupings | Optical amplifier parameters (gain, noise figure, tilt, output power) |
| `org-openroadm-xponder` | 2025-12-12 | 📦 Groupings | Transponder/muxponder client and line port groupings |
| `org-openroadm-link` | 2025-12-12 | 📦 Groupings | Link attribute groupings (fiber type, span loss, OSNR budget) |
| `org-openroadm-network-resource` | 2025-12-12 | 📦 Groupings | Resource identifier groupings shared across network objects |
| `org-openroadm-external-pluggable` | 2025-03-28 | 📦 Groupings | External pluggable transceiver (QSFP-DD, etc.) port attributes |
| `org-openroadm-network-topology-types` | 2025-05-30 | 📦 Types | Topology type identity definitions (openroadm-topology, otn-topology) |

## OpenROADM Type Modules

Pure type, identity, and enumeration definitions consumed by the modules above.

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `org-openroadm-common-types` | 2025-12-12 | 📦 Types | Base types: admin/oper state, direction, port roles |
| `org-openroadm-common-equipment-types` | 2019-11-29 | 📦 Types | Equipment category identities (amplifier, transponder, etc.) |
| `org-openroadm-common-link-types` | 2024-12-13 | 📦 Types | Link type identities (OMS, OTS, OTN-link) and fiber types |
| `org-openroadm-common-node-types` | 2021-05-28 | 📦 Types | Node type identities (ROADM, XPDR, EXT-PLUGGABLE, REGEN) |
| `org-openroadm-common-optical-channel-types` | 2025-03-28 | 📦 Types | Optical channel modulation and FEC format identities |
| `org-openroadm-common-state-types` | 2019-11-29 | 📦 Types | Lifecycle state machine types |
| `org-openroadm-common-amplifier-types` | 2025-03-28 | 📦 Types | Amplifier technology type identities |
| `org-openroadm-network-types` | 2025-12-12 | 📦 Types | Network type identity (`openroadm-common-network`) |
| `org-openroadm-otn-common-types` | 2021-09-24 | 📦 Types | OTN tributary slot and ODU type definitions |
| `org-openroadm-port-types` | 2025-05-30 | 📦 Types | Port type identities (client, line, bidirectional) |
| `org-openroadm-service-format` | 2025-05-30 | 📦 Types | Service format identities (Ethernet, OC, OTU, ODU) |
| `org-openroadm-switching-pool-types` | 2019-11-29 | 📦 Types | Switching pool type identities (blocking/non-blocking) |
| `org-openroadm-equipment-states-types` | 2019-11-29 | 📦 Types | Equipment administrative state types |

## IETF Base Dependency Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-network` | 2018-02-26 | 🌳 **Root** | RFC 8345 — `networks` container; the single YANG tree entry point for ROADM topology |
| `ietf-te-types` | 2020-06-10 | 📦 Types | RFC 8776 — TE common type definitions (bandwidth, switching capability, SRLG) |
| `ietf-routing-types` | 2017-12-04 | 📦 Types | RFC 8294 — routing address family and protocol type definitions |
| `ietf-inet-types` | 2025-12-22 | 📦 Types | RFC 6991 — IP address and prefix types |
| `ietf-yang-types` | 2025-12-22 | 📦 Types | RFC 6991 — `yang:date-and-time`, `yang:uuid`, and other base types |

## YANG Tree Generation

Run from the project root:

```bash
./generate-yang-tree.sh yang-per-network-function/ROADM
```

Output is written to `yang-tree.txt` in this folder. The tree starts at `ietf-network` (`/networks`)
with all OpenROADM augmentations folded in by pyang automatically.
