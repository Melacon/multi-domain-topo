#!/usr/bin/env python3
"""
generate_html.py — reads ietf-network-topology.json, writes ietf-network-topology.html

Usage:
    python3 generate_html.py [input.json] [output.html]

Defaults:
    input  = ietf-network-topology.json  (relative to this script)
    output = ietf-network-topology.html  (same directory)

Features:
    - Per-network (single-layer) filter view
    - Multi-layer view using supporting-node/supporting-network relationships
    - Node type detection from node-id naming conventions
    - Link type detection from link-id naming conventions
    - Click-to-inspect info panel (TPs, supporting refs)
    - fCoSE / CoSE layout toggle, SVG export
"""

import json
import sys
from pathlib import Path


NODE_TYPE_PREFIXES = [
    ("roadm",    "ROADM"),
    ("txp",      "TXP"),
    ("o-cu-cp",  "O-CU-CP"),
    ("o-cu-up",  "O-CU-UP"),
    ("o-du",     "O-DU"),
    ("o-ru",     "O-RU"),
    ("ofh-sw",   "OFH-SW"),
    ("wt-",      "WT"),
    ("ip-rtr",   "IP-RTR"),
    ("5gc",      "5GC"),
    ("net-",     "NET"),
    ("ue-",      "UE"),
]

LINK_TYPE_PREFIXES = [
    ("ring",      "RING"),
    ("optical",   "OPTICAL"),
    ("backhaul",  "BACKHAUL"),
    ("e1-",       "E1"),
    ("f1-c",      "F1-C"),
    ("f1-u",      "F1-U"),
    ("fronthaul", "FRONTHAUL"),
    ("air-",      "AIR"),
    ("wireless",  "WIRELESS"),
]


def short_id(urn: str) -> str:
    return urn.split(":")[-1]


def detect_node_type(node_id: str) -> str:
    seg = node_id.split(":")[-1].lower()
    for prefix, t in NODE_TYPE_PREFIXES:
        if seg.startswith(prefix):
            return t
    return "UNKNOWN"


def detect_link_type(link_id: str) -> str:
    seg = link_id.split(":")[-1].lower()
    for prefix, t in LINK_TYPE_PREFIXES:
        if seg.startswith(prefix):
            return t
    return "UNKNOWN"


def parse_topology(json_path: Path) -> list:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    networks_raw = data["ietf-network:networks"]["network"]

    networks = []
    for net in networks_raw:
        net_id = net["network-id"]
        supporting = [sn["network-ref"] for sn in net.get("supporting-network", [])]

        nodes = []
        for node in net.get("node", []):
            node_id = node["node-id"]
            sup_nodes = [
                {"network-ref": sn["network-ref"], "node-ref": sn["node-ref"]}
                for sn in node.get("supporting-node", [])
            ]
            tps = [
                tp["tp-id"]
                for tp in node.get("ietf-network-topology:termination-point", [])
            ]
            nodes.append({
                "node-id":         node_id,
                "type":            detect_node_type(node_id),
                "label":           short_id(node_id),
                "supporting-nodes": sup_nodes,
                "tps":             tps,
            })

        links = []
        for link in net.get("ietf-network-topology:link", []):
            link_id = link["link-id"]
            links.append({
                "link-id":     link_id,
                "type":        detect_link_type(link_id),
                "source-node": link["source"]["source-node"],
                "source-tp":   link["source"].get("source-tp", ""),
                "dest-node":   link["destination"]["dest-node"],
                "dest-tp":     link["destination"].get("dest-tp", ""),
            })

        networks.append({
            "network-id":          net_id,
            "supporting-networks": supporting,
            "nodes":               nodes,
            "links":               links,
        })

    return networks


