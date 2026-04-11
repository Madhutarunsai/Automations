#!/usr/bin/env python3
"""
10-Day Investment Tracker
Track trades, calculate P&L, and monitor portfolio allocation.

Usage:
    python tracker.py add --ticker AAPL --type stock --action buy --qty 10 --price 185.50
    python tracker.py close --ticker AAPL --price 192.30
    python tracker.py status
    python tracker.py pnl
    python tracker.py allocation
"""

import argparse
import csv
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
TRADES_FILE = DATA_DIR / "trades.csv"
CONFIG_FILE = DATA_DIR / "config.json"

TRADE_HEADERS = [
    "id", "date", "ticker", "type", "action", "quantity", "price",
    "total", "stop_loss", "take_profit", "status", "close_price",
    "close_date", "pnl", "notes"
]

DEFAULT_CONFIG = {
    "total_capital": 10000,
    "max_risk_per_trade_pct": 2.0,
    "tier_allocations": {
        "tier1_safe": 0.40,
        "tier2_moderate": 0.35,
        "tier3_aggressive": 0.20,
        "tier4_speculative": 0.05
    },
    "start_date": "2026-04-11",
    "end_date": "2026-04-21"
}

TIER_MAP = {
    "savings": "tier1_safe", "tbill": "tier1_safe", "bond_etf": "tier1_safe",
    "stock": "tier2_moderate", "covered_call": "tier2_moderate",
    "credit_spread": "tier2_moderate", "dividend": "tier2_moderate",
    "option": "tier3_aggressive", "crypto": "tier3_aggressive",
    "leveraged_etf": "tier3_aggressive",
    "meme": "tier4_speculative", "altcoin": "tier4_speculative",
    "defi": "tier4_speculative"
}


def ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)
    if not TRADES_FILE.exists():
        with open(TRADES_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(TRADE_HEADERS)
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)


def load_config():
    ensure_data_dir()
    with open(CONFIG_FILE) as f:
        return json.load(f)


