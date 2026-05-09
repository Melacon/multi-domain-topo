#!/usr/bin/env python3
"""
generate_html.py — reads ietf-network-topology.json (microwave topology),
                   writes ietf-network-topology.html

Supports multi-network files: the carrier layer (MW-1-CARRIERS) is rendered
at the bottom and the radio-link layer (MW-1) at the top.  Supporting-
termination-point and supporting-link relationships are drawn as dashed
grey edges between the layers.

Usage:
    python3 generate_html.py [input.json] [output.html]

Defaults:
    input  = ietf-network-topology.json  (relative to this script)
    output = ietf-network-topology.html  (same directory)
"""

import json
import sys
from pathlib import Path


def _short(urn: str) -> str:
    """Return the last colon-separated segment of a URN.

    'urn:if:WT-1:RLT-1:CT-1'  →  'CT-1'
    'urn:node:WT-1'             →  'WT-1'
    """
    return urn.split(":")[-1]


def parse_topology(json_path: Path):
    with open(json_path) as f:
        data = json.load(f)

    all_networks = data["ietf-network:networks"]["network"]

    cy_nodes = []
    cy_edges = []

    # link_id → (src_uid, dst_uid) — built in first pass for supporting-link lookup
    link_uid_map: dict[str, tuple[str, str]] = {}
    # Collected supporting-link associations for second pass
    pending_sup_links: list[tuple[str, str, list[dict]]] = []
    seen_sup_link_edges: set[str] = set()

    for net in all_networks:
        network_id = net["network-id"]
        net_label  = _short(network_id)

        # ── nodes ────────────────────────────────────────────────────────────
        for node in net.get("node", []):
            node_id     = node["node-id"]
            compound_id = f"{network_id}::{node_id}"

            cy_nodes.append({
                "id":       compound_id,
                "label":    _short(node_id),
                "type":     "WT-DEVICE",
                "network":  net_label,
                "node_uri": node_id,
                "parent":   None,
            })

            for tp in node.get("ietf-network-topology:termination-point", []):
                tp_id       = tp["tp-id"]
                mw_tp       = (tp.get("ietf-te-topology:te", {})
                                 .get("ietf-microwave-topology:mw-tp", {}))
                tp_id_short = _short(tp_id)

                if "microwave-rltp" in mw_tp:
                    tp_type = "RLTP"
                elif "microwave-ctp" in mw_tp:
                    tp_type = "CTP"
                elif tp_id_short.startswith("ETH-"):
                    tp_type = "ETH-PORT"
                elif tp_id_short.startswith("PORT-"):
                    tp_type = "PHYSICAL-PORT"
                else:
                    tp_type = "TP"

                tp_uid = f"{network_id}::{tp_id}"

                cy_nodes.append({
                    "id":      tp_uid,
                    "label":   tp_id_short,
                    "type":    tp_type,
                    "network": net_label,
                    "tp_uri":  tp_id,
                    "parent":  compound_id,
                })

                # supporting-termination-point → SUPPORTING-TP edges
                for stp in tp.get(
                        "ietf-network-topology:supporting-termination-point", []):
                    sup_uid = f"{stp['network-ref']}::{stp['tp-ref']}"
                    cy_edges.append({
                        "id":     f"stp::{tp_uid}→{sup_uid}",
                        "source": tp_uid,
                        "target": sup_uid,
                        "type":   "SUPPORTING-TP",
                        "label":  "",
                    })

        # ── links ────────────────────────────────────────────────────────────
        for link in net.get("ietf-network-topology:link", []):
            link_id  = link["link-id"]
            src_tp   = link["source"]["source-tp"]
            src_node = link["source"]["source-node"]
            dst_tp   = link["destination"]["dest-tp"]
            dst_node = link["destination"]["dest-node"]

            src_uid = f"{network_id}::{src_tp}"
            dst_uid = f"{network_id}::{dst_tp}"

            # Record for supporting-link lookup
            link_uid_map[link_id] = (src_uid, dst_uid)

            # Collect supporting-link for second pass
            sup_links = link.get("ietf-network-topology:supporting-link", [])
            if sup_links:
                pending_sup_links.append((src_uid, dst_uid, sup_links))

            mw_link = (link.get("ietf-te-topology:te", {})
                           .get("te-link-attributes", {})
                           .get("ietf-microwave-topology:mw-link", {}))

            if "microwave-radio-link" in mw_link:
                link_type  = "RADIO-LINK"
                mode       = mw_link["microwave-radio-link"].get("rlt-mode", {})
                bonded     = mode.get("num-bonded-carriers", "?")
                protecting = mode.get("num-protecting-carriers", "?")
                label      = f"{bonded}+{protecting} mode"
                extra      = {"bonded": bonded, "protecting": protecting}
            elif "microwave-carrier" in mw_link:
                link_type = "CARRIER"
                mc        = mw_link["microwave-carrier"]
                tx_khz    = mc.get("tx-frequency", 0)
                label     = f"{tx_khz // 1000} MHz"
                extra     = {"tx_frequency": tx_khz}
            elif _short(src_tp).startswith("ETH-"):
                link_type = "ETH-LINK"
                label     = ""
                extra     = {}
            else:
                link_type = "UNKNOWN"
                label     = ""
                extra     = {}

            cy_edges.append({
                "id":          link_id,
                "source":      src_uid,
                "target":      dst_uid,
                "source_node": _short(src_node),
                "target_node": _short(dst_node),
                "type":        link_type,
                "label":       label,
                **extra,
            })

    # ── supporting-link edges (second pass, after link_uid_map is complete) ──
    # For each link that has supporting-link references, draw a dashed edge
    # from the dependent link's source TP to the supporting link's source TP.
    # This makes the "carried by" relationship visible across network layers.
    for dep_src_uid, dep_dst_uid, sup_link_refs in pending_sup_links:
        for sl in sup_link_refs:
            sup_link_id = sl["link-ref"]
            if sup_link_id not in link_uid_map:
                continue
            sup_src_uid, _ = link_uid_map[sup_link_id]
            # One edge per (dep_src, sup_src) pair — deduplicate
            edge_id = f"sl::{dep_src_uid}→{sup_src_uid}"
            if edge_id in seen_sup_link_edges:
                continue
            seen_sup_link_edges.add(edge_id)
            cy_edges.append({
                "id":     edge_id,
                "source": dep_src_uid,
                "target": sup_src_uid,
                "type":   "SUPPORTING-LINK",
                "label":  "",
            })

    return all_networks, cy_nodes, cy_edges


