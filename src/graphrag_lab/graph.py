from __future__ import annotations

from collections import defaultdict, deque

from graphrag_lab.schema import Triple


class KnowledgeGraph:
    def __init__(self, triples: list[Triple]) -> None:
        self.triples = triples
        self.nodes = sorted({triple.subject for triple in triples} | {triple.object for triple in triples})
        self.adjacent: dict[str, list[Triple]] = defaultdict(list)
        self.reverse_adjacent: dict[str, list[Triple]] = defaultdict(list)
        for triple in triples:
            self.adjacent[triple.subject].append(triple)
            self.reverse_adjacent[triple.object].append(triple)

    def find_nodes(self, question: str) -> list[str]:
        question_lower = question.lower()
        exact = [node for node in self.nodes if node.lower() in question_lower]
        if exact:
            return sorted(exact, key=len, reverse=True)

        tokens = {token.strip("?,.").lower() for token in question.split() if len(token) > 2}
        scored: list[tuple[int, str]] = []
        for node in self.nodes:
            node_tokens = {part.lower() for part in node.split()}
            score = len(tokens & node_tokens)
            if score:
                scored.append((score, node))
        return [node for _, node in sorted(scored, reverse=True)]

    def neighborhood(self, seeds: list[str], hops: int = 2) -> list[Triple]:
        visited_nodes = set(seeds)
        visited_edges: set[tuple[str, str, str]] = set()
        output: list[Triple] = []
        queue: deque[tuple[str, int]] = deque((seed, 0) for seed in seeds)

        while queue:
            node, depth = queue.popleft()
            if depth >= hops:
                continue

            edges = self.adjacent.get(node, []) + self.reverse_adjacent.get(node, [])
            for edge in edges:
                key = (edge.subject, edge.predicate, edge.object)
                if key not in visited_edges:
                    visited_edges.add(key)
                    output.append(edge)

                next_node = edge.object if edge.subject == node else edge.subject
                if next_node not in visited_nodes:
                    visited_nodes.add(next_node)
                    queue.append((next_node, depth + 1))

        return output

    @staticmethod
    def textualize(triples: list[Triple]) -> str:
        return "\n".join(f"{t.subject} --{t.predicate}--> {t.object}" for t in triples)

    def to_graphml(self) -> str:
        node_ids = {node: f"n{idx}" for idx, node in enumerate(self.nodes)}
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">',
            '<key id="label" for="all" attr.name="label" attr.type="string"/>',
            '<graph edgedefault="directed">',
        ]
        for node, node_id in node_ids.items():
            lines.append(f'<node id="{node_id}"><data key="label">{_xml_escape(node)}</data></node>')
        for idx, triple in enumerate(self.triples):
            lines.append(
                f'<edge id="e{idx}" source="{node_ids[triple.subject]}" target="{node_ids[triple.object]}">'
                f'<data key="label">{_xml_escape(triple.predicate)}</data></edge>'
            )
        lines.extend(["</graph>", "</graphml>"])
        return "\n".join(lines)


def _xml_escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )
