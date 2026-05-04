# Telegram Daily Task System — Setup

A 5-minute setup that drops the day's LinkedIn task list in your Telegram every morning.

---

## What you get

Every morning at the time you choose, a Telegram message like:

```
LinkedIn Day Plan - Mon May 04 (Week 1)

Thesis: I automate the back office of staffing firms. 6-week hires become 1-week hires.

TODAY'S POST
- Format: Carousel (8-10 slides)
- Pillar: Hiring automation playbook
- Topic idea: How I cut hiring from 6 weeks to 1 - the 7-step system
- CTA keyword: HIRING (auto-DM trigger)

DISTRIBUTION
- 15 thoughtful comments (3-Sentence Rule: Acknowledge / Expand / Engage)
- 5 comments BEFORE you publish (Tier A creators) - lifts your reach ~20%
- 10 connection invites to people who liked/commented on your last 3 posts (warm only)
- Reply to every comment on today's post within 60 minutes
- Trigger keyword-DM follow-ups (24h) for yesterday's magnet grabbers

REVENUE (Track A)
- 20 warm DM follow-ups (D2 voice notes for non-repliers)
- 1 audit call slot held open (block 14:00-15:00)

WEEK 1 MILESTONES
- Apply for LinkedIn verification
- Rewrite headline + banner + About using docs/profile-audit.md paste blocks
- ...

LOG TONIGHT
- Today's post impressions
- Followers added today
- ...

Distribution > Content. Always.
```

Content rotates by day of week. Milestones swap as you progress through the 26-week program. Tasks adapt to weekend / off days.

---

## Setup (5 minutes)

### 1. Create the Telegram bot

1. In Telegram, search for **@BotFather** and start a chat.
2. Send `/newbot`. Pick a name and a username (must end in `bot`, e.g. `madhu_linkedin_bot`).
3. BotFather replies with an **HTTP API token** like `8123456789:AAH...`. Copy it.

### 2. Get your chat_id

1. DM your new bot any message (e.g. `start`).
2. From the repo root:
   ```bash
   # Temporarily put your token in an env var
   export BOT_TOKEN="8123456789:AAH..."
   python -c "from linkedin_engine.telegram import get_chat_id_hint; print(get_chat_id_hint('$BOT_TOKEN'))"
   ```
3. Output: `chat_id = 12345678 (from yourname)`. Copy the number.

### 3. Configure

```bash
cp linkedin_engine/config.example.json linkedin_engine/config.json
```

Edit `linkedin_engine/config.json`:

```json
{
  "telegram": {
    "bot_token": "8123456789:AAH...",
    "chat_id": "12345678"
  },
  "program": {
    "start_date": "2026-05-04",
    "thesis": "I automate the back office of staffing firms. 6-week hires become 1-week hires.",
    "calendly_url": "https://calendly.com/madhu-tarun-sai/audit",
    "stripe_offer_url": "https://buy.stripe.com/your-link",
    "newsletter_name": "The Staffing Automation Brief"
  },
  "cadence": {
    "posts_per_week": 4,
    "comments_per_day": 15,
    "invites_per_day": 10,
    "warm_dms_per_day": 20,
    "podcast_pitches_per_week": 5
  }
}
```

`config.json` is gitignored — your token won't get committed.

### 4. Test

```bash
# Print today's plan to stdout (no Telegram call)
python -m linkedin_engine preview

# Send a real Telegram message (the actual command)
python -m linkedin_engine send-daily

# Print only, don't send
python -m linkedin_engine send-daily --dry-run

# Test a future date to see how week-N milestones render
python -m linkedin_engine preview --date 2026-07-31
```

### 5. Schedule it daily

#### Option A: cron (Linux / macOS)

```bash
crontab -e
```

Add this line (sends at 07:30 every morning):

```
30 7 * * * cd /home/user/Automations && /usr/bin/python3 -m linkedin_engine send-daily >> /tmp/linkedin_daily.log 2>&1
```

#### Option B: systemd timer (Linux)

`/etc/systemd/system/linkedin-daily.service`:

```ini
[Unit]
Description=LinkedIn daily task notifier

[Service]
Type=oneshot
WorkingDirectory=/home/user/Automations
ExecStart=/usr/bin/python3 -m linkedin_engine send-daily
```

`/etc/systemd/system/linkedin-daily.timer`:

```ini
[Unit]
Description=Daily LinkedIn task notifier at 07:30

[Timer]
OnCalendar=*-*-* 07:30:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable:
```bash
sudo systemctl enable --now linkedin-daily.timer
sudo systemctl list-timers linkedin-daily.timer
```

#### Option C: GitHub Actions (run from the cloud, no server needed)

`.github/workflows/linkedin-daily.yml`:

```yaml
name: LinkedIn daily plan
on:
  schedule:
    - cron: '30 7 * * *'  # 07:30 UTC daily
  workflow_dispatch:

jobs:
  send:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - name: Write config
        env:
          TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
        run: |
          python -c "import json,os; json.dump({
            'telegram': {'bot_token': os.environ['TELEGRAM_TOKEN'],
                         'chat_id': os.environ['TELEGRAM_CHAT_ID']},
            'program': {'start_date': '2026-05-04',
                        'thesis': 'I automate the back office of staffing firms. 6-week hires become 1-week hires.',
                        'calendly_url': '', 'stripe_offer_url': '', 'newsletter_name': 'The Staffing Automation Brief'},
            'cadence': {'posts_per_week': 4, 'comments_per_day': 15,
                        'invites_per_day': 10, 'warm_dms_per_day': 20,
                        'podcast_pitches_per_week': 5}
          }, open('linkedin_engine/config.json','w'))"
      - run: python -m linkedin_engine send-daily
```

Add `TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID` as GitHub repo secrets.

---

## Other commands

```bash
python -m linkedin_engine week      # which week of the program am I in?
python -m linkedin_engine chat-id   # find your chat_id (after DMing the bot)
```

---

## Customizing the plan

The day-by-day content rotation lives in `linkedin_engine/planner.py`:

- `CONTENT_BY_WEEKDAY` — what format/pillar/topic for each day of the week
- `WEEK_MILESTONES` — the milestones that fire in specific weeks (1, 2, 3, 4, 5, 8, 12, 16, 20, 24)

Edit either dict and the next message picks up the change. No restart needed.

---

## Troubleshooting

**`Telegram API error: chat not found`**
You haven't messaged the bot yet, or the chat_id is wrong. DM the bot first, then run `python -m linkedin_engine chat-id`.

**`Config not found`**
You skipped step 3. Copy `config.example.json` to `config.json`.

**Cron job runs but no message arrives**
Cron's `$PATH` is minimal. Use absolute paths: `/usr/bin/python3` and absolute `cd /home/user/Automations` first. Check `/tmp/linkedin_daily.log` for errors.

**Message looks broken (asterisks showing as raw `*`)**
Telegram parse_mode is `Markdown`. If you switch to `MarkdownV2`, you have to escape `_*[]()~``>#+-=|{}.!`. Stay on `Markdown` unless you have a reason.
