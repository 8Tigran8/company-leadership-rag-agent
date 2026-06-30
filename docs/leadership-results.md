# Leadership Results

This file is a human-readable view of the structured leadership data stored in the committed fixtures:

- `data/fixtures/robinhood.com.json`
- `data/fixtures/meetcampfire.com.json`

The fixtures are the canonical stored dataset. Loading them with `company-rag load-fixture` writes the same people, claims, sources, and evidence into SQLite.

## Summary

| Company | People | Claims | Sources | Notes |
| --- | ---: | ---: | ---: | --- |
| Robinhood | 24 | 25 | 3 | Current leadership roster plus former CTO evidence |
| Campfire | 5 | 6 | 6 | Current leadership claims plus former CTO evidence |

## Robinhood Leadership

Source-backed fixture: `data/fixtures/robinhood.com.json`

| Person | Title | Normalized Role | Department | Status | Source |
| --- | --- | --- | --- | --- | --- |
| Vlad Tenev | Chairman & Chief Executive Officer | CEO | Executive | current | Robinhood Investor Relations - Leadership |
| Robb Baldwin | Managing Director, Robinhood Strategies | DIRECTOR |  | current | Robinhood Investor Relations - Leadership |
| Matt Billings | VP, Brokerage; President, Robinhood Financial and Robinhood Securities | VP | Finance | current | Robinhood Investor Relations - Leadership |
| Taylor Brown | Chief of Staff | HEAD | Operations | current | Robinhood Investor Relations - Leadership |
| Nora Chan | Senior Director, Communications | DIRECTOR | Marketing | current | Robinhood Investor Relations - Leadership |
| Abhishek Fatehpuria | VP, Product Management | VP | Product | current | Robinhood Investor Relations - Leadership |
| Dan Gallagher | Chief Legal, Compliance and Corporate Affairs Officer | CLO | Legal | current | Robinhood Investor Relations - Leadership |
| Stephanie Guild, CFA | Chief Investment Officer | CIO |  | current | Robinhood Investor Relations - Leadership |
| Johann Kerbrat | SVP and GM, Crypto and International | SVP | Crypto | current | Robinhood Investor Relations - Leadership |
| Chris Koegel | VP, Corporate Finance & Investor Relations | VP | Finance | current | Robinhood Investor Relations - Leadership |
| Walter Koller | VP and COO, Robinhood Financial | VP | Finance | current | Robinhood Investor Relations - Leadership |
| Seok Lee | Vice President, Total Rewards | VP | People | current | Robinhood Investor Relations - Leadership |
| JB Mackenzie | Vice President and General Manager, Futures and Prediction Markets | VP | Markets | current | Robinhood Investor Relations - Leadership |
| Evan McHenry | VP and Chief Information Security Officer | VP | Security | current | Robinhood Investor Relations - Leadership |
| Ravi Mehta | Vice President, Credit Cards and Chief Credit Officer | VP | Credit Cards | current | Robinhood Investor Relations - Leadership |
| Lucas Moskowitz | SVP, General Counsel and Corporate Secretary | SVP | Legal | current | Robinhood Investor Relations - Leadership |
| Carley Olivas | Senior Director, Brand Marketing and Marketing Operations | DIRECTOR | Marketing | current | Robinhood Investor Relations - Leadership |
| Deepak Rao | SVP and GM, Robinhood Money, Robinhood Gold, Growth, and Marketing | SVP | Marketing | current | Robinhood Investor Relations - Leadership |
| Steve Quirk | Chief Brokerage Officer | CXO | Brokerage | current | Robinhood Investor Relations - Leadership |
| Shiv Verma | Chief Financial Officer | CFO | Finance | current | Robinhood Investor Relations - Leadership |
| Connie Schan | Chief People Officer | CPO | People | current | Robinhood Investor Relations - Leadership |
| Jordan Sinclair | President of Robinhood UK and General Manager of Bitstamp UK | HEAD | Crypto | current | Robinhood Investor Relations - Leadership |
| Nicola White | VP, Institutional Crypto; GM, Bitstamp | VP | Crypto | current | Robinhood Investor Relations - Leadership |
| Jeffrey Pinner | Chief Technology Officer | CTO | Engineering | former | Robinhood Form 8-K - CTO Departure |

Additional source-backed claim:

| Person | Claim Type | Value | Status | Source |
| --- | --- | --- | --- | --- |
| Vlad Tenev | location | Bay Area of California | current | Robinhood Management - Vlad Tenev |

Question results:

| Question | Answer |
| --- | --- |
| Who's their CTO? | No verified current CTO in the collected public sources; former CTO evidence is excluded from current-role answers |
| How many VPs do they have? | 12 current VP/SVP/EVP leaders |
| Who heads marketing? | Deepak Rao |
| Where is their CEO based? | Vlad Tenev is listed as based in the Bay Area of California |

## Campfire Leadership

Source-backed fixture: `data/fixtures/meetcampfire.com.json`

| Person | Title | Normalized Role | Department | Status | Source |
| --- | --- | --- | --- | --- | --- |
| John Glasgow | Founder & CEO | CEO | Executive | current | Campfire Series B Blog |
| Paul Nichols | Chief Technology Officer | CTO | Engineering | current | Campfire Accelerates Accounting with Claude |
| Brendan Doyle | Head of Product | HEAD | Product | current | Introducing AskEmber in Slack |
| Katrina Queirolo | VP, Marketing | VP | Marketing | current | Campfire Marketing Leadership Public Sources |
| Fernando San Martin | Co-founder / CTO | CTO | Engineering | former | Campfire Launch Blog |

Additional source-backed claim:

| Person | Claim Type | Value | Status | Source |
| --- | --- | --- | --- | --- |
| John Glasgow | location | San Francisco, California | current | Campfire Series B Blog |

Question results:

| Question | Answer |
| --- | --- |
| Who's their CTO? | Paul Nichols |
| How many VPs do they have? | 1 current VP/SVP/EVP leader |
| Who heads marketing? | Katrina Queirolo |
| Where is their CEO based? | John Glasgow is listed as based in San Francisco, California |

## How To Reproduce

```bash
uv run company-rag load-fixture data/fixtures/robinhood.com.json
uv run company-rag inspect robinhood.com --people --sources
uv run company-rag ask robinhood.com "How many VPs do they have?" --no-llm

uv run company-rag load-fixture data/fixtures/meetcampfire.com.json
uv run company-rag inspect meetcampfire.com --people --sources
uv run company-rag ask meetcampfire.com "Who's their CTO?" --no-llm

uv run python scripts/evaluate.py
```
