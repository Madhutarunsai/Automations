# Investment Strategy Framework (April 11-21, 2026)

> **DISCLAIMER:** Educational framework only. NOT financial advice. Consult a
> licensed financial advisor. Never invest money you cannot afford to lose.

## Files

| File | Purpose |
|------|---------|
| `STRATEGY.md` | Complete 10-day strategy with tiers, allocation, daily plan |
| `tracker.py` | CLI tool to track trades, P&L, and portfolio allocation |
| `screener.py` | Trade scoring checklist to evaluate setups before entering |

## Quick Start

```bash
# Set your starting capital
python tracker.py capital 10000

# Score a trade before entering
python screener.py checklist
python screener.py score --ticker AAPL

# Add a trade
python tracker.py add --ticker AAPL --type stock --action buy \
  --qty 10 --price 185.50 --stop-loss 178 --take-profit 200

# Check portfolio status
python tracker.py status
python tracker.py allocation

# Close a trade
python tracker.py close --ticker AAPL --price 192.30

# View P&L
python tracker.py pnl
```
