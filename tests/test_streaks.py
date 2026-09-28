import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(__file__)
SCRIPTS = os.path.join(HERE, "..", "plugins", "tw-institutional-flows", "skills", "trust-flows", "scripts")
sys.path.insert(0, SCRIPTS)

import streaks  # noqa: E402


def row(code, net, name="X", price=10.0):
    return {"code": code, "name": name, "price": price, "change_pct": 0.0, "volume": 100, "net": net}


def snap(d, buy, sell=()):
    return {"date": d, "buy": list(buy), "sell": list(sell)}


class StreaksTest(unittest.TestCase):
    def test_counts_running_streak_and_sums_net(self):
        snaps = [
            snap("2026-09-21", [row("2330", 100), row("2317", 50)]),
            snap("2026-09-22", [row("2330", 200)]),
            snap("2026-09-23", [row("2330", 300), row("2317", 70)]),
        ]
        result = streaks.streaks(snaps, "buy", min_days=1)
        self.assertEqual(result[0]["code"], "2330")
        self.assertEqual(result[0]["days"], 3)
        self.assertEqual(result[0]["total_net"], 600)
        # 2317 dropped off on 09-22, so its streak restarts at 1.
        self.assertEqual(result[1], {**result[1], "code": "2317", "days": 1})

    def test_min_days_filters(self):
        snaps = [snap("2026-09-22", [row("2330", 1)]), snap("2026-09-23", [row("2330", 1), row("2603", 1)])]
        self.assertEqual([r["code"] for r in streaks.streaks(snaps, "buy", 2)], ["2330"])

    def test_sell_side_sorted_by_abs_total(self):
        snaps = [
            snap("2026-09-22", [], [row("2603", -100), row("2609", -900)]),
            snap("2026-09-23", [], [row("2603", -100), row("2609", -900)]),
        ]
        self.assertEqual([r["code"] for r in streaks.streaks(snaps, "sell", 2)], ["2609", "2603"])

    def test_gap_warning_ignores_weekends(self):
        self.assertEqual(streaks.find_gaps(["2026-09-25", "2026-09-28"]), [])  # Fri -> Mon
        self.assertEqual(len(streaks.find_gaps(["2026-09-21", "2026-09-28"])), 1)

    def test_end_to_end_from_fixture(self):
        fetch = os.path.join(SCRIPTS, "fetch_trust_flows.py")
        fixture = os.path.join(HERE, "fixtures", "histock_sample.html")
        with tempfile.TemporaryDirectory() as d:
            for day in ("2026-09-24", "2026-09-25"):
                subprocess.run([sys.executable, fetch, "--html", fixture, "--history-dir", d, "--date", day],
                               check=True, capture_output=True)
            self.assertEqual(sorted(os.listdir(d)), ["2026-09-24.json", "2026-09-25.json"])
            out = subprocess.run([sys.executable, os.path.join(SCRIPTS, "streaks.py"), d],
                                 check=True, capture_output=True, text=True).stdout
            result = json.loads(out)
            self.assertEqual(result["latest"], "2026-09-25")
            self.assertEqual({r["code"] for r in result["buy_streaks"]}, {"2330", "00878"})
            self.assertEqual(result["buy_streaks"][0]["total_net"], 8420)
            self.assertEqual(result["sell_streaks"][0]["days"], 2)


if __name__ == "__main__":
    unittest.main()
