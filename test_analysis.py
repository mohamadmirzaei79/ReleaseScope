import json
import unittest
from pathlib import Path

from analysis_core import compare, summarize
from build_demo import build


class AnalysisTests(unittest.TestCase):
    def test_percentile_is_nearest_rank(self):
        self.assertEqual(summarize([(i, 200) for i in range(1, 101)])["p95_ms"], 95)

    def test_only_server_errors_count(self):
        self.assertEqual(summarize([(1, 404), (2, 503)])["error_pct"], 50)

    def test_threshold_edges(self):
        self.assertEqual(compare([(100, 200)], [(125, 200)])["verdict"], "Pass")
        self.assertEqual(compare([(100, 200)], [(126, 200)])["verdict"], "Review")
        self.assertEqual(compare([(1, 200)], [(1, 503)])["verdict"], "Review")

    def test_invalid_windows(self):
        for rows in ([], [(-1, 200)], [(float("nan"), 200)], [(1, 600)]):
            with self.assertRaises(ValueError):
                summarize(rows)

    def test_demo_matches_static_export(self):
        stored = json.loads(Path(__file__).with_name("demo.json").read_text())
        self.assertEqual(build(), stored)
        self.assertEqual([r["verdict"] for r in stored["releases"]], ["Review", "Pass", "Pass"])