def calc_positions(all_networks: list, cy_nodes: list[dict]) -> dict:
    """
    Four-row preset layout (top = logical, bottom = physical):

      Row 0  MW-1           — radio-link layer   (RLTP)
      Row 1  MW-1-CARRIERS  — carrier layer      (CTP)
      Row 2  MW-1-ETHERNET  — ethernet layer     (ETH-PORT)
      Row 3  MW-1-PHYSICAL  — physical layer     (PORT)

    Networks are ordered bottom-up by their position in the JSON file
    (first = bottom row). WT devices are placed left/right; TPs stacked
    vertically inside each compound.
    """
    positions: dict = {}

    col_x = [220, 720]   # x centres for WT-1 and WT-2
    row_y = {}           # network_id → base y for that layer

    # Assign rows: first network in file = bottom row (highest y value)
    n_nets = len(all_networks)
    row_height = 260
    for i, net in enumerate(all_networks):
        row = n_nets - 1 - i   # 0 = top
        row_y[net["network-id"]] = 180 + row * row_height

    # TP type display order within a compound
    TYPE_ORDER = {"RLTP": 0, "CTP": 1, "ETH-PORT": 2, "PHYSICAL-PORT": 3, "TP": 4}

    devices_per_net: dict[str, list[str]] = {}
    for n in cy_nodes:
        if n["type"] == "WT-DEVICE":
            net_id = next(
                (nw["network-id"] for nw in all_networks
                 if _short(nw["network-id"]) == n["network"]),
                n["network"],
            )
            devices_per_net.setdefault(net_id, []).append(n["id"])

    for net_id, device_ids in devices_per_net.items():
        base_y = row_y.get(net_id, 300)

        for idx, dev_id in enumerate(device_ids):
            x = col_x[idx] if idx < len(col_x) else col_x[-1] + idx * 500

            children = [n for n in cy_nodes if n.get("parent") == dev_id]
            ordered  = sorted(
                children,
                key=lambda n: (TYPE_ORDER.get(n["type"], 9), n["label"]),
            )
            step    = 65
            start_y = base_y - (len(ordered) - 1) * step / 2

            for i, child in enumerate(ordered):
                positions[child["id"]] = {
                    "x": round(x, 1),
                    "y": round(start_y + i * step, 1),
                }

    return positions


