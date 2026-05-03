#!/usr/bin/env python3
"""
generate_html.py  —  reads openroadm-topology.xml, writes openroadm-topology.html

Usage:
    python3 generate_html.py [input.xml] [output.html]

Defaults:
    input  = openroadm-topology.xml  (relative to this script)
    output = openroadm-topology.html (same directory)
"""

import json
import math
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# ── XML namespaces ──────────────────────────────────────────────────────────
NS = {
    "net":    "urn:ietf:params:xml:ns:yang:ietf-network",
    "topo":   "urn:ietf:params:xml:ns:yang:ietf-network-topology",
    "common": "http://org/openroadm/common/network",
}


def parse_topology(xml_path: Path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    cy_nodes = []
    cy_edges = []
    roadm_parents: set[str] = set()
    seen_pairs: set[tuple] = set()   # dedup bidirectional links

    # ── nodes ──────────────────────────────────────────────────────────────
    for node in root.findall("net:node", NS):
        node_id   = node.find("net:node-id", NS).text
        type_el   = node.find("common:node-type", NS)
        node_type = type_el.text if type_el is not None else "UNKNOWN"

        # resolve parent ROADM via supporting-node → openroadm-network
        parent = None
        for sn in node.findall("net:supporting-node", NS):
            net_ref  = sn.find("net:network-ref", NS)
            node_ref = sn.find("net:node-ref", NS)
            if net_ref is not None and net_ref.text == "openroadm-network":
                parent = node_ref.text
                break

        cy_nodes.append({"id": node_id, "type": node_type, "parent": parent})
        if parent:
            roadm_parents.add(parent)

    # insert compound ROADM containers at the front
    for roadm in sorted(roadm_parents):
        cy_nodes.insert(0, {"id": roadm, "label": roadm, "type": "ROADM", "parent": None})

    # ── links ──────────────────────────────────────────────────────────────
    for link in root.findall("topo:link", NS):
        link_id   = link.find("topo:link-id", NS).text
        type_el   = link.find("common:link-type", NS)
        link_type = type_el.text if type_el is not None else "UNKNOWN"

        src  = link.find("topo:source/topo:source-node", NS).text
        dst  = link.find("topo:destination/topo:dest-node", NS).text
        pair = tuple(sorted([src, dst]))

        # deduplicate EXPRESS-LINK only (undirected); ROADM-TO-ROADM is kept both ways
        if link_type == "EXPRESS-LINK":
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)

        # drop reverse direction of add/drop — keep ADD only
        if link_type == "DROP-LINK":
            continue

        edge: dict = {"id": link_id, "source": src, "target": dst, "type": link_type}

        if link_type == "ROADM-TO-ROADM":
            # build a short span label  e.g.  "A1–B1"
            def short(node_id: str) -> str:
                # ROADM-A1-DEG1  →  A1
                parts = node_id.split("-")
                return parts[1] if len(parts) >= 2 else node_id
            edge["label"] = f"{short(src)}–{short(dst)}"

        cy_edges.append(edge)

    return cy_nodes, cy_edges, sorted(roadm_parents)


def calc_positions(roadm_list: list[str]) -> dict:
    """
    Place ROADM groups in a circle; within each group arrange
    DEG nodes on top row, SRG nodes on bottom row.
    """
    positions: dict = {}
    n  = len(roadm_list)
    cx, cy_center, radius = 480, 380, 260

    for i, roadm in enumerate(roadm_list):
        # start at top (π/2) and go clockwise
        angle = math.pi / 2 - (2 * math.pi * i / n)
        rx = cx + radius * math.cos(angle)
        ry = cy_center - radius * math.sin(angle)

        # fixed child layout: DEG row above, SRG row below
        child_offsets = {
            f"{roadm}-DEG1": (+38, -24),
            f"{roadm}-DEG2": (-38, -24),
            f"{roadm}-SRG1": (+38, +24),
            f"{roadm}-SRG3": (-38, +24),
        }
        for child_id, (dx, dy) in child_offsets.items():
            positions[child_id] = {"x": round(rx + dx, 1), "y": round(ry + dy, 1)}

    return positions


def build_elements_js(cy_nodes, cy_edges, positions) -> str:
    """Render the Cytoscape elements array as a JS literal."""
    lines = ["["]

    for n in cy_nodes:
        data = {k: v for k, v in n.items() if v is not None}
        if not data.get("label"):
            # use last segment as label for sub-nodes  (ROADM-A1-DEG1 → DEG1)
            data["label"] = n["id"].split("-")[-1] if "-" in n["id"] else n["id"]
        pos = positions.get(n["id"])
        if pos:
            lines.append(f'  {{ data: {json.dumps(data)}, position: {json.dumps(pos)} }},')
        else:
            lines.append(f'  {{ data: {json.dumps(data)} }},')

    lines.append("")
    for e in cy_edges:
        lines.append(f'  {{ data: {json.dumps(e)} }},')

    lines.append("]")
    return "\n".join(lines)


HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>OpenROADM Topology — {network_id}</title>
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
  <button onclick="cy.fit(undefined, 40)">Fit to view</button>
  <hr>
  <button onclick="runLayout('preset')"  title="Fixed ring positions from XML">Preset (ring)</button>
  <button onclick="runLayout('fcose')"   title="Fast Compound Spring Embedder — minimises edge crossings">fCoSE ✦</button>
  <button onclick="runLayout('cose')"    title="Standard force-directed layout">CoSE</button>
  <hr>
  <button onclick="exportSVG()">Export SVG</button>
</div>