# HTML template uses __NETWORKS_JSON__ as the only placeholder (avoids
# escaping every JS brace for Python's str.format).
HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>IETF Network Topology</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.28.1/cytoscape.min.js"></script>
  <script src="https://unpkg.com/cytoscape-fcose/cytoscape-fcose.js"></script>
  <script src="https://unpkg.com/cytoscape-svg/cytoscape-svg.js"></script>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: Arial, sans-serif; background: #f8fafc; }
    #cy { width: 100vw; height: 100vh; display: block; }

    #toolbar {
      position: absolute; top: 12px; left: 12px; z-index: 100;
      background: white; border: 1px solid #d1d5db; border-radius: 10px;
      padding: 10px 12px; display: flex; flex-direction: column; gap: 8px;
      box-shadow: 0 1px 4px rgba(0,0,0,.08); min-width: 170px; max-width: 210px;
    }
    .tb-label { font-size: 10px; color: #6b7280; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px; }
    .btn-group { display: flex; flex-wrap: wrap; gap: 4px; }
    button {
      padding: 4px 10px; border: 1px solid #9ca3af; background: white;
      border-radius: 5px; cursor: pointer; font-size: 11px; color: #111827;
    }
    button:hover { background: #f3f4f6; }
    button.active { background: #2563eb; color: white; border-color: #2563eb; }
    .sep { border-top: 1px solid #e5e7eb; }

    #info {
      position: absolute; top: 12px; right: 12px; z-index: 100;
      background: white; border: 1px solid #d1d5db; border-radius: 10px;
      padding: 12px 14px; font-size: 12px; min-width: 220px; max-width: 300px;
      box-shadow: 0 1px 4px rgba(0,0,0,.08); display: none;
      max-height: 85vh; overflow-y: auto;
    }
    #info h3 { font-size: 13px; margin-bottom: 8px; color: #111827; padding-right: 22px; word-break: break-all; }
    .info-close { position: absolute; top: 10px; right: 12px; cursor: pointer; color: #9ca3af; font-size: 18px; line-height: 1; }
    .info-row { margin: 3px 0; line-height: 1.5; }
    .info-key { color: #6b7280; margin-right: 4px; }
    .tp-badge {
      display: inline-block; font-size: 10px; color: #374151;
      padding: 1px 5px; background: #f3f4f6; border-radius: 3px; margin: 1px;
    }

    #legend {
      position: absolute; bottom: 16px; left: 16px; z-index: 100;
      background: white; border: 1px solid #d1d5db; border-radius: 10px;
      padding: 10px 14px; font-size: 11px; line-height: 1.9;
      box-shadow: 0 1px 4px rgba(0,0,0,.08); max-height: 55vh; overflow-y: auto;
    }
    #leg-toggle { cursor: pointer; font-size: 12px; font-weight: bold; color: #374151; display: flex; align-items: center; gap: 6px; user-select: none; }
    #leg-body { margin-top: 6px; }
    .leg-sec { font-size: 10px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; font-weight: bold; margin-top: 8px; margin-bottom: 2px; }
    .li { display: flex; align-items: center; gap: 6px; }
    .sw { width: 16px; height: 11px; border-radius: 2px; border: 2px solid; flex-shrink: 0; }
    .lsw { width: 24px; height: 3px; border-radius: 2px; flex-shrink: 0; }
    .lsw.dsh { background: none !important; border-top: 2px dashed currentColor; height: 0; }
    .lsw.dot { background: none !important; border-top: 2px dotted currentColor; height: 0; }

    #loading {
      position: fixed; inset: 0; z-index: 500;
      background: rgba(248,250,252,0.88);
      display: flex; align-items: center; justify-content: center;
      backdrop-filter: blur(2px);
    }
    #loading.hidden { display: none; }
    .ld-box {
      background: white; border: 1px solid #e5e7eb; border-radius: 14px;
      padding: 30px 48px; display: flex; flex-direction: column;
      align-items: center; gap: 16px;
      box-shadow: 0 4px 20px rgba(0,0,0,.1);
    }
    .ld-spinner {
      width: 38px; height: 38px;
      border: 4px solid #e5e7eb; border-top-color: #2563eb;
      border-radius: 50%; animation: ld-spin 0.7s linear infinite;
    }
    @keyframes ld-spin { to { transform: rotate(360deg); } }
    .ld-msg { font-size: 13px; font-weight: 600; color: #374151; }
    .ld-sub { font-size: 11px; color: #9ca3af; margin-top: -8px; }
  </style>
</head>
<body>
<div id="loading">
  <div class="ld-box">
    <div class="ld-spinner"></div>
    <div class="ld-msg" id="ld-msg">Loading topology…</div>
    <div class="ld-sub"  id="ld-sub"></div>
  </div>
</div>

<div id="cy"></div>

<div id="toolbar">
  <div class="tb-label">View / Layer</div>
  <div class="btn-group" id="view-btns"></div>
  <div class="sep"></div>
  <div class="tb-label">Layout</div>
  <div class="btn-group">
    <button onclick="runLayout('fcose')">fCoSE ✦</button>
    <button onclick="runLayout('cose')">CoSE</button>
    <button onclick="cy && cy.fit(undefined, 40)">Fit</button>
  </div>
  <div class="sep"></div>
  <button onclick="exportSVG()">Export SVG</button>
</div>

<div id="info">
  <span class="info-close" onclick="document.getElementById('info').style.display='none'">×</span>
  <h3 id="info-title"></h3>
  <div id="info-body"></div>
</div>

<div id="legend">
  <div id="leg-toggle" onclick="toggleLegend()">
    <span>Legend</span><span id="leg-arrow">▼</span>
  </div>
  <div id="leg-body">
    <div class="leg-sec">Nodes</div>
    <div class="li"><span class="sw" style="background:#dbeafe;border-color:#2563eb"></span>ROADM</div>
    <div class="li"><span class="sw" style="background:#f3e8ff;border-color:#7c3aed"></span>Transponder (TXP)</div>
    <div class="li"><span class="sw" style="background:#fef3c7;border-color:#d97706"></span>O-CU-CP</div>
    <div class="li"><span class="sw" style="background:#fef9c3;border-color:#ca8a04"></span>O-CU-UP</div>
    <div class="li"><span class="sw" style="background:#ccfbf1;border-color:#0d9488"></span>O-DU</div>
    <div class="li"><span class="sw" style="background:#dcfce7;border-color:#16a34a"></span>O-RU</div>
    <div class="li"><span class="sw" style="background:#e0e7ff;border-color:#4338ca"></span>OFH Switch</div>
    <div class="li"><span class="sw" style="background:#ffe4e6;border-color:#e11d48"></span>Wireless Terminal (WT)</div>
    <div class="li"><span class="sw" style="background:#f1f5f9;border-color:#475569"></span>IP Router</div>
    <div class="li"><span class="sw" style="background:#fee2e2;border-color:#dc2626"></span>5G Core</div>
    <div class="li"><span class="sw" style="background:#f3f4f6;border-color:#6b7280"></span>Network / Internet</div>
    <div class="li"><span class="sw" style="background:#fefce8;border-color:#eab308"></span>UE</div>
    <div class="leg-sec">Links</div>
    <div class="li"><span class="lsw" style="background:#2563eb"></span>Optical Ring</div>
    <div class="li"><span class="lsw" style="background:#7c3aed"></span>Optical (ROADM↔TXP)</div>
    <div class="li"><span class="lsw" style="background:#d97706"></span>Backhaul</div>
    <div class="li"><span class="lsw" style="background:#dc2626"></span>E1</div>
    <div class="li"><span class="lsw" style="background:#0d9488"></span>F1-C</div>
    <div class="li"><span class="lsw" style="background:#16a34a"></span>F1-U</div>
    <div class="li"><span class="lsw" style="background:#4338ca"></span>Fronthaul</div>
    <div class="li"><span class="lsw dsh" style="color:#eab308"></span>Air (RU↔UE)</div>
    <div class="li"><span class="lsw dsh" style="color:#e11d48"></span>Wireless</div>
    <div class="li"><span class="lsw dot" style="color:#94a3b8"></span>Supporting (inter-layer)</div>
  </div>
</div>

<script>
// ── Data (auto-generated) ────────────────────────────────────────────────────
const ALL_NETWORKS = __NETWORKS_JSON__;

// ── Element builder ──────────────────────────────────────────────────────────
// Both directions of a bidirectional link pair are kept; bezier curve-style
// automatically fans parallel edges apart so they never overlap.
function buildElements(mode, filterId) {
  const elems = [];

  if (mode === 'single') {
    const net = ALL_NETWORKS.find(n => n['network-id'] === filterId);
    if (!net) return [];

    for (const node of net.nodes) {
      elems.push({ data: {
        id: node['node-id'], label: node.label, type: node.type,
        networkId: filterId, tps: node.tps,
        supportingNodes: node['supporting-nodes'],
      }});
    }

    for (const link of net.links) {
      elems.push({ data: {
        id: link['link-id'],
        source: link['source-node'], target: link['dest-node'],
        type: link.type,
        sourceTp: link['source-tp'], destTp: link['dest-tp'],
      }});
    }

  } else {
    // Multi-layer: scope all ids as "networkId::originalId"
    const allScopedIds = new Set();
    for (const net of ALL_NETWORKS) {
      allScopedIds.add('layer::' + net['network-id']);
      for (const n of net.nodes) allScopedIds.add(net['network-id'] + '::' + n['node-id']);
    }

    for (const net of ALL_NETWORKS) {
      const nid = net['network-id'];

      // Layer compound container
      elems.push({ data: { id: 'layer::' + nid, label: nid, type: 'LAYER' } });

      for (const node of net.nodes) {
        const sid = nid + '::' + node['node-id'];
        elems.push({ data: {
          id: sid, label: node.label, type: node.type,
          parent: 'layer::' + nid, networkId: nid,
          originalId: node['node-id'],
          tps: node.tps, supportingNodes: node['supporting-nodes'],
        }});

        // Inter-layer supporting edges (only when target network is present)
        for (const sn of node['supporting-nodes']) {
          const tgt = sn['network-ref'] + '::' + sn['node-ref'];
          if (allScopedIds.has(tgt)) {
            elems.push({ data: {
              id: 'sup::' + sid + '::' + tgt,
              source: sid, target: tgt, type: 'SUPPORTING',
            }});
          }
        }
      }

      // Intra-layer links — both directions kept, bezier fans them apart
      for (const link of net.links) {
        const src = nid + '::' + link['source-node'];
        const dst = nid + '::' + link['dest-node'];
        elems.push({ data: {
          id: nid + '::' + link['link-id'],
          source: src, target: dst, type: link.type,
          sourceTp: link['source-tp'], destTp: link['dest-tp'],
        }});
      }
    }
  }

  return elems;
}

// ── Style ────────────────────────────────────────────────────────────────────
const NODE_COLORS = {
  'ROADM':    { bg: '#dbeafe', bd: '#2563eb' },
  'TXP':      { bg: '#f3e8ff', bd: '#7c3aed' },
  'O-CU-CP':  { bg: '#fef3c7', bd: '#d97706' },
  'O-CU-UP':  { bg: '#fef9c3', bd: '#ca8a04' },
  'O-DU':     { bg: '#ccfbf1', bd: '#0d9488' },
  'O-RU':     { bg: '#dcfce7', bd: '#16a34a' },
  'OFH-SW':   { bg: '#e0e7ff', bd: '#4338ca' },
  'WT':       { bg: '#ffe4e6', bd: '#e11d48' },
  'IP-RTR':   { bg: '#f1f5f9', bd: '#475569' },
  '5GC':      { bg: '#fee2e2', bd: '#dc2626' },
  'NET':      { bg: '#f3f4f6', bd: '#6b7280' },
  'UE':       { bg: '#fefce8', bd: '#eab308' },
  'UNKNOWN':  { bg: '#f9fafb', bd: '#9ca3af' },
};
const EDGE_COLORS = {
  'RING':       { c: '#2563eb', dash: false, w: 2.5 },
  'OPTICAL':    { c: '#7c3aed', dash: false, w: 2   },
  'BACKHAUL':   { c: '#d97706', dash: false, w: 2   },
  'E1':         { c: '#dc2626', dash: false, w: 1.5 },
  'F1-C':       { c: '#0d9488', dash: false, w: 1.5 },
  'F1-U':       { c: '#16a34a', dash: false, w: 1.5 },
  'FRONTHAUL':  { c: '#4338ca', dash: false, w: 2   },
  'AIR':        { c: '#eab308', dash: true,  w: 1.5 },
  'WIRELESS':   { c: '#e11d48', dash: true,  w: 2   },
  'UNKNOWN':    { c: '#9ca3af', dash: false, w: 1   },
};

function buildStyle() {
  const s = [
    {
      selector: 'node[type = "LAYER"]',
      style: {
        content: 'data(label)', 'text-valign': 'top', 'text-halign': 'center',
        'font-weight': 'bold', 'font-size': 14, color: '#334155',
        'background-color': 'rgba(241,245,249,0.6)',
        'border-color': '#94a3b8', 'border-width': 1.5, 'border-style': 'dashed',
        padding: '30px', shape: 'roundrectangle',
      }
    },
    {
      selector: 'edge[type = "SUPPORTING"]',
      style: {
        width: 1.5, 'line-color': '#94a3b8', 'line-style': 'dotted',
        'curve-style': 'bezier',
        'target-arrow-shape': 'triangle', 'target-arrow-color': '#94a3b8',
        'arrow-scale': 0.8, opacity: 0.75,
      }
    },
    {
      selector: 'edge',
      style: {
        'curve-style': 'bezier',
        'target-arrow-shape': 'triangle',
        'arrow-scale': 0.7,
      }
    },
    { selector: ':selected', style: { 'overlay-color': '#f59e0b', 'overlay-opacity': 0.25 } },
  ];

  for (const [type, c] of Object.entries(NODE_COLORS)) {
    s.push({
      selector: `node[type = "${type}"]`,
      style: {
        content: 'data(label)', 'text-valign': 'center', 'text-halign': 'center',
        'font-size': 11, 'font-weight': 'bold', color: '#111827',
        width: 72, height: 30,
        'background-color': c.bg, 'border-color': c.bd, 'border-width': 2,
        shape: 'roundrectangle',
      }
    });
  }

  for (const [type, c] of Object.entries(EDGE_COLORS)) {
    s.push({
      selector: `edge[type = "${type}"]`,
      style: {
        width: c.w,
        'line-color': c.c,
        'line-style': c.dash ? 'dashed' : 'solid',
        'target-arrow-color': c.c,
      }
    });
  }

  return s;
}

// ── Cytoscape ────────────────────────────────────────────────────────────────
let cy = null;
let curMode = 'single', curFilter = null;

function initCy(elements) {
  if (cy) cy.destroy();
  cy = cytoscape({
    container: document.getElementById('cy'),
    elements,
    style: buildStyle(),
    layout: { name: 'preset' },
  });
  cy.on('tap', 'node', e => { if (e.target.data('type') !== 'LAYER') showNode(e.target); });
  cy.on('tap', 'edge', e => showEdge(e.target));
  cy.on('tap', e => { if (e.target === cy) document.getElementById('info').style.display = 'none'; });
  runLayout('fcose');
}

// ── Loading overlay ───────────────────────────────────────────────────────────
function showLoading(msg, sub) {
  const el = document.getElementById('loading');
  document.getElementById('ld-msg').textContent = msg || 'Loading…';
  document.getElementById('ld-sub').textContent = sub || '';
  el.classList.remove('hidden');
}
function hideLoading() {
  if (_loadingTimer) { clearTimeout(_loadingTimer); _loadingTimer = null; }
  document.getElementById('loading').classList.add('hidden');
}

function setView(mode, filterId) {
  curMode = mode; curFilter = filterId;
  document.querySelectorAll('#view-btns button').forEach(b => {
    const isActive = (mode === 'multi' && b.dataset.view === 'multi') ||
                     (mode === 'single' && b.dataset.view === filterId);
    b.classList.toggle('active', isActive);
  });
  document.getElementById('info').style.display = 'none';
  const label = mode === 'multi' ? 'All layers' : filterId;
  showLoading('Building graph…', label);
  // defer initCy one frame so the loading overlay paints first
  requestAnimationFrame(() => requestAnimationFrame(() => initCy(buildElements(mode, filterId))));
}

// ── Layouts ──────────────────────────────────────────────────────────────────
const LAYOUTS = {
  fcose: {
    name: 'fcose', animate: true, animationDuration: 700,
    fit: true, padding: 50,
    nodeRepulsion: 8000, idealEdgeLength: 120, edgeElasticity: 0.45,
    numIter: 2500, gravity: 0.25, gravityRange: 3.8,
    nestingFactor: 0.1, randomize: true, tile: true,
  },
  cose: {
    name: 'cose', animate: true, animationDuration: 700,
    fit: true, padding: 60, nodeRepulsion: 8000, componentSpacing: 80,
  },
};
let _loadingTimer = null;
function runLayout(n) {
  if (!cy) return;
  const cfg = LAYOUTS[n] || LAYOUTS.fcose;
  showLoading('Calculating layout…', cfg.name === 'fcose' ? 'fCoSE — may take a moment' : cfg.name);
  // layoutstop fires on cy, not on the layout object
  cy.one('layoutstop', hideLoading);
  // safety net: hide after 15 s if layoutstop never arrives
  if (_loadingTimer) clearTimeout(_loadingTimer);
  _loadingTimer = setTimeout(hideLoading, 5000);
  cy.layout(cfg).run();
}

// ── Info panel ───────────────────────────────────────────────────────────────
function esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function seg(urn) { return esc(String(urn).split(':').pop()); }

function showNode(node) {
  const d = node.data();
  document.getElementById('info-title').textContent = d.label || seg(d.id);
  let h = `
    <div class="info-row"><span class="info-key">ID:</span>${esc(d.originalId || d.id)}</div>
    <div class="info-row"><span class="info-key">Type:</span>${esc(d.type)}</div>
    <div class="info-row"><span class="info-key">Network:</span>${esc(d.networkId || curFilter)}</div>`;
  if (d.tps && d.tps.length) {
    h += `<div class="info-row" style="margin-top:6px"><span class="info-key">Termination Points:</span><br>`;
    for (const tp of d.tps) h += `<span class="tp-badge">${seg(tp)}</span>`;
    h += `</div>`;
  }
  if (d.supportingNodes && d.supportingNodes.length) {
    h += `<div class="info-row" style="margin-top:6px"><span class="info-key">Supporting:</span>`;
    for (const sn of d.supportingNodes) h += ` <span class="tp-badge">${esc(sn['network-ref'])}/${seg(sn['node-ref'])}</span>`;
    h += `</div>`;
  }
  document.getElementById('info-body').innerHTML = h;
  document.getElementById('info').style.display = 'block';
}

function showEdge(edge) {
  const d = edge.data();
  const rawId = (d.id || '').replace(/^[^:]+::/, '');
  document.getElementById('info-title').textContent = rawId.split(':').pop() || d.id;
  let h = `
    <div class="info-row"><span class="info-key">Type:</span>${esc(d.type)}</div>
    <div class="info-row"><span class="info-key">Source:</span>${seg(d.source)}</div>`;
  if (d.sourceTp) h += `<div class="info-row"><span class="info-key">src-tp:</span>${seg(d.sourceTp)}</div>`;
  h += `<div class="info-row"><span class="info-key">Target:</span>${seg(d.target)}</div>`;
  if (d.destTp) h += `<div class="info-row"><span class="info-key">dst-tp:</span>${seg(d.destTp)}</div>`;
  document.getElementById('info-body').innerHTML = h;
  document.getElementById('info').style.display = 'block';
}

// ── SVG export ───────────────────────────────────────────────────────────────
function exportSVG() {
  const svg  = cy.svg({ scale: 1.5, full: true, bg: '#ffffff' });
  const blob = new Blob([svg], { type: 'image/svg+xml' });
  const url  = URL.createObjectURL(blob);
  const a    = Object.assign(document.createElement('a'), { href: url, download: 'topology.svg' });
  a.click();
  URL.revokeObjectURL(url);
}

// ── Legend toggle ─────────────────────────────────────────────────────────────
function toggleLegend() {
  const body  = document.getElementById('leg-body');
  const arrow = document.getElementById('leg-arrow');
  const hide  = body.style.display !== 'none';
  body.style.display  = hide ? 'none' : '';
  arrow.textContent   = hide ? '▶' : '▼';
}

// ── Toolbar ───────────────────────────────────────────────────────────────────
(function buildToolbar() {
  const c = document.getElementById('view-btns');

  function mkBtn(text, mode, filter) {
    const b = document.createElement('button');
    b.textContent  = text;
    b.dataset.view = filter !== null ? filter : mode;
    b.onclick      = () => setView(mode, filter);
    c.appendChild(b);
  }

  mkBtn('All layers', 'multi', null);
  for (const net of ALL_NETWORKS) mkBtn(net['network-id'], 'single', net['network-id']);
})();

// ── Start — default to the network with the most links ───────────────────────
const startNet = ALL_NETWORKS.reduce((a, b) => b.links.length > a.links.length ? b : a);
setView('single', startNet['network-id']);
</script>
</body>
</html>
"""


def main():
    script_dir = Path(__file__).parent
    json_path  = Path(sys.argv[1]) if len(sys.argv) > 1 else script_dir / "ietf-network-topology.json"
    html_path  = Path(sys.argv[2]) if len(sys.argv) > 2 else script_dir / "ietf-network-topology.html"

    print(f"Reading  {json_path}")
    networks = parse_topology(json_path)
    networks_json = json.dumps(networks, indent=2)

    html = HTML_TEMPLATE.replace("__NETWORKS_JSON__", networks_json)

    html_path.write_text(html, encoding="utf-8")
    print(f"Written  {html_path}")
    node_count = sum(len(n["nodes"]) for n in networks)
    link_count = sum(len(n["links"]) for n in networks)
    print(f"         {len(networks)} networks, {node_count} nodes, {link_count} links (before dedup)")


if __name__ == "__main__":
    main()
