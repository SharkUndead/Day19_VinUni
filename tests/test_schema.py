from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from graphrag_lab.schema import Triple


class TripleTest(unittest.TestCase):
    def test_triple_holds_graph_edge_data(self) -> None:
        triple = Triple("OpenAI", "FOUNDED_BY", "Sam Altman")

        self.assertEqual(triple.subject, "OpenAI")
        self.assertEqual(triple.predicate, "FOUNDED_BY")
        self.assertEqual(triple.object, "Sam Altman")


if __name__ == "__main__":
    unittest.main()
