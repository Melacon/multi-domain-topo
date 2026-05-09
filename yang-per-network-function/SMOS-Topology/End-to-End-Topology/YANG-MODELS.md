# End-to-End-Topology — YANG Models

The **End-to-End Topology** is the base network topology layer used by the SMO to represent
nodes, links, and termination points across all technology domains (microwave, optical, 5G).
It is modeled after IETF RFC 8345 (`ietf-network`) with the topology extension RFC 8345
(`ietf-network-topology`) that adds directed links and termination points. All domain-specific
topology views (Microwave-Topology, Service-Topology, ROADM-Topology) augment this base layer.

## YANG Tree Entry Point

| Module | Role |
|--------|------|
| `ietf-network` | 🌳 **Root** — RFC 8345 `networks` container; nodes and their supporting-network hierarchy |

## IETF Network Topology Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-network` | 2018-02-26 | 🌳 **Root** | RFC 8345 — `networks` container with `network`, `node`, and `supporting-network` lists; the base entry point for all SMO topology views |
| `ietf-network-topology` | 2018-02-26 | 🔀 Augment | RFC 8345 — adds `link` and `termination-point` to `ietf-network`; referenced by all domain-specific augmenters (microwave, SAP, ROADM) |

## Type Dependency Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-inet-types` | 2013-07-15 | 📦 Types | RFC 6991 — IP address, prefix, and URI types used by `ietf-network` and `ietf-network-topology` |

## YANG Tree Generation

Run from the project root:

```bash
./generate-yang-tree.sh yang-per-network-function/SMOS-Topology/End-to-End-Topology
```

Output is written to `yang-tree.txt` in this folder. The tree starts at `ietf-network`
(`/networks`) with `ietf-network-topology` augmentations (links and termination points)
folded in by pyang automatically.
