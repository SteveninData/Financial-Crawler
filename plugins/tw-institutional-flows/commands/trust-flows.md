---
description: Fetch today's Top 50 投信 net buy/sell lists, export to Excel, and summarize
argument-hint: "[output .xlsx path]"
---

# 投信買賣超 Command

## Step 1: Choose output

Use the provided path if given; otherwise default to `投信買賣超數據.xlsx` in the working directory.

## Step 2: Run the skill

Use `skill: "trust-flows"`:

1. Run `scripts/fetch_trust_flows.py --xlsx <path>`.
2. Run the Step 2 sanity checks from the skill. Stop and report if any fail.
3. Write the Step 3 summary.

## Step 3: Deliver

Reply with:
- The workbook path
- The summary (top buys, top sells, concentration, notable flags)
- The `fetched_at` timestamp
