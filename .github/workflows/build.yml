name: Build ICS feeds
on:
  workflow_dispatch:
  schedule:
    - cron: '0 * * * *'   # hourly (UTC)

permissions:
  contents: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0   # allow rebase before pushing

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install deps
        run: pip install "ics==0.7.2" python-dateutil requests

      - name: Generate feeds
        run: python gen_ics.py

      - name: Show outputs
        shell: bash
        run: |
          echo "::group::ls docs/feeds"
          ls -la docs/feeds || true
          echo "::endgroup::"
          echo "::group::preview ICS"
          for f in docs/feeds/*.ics; do
            [ -f "$f" ] && { echo "---- $f ----"; head -n 12 "$f"; }
          done
          echo "::endgroup::"

      - name: Upload ICS as artifact (debug)
        uses: actions/upload-artifact@v4
        with:
          name: ics-output
          path: docs/feeds/*.ics
          if-no-files-found: warn

      - name: Commit changes (rebase & push)
        shell: bash
        run: |
          git config user.name "github-actions"
          git config user.email "actions@github.com"
          git fetch origin
          git add -f docs/feeds/*.ics || true
          if git diff --staged --quiet; then
            echo "No changes to commit."
          else
            git commit -m "Update ICS feeds"
            git rebase origin/main || git pull --rebase origin main
            git push origin HEAD:main
          fi
