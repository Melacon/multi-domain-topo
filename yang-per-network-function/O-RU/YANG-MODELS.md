# O-RU — YANG Models

The **O-RAN Radio Unit (O-RU)** is the remote radio head in the O-RAN split architecture,
responsible for antenna transmission and reception. It communicates with the O-DU over the
Open Fronthaul M-Plane (management plane) using NETCONF/YANG as defined by O-RAN WG4
(MP-YANGs). The O-RU exposes a rich YANG management interface covering U-Plane configuration,
beamforming, synchronization, hardware inventory, software management, fault management,
security, and performance monitoring. Most functional modules define their own top-level
containers; augmentation is used selectively to extend IETF and IEEE standard models.

## YANG Tree Entry Points

The following modules define top-level `container` or `list` statements and serve as the
entry points for the YANG tree:

| Module | Top-level node(s) |
|--------|-------------------|
| `o-ran-ald-port` | `ald-ports` |
| `o-ran-antenna-calibration` | `antenna-calibration` |
| `o-ran-beamforming` | `beamforming-config` |
| `o-ran-certificates` | `certificates` (also augments ietf-keystore) |
| `o-ran-delay-management` | `delay-management` |
| `o-ran-dhcp` | `dhcp` |
| `o-ran-ecpri-delay` | `ecpri-delay-message` |
| `o-ran-ethernet-forwarding` | `ethernet-forwarding` |
| `o-ran-externalio` | `external-io` |
| `o-ran-fan` | `fan-tray` |
| `o-ran-file-management` | `file-management` |
| `o-ran-fm` | `active-alarm-list` |
| `o-ran-frequency-band-measurement` | `frequency-band-measurement` |
| `o-ran-laa` | `laa-config` |
| `o-ran-lbm` | `md-data-definitions` |
| `o-ran-module-cap` | `module-capability` |
| `o-ran-mplane-int` | `mplane-info` |
| `o-ran-operations` | `operational-info` |
| `o-ran-performance-management` | `performance-measurement-jobs` |
| `o-ran-processing-element` | `processing-elements` |
| `o-ran-shared-cell` | `shared-cell` |
| `o-ran-software-management` | `software-inventory` |
| `o-ran-supervision` | `supervision` |
| `o-ran-sync` | `sync` |
| `o-ran-transceiver` | `port-transceivers` |
| `o-ran-udp-echo` | `udp-echo` |
| `o-ran-uplane-conf` | `user-plane-configuration` |
| `o-ran-usermgmt` | `users` |
| `ieee802-dot1q-cfm` | `maintenance-domain` |
| `ieee802-dot1x` | `pae-system` (also augments ietf-interfaces) |
| `ietf-hardware` | `hardware` |
| `ietf-interfaces` | `interfaces` |
| `ietf-keystore` | `keystore` |
| `ietf-netconf-acm` | `nacm` |
| `ietf-netconf-monitoring` | `netconf-state` |
| `ietf-network-instance` | `network-instances` (also augments ietf-interfaces) |
| `ietf-ssh-common` | `supported-algorithms` |
| `ietf-subscribed-notifications` | `streams`, `subscriptions` |
| `ietf-system` | `system`, `system-state` |
| `ietf-tls-common` | `supported-algorithms` |
| `ietf-truststore` | `truststore` |
| `ietf-yang-schema-mount` | `schema-mounts` |

## O-RAN WG4 Core Functional Modules

### Radio Interface and U-Plane

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `o-ran-uplane-conf` | 2025-12-22 | 🌳 Root | User-plane configuration: array carriers, low-level RX/TX links, endpoint mapping, and compression |
| `o-ran-beamforming` | 2025-04-14 | 🌳 Root | Beamforming configuration: static and dynamic beamweights, beam groups, per-band capabilities |
| `o-ran-processing-element` | 2024-12-23 | 🌳 Root | Transport endpoint mapping: associates U-Plane traffic streams with eCPRI or Ethernet endpoints |
| `o-ran-delay-management` | 2025-04-14 | 🌳 Root | Fronthaul transport delay parameters: T12/T34, bandwidth-SCS delay profiles, TAD values |
| `o-ran-ecpri-delay` | 2023-12-23 | 🌳 Root | eCPRI one-way delay measurement (O-DU–O-RU latency characterization) |
| `o-ran-module-cap` | 2025-04-14 | 🌳 Root | Module capabilities: RU bands, CC counts, digital beamforming limits, feature list |
| `o-ran-compression-factors` | 2025-04-14 | 📦 Types | Compression method and IQ compression factor type definitions used by `o-ran-uplane-conf` |
| `o-ran-shared-cell` | 2024-12-23 | 🌳 Root | Shared cell (cascaded O-RU) topology: upstream/downstream link configuration |

