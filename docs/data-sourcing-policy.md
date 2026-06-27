# Data Sourcing Policy

## Goal

Collect public professional leadership data with enough provenance that the chat can answer directly and cite why it believes the answer.

## Source Priority

1. Official company pages on the input domain.
2. Official investor relations or governance pages.
3. Official company blog/profile pages.
4. Regulatory filings for public companies.
5. Trusted startup/company profile pages, such as accelerator profiles.
6. Press releases and reputable business media.
7. Search snippets only as discovery hints, not as final claim evidence.
8. LinkedIn profile URLs as references only; do not depend on LinkedIn scraping.

## Discovery Strategy

For each input domain:

- Normalize domain and canonical URL.
- Check `sitemap.xml`.
- Probe likely paths:
  - `/about`
  - `/about-us`
  - `/team`
  - `/leadership`
  - `/management`
  - `/company`
  - `/people`
  - `/investor-relations`
  - `/governance`
  - `/newsroom`
- Parse internal links from high-signal pages.
- Optionally use a search API if configured.
- For public companies, optionally query SEC/EDGAR-like sources.

## Leadership Inclusion Rules

Include:

- Current C-level executives.
- Current Vice Presidents, including SVP and EVP.
- Current Heads of departments or functions.
- Founders only when they also hold a current executive or head role.

Exclude by default:

- Board members without an operating role.
- Advisors.
- Investors.
- Former employees.
- Article authors who are not company leaders.
- External consultants.

## Claim Model

Store facts as claims, not as one mutable person row.

Claim examples:

- role: `Chief Executive Officer`
- normalized_role: `CEO`
- department: `Executive`
- location: `Menlo Park, CA`
- profile_url: `https://...`

Each claim needs:

- source URL
- evidence snippet
- extracted timestamp
- extraction method
- confidence label

## Confidence Labels

Use a simple explainable label:

- High: official/current source with explicit title near the person's name.
- Medium: trusted third-party or multiple partial sources.
- Low: weak, dated, ambiguous, or single indirect evidence.

Do not expose confidence as fake precision unless there is a real scoring model. A label plus explanation is better for this prototype.

## Answering Policy

The chat must not invent missing facts.

Examples:

- If no CTO is found: "I could not verify a current CTO in the collected public sources."
- If only Head of Engineering is found: "I did not find a CTO; the closest technical leader in the dataset is..."
- If CEO location is absent: "The dataset does not state where the CEO is based; the company HQ is not enough to infer that."

