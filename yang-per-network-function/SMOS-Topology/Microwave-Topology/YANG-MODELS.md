# Microwave-Topology — YANG Models

The **Microwave Topology** layer augments the End-to-End base topology (RFC 8345) with
microwave radio link attributes defined in IETF RFC 8570 (`ietf-microwave-topology`).
It extends network nodes, termination points, and links with microwave-specific attributes
such as channel-separation, air-interface references, and microwave link types. Traffic
Engineering (TE) topology attributes from RFC 8795 (`ietf-te-topology`) are also included
as `ietf-microwave-topology` augments TE nodes and links to carry MW-specific bandwidth and
protection information.

## YANG Tree Entry Point

| Module | Role |
|--------|------|
| `ietf-network` | 🌳 **Root** — RFC 8345 `networks` container; microwave topology attributes folded in via augmentation |

## Microwave Topology Module

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-microwave-topology` | 2024-09-30 | 🔀 Augment | RFC 8570 — augments `ietf-network` network-types with `mw-topology` identity, `ietf-te-topology` node and link TE attributes with MW channel separation and air-interface references, and `ietf-network-topology` termination points with microwave port attributes |
| `ietf-microwave-types` | 2019-06-19 | 📦 Types | RFC 8561 — microwave-specific type definitions: modulation schemes, channel separation values, MIMO mode identities, and frame structure types referenced by `ietf-microwave-topology` |

## IETF Network Topology Base Modules

These modules define the base topology that `ietf-microwave-topology` augments.

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-network` | 2018-02-26 | 🌳 **Root** | RFC 8345 — `networks` container; the base topology entry point |
| `ietf-network-topology` | 2018-02-26 | 🔀 Augment | RFC 8345 — adds `link` and `termination-point` to `ietf-network`; augmented by `ietf-microwave-topology` to add MW termination-point attributes |
| `ietf-te-topology` | 2020-08-06 | 🔀 Augment | RFC 8795 — adds TE attributes (bandwidth, SRLG, switching capability) to network nodes and links; augmented by `ietf-microwave-topology` to add MW-specific TE data |

## IETF/IANA Type Dependency Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-te-types` | 2020-06-10 | 📦 Types | RFC 8776 — TE common type definitions (bandwidth, switching capability, SRLG) used by `ietf-te-topology` |
| `ietf-routing-types` | 2017-12-04 | 📦 Types | RFC 8294 — routing address family and protocol type definitions used by `ietf-te-types` |
| `ietf-inet-types` | 2013-07-15 | 📦 Types | RFC 6991 — IP address and prefix types |
| `ietf-yang-types` | 2013-07-15 | 📦 Types | RFC 6991 — `yang:date-and-time`, `yang:counter64`, and other base types |

## YANG Tree Generation

Run from the project root:

```bash
./generate-yang-tree.sh yang-per-network-function/SMOS-Topology/Microwave-Topology
```

Output is written to `yang-tree.txt` in this folder. The tree starts at `ietf-network`
(`/networks`) with `ietf-network-topology`, `ietf-te-topology`, and `ietf-microwave-topology`
augmentations all folded in by pyang automatically.
