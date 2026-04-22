# OpenFronthaul-Switch — YANG Models

The **Open Fronthaul Switch** is a Layer-2 Ethernet switch that carries eCPRI or IEEE 1914.3
traffic between O-DU and O-RU units in the O-RAN Open Fronthaul. IEEE 802.1Q bridge management
and LLDP neighbor discovery are the primary management-plane functions. The switch fabric is
modeled using IEEE YANG standards (`ieee802-dot1q-bridge`, `ieee802-dot1ab-lldp`) with IETF
interface and routing models as the underlying infrastructure base.

## YANG Tree Entry Points

| Module | Role |
|--------|------|
| `ieee802-dot1q-bridge` | 🌳 **Root** — IEEE 802.1Q bridge management (`bridges` container): VLAN configuration, port membership, forwarding databases |
| `ieee802-dot1ab-lldp` | 🌳 **Root** — LLDP management (`lldp` container): neighbor discovery, chassis/port TLVs, remote system data |
| `ietf-interfaces` | 🌳 **Root** — RFC 8343 `interfaces` container; physical and logical switch port interfaces |
| `ietf-routing` | 🌳 **Root** — RFC 8022 `routing` container; imported by `ieee802-dot1ab-lldp` for routing management integration |

## IEEE 802.1Q Bridge Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ieee802-dot1q-bridge` | 2023-10-26 | 🌳 **Root** | IEEE 802.1Q — `bridges` and `bridge-ports` containers; VLAN membership, per-port filtering, spanning tree, and FDB management |
| `ieee802-dot1q-vlan-bridge` | 2018-03-07 | 📦 Groupings | IEEE 802.1Q VLAN bridge extensions; provides groupings for VLAN-aware bridge components, referenced by `ieee802-dot1q-bridge` |
| `ieee802-dot1q-types` | 2023-10-26 | 📦 Types | IEEE 802.1Q type definitions: VLAN-ID, priority, service VLAN identifiers, and filtering database types |
| `ieee802-types` | 2023-10-22 | 📦 Types | IEEE base types: MAC address (`mac-address`), port ID, EUI-64, and chassis ID formats used across all IEEE modules |

## IEEE 802.1AB LLDP Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ieee802-dot1ab-lldp` | 2022-03-15 | 🌳 **Root** | IEEE 802.1AB — `lldp` container; local system data (chassis ID, port ID, TTL), per-port LLDP enable/disable, and remote-systems-data for discovered neighbors |
| `ieee802-dot1ab-types` | 2022-03-15 | 📦 Types | LLDP type definitions: chassis-id-subtype, port-id-subtype, TLV type enumerations |

## IETF Base Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-interfaces` | 2018-02-20 | 🌳 **Root** | RFC 8343 — `interfaces` container; switch ports appear as interface entries; imported by the IEEE bridge and LLDP modules |
| `ietf-routing` | 2018-03-13 | 🌳 **Root** | RFC 8022 — `routing` container; pulled in as a transitive dependency by `ieee802-dot1ab-lldp` for management-plane routing integration |
| `ietf-yang-types` | 2025-12-22 | 📦 Types | RFC 6991 — `yang:date-and-time`, `yang:mac-address`, and other base types used by IETF and IEEE modules |
| `iana-if-type` | 2014-05-08 | 📦 Types | IANA interface type registry; provides `ianaift:ethernetCsmacd` and `ianaift:ieee8023adLag` identities for switch port interfaces |

## YANG Tree Generation

Run from the project root:

```bash
./generate-yang-tree.sh yang-per-network-function/OpenFronthaul-Switch
```

Output is written to `yang-tree.txt` in this folder. The tree covers four entry points:
`/bridges` (ieee802-dot1q-bridge), `/lldp` (ieee802-dot1ab-lldp), `/interfaces` (ietf-interfaces),
and `/routing` (ietf-routing).
