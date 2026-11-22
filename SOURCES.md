# Sources

Every news source used by the site, how it was checked, and the rules we follow.
The list the pipeline actually uses is `pipeline/sources.yml`.

## Rules for every source

- **Only English-language sources.**
- **Only the headline, the short description provided in the feed (cut to 280 characters), the date and a link to the original article are shown.** Articles are never copied in full.
- **Explicit User-Agent** on every request: `FinancePlatformBot/1.0 (+repository URL; educational news reader, fetches at most once per hour)`.
- **Low frequency**: each feed is requested once per hourly run.
- **Caching**: conditional requests (`If-None-Match` / `If-Modified-Since`) are sent, so an unchanged feed costs the publisher almost nothing; the last good articles are kept if a feed fails.
- If a publisher asks us to stop using its feed, remove it from `sources.yml`.

## Active sources

Checked from GitHub's servers on 22 November 2026 with `python -m pipeline.check_sources` (the "Check sources" workflow): every feed below returned a valid RSS feed with recent items.

| Source | Feed URL | Themes | Type |
|---|---|---|---|
| European Central Bank (press) | https://www.ecb.europa.eu/rss/press.html | Europe, Macro | Official |
| European Central Bank (blog) | https://www.ecb.europa.eu/rss/blog.html | Europe, Macro | Official |
| Federal Reserve (all press releases) | https://www.federalreserve.gov/feeds/press_all.xml | US, Macro | Official |
| Federal Reserve (monetary policy) | https://www.federalreserve.gov/feeds/press_monetary.xml | US, Macro | Official |
| Federal Reserve (speeches) | https://www.federalreserve.gov/feeds/speeches.xml | US, Macro | Official |
| Bank of England (news) | https://www.bankofengland.co.uk/rss/news | Europe, Macro | Official |
| BIS (central bankers' speeches) | https://www.bis.org/doclist/cbspeeches.rss | Macro | Official |
| U.S. SEC (press releases) | https://www.sec.gov/news/pressreleases.rss | US, Markets | Official |
| Seeking Alpha (market news) | https://seekingalpha.com/market_currents.xml | Markets, US | Media |
| Investing.com (stock market news) | https://www.investing.com/rss/news_25.rss | Markets | Media |
| Investing.com (economy news) | https://www.investing.com/rss/news_14.rss | Macro | Media |
| Investing.com (forex news) | https://www.investing.com/rss/news_1.rss | Markets | Media |
| BBC News (business) | https://feeds.bbci.co.uk/news/business/rss.xml | Europe | Media |
| The Guardian (business) | https://www.theguardian.com/business/rss | Europe | Media |
| The Guardian (economics) | https://www.theguardian.com/business/economics/rss | Europe, Macro | Media |
| CNBC (economy) | https://www.cnbc.com/id/20910258/device/rss/rss.html | US, Macro | Media |
| CNBC (finance) | https://www.cnbc.com/id/10000664/device/rss/rss.html | US, Markets | Media |
| MarketWatch (top stories) | https://feeds.content.dowjones.io/public/rss/mw_topstories | US, Markets | Media |
| The Economist (finance and economics) | https://www.economist.com/finance-and-economics/rss.xml | Macro, Markets | Media |

Notes:
- The live status of each feed after every hourly run is shown on the site's About page.
- The SEC asks automated clients to declare who they are in the User-Agent and to stay well below 10 requests per second; one request per hour respects this.
- The BIS feed is in RSS 1.0 (RDF) format, which the pipeline supports.
- Media feeds are offered for personal, non-commercial use of headlines with links back (for example the BBC and Guardian RSS terms). Check each publisher's current terms before any commercial use of the site.

## Disabled: failed from GitHub's servers

Kept in `sources.yml` with `enabled: false`. Run the "Check sources" workflow before switching one back on.

| Source | Feed URL | Result on 22 Nov 2026 |
|---|---|---|
| Yahoo Finance | https://finance.yahoo.com/news/rssindex | HTTP 404 |
| Nasdaq (markets) | https://www.nasdaq.com/feed/rssoutbound?category=Markets | Timed out |
| FXStreet (forex and commodities) | https://www.fxstreet.com/rss/news | HTTP 403 |

Also tried and rejected: Yahoo Finance top stories RSS (HTTP 404), Bureau of Economic Analysis RSS (robots.txt disallows automated access), Eurostat news RSS and IMF news RSS (errors), Financial Times (not checked further: its RSS terms are restrictive), Bureau of Labor Statistics "latest numbers" feed (a single table item, not news).

## How to check a source

```bash
python -m pipeline.check_sources
```

or, on GitHub: *Actions* tab > **Check sources** > **Run workflow**. The report lists every feed in `sources.yml`, enabled or not, with the number of items and the date of the newest one.

## Planned for Phase 2 (market data, not used yet)

FRED (free API key), Eurostat and ECB statistical data APIs, SEC EDGAR. These will be documented here when they are added.