### Antenna and RF

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `o-ran-antenna-calibration` | 2024-04-15 | 🌳 Root | Antenna calibration procedures and result reporting |
| `o-ran-transceiver` | 2025-12-22 | 🌳 Root | Port transceiver information: SFP/QSFP inventory, Tx/Rx power, temperature |
| `o-ran-frequency-band-measurement` | 2024-08-12 | 🌳 Root | Frequency band measurement results (RSSI, noise floor) |
| `o-ran-laa` | 2022-08-15 | 🌳 Root | Licensed Assisted Access (LAA) configuration for unlicensed spectrum coexistence |
| `o-ran-laa-operations` | 2021-12-01 | 📦 Groupings | LAA channel access procedure groupings used by `o-ran-laa` |

### Synchronization

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `o-ran-sync` | 2025-08-11 | 🌳 Root | Synchronization configuration and state: PTP, SyncE, GNSS, air-interface sync modes and status |

### M-Plane Transport and Access

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `o-ran-mplane-int` | 2025-12-22 | 🌳 Root | M-Plane interface: NETCONF call-home configuration, access control, VLAN/interface bindings |
| `o-ran-dhcp` | 2024-08-12 | 🌳 Root | DHCP client configuration and obtained lease data for O-RU management addressing |
| `o-ran-ethernet-forwarding` | 2021-12-01 | 🌳 Root | Ethernet forwarding and VLAN configuration for the internal O-RU management bridge |
| `o-ran-interfaces` | 2025-12-22 | 🔀 Augment | Augments `ietf-interfaces` with O-RAN fronthaul port attributes (MAC learning, M-Plane VLAN) |
| `o-ran-udp-echo` | 2019-02-04 | 🌳 Root | UDP echo server configuration for one-way delay measurement |

### Operations, Administration, and Maintenance

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `o-ran-operations` | 2025-12-22 | 🌳 Root | Operational information: restart cause, re-call-home timer, operational state |
| `o-ran-supervision` | 2022-12-05 | 🌳 Root | Supervision watchdog timer and notification for M-Plane session monitoring |
| `o-ran-fm` | 2024-08-12 | 🌳 Root | Fault management: active alarm list and alarm notification definitions |
| `o-ran-file-management` | 2024-12-23 | 🌳 Root | File upload/download RPCs and file inventory for log and configuration transfers |
| `o-ran-software-management` | 2025-08-11 | 🌳 Root | Software slot inventory, activation, and download RPCs |
| `o-ran-trace` | 2022-08-15 | 📦 Groupings | Trace collection groupings (referenced by other modules; no own top-level container) |
| `o-ran-troubleshooting` | 2025-04-14 | 📦 Groupings | Troubleshooting data collection groupings |
| `o-ran-lbm` | 2024-08-12 | 🌳 Root | Ethernet Loopback Measurement (IEEE 802.1ag-style): maintenance domain data definitions |
| `o-ran-ieee802-dot1q-cfm` | 2023-04-10 | 🔀 Augment | Augments `ieee802-dot1q-cfm` with O-RAN-specific CFM extensions |

### Hardware

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `o-ran-hardware` | 2025-04-14 | 🔀 Augment | Augments `ietf-hardware` with O-RAN hardware component labels and inventory extensions |
| `o-ran-fan` | 2025-08-11 | 🌳 Root | Fan tray inventory and cooling operational state |
| `o-ran-externalio` | 2023-08-14 | 🌳 Root | External GPIO input/output port state and configuration |
| `o-ran-ald-port` | 2025-04-14 | 🌳 Root | Antenna Line Device (ALD) port inventory (AISG port management) |
| `o-ran-ald` | 2021-12-01 | 🔀 Augment | Augments `o-ran-ald-port` with ALD device communication RPCs |

