#!/usr/bin/env python3
"""Find stocks on the 投信 buy (or sell) list for several snapshots in a row.

Reads the <date>.json snapshots written by `fetch_trust_flows.py --history-dir`
and reports, for the latest snapshot, how many consecutive snapshots each stock
has appeared on the same side.

Usage:
    python3 streaks.py history                 # streaks of 2+ snapshots
    python3 streaks.py history --min-days 3
"""
import argparse
import glob
import json
import os
import sys
from datetime import date

# Weekends and one-day holidays leave gaps of up to 4 calendar days between
# trading days. A longer gap usually means a missed run, which would make a
# streak look longer than it really is, so it is reported as a warning.
MAX_GAP_DAYS = 4


def load_snapshots(history_dir):
    snapshots = []
    for path in sorted(glob.glob(os.path.join(history_dir, "*.json"))):
        with open(path, encoding="utf-8") as f:
            snap = json.load(f)
        snap.setdefault("date", os.path.splitext(os.path.basename(path))[0])
        snapshots.append(snap)
    snapshots.sort(key=lambda s: s["date"])
    return snapshots


def find_gaps(dates):
    gaps = []
    for prev, cur in zip(dates, dates[1:]):
        days = (date.fromisoformat(cur) - date.fromisoformat(prev)).days
        if days > MAX_GAP_DAYS:
            gaps.append({"from": prev, "to": cur, "calendar_days": days})
    return gaps


def streaks(snapshots, side, min_days=2):
    """Streaks that are still running on the latest snapshot, longest first."""
    if not snapshots:
        return []
    latest = {row["code"]: row for row in snapshots[-1][side]}
    result = []
    for code, row in latest.items():
        days, total_net = 0, 0
        for snap in reversed(snapshots):
            match = next((r for r in snap[side] if r["code"] == code), None)
            if match is None:
                break
            days += 1
            if isinstance(match["net"], (int, float)):
                total_net += match["net"]
        if days >= min_days:
            result.append({
                "code": code,
                "name": row["name"],
                "days": days,
                "latest_net": row["net"],
                "total_net": total_net,
                "price": row["price"],
            })
    result.sort(key=lambda r: (-r["days"], -abs(r["total_net"])))
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("history_dir")
    ap.add_argument("--min-days", type=int, default=2)
    args = ap.parse_args(argv)

    snapshots = load_snapshots(args.history_dir)
    if not snapshots:
        sys.exit(f"No snapshots found in {args.history_dir}; run fetch_trust_flows.py --history-dir first.")

    dates = [s["date"] for s in snapshots]
    out = {
        "latest": dates[-1],
        "snapshots": len(dates),
        "gaps": find_gaps(dates),
        "buy_streaks": streaks(snapshots, "buy", args.min_days),
        "sell_streaks": streaks(snapshots, "sell", args.min_days),
    }
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    print()


if __name__ == "__main__":
    main()
