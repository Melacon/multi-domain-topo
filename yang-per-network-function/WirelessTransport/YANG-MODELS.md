# WirelessTransport — YANG Models

A **Wireless Transport** link provides microwave or millimeter-wave radio connectivity for
RAN backhaul and midhaul segments. IETF RFC 8561 (`ietf-microwave-radio-link`) is the
vendor-neutral management-plane standard for configuring and monitoring point-to-point radio
links, covering carrier termination, bonding/MIMO, and radio performance. Network topology
is modeled as augmentations of the IETF RFC 8345 network model, while individual interfaces
follow RFC 8343 (`ietf-interfaces`). Three modules define top-level YANG tree entry points.

## YANG Tree Entry Points

| Module | Role |
|--------|------|
| `ietf-interfaces` | 🌳 **Root** — RFC 8343 `interfaces` container; radio carriers appear as interface entries |
| `ietf-microwave-radio-link` | 🌳 **Root** — RFC 8561 `carrier-terminations` and `radio-link-terminals` containers; also augments `ietf-interfaces` |
| `ietf-network` | 🌳 **Root** — RFC 8345 `networks` container; microwave topology links are folded in via augmentation |

## Microwave Functional Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-microwave-radio-link` | 2019-06-19 | 🌳 Root + 🔀 Augment | RFC 8561 — core radio link management: TX/RX frequency, power, modulation, MIMO/bonding configuration, and performance monitoring; also augments `ietf-interfaces` with radio-specific attributes |
| `ietf-microwave-topology` | 2024-09-30 | 🔀 Augment | Augments `ietf-network` and `ietf-network-topology` with microwave link topology (MW link type identity, carrier references) |
| `ietf-microwave-types` | 2019-06-19 | 📦 Types | Microwave-specific types: modulation schemes, MIMO mode identities, frame structures |
| `ietf-interface-protection` | 2019-06-19 | 📦 Groupings | Protection switching groupings (1+1, 1:N) referenced by `ietf-microwave-radio-link` for radio link protection |

## IETF Network Topology Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-network` | 2018-02-26 | 🌳 **Root** | RFC 8345 — `networks` container; the network topology entry point |
| `ietf-network-topology` | 2018-02-26 | 🔀 Augment | RFC 8345 — adds `link` and `termination-point` to `ietf-network`; required by microwave topology |
| `ietf-te-topology` | 2020-08-06 | 🔀 Augment | RFC 8795 — adds TE attributes (bandwidth, SRLG, switching capability) to network links and nodes |

## IETF Interface Module

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-interfaces` | 2018-02-20 | 🌳 **Root** | RFC 8343 — `interfaces` container; each radio carrier appears as an interface entry augmented by `ietf-microwave-radio-link` |

## IETF/IANA Type Dependency Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-te-types` | 2020-06-10 | 📦 Types | RFC 8776 — TE type definitions (bandwidth, switching capability) used by `ietf-te-topology` |
| `ietf-routing-types` | 2017-12-04 | 📦 Types | RFC 8294 — routing address family types used by `ietf-te-topology` |
| `ietf-inet-types` | 2025-12-22 | 📦 Types | RFC 6991 — IP address and prefix types |
| `ietf-yang-types` | 2025-12-22 | 📦 Types | RFC 6991 — `yang:date-and-time`, `yang:counter64`, and other base types |
| `iana-if-type` | 2014-05-08 | 📦 Types | IANA interface type registry; provides `ianaift:radioMAC` and related identities for microwave interfaces |

## YANG Tree Generation

Run from the project root:

```bash
./generate-yang-tree.sh yang-per-network-function/WirelessTransport
```

Output is written to `yang-tree.txt` in this folder. The tree covers three entry points:
`/interfaces` (ietf-interfaces with microwave augmentation), `/carrier-terminations` and
`/radio-link-terminals` (ietf-microwave-radio-link), and `/networks` (ietf-network with
microwave topology augmentation).
