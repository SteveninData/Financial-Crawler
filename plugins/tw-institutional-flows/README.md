# TW Institutional Flows

`Financial Crawler.ipynb`, rebuilt as a Claude plugin using the same layout as
[anthropics/financial-services](https://github.com/anthropics/financial-services).

## Notebook → plugin

| Notebook | Plugin |
|---|---|
| One cell that scrapes and writes Excel | `scripts/fetch_trust_flows.py`: the same selectors, as a reusable script |
| `xlwings` (needs desktop Excel) | `openpyxl` (headless, runs anywhere) |
| You read the sheet yourself | `SKILL.md` tells Claude how to check and summarize the data |
| You run the cell | `/trust-flows` command, or ask "今天投信買超什麼?" |

## Layout

```
.claude-plugin/marketplace.json          ← registers this repo as a plugin marketplace
plugins/tw-institutional-flows/
  .claude-plugin/plugin.json             ← plugin name + version
  commands/trust-flows.md                ← the /trust-flows slash command
  skills/trust-flows/
    SKILL.md                             ← the method: fetch → check → summarize
    scripts/fetch_trust_flows.py         ← the crawler (--history-dir saves daily snapshots)
    scripts/streaks.py                   ← consecutive buy/sell streaks from the snapshots
tests/                                   ← parser tests on a synthetic HTML fixture
```

## Install (Claude Code)

```bash
pip install -r requirements.txt
claude plugin marketplace add SteveninData/Financial-Crawler
claude plugin install tw-institutional-flows@financial-crawler
```

Then run `/trust-flows`, or ask about 投信買賣超 in plain language.

## Run the script directly

```bash
S=plugins/tw-institutional-flows/skills/trust-flows/scripts
python3 $S/fetch_trust_flows.py --xlsx 投信買賣超數據.xlsx --history-dir history   # run once per trading day
python3 $S/streaks.py history --min-days 3                                        # 連續 3 天以上買超/賣超
python3 -m unittest discover -s tests
```
