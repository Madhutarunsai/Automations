#!/usr/bin/env python3
"""
Quick Investment Screener — checklist-based scoring for short-term trades.

Usage:
    python screener.py score --ticker AAPL
    python screener.py checklist
    python screener.py watchlist
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
WATCHLIST_FILE = DATA_DIR / "watchlist.json"


SCORING_CRITERIA = {
    "technical": [
        {"name": "RSI below 30 (oversold) or above 70 (overbought in correct direction)",
         "weight": 2, "key": "rsi_signal"},
        {"name": "Price near key moving average (50d or 200d)",
         "weight": 2, "key": "near_ma"},
        {"name": "Volume spike (1.5x+ average)",
         "weight": 1, "key": "volume_spike"},
        {"name": "MACD crossover signal",
         "weight": 1, "key": "macd_signal"},
        {"name": "Support/resistance level nearby",
         "weight": 2, "key": "sr_level"},
    ],
    "fundamental": [
        {"name": "Upcoming catalyst (earnings, FDA, product launch)",
         "weight": 3, "key": "catalyst"},
        {"name": "Sector momentum (sector ETF trending up)",
         "weight": 1, "key": "sector_momentum"},
        {"name": "No negative news/headwinds",
         "weight": 2, "key": "no_negative_news"},
        {"name": "Analyst upgrades or positive sentiment",
         "weight": 1, "key": "analyst_positive"},
    ],
    "risk": [
        {"name": "Clear stop-loss level identified",
         "weight": 3, "key": "stop_loss_clear"},
        {"name": "Risk/reward ratio >= 2:1",
         "weight": 3, "key": "rr_ratio"},
        {"name": "Position size within 2% risk rule",
         "weight": 2, "key": "position_sized"},
        {"name": "Not correlated with other open positions",
         "weight": 1, "key": "uncorrelated"},
    ]
}


def show_checklist():
    """Print the full scoring checklist."""
    print("\n10-DAY TRADE SCORING CHECKLIST")
    print("=" * 60)
    print("Score each criterion: 1 (yes) or 0 (no)")
    print("Weighted total determines trade quality.\n")

    total_weight = 0
    for category, criteria in SCORING_CRITERIA.items():
        print(f"\n{category.upper()} FACTORS:")
        print("-" * 40)
        for c in criteria:
            print(f"  [{' '}] {c['name']} (weight: {c['weight']})")
            total_weight += c['weight']

    print(f"\nMax possible score: {total_weight}")
    print(f"Minimum to trade:  {int(total_weight * 0.6)} "
          f"({60}% threshold)")
    print(f"Strong trade:      {int(total_weight * 0.8)}+ "
          f"({80}%+ threshold)")


def score_trade(args):
    """Interactive scoring for a trade."""
    ticker = args.ticker.upper()
    print(f"\nSCORING: {ticker}")
    print("=" * 50)
    print("Answer 1 (yes) or 0 (no) for each criterion:\n")

    total_score = 0
    total_weight = 0
    scores = {}

    for category, criteria in SCORING_CRITERIA.items():
        print(f"\n{category.upper()}:")
        for c in criteria:
            while True:
                try:
                    val = input(f"  {c['name']}? (1/0): ").strip()
                    val = int(val)
                    if val in (0, 1):
                        break
                except (ValueError, EOFError):
                    pass
                print("    Please enter 1 or 0")

            weighted = val * c["weight"]
            total_score += weighted
            total_weight += c["weight"]
            scores[c["key"]] = val

    pct = (total_score / total_weight) * 100

    print(f"\n{'=' * 50}")
    print(f"  {ticker} SCORE: {total_score}/{total_weight} ({pct:.0f}%)")

    if pct >= 80:
        verdict = "STRONG BUY SIGNAL - proceed with full position"
    elif pct >= 60:
        verdict = "MODERATE SIGNAL - proceed with half position"
    elif pct >= 40:
        verdict = "WEAK SIGNAL - consider skipping or very small position"
    else:
        verdict = "NO TRADE - criteria not met, skip this one"

    print(f"  Verdict: {verdict}")
    print(f"{'=' * 50}")

    # Save to watchlist
    DATA_DIR.mkdir(exist_ok=True)
    watchlist = []
    if WATCHLIST_FILE.exists():
        with open(WATCHLIST_FILE) as f:
            watchlist = json.load(f)

    watchlist.append({
        "ticker": ticker,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "score": total_score,
        "max_score": total_weight,
        "pct": round(pct, 1),
        "verdict": verdict,
        "scores": scores
    })

    with open(WATCHLIST_FILE, "w") as f:
        json.dump(watchlist, f, indent=2)

    print(f"\nSaved to watchlist.")


def show_watchlist(args=None):
    """Show all scored tickers."""
    if not WATCHLIST_FILE.exists():
        print("No watchlist entries yet. Run: python screener.py score --ticker AAPL")
        return

    with open(WATCHLIST_FILE) as f:
        watchlist = json.load(f)

    if not watchlist:
        print("Watchlist is empty.")
        return

    print("\nWATCHLIST — Scored Tickers")
    print("=" * 65)
    print(f"  {'Ticker':<8s} {'Score':>8s} {'%':>6s} {'Date':<18s} Verdict")
    print("-" * 65)

    for entry in sorted(watchlist, key=lambda x: x["pct"], reverse=True):
        print(f"  {entry['ticker']:<8s} "
              f"{entry['score']:>3d}/{entry['max_score']:<3d} "
              f"{entry['pct']:>5.1f}% "
              f"{entry['date']:<18s} "
              f"{entry['verdict'][:30]}")


def main():
    parser = argparse.ArgumentParser(description="Trade Screener & Scorer")
    sub = parser.add_subparsers(dest="command")

    p_score = sub.add_parser("score", help="Score a potential trade")
    p_score.add_argument("--ticker", required=True, help="Ticker to score")

    sub.add_parser("checklist", help="Show the full scoring checklist")
    sub.add_parser("watchlist", help="Show scored watchlist")

    args = parser.parse_args()

    if args.command == "score":
        score_trade(args)
    elif args.command == "checklist":
        show_checklist()
    elif args.command == "watchlist":
        show_watchlist()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
