# Saturday 21 November 2026 — The World in One Day

[![news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/c/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/besan11/news-image-20261121-r2-local/rank.svg)](https://make.fun/c/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/besan11/news-image-20261121-r2-local/reward.svg)](https://make.fun/c/news-image-20261121)

One front page for Saturday 21 November 2026: the COP31 climate talks running
into overtime with no deal, three Houthi missiles shot down over Riyadh, and
the magnitude 6.7 earthquake in Peru — plus 32 more stories, from Zelensky's
warning on the Crimea bridge to BepiColombo reaching Mercury, Bitcoin slipping
below $59,000, and K L Rahul's century in Wellington. 35 stories across
7 regions, every number checked against fresh reporting (Reuters, AP, AFP,
ESA, USGS, CoinGecko, Formula 1) before drawing. Each card carries a status
tag — CONFIRMED, OFFICIAL, REPORTED or CLAIM — so the page says plainly how
solid each story is, and a DATE CHECK box names the Friday news that was
deliberately left out.

The page is a cream newspaper front page: giant serif date, red italic
sub-dek, a six-number stats ticker, coloured region chips, three leads with
big filled art, ten secondary panels as solid mini-scenes, a numbered world
map, two-column briefs, the DATE CHECK box, and a one-day assertion footer.

## How it works

- `render.py` draws `entry.png` (1024×1024, under 1 MiB) with PIL from the
  story data at the top of the file. No network, no input besides the DejaVu
  fonts in `fonts/`. Text is measured before it is drawn: any block that
  would overflow its box raises instead of shipping clipped text.
- `main.py` (Python 3.13, standard library only) is the entry program the
  grader runs: it copies `entry.png` to `$MAKEFUN_OUTPUT_DIR/entry.png` and
  checks the PNG magic bytes and the 1 MiB cap first. It never deletes the
  output directory or its contents — it only overwrites the one file
  `entry.png` — so it is safe when the output directory is a bind mount.
  Both runs write identical bytes.

## Run it

```sh
python3 render.py            # rebuild entry.png from the story data
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py   # entry program
python3 check.py             # self-check: gates + two-run identity + grader rehearsal
```

## Files

- `entry.png` — the entry image (the deliverable)
- `render.py` — the renderer (PIL; local use only, not run by the grader)
- `main.py` — the graded entry program (stdlib only)
- `check.py` — self-check script
- `fonts/` — DejaVu Sans / DejaVu Serif TTFs used by the renderer
- `NOTES.md` — engineering notes: design decisions, verified facts, limits

Referral code: `jpgk45b3` — https://make.fun/r/jpgk45b3
