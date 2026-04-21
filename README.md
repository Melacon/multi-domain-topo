# Multi-Domain Topology — Network Topology Abstraction for SMO

A **unified network topology service** for the O-RAN Service Management and
Orchestration (SMO) framework.  It ingests heterogeneous, device-centric YANG
models from every domain of a reference network (RAN, Open Fronthaul, Wireless
Transport, DWDM/ROADM, 5G Core) and abstracts them into a single, multi-layer
model based on [RFC 8345](https://www.rfc-editor.org/rfc/rfc8345)
(`ietf-network` / `ietf-network-topology`) and its augmentations.

The resulting topology is exposed northbound via RESTCONF/NETCONF so that rApps
and other SMO consumers can query and subscribe to topology changes across all
domains from a single API.

## Reference topology

```
Branch 1 (macro cell):
  UE-1/2 → O-RU-1 → O-DU-1 → O-CU-1 → ROADM-1

Branch 2 (small cells via wireless transport):
  UE-3..8 → O-RU-2/3/4 → OFH-SW-1 → O-DU-2 → WT-2 ~~wireless~~ WT-1 → O-CU-2 → ROADM-3

DWDM/ROADM Ring:
  ROADM-1 — ROADM-2 — ROADM-3 — ROADM-1  (optical ring)

Core:
  ROADM-2 → 5GC-1 → Internet
```

See [topology/usecase.svg](topology/usecase.svg) for the visual diagram and
[topology/EPIC-transport-inclusion-topology.md](topology/EPIC-transport-inclusion-topology.md)
for the full epic specification (features, user stories, acceptance criteria).

## Repository layout

```
multi-domain-topo/
├── topology/                          # Epic specification and use-case diagram
├── yang-per-network-function/         # YANG model sets organised by NF type
│   ├── O-RU/
│   ├── O-DU/
│   ├── O-CU-CP / O-CU-UP/
│   ├── OpenFronthaul-Switch/
│   ├── WirelessTransport/
│   ├── ROADM/
│   └── 5GCore/
├── data-models-per-network-function-instance/   # Per-instance data (O-RU-1 … 5GC-1)
├── yang-repos/                        # External YANG model repos — NOT in git (see below)
├── setup-yang-repos.sh                # Script to populate yang-repos/
└── README.md
```

## YANG model repositories

The `yang-repos/` folder contains external YANG model collections.  It is
**excluded from this git repository** for two reasons:

1. **Size** — the collections total ~4.6 GB (well above GitHub's limits).
2. **Licenses** — each collection has its own license that restricts
   redistribution (3GPP, O-RAN Alliance, OpenROADM MSA).

Run the setup script to populate the folder:

```bash
./setup-yang-repos.sh
```

The script will:

| Folder | Source | Method |
|---|---|---|
| `yang-repos/yang/` | [YangModels/yang](https://github.com/YangModels/yang) | `git clone` (automatic) |
| `yang-repos/OpenROADM_MSA_Public/` | [OpenROADM/OpenROADM_MSA_Public](https://github.com/OpenROADM/OpenROADM_MSA_Public) | `git clone` (automatic) |
| `yang-repos/MnS/` | [3GPP SA5 forge](https://forge.3gpp.org/rep/sa5/MnS) | `git clone` (automatic) |
| `yang-repos/O-RAN.WG4.TS.MP-YANGs-R005-v20.00/` | O-RAN Alliance | manual download (see below) |
| `yang-repos/O-RAN.WG4.CTI-TMP-YANG-v03.00/` | O-RAN Alliance | manual download (see below) |
| `yang-repos/O-RAN.WG5.O-DU-O1.1-R003-v09.00/` | O-RAN Alliance | manual download (see below) |
| `yang-repos/O-RAN.WG5.O-CU-O1.1-R003-v07.00/` | O-RAN Alliance | manual download (see below) |
| `yang-repos/O-RAN.WG9.XTRP-SYN.1-R004-v06.00_YANG/` | O-RAN Alliance | manual download (see below) |

### Manual download — O-RAN Alliance spec packages

O-RAN Alliance specifications require registration at
<https://specifications.o-ran.org>.

1. Register / log in at <https://specifications.o-ran.org>.
2. Search for each spec listed in the table above.
3. Download the YANG model ZIP attachment from the spec page.
4. Extract the archive into the corresponding target folder under `yang-repos/`.

The script will print a reminder for any packages that are still missing.

## Standards used

| Standard | Description |
|---|---|
| RFC 8345 | `ietf-network` / `ietf-network-topology` — base topology model |
| RFC 8795 | `ietf-te-topology` — Traffic Engineering extensions |
| RFC 8561 | `ietf-microwave-topology` — Wireless transport layer |
| `ietf-l2-topology` | Ethernet / Layer-2 layer |
| `ietf-l3-unicast-topology` | IP / Layer-3 layer |
| `org-openroadm-network-topology` | DWDM / photonic layer |
| `o-ran-*` | O-RU, O-DU, O-CU topology augmentations |

## Contributing

Contributions are welcome.  Please open an issue or pull request.  When adding
or updating YANG model mappings, reference the relevant RFC or spec version in
the commit message.