def build_elements_js(cy_nodes: list[dict],
                      cy_edges: list[dict],
                      positions: dict) -> str:
    lines = ["["]
    for n in cy_nodes:
        data = {k: v for k, v in n.items() if v is not None}
        pos  = positions.get(n["id"])
        if pos:
            lines.append(f"  {{ data: {json.dumps(data)}, "
                         f"position: {json.dumps(pos)} }},")
        else:
            lines.append(f"  {{ data: {json.dumps(data)} }},")
    lines.append("")
    for e in cy_edges:
        lines.append(f"  {{ data: {json.dumps(e)} }},")
    lines.append("]")
    return "\n".join(lines)


# ── HTML template ─────────────────────────────────────────────────────────────

HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Microwave Topology — {network_id}</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.28.1/cytoscape.min.js"></script>
  <script src="https://unpkg.com/cytoscape-fcose/cytoscape-fcose.js"></script>
  <script src="https://unpkg.com/cytoscape-svg/cytoscape-svg.js"></script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: Arial, sans-serif; background: #f8fafc; }}
    #cy {{ width: 100vw; height: 100vh; display: block; }}
    #toolbar {{
      position: absolute; top: 12px; left: 12px; z-index: 100;
      display: flex; flex-direction: column; gap: 6px;
    }}
    button {{
      padding: 6px 14px; border: 1px solid #9ca3af; background: white;
      border-radius: 6px; cursor: pointer; font-size: 13px; color: #111827;
    }}
    button:hover {{ background: #f3f4f6; }}
    #toolbar hr {{ border: none; border-top: 1px solid #e5e7eb; margin: 2px 0; }}
    #legend {{
      position: absolute; bottom: 16px; left: 16px;
      background: white; border: 1px solid #d1d5db; border-radius: 10px;
      padding: 14px 18px; font-size: 12px; line-height: 2;
      box-shadow: 0 1px 4px rgba(0,0,0,.08);
    }}
    #legend strong {{ display: block; margin-bottom: 4px; font-size: 13px; }}
    .li  {{ display: flex; align-items: center; gap: 8px; }}
    .sw  {{ width: 22px; height: 14px; border-radius: 3px; border: 2px solid; flex-shrink: 0; }}
    .lsw {{ width: 30px; height: 3px; border-radius: 2px; flex-shrink: 0; }}
  </style>
</head>
<body>

<div id="toolbar">
  <button onclick="cy.fit(undefined, 60)">Fit to view</button>
  <hr>
  <button onclick="runLayout('preset')"  title="Fixed layered positions">Preset</button>
  <button onclick="runLayout('fcose')"   title="Fast Compound Spring Embedder">fCoSE …</button>
  <button onclick="runLayout('cose')"    title="Standard force-directed layout">CoSE</button>
  <hr>
  <button onclick="exportSVG()">Export SVG</button>
</div>

