from __future__ import annotations

from math import cos, pi, sin
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from graphrag_lab.io import read_triples_csv


TRIPLES_PATH = ROOT / "data" / "processed" / "triples.csv"
PNG_PATH = ROOT / "reports" / "figures" / "knowledge_graph_networkx.png"
SVG_PATH = ROOT / "reports" / "figures" / "knowledge_graph.svg"
HTML_PATH = ROOT / "reports" / "figures" / "knowledge_graph.html"


def try_networkx_png() -> bool:
    try:
        import matplotlib.pyplot as plt
        import networkx as nx
    except ImportError:
        return False

    triples = read_triples_csv(TRIPLES_PATH)
    graph = nx.DiGraph()
    for triple in triples:
        graph.add_edge(triple.subject, triple.object, label=triple.predicate)

    plt.figure(figsize=(18, 14))
    positions = nx.spring_layout(graph, seed=19, k=0.55)
    nx.draw_networkx_nodes(graph, positions, node_size=650, node_color="#dbeafe", edgecolors="#1d4ed8")
    nx.draw_networkx_edges(graph, positions, arrows=True, alpha=0.35, edge_color="#475569", width=1)
    nx.draw_networkx_labels(graph, positions, font_size=7)
    edge_labels = nx.get_edge_attributes(graph, "label")
    nx.draw_networkx_edge_labels(graph, positions, edge_labels=edge_labels, font_size=5, alpha=0.7)
    plt.axis("off")
    plt.tight_layout()
    PNG_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(PNG_PATH, dpi=200)
    plt.close()
    return True


def write_svg_fallback() -> None:
    triples = read_triples_csv(TRIPLES_PATH)
    nodes = sorted({triple.subject for triple in triples} | {triple.object for triple in triples})
    node_positions = {}
    width, height = 1600, 1200
    cx, cy = width / 2, height / 2
    radius = 470
    for index, node in enumerate(nodes):
        angle = 2 * pi * index / len(nodes)
        node_positions[node] = (cx + radius * cos(angle), cy + radius * sin(angle))

    svg_lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1200" viewBox="0 0 1600 1200">',
        "<style>text{font-family:Arial,sans-serif;font-size:10px}.node{fill:#dbeafe;stroke:#1d4ed8;stroke-width:1}.edge{stroke:#64748b;stroke-width:1;opacity:.35}.label{fill:#0f172a}</style>",
        '<rect width="1600" height="1200" fill="#ffffff"/>',
    ]
    for triple in triples:
        x1, y1 = node_positions[triple.subject]
        x2, y2 = node_positions[triple.object]
        svg_lines.append(f'<line class="edge" x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')
    for node, (x, y) in node_positions.items():
        svg_lines.append(f'<circle class="node" cx="{x:.1f}" cy="{y:.1f}" r="18"/>')
        svg_lines.append(f'<text class="label" x="{x + 22:.1f}" y="{y + 4:.1f}">{escape_xml(node)}</text>')
    svg_lines.append("</svg>")

    SVG_PATH.parent.mkdir(parents=True, exist_ok=True)
    SVG_PATH.write_text("\n".join(svg_lines), encoding="utf-8")
    HTML_PATH.write_text(
        f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Knowledge Graph</title></head>
<body>
<h1>Knowledge Graph Visualization</h1>
<p>Fallback SVG generated without NetworkX/Matplotlib. Install requirements to generate PNG.</p>
{SVG_PATH.read_text(encoding="utf-8")}
</body>
</html>
""",
        encoding="utf-8",
    )


def escape_xml(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def main() -> None:
    if try_networkx_png():
        print(f"Wrote NetworkX visualization to {PNG_PATH}")
    else:
        write_svg_fallback()
        print("NetworkX/Matplotlib are not installed; wrote fallback visualization:")
        print(f"- {SVG_PATH}")
        print(f"- {HTML_PATH}")


if __name__ == "__main__":
    main()
