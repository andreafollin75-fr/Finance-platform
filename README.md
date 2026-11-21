# Finance Explained

A free, static website that follows financial news and explains it for non-experts.

- **News feed**: headlines from central banks, regulators and financial media, updated every hour, filterable by theme (Europe, United States, Macro & central banks, Markets).
- **Glossary**: 50 financial concepts in plain English (definition, example, why it matters, related concepts). Glossary words are detected automatically in the news and linked to their definition.
- **Daily Briefing**: the most important stories of the last 36 hours, ranked by a simple, documented rule (no AI).
- **About & Legal**: disclaimer, how news is handled, and the live status of every source.

> Educational and informational content only. This site does not provide investment advice.

Everything runs on free services: GitHub Actions fetches the feeds and builds the site, GitHub Pages hosts it. There is no server, no database, no paid API and no API key.

## How it works

```
pipeline/            Python: fetch feeds, clean, classify, de-duplicate, rank, write JSON
  sources.yml        the list of news feeds  <- edit this to add or remove sources
content/glossary/    one Markdown file per glossary concept  <- edit or add concepts here
site/                the website builder (Python + Jinja2 templates, one CSS file, a little JS)
data/                JSON written by the pipeline (not committed; kept between runs by the Actions cache)
dist/                the built website (not committed)
tests/               automated tests (pytest)
.github/workflows/   GitHub Actions: hourly update + deploy, and tests on pull requests
```

1. `python -m pipeline.run` downloads every feed in `pipeline/sources.yml`, keeps only the title, a short excerpt, the date and the link, assigns themes, removes duplicates, groups similar headlines into stories, ranks the Daily Briefing, and writes `data/*.json`.
2. `python site/build.py` reads `data/` and `content/` and writes plain HTML pages into `dist/`.
3. The workflow `.github/workflows/deploy.yml` does both every hour and publishes `dist/` to GitHub Pages.

If a feed is down, the error is logged, shown on the About page, and the articles already collected from that source are kept (for up to 7 days). One broken feed never stops the update.

**Why Python for the website instead of Astro?** The pipeline is already in Python, so one language and one set of dependencies is simpler to run and maintain. The site is plain HTML and CSS with about 80 lines of optional JavaScript, so pages are very light.

## Run it on your computer

You need [Python 3.11 or newer](https://www.python.org/downloads/).

```bash
python -m venv .venv
source .venv/bin/activate          # on Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m pytest                   # run the tests
python -m pipeline.run             # fetch the news into data/
python site/build.py               # build the website into dist/
python -m http.server --directory dist 8000
```

Then open <http://localhost:8000> in your browser.

## Publish it on GitHub Pages (one-time setup)

1. The repository must be **public** for GitHub Pages and hourly Actions to be free.
   *Settings > General > Danger Zone > Change visibility > Make public.*
2. Turn on Pages: *Settings > Pages > Build and deployment > Source:* choose **GitHub Actions**.
3. Go to the *Actions* tab, open **Update and deploy**, and click **Run workflow**.
   After about two minutes the site is live at `https://<your-user-name>.github.io/<repository-name>/`.

After that it updates by itself every hour.
Note: GitHub pauses scheduled workflows in a repository that has had no activity for 60 days. If that happens, GitHub sends an email; re-enable the workflow from the *Actions* tab.

## Add or remove a news source

Edit `pipeline/sources.yml` and add a block like this:

```yaml
  - name: Example News (markets)
    url: https://example.com/markets/rss.xml
    themes: [markets]        # any of: europe, us, macro, markets
    kind: media              # "official" for central banks, regulators and statistics offices
    enabled: true
```

Before adding a source, check that the URL really is an RSS or Atom feed in English, and that its terms of use allow this kind of reuse (headline, short excerpt and link). Record it in [SOURCES.md](SOURCES.md). To switch a source off, set `enabled: false`.

## Add a glossary concept

Create a file in `content/glossary/`, for example `content/glossary/stagflation.md`. The file name becomes the page address (`/glossary/stagflation/`).

```markdown
---
title: Stagflation
short: "One sentence, shown in the pop-up definitions."
aliases: [stagflation, stagflationary]
related: [inflation, recession]
---
## Definition

...

## Example

...

## Why it matters

...
```

- `aliases` are the words detected in news headlines. A word written in lowercase matches in any case (`inflation` matches "Inflation"). A word with a capital letter only matches that exact spelling (`Fed` matches "Fed" but not "fed up").
- `related` lists file names (without `.md`) of other concepts.
- The three sections are required; the tests check this.
- Examples with numbers must be marked *Hypothetical example* unless they cite a real, sourced fact.

Run `python -m pytest` to check that the new file is valid.

## How the Daily Briefing is ranked

See `pipeline/briefing.py` (the rule is also explained on the Briefing page):

```
score = 3 x number of sources covering the story (max 5)
      + up to 5 points for freshness, halved every 12 hours
      + 2 if macro/central banks, or 1 if markets
      + 2 if published by an official source
```

The top 10 stories of the last 36 hours are shown, with at most 3 led by the same source.

## Content rules

- Never republish full articles: headline, the feed's own short description (cut to 280 characters) and a link to the original only.
- No buy or sell recommendations, no price forecasts.
- No invented figures: numbers shown come from an identified source, or are clearly marked as hypothetical examples.
- Everything on the site, in the code and in the documentation is in English.

## License

Not chosen yet. Article headlines and excerpts belong to their publishers.
