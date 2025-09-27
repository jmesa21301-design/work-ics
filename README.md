# Zero-Cost Google Sheets → iCal (ICS) Feeds

This repo lets you publish one or more **auto-updating calendar feeds** from a Google Sheet (or a CSV in the repo) using **GitHub Pages** + **GitHub Actions** — no server, no monthly hosting bill.

Your feed URL(s) will look like:
```
https://<your-username>.github.io/<this-repo-name>/feeds/<token>.ics
```
> GitHub Pages serves everything inside the `docs/` folder. Our Action drops the generated `.ics` files into `docs/feeds/` on a schedule.

---

## Quick Start (10–15 minutes)

1. **Create a new GitHub repo** and upload these files (or `git init` → `git remote add` → `git push`).  
2. **Enable GitHub Pages** for this repo: Settings → Pages →
   - Source: **Deploy from a branch**
   - Branch: **main** / folder: **/docs**
   - Save (copy the site URL it shows).
3. **Create your schedule Google Sheet** from the template below, or edit `schedule_template.csv` and commit it.  
   Columns required:
   ```
   title,start,end,all_day,location,description,timezone(optional),uid(optional)
   ```
   Example row:
   ```
   Day shift,2025-10-05 07:00,2025-10-05 19:00,FALSE,Unit 3,Med-Surg,America/New_York,NURSE-1001
   ```
4. **(Recommended) Publish your Sheet as CSV** so it stays easy to edit from your phone:
   - File → **Share** → **Publish to web** → select the correct sheet → **CSV** → Copy the link.
5. **Edit `config.json`** — replace the placeholder `csv_url` with your **published CSV link** (or a path like `data/schedule.csv` if committing a CSV in the repo).  
   Optionally change `name` and `timezone`. For privacy, also change the `token` (use `scripts/generate_token.py`).
6. **Commit & push**. The GitHub Action runs on a schedule (hourly by default).  
   When it finishes, your feed will be at:
   ```
   https://<your-username>.github.io/<this-repo-name>/feeds/<token>.ics
   ```
7. **Subscribe in your calendar app:**
   - **Google Calendar (web):** Other calendars → From URL → paste your feed URL.
   - **Apple Calendar (Mac):** File → New Calendar Subscription → paste URL.
   - **iPhone:** Settings → Calendar → Accounts → Add Account → Other → Add Subscribed Calendar → paste URL.

> Note: Calendar clients refresh subscribed calendars every few hours (Apple sometimes 4–12h; Google similar). You can keep the Action hourly/daily; the client decides when it re-fetches.

---

## Configuring multiple feeds
Add more entries to `config.json`, e.g. one for your work shifts and one for class times. Each entry creates a separate `.ics` file in `docs/feeds/`.

```json
[
  {
    "token": "my-work-<random>",
    "name": "My Work Shifts",
    "csv_url": "https://docs.google.com/spreadsheets/d/e/.../pub?output=csv",
    "timezone": "America/New_York"
  },
  {
    "token": "classes-<random>",
    "name": "Fall Semester",
    "csv_url": "data/classes.csv",
    "timezone": "America/New_York"
  }
]
```

---

## Troubleshooting

- **No updates showing?**  
  Check the **Actions** tab for run status. Re-run if needed.
- **Sheet changed columns/format?**  
  Keep the required column names. Dates like `YYYY-MM-DD HH:MM` work best.
- **Times off?**  
  Set `timezone` in `config.json`, or include a `timezone` column per row.
- **Link leaked?**  
  Change the `token` in `config.json` and delete the old `.ics` under `docs/feeds/`.

---

## Local test (optional)
```
pip install ics python-dateutil requests
python gen_ics.py
# Generated files will appear in docs/feeds/
```

---

## Security & Privacy
- Feeds are “private by URL” using long, random tokens. Don’t share your link publicly.  
- For truly private Sheets, switch from published CSV to Google Sheets API with a service account (store the key in GitHub Secrets). That’s an advanced, optional upgrade.