def load_trades():
    ensure_data_dir()
    trades = []
    with open(TRADES_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            trades.append(row)
    return trades


def save_trade(trade):
    ensure_data_dir()
    with open(TRADES_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TRADE_HEADERS)
        writer.writerow(trade)


def update_trades(trades):
    ensure_data_dir()
    with open(TRADES_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=TRADE_HEADERS)
        writer.writeheader()
        for t in trades:
            writer.writerow(t)


def next_id(trades):
    if not trades:
        return 1
    return max(int(t["id"]) for t in trades) + 1


def add_trade(args):
    trades = load_trades()
    config = load_config()

    total = float(args.qty) * float(args.price)
    max_risk = config["total_capital"] * (config["max_risk_per_trade_pct"] / 100)

    if total > max_risk * 10:
        print(f"WARNING: Trade size ${total:.2f} is large relative to "
              f"2% risk rule (max risk ${max_risk:.2f})")

    stop_loss = args.stop_loss or ""
    take_profit = args.take_profit or ""

    trade = {
        "id": next_id(trades),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "ticker": args.ticker.upper(),
        "type": args.type,
        "action": args.action,
        "quantity": args.qty,
        "price": args.price,
        "total": f"{total:.2f}",
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "status": "open",
        "close_price": "",
        "close_date": "",
        "pnl": "",
        "notes": args.notes or ""
    }
    save_trade(trade)
    tier = TIER_MAP.get(args.type, "unknown")
    print(f"Trade #{trade['id']} added: {args.action.upper()} {args.qty} "
          f"{args.ticker.upper()} @ ${args.price} (${total:.2f}) [{tier}]")


def close_trade(args):
    trades = load_trades()
    found = False
    for t in trades:
        if t["ticker"].upper() == args.ticker.upper() and t["status"] == "open":
            entry = float(t["price"])
            exit_price = float(args.price)
            qty = float(t["quantity"])

            if t["action"] == "buy":
                pnl = (exit_price - entry) * qty
            else:
                pnl = (entry - exit_price) * qty

            t["close_price"] = args.price
            t["close_date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            t["pnl"] = f"{pnl:.2f}"
            t["status"] = "closed"
            found = True

            pnl_pct = (pnl / (entry * qty)) * 100
            emoji = "PROFIT" if pnl > 0 else "LOSS"
            print(f"Closed {t['ticker']}: {emoji} ${pnl:.2f} ({pnl_pct:+.1f}%)")
            break

    if not found:
        print(f"No open trade found for {args.ticker.upper()}")
        return

    update_trades(trades)


def show_status(args):
    trades = load_trades()
    config = load_config()

    open_trades = [t for t in trades if t["status"] == "open"]
    closed_trades = [t for t in trades if t["status"] == "closed"]

    start = datetime.strptime(config["start_date"], "%Y-%m-%d")
    end = datetime.strptime(config["end_date"], "%Y-%m-%d")
    today = datetime.now()
    days_left = max(0, (end - today).days)

    print("=" * 60)
    print("  10-DAY INVESTMENT TRACKER")
    print(f"  Period: {config['start_date']} to {config['end_date']}")
    print(f"  Days remaining: {days_left}")
    print(f"  Starting capital: ${config['total_capital']:,.2f}")
    print("=" * 60)

    if open_trades:
        print(f"\nOPEN POSITIONS ({len(open_trades)}):")
        print("-" * 60)
        for t in open_trades:
            tier = TIER_MAP.get(t["type"], "?")
            print(f"  #{t['id']} {t['action'].upper()} {t['quantity']} "
                  f"{t['ticker']} @ ${t['price']} "
                  f"(${t['total']}) [{tier}]")
            if t["stop_loss"]:
                print(f"       Stop: ${t['stop_loss']}  Target: ${t['take_profit']}")
    else:
        print("\nNo open positions.")

    if closed_trades:
        total_pnl = sum(float(t["pnl"]) for t in closed_trades)
        winners = sum(1 for t in closed_trades if float(t["pnl"]) > 0)
        losers = len(closed_trades) - winners
        win_rate = (winners / len(closed_trades) * 100) if closed_trades else 0

        print(f"\nCLOSED TRADES ({len(closed_trades)}):")
        print("-" * 60)
        for t in closed_trades:
            pnl = float(t["pnl"])
            tag = "WIN" if pnl > 0 else "LOSS"
            print(f"  #{t['id']} {t['ticker']}: {tag} ${pnl:+.2f}")

        print(f"\n  Total P&L: ${total_pnl:+,.2f}")
        print(f"  Win rate: {win_rate:.0f}% ({winners}W / {losers}L)")
        pnl_pct = (total_pnl / config["total_capital"]) * 100
        print(f"  Return on capital: {pnl_pct:+.2f}%")


def show_pnl(args):
    trades = load_trades()
    config = load_config()

    closed = [t for t in trades if t["status"] == "closed"]
    if not closed:
        print("No closed trades yet.")
        return

    total_pnl = sum(float(t["pnl"]) for t in closed)
    capital = config["total_capital"]

    print("\nP&L BREAKDOWN BY TYPE:")
    print("-" * 40)
    by_type = {}
    for t in closed:
        ttype = t["type"]
        if ttype not in by_type:
            by_type[ttype] = 0
        by_type[ttype] += float(t["pnl"])

    for ttype, pnl in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
        tier = TIER_MAP.get(ttype, "?")
        print(f"  {ttype:20s} ${pnl:+10.2f}  [{tier}]")

    print("-" * 40)
    print(f"  {'TOTAL':20s} ${total_pnl:+10.2f}")
    print(f"  {'Return':20s} {(total_pnl/capital)*100:+10.2f}%")

    # Annualized
    ann = (total_pnl / capital) * (365 / 10) * 100
    print(f"  {'Annualized':20s} {ann:+10.1f}%")


def show_allocation(args):
    trades = load_trades()
    config = load_config()

    capital = config["total_capital"]
    tier_alloc = config["tier_allocations"]

    open_trades = [t for t in trades if t["status"] == "open"]

    actual = {"tier1_safe": 0, "tier2_moderate": 0,
              "tier3_aggressive": 0, "tier4_speculative": 0}

    for t in open_trades:
        tier = TIER_MAP.get(t["type"], "tier4_speculative")
        actual[tier] += float(t["total"])

    total_deployed = sum(actual.values())
    cash = capital - total_deployed

    print("\nPORTFOLIO ALLOCATION:")
    print("=" * 55)
    print(f"  {'Tier':<25s} {'Target':>8s} {'Actual':>8s} {'$':>10s}")
    print("-" * 55)

    tier_names = {
        "tier1_safe": "Tier 1 (Safe)",
        "tier2_moderate": "Tier 2 (Moderate)",
        "tier3_aggressive": "Tier 3 (Aggressive)",
        "tier4_speculative": "Tier 4 (Speculative)"
    }

    for tier_key, name in tier_names.items():
        target_pct = tier_alloc[tier_key] * 100
        actual_pct = (actual[tier_key] / capital * 100) if capital > 0 else 0
        diff = actual_pct - target_pct
        flag = " <<" if abs(diff) > 5 else ""
        print(f"  {name:<25s} {target_pct:>7.1f}% {actual_pct:>7.1f}% "
              f"${actual[tier_key]:>9,.2f}{flag}")

    print("-" * 55)
    deployed_pct = (total_deployed / capital * 100) if capital > 0 else 0
    print(f"  {'Deployed':<25s} {'':>8s} {deployed_pct:>7.1f}% "
          f"${total_deployed:>9,.2f}")
    cash_pct = (cash / capital * 100) if capital > 0 else 0
    print(f"  {'Cash':<25s} {'':>8s} {cash_pct:>7.1f}% ${cash:>9,.2f}")
    print(f"  {'Total':<25s} {'100.0%':>8s} {'100.0%':>8s} "
          f"${capital:>9,.2f}")


def set_capital(args):
    config = load_config()
    config["total_capital"] = float(args.amount)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Capital set to ${float(args.amount):,.2f}")


def main():
    parser = argparse.ArgumentParser(description="10-Day Investment Tracker")
    sub = parser.add_subparsers(dest="command")

    # Add trade
    p_add = sub.add_parser("add", help="Add a new trade")
    p_add.add_argument("--ticker", required=True, help="Ticker symbol")
    p_add.add_argument("--type", required=True,
                       choices=list(TIER_MAP.keys()),
                       help="Investment type")
    p_add.add_argument("--action", default="buy", choices=["buy", "sell"])
    p_add.add_argument("--qty", required=True, type=float, help="Quantity")
    p_add.add_argument("--price", required=True, type=float, help="Entry price")
    p_add.add_argument("--stop-loss", type=float, help="Stop loss price")
    p_add.add_argument("--take-profit", type=float, help="Take profit price")
    p_add.add_argument("--notes", help="Trade notes")

    # Close trade
    p_close = sub.add_parser("close", help="Close an open trade")
    p_close.add_argument("--ticker", required=True)
    p_close.add_argument("--price", required=True, type=float)

    # Status
    sub.add_parser("status", help="Show portfolio status")

    # P&L
    sub.add_parser("pnl", help="Show P&L breakdown")

    # Allocation
    sub.add_parser("allocation", help="Show portfolio allocation")

    # Set capital
    p_cap = sub.add_parser("capital", help="Set starting capital")
    p_cap.add_argument("amount", type=float)

    args = parser.parse_args()

    if args.command == "add":
        add_trade(args)
    elif args.command == "close":
        close_trade(args)
    elif args.command == "status":
        show_status(args)
    elif args.command == "pnl":
        show_pnl(args)
    elif args.command == "allocation":
        show_allocation(args)
    elif args.command == "capital":
        set_capital(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