<div id="legend">
  <strong>{network_id}</strong>
  <div class="li"><span class="sw"  style="background:#dbeafe;border-color:#2563eb"></span>Wireless Transport device</div>
  <div class="li"><span class="sw"  style="background:#fef3c7;border-color:#d97706"></span>Radio Link Termination Point (RLTP)</div>
  <div class="li"><span class="sw"  style="background:#f3e8ff;border-color:#9333ea"></span>Carrier Termination Point (CTP)</div>
  <div class="li"><span class="lsw" style="background:#1d4ed8"></span>Radio link (bonded carriers)</div>
  <div class="li"><span class="lsw" style="background:#9333ea"></span>Carrier (TX frequency)</div>
  <div class="li"><span class="sw"  style="background:#d1fae5;border-color:#059669"></span>Ethernet port (ETH-PORT, l2vlan)</div>
  <div class="li"><span class="sw"  style="background:#f3f4f6;border-color:#6b7280"></span>Physical port (PORT, ethernetCsmacd)</div>
  <div class="li"><span class="lsw" style="background:#059669"></span>Ethernet link (aggregated via RLT)</div>
  <div class="li"><span class="lsw" style="background:#f59e0b;border-top:2px dashed #f59e0b;height:0"></span>Supporting link (carried-by relationship)</div>
  <div class="li"><span class="lsw" style="background:#9ca3af;border-top:2px dotted #9ca3af;height:0"></span>Supporting termination point</div>
</div>

<div id="cy"></div>

<script>
// Auto-generated from {source_file} — do not edit by hand.
const elements = {elements_js};

const cy = cytoscape({{
  container: document.getElementById('cy'),
  elements,
  style: [
    {{
      selector: 'node[type = "WT-DEVICE"]',
      style: {{
        content: 'data(label)',
        'text-valign': 'top', 'text-halign': 'center',
        'font-weight': 'bold', 'font-size': 16, color: '#1e3a8a',
        'background-color': '#dbeafe', 'border-color': '#2563eb', 'border-width': 2.5,
        padding: '36px', shape: 'roundrectangle',
      }},
    }},
    {{
      selector: 'node[type = "RLTP"]',
      style: {{
        content: 'data(label)',
        'text-valign': 'center', 'font-size': 11, 'font-weight': 'bold', color: '#78350f',
        width: 70, height: 30,
        'background-color': '#fef3c7', 'border-color': '#d97706', 'border-width': 2,
        shape: 'roundrectangle',
      }},
    }},
    {{
      selector: 'node[type = "CTP"]',
      style: {{
        content: 'data(label)',
        'text-valign': 'center', 'font-size': 11, color: '#581c87',
        width: 70, height: 30,
        'background-color': '#f3e8ff', 'border-color': '#9333ea', 'border-width': 2,
        shape: 'roundrectangle',
      }},
    }},
    {{
      selector: 'edge[type = "RADIO-LINK"]',
      style: {{
        width: 4, 'line-color': '#1d4ed8',
        'curve-style': 'bezier',
        'target-arrow-shape': 'triangle', 'target-arrow-color': '#1d4ed8',
        'arrow-scale': 1.2,
        label: 'data(label)', 'font-size': 11, color: '#1e3a8a',
        'font-weight': 'bold',
        'text-background-color': '#eff6ff', 'text-background-opacity': 1,
        'text-background-padding': '3px', 'text-rotation': 'autorotate',
      }},
    }},
    {{
      selector: 'edge[type = "CARRIER"]',
      style: {{
        width: 2, 'line-color': '#9333ea',
        'curve-style': 'bezier',
        'target-arrow-shape': 'triangle', 'target-arrow-color': '#9333ea',
        'arrow-scale': 0.8,
        label: 'data(label)', 'font-size': 10, color: '#6b21a8',
        'text-background-color': '#faf5ff', 'text-background-opacity': 1,
        'text-background-padding': '2px', 'text-rotation': 'autorotate',
      }},
    }},
    {{
      selector: 'node[type = "ETH-PORT"]',
      style: {{
        content: 'data(label)',
        'text-valign': 'center', 'font-size': 10, color: '#065f46',
        width: 70, height: 26,
        'background-color': '#d1fae5', 'border-color': '#059669', 'border-width': 1.5,
        shape: 'roundrectangle',
      }},
    }},
    {{
      selector: 'node[type = "PHYSICAL-PORT"]',
      style: {{
        content: 'data(label)',
        'text-valign': 'center', 'font-size': 10, color: '#374151',
        width: 70, height: 26,
        'background-color': '#f3f4f6', 'border-color': '#6b7280', 'border-width': 1.5,
        shape: 'roundrectangle',
      }},
    }},
    {{
      selector: 'edge[type = "ETH-LINK"]',
      style: {{
        width: 1.5, 'line-color': '#059669',
        'curve-style': 'bezier',
        'target-arrow-shape': 'triangle', 'target-arrow-color': '#059669',
        'arrow-scale': 0.7,
        opacity: 0.8,
      }},
    }},
    {{
      selector: 'edge[type = "SUPPORTING-LINK"]',
      style: {{
        width: 2, 'line-color': '#f59e0b', 'line-style': 'dashed',
        'curve-style': 'bezier',
        'target-arrow-shape': 'triangle', 'target-arrow-color': '#f59e0b',
        'arrow-scale': 0.9,
        opacity: 0.85,
        label: 'data(label)', 'font-size': 9,
      }},
    }},
    {{
      selector: 'edge[type = "SUPPORTING-TP"]',
      style: {{
        width: 1.5, 'line-color': '#9ca3af', 'line-style': 'dotted',
        'curve-style': 'bezier',
        'target-arrow-shape': 'triangle', 'target-arrow-color': '#9ca3af',
        'arrow-scale': 0.7,
        opacity: 0.8,
      }},
    }},
    {{ selector: ':selected', style: {{ 'overlay-color': '#f59e0b', 'overlay-opacity': 0.25 }} }},
  ],
  layout: {{ name: 'preset' }},
}});

