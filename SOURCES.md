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

Checked on 21 November 2026: each URL returned a valid RSS feed with items.
"Last item" is the date of the newest item seen during that check.

| Source | Feed URL | Themes | Type | Last item at check |
|---|---|---|---|---|
| European Central Bank (press) | https://www.ecb.europa.eu/rss/press.html | Europe, Macro | Official | 20 Nov 2026 |
| European Central Bank (blog) | https://www.ecb.europa.eu/rss/blog.html | Europe, Macro | Official | 21 Oct 2026 |
| Federal Reserve (all press releases) | https://www.federalreserve.gov/feeds/press_all.xml | US, Macro | Official | 20 Nov 2026 |
| Federal Reserve (monetary policy) | https://www.federalreserve.gov/feeds/press_monetary.xml | US, Macro | Official | 18 Nov 2026 |
| Federal Reserve (speeches) | https://www.federalreserve.gov/feeds/speeches.xml | US, Macro | Official | 20 Nov 2026 |
| Bank of England (news) | https://www.bankofengland.co.uk/rss/news | Europe, Macro | Official | 19 Nov 2026 |
| BIS (central bankers' speeches) | https://www.bis.org/doclist/cbspeeches.rss | Macro | Official | 19 Nov 2026 |
| U.S. SEC (press releases) | https://www.sec.gov/news/pressreleases.rss | US, Markets | Official | 20 Nov 2026 |
| Seeking Alpha (market news) | https://seekingalpha.com/market_currents.xml | Markets, US | Media | 21 Nov 2026 |
| Investing.com (stock market news) | https://www.investing.com/rss/news_25.rss | Markets | Media | 15 Nov 2026 |
| Investing.com (economy news) | https://www.investing.com/rss/news_14.rss | Macro | Media | 31 Oct 2026 |
| Investing.com (forex news) | https://www.investing.com/rss/news_1.rss | Markets | Media | 23 Oct 2026 |
| Yahoo Finance | https://finance.yahoo.com/news/rssindex | Markets, US | Media | 23 Sep 2026 |
| Nasdaq (markets) | https://www.nasdaq.com/feed/rssoutbound?category=Markets | Markets, US | Media | 27 Oct 2026 |
| FXStreet (forex and commodities) | https://www.fxstreet.com/rss/news | Markets | Media | 14 Oct 2026 |

Notes:
- Several media feeds showed old "newest item" dates during the check. This may come from caching by the tool used for checking rather than from the feeds themselves. The live status of each feed after every hourly run is shown on the site's About page; replace any feed that stays stale.
- The SEC asks automated clients to declare who they are in the User-Agent and to stay well below 10 requests per second; one request per hour respects this.
- The BIS feed is in RSS 1.0 (RDF) format, which the pipeline supports.
- Media feeds (Seeking Alpha, Investing.com, Yahoo Finance, Nasdaq, FXStreet) are offered for personal, non-commercial use of headlines with links back. Check their current terms before any commercial use of the site.

## Disabled: could not be verified

These feeds could not be reached from the machine used to build the project (blocked or refused), so it was not possible to confirm that they work. They are listed in `sources.yml` with `enabled: false`. To try one, set `enabled: true`, run the workflow, and check the About page.

| Source | Feed URL |
|---|---|
| BBC News (business) | https://feeds.bbci.co.uk/news/business/rss.xml |
| The Guardian (business) | https://www.theguardian.com/business/rss |
| CNBC (economy) | https://www.cnbc.com/id/20910258/device/rss/rss.html |

Also tried and rejected: Bureau of Economic Analysis RSS (robots.txt disallows automated access), Eurostat news RSS (error), IMF news RSS (error), Financial Times, The Economist and MarketWatch (blocked), Bureau of Labor Statistics "latest numbers" feed (a single table item, not news).

## Planned for Phase 2 (market data, not used yet)

FRED (free API key), Eurostat and ECB statistical data APIs, SEC EDGAR. These will be documented here when they are added.