<div id="legend">
  <strong>{network_id}</strong>
  <div class="li"><span class="sw"  style="background:#dbeafe;border-color:#2563eb"></span>ROADM node</div>
  <div class="li"><span class="sw"  style="background:#fef3c7;border-color:#d97706"></span>DEGREE sub-node</div>
  <div class="li"><span class="sw"  style="background:#dcfce7;border-color:#16a34a"></span>SRG sub-node</div>
  <div class="li"><span class="lsw" style="background:#2563eb"></span>ROADM-to-ROADM span</div>
  <div class="li"><span class="lsw" style="background:#9ca3af"></span>Express link</div>
  <div class="li"><span class="lsw" style="background:#16a34a"></span>Add / Drop link</div>
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
      selector: 'node[type = "ROADM"]',
      style: {{
        content: 'data(label)',
        'text-valign': 'top', 'text-halign': 'center',
        'font-weight': 'bold', 'font-size': 15, color: '#1e3a8a',
        'background-color': '#dbeafe', 'border-color': '#2563eb', 'border-width': 2.5,
        padding: '22px', shape: 'roundrectangle',
      }}
    }},
    {{
      selector: 'node[type = "DEGREE"]',
      style: {{
        content: 'data(label)',
        'text-valign': 'center', 'font-size': 11, 'font-weight': 'bold', color: '#78350f',
        width: 56, height: 28,
        'background-color': '#fef3c7', 'border-color': '#d97706', 'border-width': 2,
        shape: 'roundrectangle',
      }}
    }},
    {{
      selector: 'node[type = "SRG"]',
      style: {{
        content: 'data(label)',
        'text-valign': 'center', 'font-size': 11, color: '#14532d',
        width: 56, height: 28,
        'background-color': '#dcfce7', 'border-color': '#16a34a', 'border-width': 2,
        shape: 'roundrectangle',
      }}
    }},
    {{
      selector: 'edge[type = "ROADM-TO-ROADM"]',
      style: {{
        width: 3, 'line-color': '#2563eb',
        'curve-style': 'bezier',
        'target-arrow-shape': 'triangle',
        'target-arrow-color': '#2563eb',
        'arrow-scale': 1.2,
        label: 'data(label)', 'font-size': 10, color: '#1d4ed8',
        'text-background-color': '#eff6ff', 'text-background-opacity': 1,
        'text-background-padding': '3px', 'text-rotation': 'autorotate',
      }}
    }},
    {{
      selector: 'edge[type = "EXPRESS-LINK"]',
      style: {{
        width: 1.5, 'line-color': '#9ca3af', 'line-style': 'dashed', 'curve-style': 'bezier',
      }}
    }},
    {{
      selector: 'edge[type = "ADD-LINK"]',
      style: {{
        width: 1.5, 'line-color': '#16a34a',
        'target-arrow-shape': 'triangle', 'target-arrow-color': '#16a34a',
        'curve-style': 'bezier', 'arrow-scale': 0.7,
      }}
    }},
    {{ selector: ':selected', style: {{ 'overlay-color': '#f59e0b', 'overlay-opacity': 0.25 }} }},
  ],
  layout: {{ name: 'preset' }},
}});

cy.fit(undefined, 40);

// Layout configurations keyed by name
const layouts = {{
  preset: {{
    name: 'preset',
    animate: true, animationDuration: 500, fit: true, padding: 40,
  }},
  // fCoSE: Fast Compound Spring Embedder
  // Uses a force-directed algorithm that explicitly minimises edge crossings
  // while respecting compound-node containment constraints.
  fcose: {{
    name: 'fcose',
    animate: true, animationDuration: 700,
    fit: true, padding: 40,
    // Repulsion between nodes — increase to spread the graph more
    nodeRepulsion: 6500,
    // Ideal edge length for inter-compound edges
    idealEdgeLength: 120,
    // Strength of the edge-length enforcement
    edgeElasticity: 0.45,
    // Iterations of the crossing-minimisation phase
    numIter: 2500,
    // Gravity pulls disconnected components toward centre
    gravity: 0.25,
    gravityRange: 3.8,
    // Tighter nesting inside compound nodes
    nestingFactor: 0.1,
    // Randomise start positions to escape local minima
    randomize: true,
    // Tile disconnected nodes
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
  const cfg = layouts[name] || layouts.fcose;
  cy.layout(cfg).run();
}}

function exportSVG() {{
  const svg  = cy.svg({{ scale: 1.5, full: true, bg: '#ffffff' }});
  const blob = new Blob([svg], {{ type: 'image/svg+xml' }});
  const url  = URL.createObjectURL(blob);
  const a    = Object.assign(document.createElement('a'), {{ href: url, download: '{output_stem}.svg' }});
  a.click();
  URL.revokeObjectURL(url);
}}
</script>
</body>
</html>
"""


def main():
    script_dir = Path(__file__).parent
    xml_path  = Path(sys.argv[1]) if len(sys.argv) > 1 else script_dir / "openroadm-topology.xml"
    html_path = Path(sys.argv[2]) if len(sys.argv) > 2 else script_dir / "openroadm-topology.html"

    print(f"Reading  {xml_path}")
    cy_nodes, cy_edges, roadm_list = parse_topology(xml_path)
    positions = calc_positions(roadm_list)
    elements_js = build_elements_js(cy_nodes, cy_edges, positions)

    # read network-id from XML for the page title
    tree = ET.parse(xml_path)
    root = tree.getroot()
    nid_el = root.find("net:network-id", NS)
    network_id = nid_el.text if nid_el is not None else xml_path.stem

    html = HTML_TEMPLATE.format(
        network_id   = network_id,
        source_file  = xml_path.name,
        output_stem  = html_path.stem,
        elements_js  = elements_js,
    )

    html_path.write_text(html, encoding="utf-8")
    print(f"Written  {html_path}")
    print(f"         {len(cy_nodes)} nodes, {len(cy_edges)} edges")


if __name__ == "__main__":
    main()