cy.fit(undefined, 60);

const layouts = {{
  preset: {{
    name: 'preset',
    animate: true, animationDuration: 500, fit: true, padding: 60,
  }},
  fcose: {{
    name: 'fcose',
    animate: true, animationDuration: 700,
    fit: true, padding: 60,
    nodeRepulsion: 8000,
    idealEdgeLength: 160,
    edgeElasticity: 0.45,
    numIter: 2500,
    gravity: 0.25,
    gravityRange: 3.8,
    nestingFactor: 0.1,
    randomize: true,
    tile: true,
  }},
  cose: {{
    name: 'cose',
    animate: true, animationDuration: 700,
    fit: true, padding: 60,
    nodeRepulsion: 8000,
    componentSpacing: 80,
  }},
}};

function runLayout(name) {{
  cy.layout(layouts[name] || layouts.fcose).run();
}}

function exportSVG() {{
  const svg  = cy.svg({{ scale: 1.5, full: true, bg: '#ffffff' }});
  const blob = new Blob([svg], {{ type: 'image/svg+xml' }});
  const url  = URL.createObjectURL(blob);
  const a    = Object.assign(document.createElement('a'),
                 {{ href: url, download: '{output_stem}.svg' }});
  a.click();
  URL.revokeObjectURL(url);
}}
</script>
</body>
</html>
"""


def main():
    script_dir = Path(__file__).parent
    json_path  = Path(sys.argv[1]) if len(sys.argv) > 1 \
                 else script_dir / "ietf-network-topology.json"
    html_path  = Path(sys.argv[2]) if len(sys.argv) > 2 \
                 else script_dir / "ietf-network-topology.html"

    print(f"Reading  {json_path}")
    all_networks, cy_nodes, cy_edges = parse_topology(json_path)

    # Use the last network's ID as the page title (the top-level logical layer)
    network_id  = all_networks[-1]["network-id"]
    positions   = calc_positions(all_networks, cy_nodes)
    elements_js = build_elements_js(cy_nodes, cy_edges, positions)

    html = HTML_TEMPLATE.format(
        network_id  = network_id,
        source_file = json_path.name,
        output_stem = html_path.stem,
        elements_js = elements_js,
    )

    html_path.write_text(html, encoding="utf-8")
    print(f"Written  {html_path}")
    print(f"         {len(cy_nodes)} nodes, {len(cy_edges)} edges")


if __name__ == "__main__":
    main()