### Security and Access Control

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `o-ran-certificates` | 2025-12-22 | 🌳 Root + 🔀 Augment | Certificate inventory and CSR/install RPCs; also augments `ietf-keystore` |
| `o-ran-usermgmt` | 2024-08-12 | 🌳 Root | User account management: local user list, password policy, SUDO rules |

### Performance Management

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `o-ran-performance-management` | 2025-12-22 | 🌳 Root | PM job configuration: measurement intervals, file upload triggers, measurement object references |
| `o-ran-pm-general` | 2025-12-22 | 📦 Groupings | General PM groupings and counter type definitions shared across PM statistics modules |
| `o-ran-pm-rx-windows-stats` | 2025-12-22 | 📦 Groupings | RX window statistics: on-time, early, late, and FFT overflow counters |
| `o-ran-pm-tx-stats` | 2025-12-22 | 📦 Groupings | TX statistics per carrier |
| `o-ran-pm-tx-antenna-stats` | 2025-12-22 | 📦 Groupings | TX per-antenna power and error statistics |
| `o-ran-pm-tx-output-power-stats` | 2025-12-22 | 📦 Groupings | TX output power measurement statistics |
| `o-ran-pm-tssi-stats` | 2025-12-22 | 📦 Groupings | TX power spectral density statistics |
| `o-ran-pm-rssi-stats` | 2025-12-22 | 📦 Groupings | RSSI (Received Signal Strength Indicator) statistics per antenna |
| `o-ran-pm-symbol-rssi-stats` | 2025-12-22 | 📦 Groupings | Per-symbol RSSI statistics |
| `o-ran-pm-transceiver-stats` | 2025-12-22 | 📦 Groupings | Transceiver optical power, temperature, and bias statistics |
| `o-ran-pm-ethernet-stats` | 2025-12-22 | 📦 Groupings | Fronthaul Ethernet port traffic counters |
| `o-ran-pm-epe-statistics` | 2025-12-22 | 📦 Groupings | Energy and power efficiency (EPE) statistics |
| `o-ran-pm-shared-cell-stats` | 2025-12-22 | 📦 Groupings | Shared cell (cascaded O-RU) link statistics |

### O-RAN Common Type Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `o-ran-common-yang-types` | 2025-04-14 | 📦 Types | O-RAN common types: frequencies, bandwidths, SCS, slot/symbol indices, TX/RX window bounds |
| `o-ran-common-identity-refs` | 2022-08-15 | 📦 Types | O-RAN identity references: interface type, hardware component, and feature identity bases |
| `o-ran-wg4-features` | 2025-12-22 | 📦 Types | WG4 feature identities used in `if-feature` guards throughout O-RAN WG4 modules |
| `o-ran-ves-subscribed-notifications` | 2020-12-10 | 🔀 Augment | Augments `ietf-subscribed-notifications` with VES (VNF Event Stream) transport binding |

## IEEE Security and OAM Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ieee802-dot1q-cfm` | 2022-01-19 | 🌳 Root | IEEE 802.1Q CFM (Connectivity Fault Management): maintenance domains, MEPs, CCM |
| `ieee802-dot1q-cfm-types` | 2022-10-29 | 📦 Types | CFM type definitions: MEP-ID, MAID, priority, CCM interval |
| `ieee802-dot1x` | 2020-02-18 | 🌳 Root + 🔀 Augment | IEEE 802.1X port-based access control: PAE system, authenticator/supplicant state; augments ietf-interfaces with port-access-entity |
| `ieee802-dot1x-types` | 2020-02-18 | 📦 Types | 802.1X type definitions: port-access-entity roles, controlled/uncontrolled port states |
| `ieee802-dot1q-types` | 2023-10-26 | 📦 Types | IEEE 802.1Q VLAN ID, priority, and service VLAN types |
| `ieee802-types` | 2023-10-22 | 📦 Types | IEEE base types: MAC address, EUI-64, chassis and port ID formats |

## IETF Protocol Modules

### NETCONF and System Management

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-netconf-acm` | 2018-02-14 | 🌳 Root | RFC 8341 — `nacm` container; NETCONF access control rules for O-RU operations |
| `ietf-netconf-monitoring` | 2010-10-04 | 🌳 Root | RFC 6022 — `netconf-state` container; NETCONF session and capability monitoring |
| `ietf-system` | 2014-08-06 | 🌳 Root | RFC 7317 — `system` container; hostname, NTP, DNS, authentication configuration |
| `ietf-subscribed-notifications` | 2019-09-09 | 🌳 Root | RFC 8639 — `streams` and `subscriptions` containers; YANG push subscription management |
| `ietf-yang-schema-mount` | 2019-01-14 | 🌳 Root | RFC 8528 — `schema-mounts` container; schema mount point declarations |
| `ietf-restconf` | 2017-01-26 | 📦 Types | RFC 8040 — RESTCONF error and media-type type definitions |

### Interface and Network Instance

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-interfaces` | 2018-02-20 | 🌳 Root | RFC 8343 — `interfaces` container; fronthaul Ethernet and logical interfaces |
| `ietf-ip` | 2018-02-22 | 🔀 Augment | RFC 8344 — augments `ietf-interfaces` with IPv4/IPv6 address configuration |
| `ietf-network-instance` | 2019-01-21 | 🌳 Root + 🔀 Augment | RFC 8529 — `network-instances` container and augmentation of `ietf-interfaces` for VRF binding |

### Hardware

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-hardware` | 2018-03-13 | 🌳 Root | RFC 8348 — `hardware` container; physical component tree (chassis, cards, ports, sensors) |

### Cryptography and Security

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-keystore` | 2024-10-10 | 🌳 Root | RFC 9642 — `keystore` container; asymmetric key pairs and certificate storage |
| `ietf-truststore` | 2024-10-10 | 🌳 Root | RFC 9641 — `truststore` container; trusted certificate authority bags |
| `ietf-crypto-types` | 2024-10-10 | 📦 Types | RFC 9640 — cryptographic algorithm identities and key format types |
| `ietf-ssh-common` | 2024-10-10 | 🌳 Root | RFC 9644 — `supported-algorithms` for SSH key exchange, host-key, encryption, MAC |
| `ietf-tls-common` | 2024-10-10 | 🌳 Root | RFC 9645 — `supported-algorithms` for TLS cipher suites and key exchange |
| `ietf-x509-cert-to-name` | 2014-12-10 | 📦 Types | RFC 7407 — X.509 certificate field to NETCONF username mapping types |

### DHCP

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-dhcpv6-common` | 2022-06-20 | 📦 Types | DHCPv6 common option type definitions |
| `ietf-dhcpv6-types` | 2018-09-04 | 📦 Types | DHCPv6 base type definitions (DUID, option codes) |

### Common Types

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `ietf-inet-types` | 2025-12-22 | 📦 Types | RFC 6991 — IP address and prefix types |
| `ietf-yang-types` | 2025-12-22 | 📦 Types | RFC 6991 — `yang:date-and-time`, `yang:counter64`, and other base types |

## IANA Registry Modules

| Module | Revision | Role | Description |
|--------|----------|------|-------------|
| `iana-hardware` | 2018-03-13 | 📦 Types | IANA hardware component type identities (chassis, module, port, sensor) |
| `iana-if-type` | 2014-05-08 | 📦 Types | IANA interface type registry (ethernetCsmacd, softwareLoopback, etc.) |
| `iana-crypt-hash` | 2014-08-06 | 📦 Types | IANA cryptographic hash algorithm identities (MD5, SHA-256, etc.) for password hashing |
| `iana-ssh-encryption-algs` | 2024-10-16 | 📦 Types | IANA SSH encryption algorithm identities |
| `iana-ssh-key-exchange-algs` | 2024-10-16 | 📦 Types | IANA SSH key exchange algorithm identities |
| `iana-ssh-mac-algs` | 2024-10-16 | 📦 Types | IANA SSH MAC algorithm identities |
| `iana-ssh-public-key-algs` | 2024-10-16 | 📦 Types | IANA SSH public key algorithm identities |
| `iana-tls-cipher-suite-algs` | 2024-10-16 | 📦 Types | IANA TLS cipher suite identities |

## YANG Tree Generation

Run from the project root:

```bash
./generate-yang-tree.sh yang-per-network-function/O-RU
```

Output is written to `yang-tree.txt` in this folder. The tree covers all 43 root module
entry points listed above. O-RAN augmentation modules (o-ran-hardware, o-ran-interfaces, etc.)
are automatically folded into their respective IETF/IEEE base module trees by pyang.
