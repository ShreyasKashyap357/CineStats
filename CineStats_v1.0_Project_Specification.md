# CineStats
## Global Movies, TV & Animation Analytics Tracker
### Project Requirements & Technical Specification — v1.0 (Initial Release)

---

| Field | Value |
|---|---|
| Project Name | CineStats — Global Movies, TV & Animation Analytics Tracker |
| Version | v1.0 — Initial Release |
| Document Type | Project Requirements & Technical Specification |
| Audience | Indian & Global Movie / TV / Animation Enthusiasts |
| Platform | Streamlit Web Application |
| Default Theme | Dark Mode (Light Mode available) |
| Monetization | Free Forever — No Ads, No Paid Tier |
| Status | Planning / Pre-Development |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Project Overview](#2-project-overview)
   - 2.1 [Goals & Objectives](#21-goals--objectives)
   - 2.2 [Target Audience](#22-target-audience)
   - 2.3 [Scope & Boundaries](#23-scope--boundaries)
3. [Navigation & UI Structure](#3-navigation--ui-structure)
   - 3.1 [Sidebar Navigation](#31-sidebar-navigation)
   - 3.2 [Dark & Light Mode](#32-dark--light-mode)
   - 3.3 [Currency Selector](#33-currency-selector)
   - 3.4 [Country Lens Selector](#34-country-lens-selector)
   - 3.5 [Expandable Sections Setting](#35-expandable-sections-setting)
   - 3.6 [Anonymous User Identity](#36-anonymous-user-identity)
4. [Home Tab](#4-home-tab)
   - 4.1 [Currently in Theatres](#41-currently-in-theatres)
   - 4.2 [Currently Airing](#42-currently-airing)
   - 4.3 [Daily / Weekend Movers](#43-daily--weekend-movers)
   - 4.4 [Trending This Week](#44-trending-this-week)
   - 4.5 [On This Day Preview](#45-on-this-day-preview)
   - 4.6 [Top of Year by Content Type](#46-top-of-year-by-content-type)
   - 4.7 [What's New](#47-whats-new)
   - 4.8 [Home PDF Export](#48-home-pdf-export)
5. [Movies Tab](#5-movies-tab)
   - 5.1 [Movie List & Filters](#51-movie-list--filters)
   - 5.2 [Movie Detail View](#52-movie-detail-view)
   - 5.3 [Franchise & Parent Franchise View](#53-franchise--parent-franchise-view)
   - 5.4 [Origin Country](#54-origin-country)
6. [TV Series Tab](#6-tv-series-tab)
   - 6.1 [Series List & Filters](#61-series-list--filters)
   - 6.2 [TV Series Detail View](#62-tv-series-detail-view)
   - 6.3 [India & International TV](#63-india--international-tv)
7. [Animated Shows Tab](#7-animated-shows-tab)
   - 7.1 [Anime Sub-section](#71-anime-sub-section)
   - 7.2 [Western Animation Sub-section](#72-western-animation-sub-section)
   - 7.3 [Cartoons Sub-section](#73-cartoons-sub-section)
8. [On This Day Tab](#8-on-this-day-tab)
9. [Compare Tab](#9-compare-tab)
   - 9.1 [Within-Category Compare](#91-within-category-compare)
   - 9.2 [Cross-Category Compare](#92-cross-category-compare)
   - 9.3 [Saved Comparisons](#93-saved-comparisons)
10. [Search](#10-search)
11. [PDF Report Export](#11-pdf-report-export)
12. [Posters & Media](#12-posters--media)
13. [Core Features Reference](#13-core-features-reference)
14. [Data Sources](#14-data-sources)
    - 14.1 [Box Office Mojo](#141-box-office-mojo)
    - 14.2 [Sacnilk](#142-sacnilk)
    - 14.3 [TMDB API](#143-tmdb-api)
    - 14.4 [Jikan API (MAL)](#144-jikan-api-mal)
    - 14.5 [AniList GraphQL API](#145-anilist-graphql-api)
    - 14.6 [TVMaze API](#146-tvmaze-api)
    - 14.7 [Wikipedia Episode Tables](#147-wikipedia-episode-tables)
    - 14.8 [Exchange Rate API](#148-exchange-rate-api)
    - 14.9 [Trending Sources](#149-trending-sources)
    - 14.10 [Data Matching & Unification](#1410-data-matching--unification)
15. [Technology Stack](#15-technology-stack)
16. [System Architecture](#16-system-architecture)
    - 16.1 [Data Layer](#161-data-layer)
    - 16.2 [Business Logic Layer](#162-business-logic-layer)
    - 16.3 [Presentation Layer](#163-presentation-layer)
    - 16.4 [Data Flow](#164-data-flow)
17. [Database Schema](#17-database-schema)
18. [Data Refresh & Caching Policy](#18-data-refresh--caching-policy)
19. [API Rate Limits](#19-api-rate-limits)
20. [Functional Requirements](#20-functional-requirements)
21. [Non-Functional Requirements](#21-non-functional-requirements)
22. [UI/UX Design Specification](#22-uiux-design-specification)
    - 22.1 [Dark Mode](#221-dark-mode-primary)
    - 22.2 [Light Mode](#222-light-mode)
    - 22.3 [Component Patterns](#223-component-patterns)
    - 22.4 [Genre Filter Drawer](#224-genre-filter-drawer)
    - 22.5 [Advanced Search](#225-advanced-search)
23. [Scraper & API Contract](#23-scraper--api-contract)
24. [Error Handling & Graceful Degradation](#24-error-handling--graceful-degradation)
25. [Logging Strategy](#25-logging-strategy)
26. [Unit Testing Strategy](#26-unit-testing-strategy)
27. [Build Plan & Milestones](#27-build-plan--milestones)
28. [Configuration & Environment Setup](#28-configuration--environment-setup)
29. [Legal & Ethical Considerations](#29-legal--ethical-considerations)
30. [Known Limitations](#30-known-limitations)
31. [Future Scope & Roadmap](#31-future-scope--roadmap)
32. [Risks & Mitigations](#32-risks--mitigations)
33. [Changelog](#33-changelog)
34. [Glossary](#34-glossary)

---

## 1. Executive Summary

CineStats is a modern, dark-mode-first interactive web analytics dashboard tracking box office performance, viewership, and ratings data across Movies, TV Series, Anime, Western Animation, and Cartoons. It is permanently free with no advertising and no paid tier.

The application has dedicated sidebar tabs for Movies, TV Series, Animated Shows (containing Anime, Western Animation, and Cartoons sub-sections), Compare, On This Day, Search, and Settings, with the Home tab as the default fully-populated landing view.

Four core principles guide CineStats: **immediate value on first load**, **responsible data access** (session caching and strict API rate limit adherence), **full analytical depth** (franchise hierarchies, anime cour/arc/season/episode views, cross-category comparison), and **portability** (every view is PDF-exportable with full metadata).

This document is the v1.0 initial release specification. All design decisions, data models, API contracts, functional requirements, and build milestones herein represent the full scope of the first release.

---

## 2. Project Overview

### 2.1 Goals & Objectives

- Deliver a fully-populated Home tab on first load with no required user input.
- Track Movies, TV Series, Anime, Western Animation, and Cartoons as first-class content types with dedicated tabs.
- Support a flexible franchise hierarchy: Episode → Season/Cour/Arc → Series → Sub-Franchise → Parent Franchise.
- Allow within-category comparison (up to 10) and opt-in cross-category comparison (TV Series, Anime, Western Animation, Cartoons).
- Provide PDF export on every view with full metadata: data date range, sources, exchange rates, country lens, N/A explanations.
- Support multi-currency display and a configurable country lens (Global + up to 3 countries).
- Enforce session-based caching and strict API rate limits.
- Be permanently free — no ads, no subscriptions, no paywalls, no data selling.

### 2.2 Target Audience

- Indian movie and TV enthusiasts tracking both Hollywood/global and domestic releases.
- Anime fans wanting score, popularity, and structural data (cour/arc/season) in one place.
- Box office analysts and hobbyist researchers seeking comparative and historical data.
- Casual users checking what is currently in theatres or airing.
- Developers and students exploring Streamlit, scraping, and multi-API data pipelines.

### 2.3 Scope & Boundaries

| Area | Detail |
|---|---|
| In Scope | Movies (global + country lens), TV Series, Anime (all demographics + origin countries), Western Animation, Cartoons/Kids, Franchise hierarchy (Parent → Sub-Franchise → Series → Season/Arc/Cour/Episode), Compare (within + cross-category), On This Day date browser, PDF export, multi-currency, posters, dark/light mode, saved comparisons, trending, watchlist. |
| Out of Scope | Ticket booking, OTT/streaming viewership (future), social media integration, user accounts, push notifications, Crunchyroll popularity data. |
| Anime Movies | Anime feature films (e.g. Your Name, Demon Slayer: Mugen Train) are tracked in the Movies tab, not Animated Shows. |
| Cross-Category Compare | TV Series, Anime, Western Animation, and Cartoons may be cross-compared (opt-in, with warning). Movies/Franchises are never cross-compared with episodic content. |
| Data Cutoff | All data is 1–2 days prior to current date. A "Data current as of [date]" label is always shown. No partial current-day data is ever displayed. |
| Monetization | Free forever. No advertising. No premium tier. |
| Deployment | Streamlit Community Cloud (free tier). SQLite for local persistence. Pre-warmed `seed.db` committed to repo for cold-start resilience (see Section 16.4). |
| Legal | Personal and educational use only. No commercial redistribution. |

---

## 3. Navigation & UI Structure

### 3.1 Sidebar Navigation

CineStats uses a persistent left sidebar for all primary navigation. The sidebar is always visible.

| Tab | Description |
|---|---|
| **Home** | Default landing view. Fully populated on load. Jump-to-section anchor nav at top. PDF export button. |
| **Movies** | Browse, filter, and explore movies. Access Movie Detail, Franchise, Sub-Franchise, and Parent Franchise views. |
| **TV Series** | Browse and explore TV series. Dedicated detail views with season and episode data. |
| **Animated Shows** | Three sub-sections: Anime, Western Animation, and Cartoons. Each has its own filters, sub-tabs, and detail views. |
| **Compare** | Within-category and cross-category comparison. Saved comparisons list. |
| **On This Day** | Full date browser: single date or date range, all content types. |
| **Search** | Unified search with content type pre-filter, advanced search, and genre drawer. |
| **Settings** | Currency, country lens, default content type, expandable sections, theme toggle, PDF settings, log viewer. |

### 3.2 Dark & Light Mode

- **Default is Dark Mode**: main canvas `#0F172A`, cards `#1E293B`, primary accent `#3B82F6` (blue), secondary `#8B5CF6` (purple), positive `#10B981` (green), negative `#EF4444` (red), anime accent `#F59E0B` (amber). Designed to feel premium and polished.
- **Light Mode** is colourful, modern, and sleek — white cards with soft shadows, vibrant accent colours, subtle gradient section headers. Not a plain white page.
- Toggle in Settings and as a quick-access icon in the top bar. Persists for the session.
- All Plotly charts use matching templates: `plotly_dark` for dark mode, a custom light template for light mode.
- Exported PDFs always use a clean neutral light theme for print legibility.

### 3.3 Currency Selector

| Field | Detail |
|---|---|
| Supported | USD ($), INR (₹), EUR (€), GBP (£), JPY (¥), AED, AUD (A$), CAD (C$), SGD (S$) |
| Default | INR (₹) |
| Worldwide Gross Rule | Always USD as primary. If non-USD selected, converted amount in brackets: e.g. $599M (₹4,980 Cr). If USD selected, only USD shown. |
| India Figures | Always INR (₹ Cr) as primary. Converted value in brackets if selected currency differs. |
| Exchange Rates | Fetched once per session from open.er-api.com. "Rates as of [time]" label shown. Hardcoded fallback if API unavailable. |
| Saveability | Saved in SQLite keyed by anonymous user UUID (see Section 3.6) and restored on next visit. |

### 3.4 Country Lens Selector

Controls which countries' specific performance data is highlighted alongside global figures.

| Field | Detail |
|---|---|
| Structure | Global is always shown. Up to 3 additional country slots (C1, C2, C3). Maximum 4 columns: Global + C1 + C2 + C3. |
| Default | Global + India (C1). C2 and C3 empty. |
| Selection | Clicking any slot opens a searchable dropdown of all countries with available data. Slot can be cleared. |
| Scope | Applies across Movies, TV Series, and Animated Shows data views. |
| Saveability | Saved in SQLite keyed by anonymous user UUID (see Section 3.6) and restored on next visit. |

### 3.5 Expandable Sections Setting

| Field | Detail |
|---|---|
| Purpose | Sections on detail views exceeding the configured line threshold are auto-collapsed on first load. |
| Default Threshold | 5 lines. User-configurable between 3 and 20 lines. |
| Per-Section Override | Individual sections can be pinned to always-expanded or always-collapsed. |
| PDF Override | PDF exports always render all sections fully expanded regardless of UI settings (configurable in Settings). |
| Persistence | Saved in SQLite keyed by anonymous user UUID (see Section 3.6). |

### 3.6 Anonymous User Identity

| Field | Detail |
|---|---|
| Purpose | Enables cross-session preference persistence (currency, country lens, theme, watchlist, saved comparisons) without requiring user accounts or login. |
| Mechanism | On first visit, a UUID v4 is generated and stored in the browser's `localStorage` via the `streamlit-local-storage` package. This UUID is read on every subsequent visit and used as the `user_uuid` key in SQLite tables that store user-specific data. |
| Scope | Used by `user_preferences`, `saved_comparisons`, and `watchlist` tables. NOT used by `scrape_cache` (which remains keyed by Streamlit's ephemeral `session_id` since cache entries are intentionally per-session). |
| Privacy | The UUID is a random string with no correlation to any personal data. No PII is collected or inferred. |
| Fallback | If `localStorage` is blocked by the browser, a new UUID is generated each visit and the user effectively gets a fresh-session experience. A subtle info label is shown: "Preferences will not persist — browser storage is unavailable." |

---

## 4. Home Tab

The Home tab is the default landing page. Fully populated on first load. A jump-to-section anchor nav bar sits at the top. A "Data current as of [date]" label is shown in the page header.

### 4.1 Currently in Theatres

- Shows movies currently running in cinemas globally and in the configured country lens.
- Movie poster cards: poster (with fallback), title, worldwide gross, country-lens gross, days in release, verdict badge.
- Sorted by current worldwide gross descending. Filterable by origin country.
- Clicking any card navigates to that Movie Detail view.

### 4.2 Currently Airing

- Shows TV series and animated content currently airing. Split into sub-sections by content type: TV Series, Anime, Western Animation, Cartoons. Empty sub-sections hidden entirely.
- For Anime, seasonal context noted (e.g. "Spring 2026") but shows all currently airing anime regardless of start date.
- Each entry: poster, title, network/platform, episode count so far, latest episode date, score/rating where available.

### 4.3 Daily / Weekend Movers

- Biggest daily and weekend gross gainers and losers among currently running films.
- **Movies (Global)**: Computed from BOM daily charts. Shows absolute daily gross change and percentage change vs prior day/weekend.
- **Movies (India)**: Computed from Sacnilk day-wise collections. Same metrics in INR Cr.
- Displayed as a compact table with colour-coded arrows (green up, red down) and % change badges.
- Refreshed on session load from the most recent available data.
- Algorithm: `MoverCalculator` computes `(today_gross - yesterday_gross) / yesterday_gross * 100` for % change. Sorted by absolute % change descending. Top 5 gainers and top 5 losers shown.

### 4.4 Trending This Week

- External signals only. Content types with no available external signal are hidden.
- **Movies**: BOM weekly chart movers (biggest weekly gross gainers).
- **Anime**: MAL trending and AniList trending scores.
- **TV Series and Western Animation**: hidden if no external trending signal available.
- Horizontally scrollable card row per content type.

### 4.5 On This Day Preview

- 4–6 notable titles released on today's date in prior years, across all content types.
- Each card: poster, title, content type badge, year, key metric.
- "View Full On This Day" link navigates to the On This Day tab.

### 4.6 Top of Year by Content Type

One sub-section per content type for the current year. Sub-sections with no data hidden. Order: Movies (Global + Country Lens), TV Series, Anime, Western Animation, Cartoons.

| Content Type | Metrics & Visualisation |
|---|---|
| Movies | Global Top: worldwide gross leaders. Country Lens Top: per configured countries. Grouped bar chart + table. |
| TV Series | Top by average viewership or rating. Bar chart + table. |
| Anime | Top by MAL score, AniList score, MAL popularity. One bar chart per metric. |
| Western Animation | Top by IMDb rating and episode count. Bar chart + table. |
| Cartoons | Top by IMDb rating for current year. Table with age rating column. |

### 4.7 What's New

- Recently fetched/added titles to CineStats shown as a horizontally scrollable card row.
- Populated from `app_log`: most recently successfully scraped or API-fetched entity records.

### 4.8 Home PDF Export

- "Download Home Report" button at the top of the Home tab.
- Exports all visible Home sections with full data tables, embedded charts, and complete metadata.

---

## 5. Movies Tab

### 5.1 Movie List & Filters

- Paginated grid of movies with poster cards. Default sort: worldwide gross descending for current year. Pagination state (current page, page size) tracked in `st.session_state`. Navigation via Previous/Next buttons and an optional page-number input. Default page size: 24 cards (configurable: 12/24/48).
- Filters: Year range, Origin Country (multi-select), Language (multi-select), Verdict (multi-select), Minimum worldwide gross, Minimum country-lens gross. Genre via modal drawer (multi-select).
- Toggle between grid view (poster cards) and compact table view.

### 5.2 Movie Detail View

| Section | Content |
|---|---|
| Header | Poster, title, release date, origin country, language, genre tags, verdict badge, runtime. |
| Key Metrics Bar | Worldwide Gross, Domestic Gross, Foreign Gross, Country Lens Gross per configured country, Opening Weekend, Days in Release, Theater Count — as stat cards. |
| Regional Breakdown | Expandable table: US, India, China, UK, Overseas, all configured country lens countries. India row splits Hindi vs regional language collections where available. |
| Daily/Weekly Chart | Plotly line chart of daily gross over full run. Global and country lens on same chart. |
| Cumulative Chart | Plotly cumulative gross trajectory. |
| Opening vs Lifetime | Opening weekend gross, opening % of total, projected lifetime with confidence range. The `PredictorEngine` uses a historical-average model: it computes the average opening-to-lifetime multiplier for films of the same language, genre, and release month over the past 5 years, applies it to the current opening weekend, and returns a projected lifetime gross with a ±1 standard deviation confidence range. |
| Clash Analyzer | If other films share the same release date, a dedicated clash section shows side-by-side opening day/weekend performance and verdict outcomes for all clashing films. Accessible via a "View Clash" button. The `ClashDetector` groups films with matching release dates (±1 day tolerance for India vs global offsets). |
| Verdict Context | How the film's verdict compares to others in its language, genre, and franchise (if applicable). Shows verdict distribution for similar films. |
| On This Day Context | Other movies that opened on the same calendar date in prior years. |
| Staff & Credits | Expandable: Director, Producers, Key Cast, Studio. |
| Franchise Link | If film belongs to a franchise, prominent link to Series/Franchise view. |
| Similar Titles | 4–6 suggestions by genre, origin country, and era. The `SimilarTitleRecommender` uses a rule-based scoring system: +3 for same genre overlap, +2 for same origin country, +1 for same decade, +2 for similar gross range (within 2× factor). Top 6 by score shown. |
| PDF Export & Compare | Available on all movie detail views. |

### 5.3 Franchise & Parent Franchise View

| Level | Description |
|---|---|
| Series View | All films in a single series. No entry limit. Per-film bar chart, cumulative trajectory, verdict distribution, regional splits. |
| Sub-Franchise View | A named branch of a Parent Franchise (e.g. MCU Spider-Man vs Raimi Spider-Man). Reboot/Continuation/Spin-off/Parallel Entry labelled. |
| Parent Franchise View | Top-level brand (e.g. Spider-Man Franchise, Fate Franchise). Combined aggregate across all sub-franchises plus per-sub-franchise breakdown. Parallel entries shown as peers, not sequels. |
| Relationship Tags | Each sub-franchise tagged: Original, Reboot, Continuation, Spin-off, Remake, Parallel Entry. |
| PDF Export & Compare | Available at each hierarchy level. |

### 5.4 Origin Country

- Movies from any country with BOM data are searchable and viewable.
- Origin country set from TMDB metadata on each movie record.
- The country lens selector (Section 3.4) controls which country performance columns are shown.

---

## 6. TV Series Tab

### 6.1 Series List & Filters

- Paginated grid with poster cards.
- Filters: Status (Ongoing/Ended), Origin Country (multi-select), Network/Streamer, Year premiered. Genre via modal drawer.
- Grid / compact table toggle.

### 6.2 TV Series Detail View

| Section | Content |
|---|---|
| Header | Poster, title, network, origin country, genre tags, status badge, premiere date, total seasons, total episodes. |
| Key Metrics Bar | Average Viewership (where available), Peak Viewership, Average Rating, Total Episodes, Seasons, Status. |
| Season Overview | All seasons: number, episode count, premiere date, average viewership, average rating, peak episode. |
| Viewership Chart | Plotly line chart of episode-by-episode viewership across all seasons with season markers. |
| Rating Chart | Plotly line chart of episode ratings across all seasons. |
| Season Comparison | Bar chart: average viewership per season. |
| Episode Table | Expandable per-season episode list: title, air date, viewership, rating. |
| Staff & Credits | Expandable: Creator, Showrunner, Key Cast, Production Studio. |
| Similar Titles | 4–6 suggestions by genre and origin country. |
| PDF Export & Compare | Available on all TV series detail views. |

### 6.3 India & International TV

- Indian TV series included. Metadata from TVMaze and IMDb. BARC TRP/TVR not publicly accessible — documented as Known Limitation.
- For Indian series: IMDb rating and episode count are the primary available metrics. Viewership shown as "Data unavailable".
- International TV viewership (UK BARB, etc.) similarly unavailable except where Wikipedia episode tables exist.

---

## 7. Animated Shows Tab

The Animated Shows tab contains three sub-sections: **Anime**, **Western Animation**, and **Cartoons**. Anime feature films are tracked in the Movies tab.

### 7.1 Anime Sub-section

#### Demographic Sub-tabs

Content organised into demographic sub-tabs. No selection shows all anime. Multiple selections are additive.

| Sub-tab | Description |
|---|---|
| Shounen | Targeted at young male audiences. Examples: Naruto, One Piece, Demon Slayer. |
| Shoujo | Targeted at young female audiences. Examples: Sailor Moon, Fruits Basket. |
| Seinen | Targeted at adult male audiences. Examples: Vinland Saga, Berserk. |
| Josei | Targeted at adult female audiences. Examples: Nana, Chihayafuru. |
| Kodomomuke / Kids | Targeted at young children. Examples: Doraemon, Pokémon. Also appears in Cartoons sub-section. |

#### Origin Country Sub-tabs

A second filter layer: Japan, Korea, China, India, Other. Multiple selectable simultaneously. None selected shows all.

#### Anime Detail View

| Section | Content |
|---|---|
| Header | Poster, title (Japanese native + English/romaji), origin country, studio, demographic tag, genre tags, source material, premiere season (e.g. Spring 2021), status badge. |
| Score Bar | MAL Score, MAL Rank, MAL Popularity, MAL Members, MAL Favourites, AniList Score, AniList Popularity — as stat cards. All shown where available; N/A where not. |
| View Selector | User chooses structural view: **Cour View**, **Season View**, **Story Arc View**, or **Episode View**. Unavailable views are hidden (not greyed out). |
| Season View | All seasons with episode count, premiere date, score, and status. Split seasons shown individually by default. |
| Flattened View Toggle | Only appears if split seasons or split cours exist. Combines all parts into a single unified entry. |
| Cour View | All cours with episode ranges, air dates, MAL score per cour where available, status. |
| Story Arc View | Named story arcs with episode ranges, source material chapters, and arc-level score where available. |
| Episode View | Full episode list with title, air date, and rating per episode. |
| Score Charts | Plotly line chart of episode ratings over the full run. Bar chart comparing scores per season/cour. |
| Intra-Series Compare | "Compare within series" button to compare seasons/cours/arcs against each other. |
| Staff & Credits | Expandable: Director, Series Composition Writer, Character Designer, Music Composer, Studio, Original Creator. Japanese voice cast + English dub cast in separate expandable sub-sections. |
| Franchise Link | If anime belongs to a larger franchise, link to Sub-Franchise or Parent Franchise view. |
| Similar Titles | 4–6 suggestions by demographic, genre, and studio. |
| PDF Export & Compare | Available on all anime detail views. |

#### Anime Franchise Hierarchy

Anime franchises follow the same Parent Franchise → Sub-Franchise → Series hierarchy as movies. Complex parallel franchises (e.g. Fate, Monogatari) are structured as: Parent Franchise = top-level brand, each named entry is its own Sub-Franchise or Series. The Parent Franchise view shows all branches as peers with clear labelling.

### 7.2 Western Animation Sub-section

Covers animated series primarily produced in Western countries not classified as anime and not primarily targeted at young children. Examples: Arcane, Invincible, Avatar: The Last Airbender, Gravity Falls, Rick and Morty.

- Filters: Origin Country (multi-select), Network/Streamer, Status. Genre via modal drawer.
- Metrics: IMDb rating, episode count, seasons, network, status. Viewership where available via Wikipedia tables.
- Detail view follows TV Series Detail View structure. Credits: Creator, Voice Cast, Animation Studio.

### 7.3 Cartoons Sub-section

Covers animated content primarily targeted at children and young audiences from any country of origin. Includes Western kids' animation, Kodomomuke anime (tagged accordingly), and kids' animated shows from India, Korea, and elsewhere.

| Field | Detail |
|---|---|
| Age Filter | US: TV-Y (all children), TV-Y7 (7+), TV-G (general), TV-PG (parental guidance). India: U (Universal), U/A 7+, U/A 13+. Both systems shown where available. Multi-select across both. |
| Kodomomuke Tag | Anime-origin kids content tagged "Kodomomuke". Badge shown on cards and detail views. |
| Origin Country | Multi-select filter across all origins. |
| Metrics | IMDb rating, episode count, seasons, network, age rating, origin country, status. Viewership where available. |
| Detail View | Same structure as TV Series detail view. Credits: Creator, Voice Cast, Production Studio. |

---

## 8. On This Day Tab

The On This Day tab is a full date browser: view content released on a specific date or within a custom date range.

| Feature | Detail |
|---|---|
| Default View | Today's date. All content released on this calendar date in any prior year, categorised by content type. |
| Date Picker | User selects any specific date. View updates accordingly. |
| Date Range Mode | Toggle to a date range picker (start + end date). |
| Released in Range / Airing During Range | Toggle switch in date range mode. "Airing During Range" shows content that was actively airing during any part of the selected range. |
| Content Type Filter | Multi-select to show only chosen content types. Default: all shown. Empty types hidden. |
| Result Layout | Cards grouped by content type. Each card: poster, title, year, key metric. Types with no results hidden. |
| PDF Export | Export the current On This Day view as a PDF report with full metadata. |

---

## 9. Compare Tab

### 9.1 Within-Category Compare

| Field | Detail |
|---|---|
| Entity Limit | Up to 10 entities per comparison. |
| Selection | Add via search-and-add input in Compare tab, or "Add to Compare" button on any detail view. |
| Movies/Franchises | Metrics table: Worldwide Gross, Domestic, Foreign, Country Lens Gross, Opening Weekend, Days in Release, Verdict. Bar chart (grouped), trajectory overlay, verdict matrix, regional pies. |
| TV Series | Metrics: Seasons, Episodes, Avg Viewership, Peak Viewership, Avg Rating, Status. Viewership-per-season and rating-per-season overlaid line charts. |
| Anime | Metrics: MAL Score, AniList Score, MAL Rank, MAL Popularity, Episodes, Seasons/Cours, Status, Studio. Score comparison bar chart. |
| Western Animation / Cartoons | Metrics: IMDb Rating, Seasons, Episodes, Network, Status. Rating comparison bar chart. |
| Anime Intra-Series Compare | Within a single anime, seasons/cours/arcs compared against each other. Accessible from anime detail view. |

### 9.2 Cross-Category Compare

Allows TV Series, Anime, Western Animation, and Cartoons to be compared in the same view. Movies and Franchises are **never** cross-compared with episodic content.

| Field | Detail |
|---|---|
| Opt-in | User enables via an explicit toggle labelled "Cross-Category Mode". |
| Visual Warning | Prominent amber banner: "You are comparing content across different categories. Some metrics may not be directly comparable. Missing metrics are shown as N/A." |
| Shared Metrics | Title, Content Type Badge, Episodes, Seasons, IMDb Rating (or equivalent), Status, Origin Country. |
| Category-Specific Metrics | Secondary expandable table: MAL Score (Anime only), Viewership (TV only), Age Rating (Cartoons only), etc. N/A for inapplicable categories. |
| Entity Limit | Up to 10 total across all categories combined. |

### 9.3 Saved Comparisons

| Field | Detail |
|---|---|
| Persistence | Saved to SQLite. Persist across sessions and accessible to all users of the deployment. |
| Naming | Auto-generated name (e.g. "MCU Franchise vs DCEU vs Spider-Man — Movies — 2026-03-25") that user can edit before saving. Name should uniquely identify the comparison so anyone can replicate it. |
| Saved List | Listed at top of Compare tab. Clicking loads it. |
| Delete | Individual deletion and "Clear All" option. |
| PDF Export | Any saved comparison can be exported as a PDF report. |

---

## 10. Search

| Feature | Detail |
|---|---|
| Search Bar | Prominent input. Searches as user types (300ms debounce) against local SQLite. |
| Content Type Pre-filter | Selector: All / Movies / TV Series / Anime / Western Animation / Cartoons / Franchise. Default: All. |
| Content Type Badges | Shown on result cards when multiple content types are included. Hidden when only one type is searched. |
| Search Page Note | Visible note: "Searching across all content types by default. Use the filter above to narrow by category. Content type badges appear when multiple categories are shown." |
| Result Cards | Poster, title, year, content type badge (when applicable), key metric, verdict/rating badge. |
| Advanced Search | Collapsible panel: year range, origin country (multi-select), language (multi-select), score range, gross range, status, network/studio. Genre via drawer. |
| Recent Searches | Last 10 queries shown as removable chips below search bar. Stored in session state. |
| No Results | Option to "Search live data" triggering a targeted scrape/API call. |

---

## 11. PDF Report Export

Every view that displays data is PDF-exportable. A "Download PDF Report" button is present on all detail views, compare views, Home, On This Day, and Search results.

| Field | Detail |
|---|---|
| Library | ReportLab for PDF layout. Plotly charts exported as PNG via kaleido (150 dpi) and embedded. |
| Cover Page | Report type, entity name(s), date generated, CineStats branding and version. |
| Sections | All sections rendered fully expanded regardless of UI collapse settings (configurable in Settings). |
| Charts | If kaleido fails, PDF generated without charts with a metadata note. |
| Theme | Always clean neutral light theme for print legibility. |
| Metadata Section | Data date range, sources used, exchange rate and rate date, country lens configuration, N/A fields and reason, generation timestamp, CineStats version. |
| File Naming | `CineStats_[EntityName or ReportType]_[YYYY-MM-DD].pdf` |

---

## 12. Posters & Media

| Field | Detail |
|---|---|
| Movies & TV Primary | TMDB API (API key in Streamlit secrets). Poster URLs are TMDB CDN links (e.g. `https://image.tmdb.org/t/p/w500/...`). Covers movies, TV series, Western animation, many cartoons. |
| Anime Primary | AniList GraphQL API (cover image CDN URL). Jikan API as secondary source for MAL cover image URL. |
| Rendering Strategy | Poster image URLs are passed directly to the frontend via `st.image(url)` or embedded `<img>` tags in `st.markdown()`. The **user's browser** fetches the image from the CDN asynchronously — no image bytes are downloaded by the Python backend. This prevents Streamlit's synchronous execution model from blocking on slow or failed image fetches. |
| Graceful Fallback | If the CDN URL returns a broken image, a CSS `onerror` handler on the `<img>` tag replaces it with a styled placeholder: grey box with content-type icon and "Poster not found" text rendered via inline SVG or a local fallback image bundled with the app. |
| URL Validation (Optional) | Before rendering, a lightweight HEAD request (timeout: 1s) may be performed to pre-validate the URL. If the HEAD check fails or is skipped, the browser-side `onerror` fallback handles it gracefully with no user-visible error. |
| Logging | Poster URL resolution attempts (source lookup success/failure per entity) logged to `app_log`. Browser-side rendering failures are not logged server-side. |
| PDF | For PDF export, poster images are downloaded server-side by `PDFReportBuilder` with a single attempt (timeout: 5s). On failure, a styled placeholder image is embedded instead. |
| TMDB API Key | Stored in `.streamlit/secrets.toml` (local dev) and Streamlit Cloud secrets. Never hardcoded or logged. |

---

## 13. Core Features Reference

| Feature | Description |
|---|---|
| Home Tab | Fully populated on load. Jump-to-section nav. Currently in Theatres (posters), Currently Airing (by type, empties hidden), Trending This Week (external signals), On This Day preview, Top of Year by content type, What's New, PDF export. |
| Movies Tab | Browse/filter (genre drawer), Movie Detail (stats, charts, predictor, credits, similar titles), Franchise/Sub-Franchise/Parent Franchise views, Reboot/parallel labelling, Country lens integration. |
| TV Series Tab | Browse/filter, TV Detail with season/episode data, viewership/rating charts, credits, similar titles. India + international TV included; TRP not available. |
| Animated Shows Tab | Anime (demographic + origin sub-tabs, 4 structural views, flattened toggle, intra-series compare, full credits inc. voice cast), Western Animation, Cartoons (age filter + Kodomomuke tag). |
| Franchise Hierarchy | Episode → Season/Cour/Arc → Series → Sub-Franchise → Parent Franchise. Parallel franchise support. Reboot/continuation/spin-off tagging. |
| Compare (Within) | Up to 10 entities within same category. Category-appropriate metrics, charts, trajectory overlays. Anime intra-series compare included. |
| Compare (Cross-category) | Opt-in. TV Series, Anime, Western Animation, Cartoons. Prominent amber warning. Shared + category-specific metric tables. Max 10 total. |
| Saved Comparisons | Persisted in SQLite. Auto-named + user-editable. Accessible from Compare tab. Deletable. PDF exportable. |
| On This Day Tab | Full date browser: single date or date range. Released in range + airing during range toggle. All content types grouped. |
| Search | Unified search across all types. Content type pre-filter. Badges when multi-type. Note about how multi-type search works. Advanced search panel. Genre drawer. Recent searches. |
| PDF Export | On every data view. Full sections, embedded charts (150dpi PNG), full metadata. Configurable default. |
| Posters | TMDB CDN, AniList CDN, Jikan CDN. URLs passed to browser for async rendering — no backend image download. CSS `onerror` fallback for broken images. Server-side download only for PDF embedding (single 5s-timeout attempt). URL resolution logged. |
| Currency Selector | USD/INR/EUR/GBP/JPY/AED/AUD/CAD/SGD. Worldwide always USD primary. Converted in brackets. Saved in SQLite. |
| Country Lens | Global + up to 3 countries (C1/C2/C3). Applies across Movies, TV, Animated Shows. Saved in SQLite. |
| Dark / Light Mode | Dark default (premium). Light is colourful + modern. Session persistent. |
| Expandable Sections | Per-section threshold, always-open/closed overrides. Saved in SQLite. PDF always full (configurable). |
| Trending This Week | External signals only: BOM movers (movies), MAL/AniList trending (anime). Others hidden if no signal. |
| What's New | Recently fetched titles shown on Home tab from app_log. |
| Data Cutoff | Always 1–2 days prior. "Data current as of [date]" label on all data views. |
| Session Cache | Same entity not re-scraped within session. Different entities always fetchable. |
| Logging | All scrape, API, poster, PDF, error, user action events logged to app_log in SQLite. |
| Similar Titles | 4–6 suggestions on every detail view. |
| Genre Filter Drawer | Modal drawer for genre multi-select. Available in all filterable tabs. |
| Watchlist | Per-session watchlist with milestone display. Stored in SQLite. |
| Table Toggle | Compact/comfortable table view toggle on all list views. |
| Daily / Weekend Movers | Home tab section: biggest daily gainers and losers (global + India) with absolute and % change. Refreshed on session load. |
| Clash Analyzer | Side-by-side view of films sharing the same release date, showing opening performance and verdict outcomes. Accessible from Movie Detail. |
| Verdict Context | On Movie Detail: how the film's verdict compares to others in its language, genre, and franchise. |
| Genre & Studio Aggregates | Roll-up views of top films by genre or by studio with Plotly charts. Accessible from Movies tab as sub-views. |
| CSV Export | Any data table in the application can be exported as a CSV file via a download button. |

---

## 14. Data Sources

### 14.1 Box Office Mojo

- Worldwide, domestic, and international gross totals (current year and historical). Daily and weekly charts. Currently in Theatres. Opening weekend, theater counts, weekly chart movers.

### 14.2 Sacnilk

- India Net and India Gross (INR Cr) for all Indian film industries. Day-wise India collections. Official verdicts. Currently running Indian films.

### 14.3 TMDB API

- Movie and TV posters, backdrop images, genre tags, cast, crew, origin country, language, runtime.
- Free API — requires API key. Rate limit: ~40 req/10 sec.
- Primary poster source for Movies, TV Series, Western Animation, and Cartoons.
- **Poster sizes**: `w500` used for detail views and PDF embedding. `w185` used for card thumbnails. `original` never fetched to conserve bandwidth.

### 14.4 Jikan API (MAL)

- Anime metadata: title (Japanese + English + native), MAL score, rank, popularity, members, favourites, episode count, status, demographic, genres, studio, source material, season/year, broadcast info, episode listings with individual ratings.
- **Pinned to Jikan API v4** (`https://api.jikan.moe/v4/`). Jikan v3 is deprecated and must not be used.
- Free, no API key required. **Rate limit: 3 req/sec, 60 req/min — the strictest individual source limit.**

### 14.5 AniList GraphQL API

- Anime metadata: title (romaji + English + native), AniList score, popularity, trending score, episodes, format, season, studio, cover image URL.
- Free, no API key required. Rate limit: 90 req/min.
- Primary anime poster source and AniList score/popularity data.

### 14.6 TVMaze API

- TV series metadata: name, network, genre, status, premiere date, episode listings with air dates.
- Free, no API key required. Rate limit: 20 req/10 sec (unauthenticated).

### 14.7 Wikipedia Episode Tables

- US network/cable TV viewership figures (scraped). Western Animation and Cartoon episode data where TVMaze is incomplete. Schema validation applied on all parsed tables.

### 14.8 Exchange Rate API

- open.er-api.com or exchangerate.host. Fetched once per session. Cached in session state. Hardcoded approximate fallback rates if unavailable.

### 14.9 Trending Sources

- BOM weekly chart (movie movers). Jikan seasonal/trending endpoint (MAL anime trending). AniList trending query via GraphQL.

### 14.10 Data Matching & Unification

- Title normalisation: lowercased, punctuation stripped, whitespace normalised.
- Fuzzy matching via `rapidfuzz`. Release date proximity matching within ±7 days.
- Manual override mapping table in SQLite for known edge cases.
- Match confidence score stored; uncertain matches flagged with a visual badge.

---

## 15. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Language | Python 3.11+ | Core application language. |
| Web Scraping | requests + BeautifulSoup4 | HTTP and HTML parsing for BOM, Sacnilk, Wikipedia. |
| Tabular Parsing | pandas.read_html | Structured HTML table extraction. |
| Fuzzy Match | rapidfuzz | Title matching across sources. |
| Data Processing | pandas | Cleaning, normalisation, calculations, merging. |
| TV Data | TVMaze REST API | TV series episode and metadata. |
| Anime Data | Jikan API + AniList GraphQL API | MAL and AniList scores, metadata, trending, posters. |
| Movie/TV Media | TMDB API | Posters, genre tags, cast, crew for movies and TV. |
| Exchange Rates | open.er-api.com | Currency conversion rates, once per session. |
| Database | SQLite3 (stdlib) | All persistence: content, cache, watchlist, comparisons, preferences, logs. |
| User Identity | streamlit-local-storage | Browser localStorage for anonymous UUID to enable cross-session preference persistence without user accounts. |
| UI Framework | Streamlit | Interactive dashboard, sidebar, session state, theming. |
| Charts | Plotly (Express + Graph Objects) | All interactive charts. Dark and light templates. |
| PDF | ReportLab | PDF report generation. |
| Chart Export | kaleido | Static PNG export of Plotly charts for PDF embedding. |
| Image Handling | Pillow | Poster image handling for PDF embedding. |
| Deployment | Streamlit Community Cloud | Free-tier hosting via GitHub. |
| Deps | pip + requirements.txt | Package management. |

---

## 16. System Architecture

### 16.1 Data Layer

- **Modules**: `bom_scraper.py`, `sacnilk_scraper.py`, `tmdb_client.py`, `jikan_client.py`, `anilist_client.py`, `tvmaze_client.py`, `wikipedia_tv_scraper.py`, `exchange_rate_client.py`. Each returns a typed pandas DataFrame or dict.
- **RateLimiter**: shared singleton managing independent per-domain token-bucket queues. Each source (Jikan, AniList, TMDB, TVMaze, BOM, Sacnilk, Wikipedia) has its own queue with its own rate limit. Sources are throttled independently — a slow Jikan queue does not block TMDB requests.
- **scrape_cache** SQLite table tracks `(source, entity_key, session_id, scraped_at)` to prevent within-session re-fetching.
- All writes use `INSERT OR REPLACE`. Schema versioning via `db_version` table and `init_db.py` migration runner.

### 16.2 Business Logic Layer

`TitleMatcher`, `FranchiseGrouper`, `AnimeStructurer` (cour/season/arc/episode views, flattened view detection), `PredictorEngine`, `ClashDetector`, `MoverCalculator`, `CurrencyConverter`, `PDFReportBuilder`, `SimilarTitleRecommender`.

### 16.3 Presentation Layer

- `app.py`: entry point, sidebar nav, session state init, page routing.
- `pages/`: `home.py`, `movies.py`, `tv_series.py`, `animated_shows.py`, `compare.py`, `on_this_day.py`, `search.py`, `settings.py`.
- `components/`: `content_card.py`, `stat_bar.py`, `chart_wrapper.py`, `pdf_button.py`, `genre_drawer.py`, `poster.py`, `franchise_tree.py`, `breadcrumb.py`, `anime_view_selector.py`.
- `theme.py`: centralised colour and style constants.

### 16.4 Data Flow

1. Tab or entity load → check `scrape_cache` for session entry.
2. Cache miss → RateLimiter → scraper/client called → data cleaned → upserted to SQLite → cache entry written.
3. Cache hit → read from SQLite only. No network call.
4. User interactions (filter, search, currency change, compare) operate on in-memory DataFrames from SQLite.
5. Poster URLs are resolved from TMDB/AniList/Jikan and passed to the frontend as CDN links. The user's browser fetches images asynchronously — no image bytes transit the Python backend. CSS `onerror` fallback renders a placeholder for broken URLs.
6. PDF export: reads current in-memory state → kaleido renders charts to PNG → ReportLab builds PDF — all locally.
7. All events (scrape, API, poster, PDF, error, user action) written to `app_log` in SQLite.

---

## 17. Database Schema

All tables in `cinestats.db` (SQLite3). Schema versioning via `db_version` table.

### `movies`

| Column | Type & Notes |
|---|---|
| id | INTEGER PRIMARY KEY AUTOINCREMENT |
| title_normalized | TEXT NOT NULL — matching key |
| title_display | TEXT — original casing |
| release_date | DATE |
| origin_country | TEXT — ISO 3166-1 alpha-2 |
| language | TEXT — primary language |
| franchise_id | INTEGER REFERENCES franchises(id) — nullable |
| worldwide_gross_usd | REAL |
| domestic_gross_usd | REAL |
| foreign_gross_usd | REAL |
| india_net_cr | REAL |
| india_gross_cr | REAL |
| opening_weekend_usd | REAL — nullable |
| theater_count | INTEGER — nullable |
| verdict | TEXT |
| days_in_release | INTEGER |
| runtime_mins | INTEGER — nullable |
| tmdb_id | INTEGER — nullable |
| source | TEXT — 'bom', 'sacnilk', or 'merged' |
| match_confidence | REAL — 0.0–1.0 |
| last_updated | TIMESTAMP |

### `franchises`

| Column | Type & Notes |
|---|---|
| id | INTEGER PRIMARY KEY AUTOINCREMENT |
| name | TEXT NOT NULL |
| name_normalized | TEXT |
| parent_franchise_id | INTEGER REFERENCES franchises(id) — null if this IS a parent franchise |
| franchise_type | TEXT — 'series', 'sub_franchise', 'parent_franchise' |
| relationship_tag | TEXT — 'original', 'reboot', 'continuation', 'spin_off', 'parallel_entry', 'remake' |
| cumulative_worldwide_usd | REAL |
| cumulative_india_net_cr | REAL |
| first_release | DATE |
| latest_release | DATE |
| total_entries | INTEGER |
| last_updated | TIMESTAMP |

### `daily_performance`
| Column | Type & Notes |
|---|---|
| id | INTEGER PRIMARY KEY AUTOINCREMENT |
| movie_id | INTEGER REFERENCES movies(id) |
| date | DATE |
| daily_gross_usd | REAL |
| daily_india_net_cr | REAL |
| cumulative_gross_usd | REAL |
| cumulative_india_net | REAL |
| theater_count | INTEGER — nullable |

### `tv_series`
| Column | Type & Notes |
|---|---|
| id | INTEGER PRIMARY KEY AUTOINCREMENT |
| title_normalized | TEXT NOT NULL |
| title_display | TEXT |
| origin_country | TEXT |
| network | TEXT |
| genre | TEXT — comma-separated |
| status | TEXT — 'Ongoing' or 'Ended' |
| premiere_date | DATE |
| total_seasons | INTEGER |
| total_episodes | INTEGER |
| avg_rating | REAL |
| content_type | TEXT — 'tv_series', 'western_animation', 'cartoon' |
| age_rating | TEXT — nullable; for cartoons |
| is_kodomomuke | INTEGER — 0/1 |
| tvmaze_id | INTEGER — nullable |
| tmdb_id | INTEGER — nullable |
| last_updated | TIMESTAMP |

### `tv_episodes`
| Column | Type & Notes |
|---|---|
| id | INTEGER PRIMARY KEY AUTOINCREMENT |
| series_id | INTEGER REFERENCES tv_series(id) |
| season | INTEGER |
| episode | INTEGER |
| title | TEXT |
| air_date | DATE |
| viewership_millions | REAL — nullable |
| rating | REAL — nullable |

### `anime`
| Column | Type & Notes |
|---|---|
| id | INTEGER PRIMARY KEY AUTOINCREMENT |
| title_romaji | TEXT NOT NULL |
| title_english | TEXT |
| title_native | TEXT |
| origin_country | TEXT — default 'JP' |
| demographic | TEXT — 'shounen','shoujo','seinen','josei','kodomomuke','unknown' |
| genre | TEXT — comma-separated |
| source_material | TEXT — 'manga','light_novel','original','visual_novel','other' |
| studio | TEXT |
| status | TEXT |
| mal_score | REAL |
| mal_rank | INTEGER |
| mal_popularity | INTEGER |
| mal_members | INTEGER |
| mal_favourites | INTEGER |
| anilist_score | REAL |
| anilist_popularity | INTEGER |
| anilist_trending | INTEGER |
| total_episodes | INTEGER |
| premiere_season | TEXT — e.g. 'Spring 2021' |
| premiere_year | INTEGER |
| franchise_id | INTEGER REFERENCES franchises(id) — nullable |
| mal_id | INTEGER — nullable |
| anilist_id | INTEGER — nullable |
| last_updated | TIMESTAMP |

### `anime_seasons`
| Column | Type & Notes |
|---|---|
| id | INTEGER PRIMARY KEY AUTOINCREMENT |
| anime_id | INTEGER REFERENCES anime(id) |
| season_number | INTEGER |
| part_number | INTEGER — nullable; for split seasons (Part 1, Part 2, etc.) |
| cour_number | INTEGER — nullable |
| title | TEXT — season/part/cour title if named |
| arc_name | TEXT — story arc name if applicable |
| episode_start | INTEGER |
| episode_end | INTEGER |
| air_start | DATE |
| air_end | DATE |
| is_split_season | INTEGER — 0/1 |
| mal_score | REAL — nullable |
| episode_count | INTEGER |

### `anime_episodes`
| Column | Type & Notes |
|---|---|
| id | INTEGER PRIMARY KEY AUTOINCREMENT |
| anime_id | INTEGER REFERENCES anime(id) |
| season_id | INTEGER REFERENCES anime_seasons(id) — nullable |
| episode_number | INTEGER |
| title | TEXT |
| air_date | DATE |
| rating | REAL — nullable |
| arc_name | TEXT — nullable |

### `saved_comparisons`
| Column | Type & Notes |
|---|---|
| id | INTEGER PRIMARY KEY AUTOINCREMENT |
| name | TEXT NOT NULL — user-editable; auto-generated default |
| comparison_type | TEXT — 'movies','tv','anime','animation','cartoons','cross_category' |
| entity_ids | TEXT — JSON array of entity IDs |
| entity_types | TEXT — JSON array of content type strings |
| created_at | TIMESTAMP |

### `scrape_cache`
| Column | Type & Notes |
|---|---|
| id | INTEGER PRIMARY KEY AUTOINCREMENT |
| source | TEXT |
| entity_key | TEXT |
| session_id | TEXT |
| scraped_at | TIMESTAMP |

### `app_log`
| Column | Type & Notes |
|---|---|
| id | INTEGER PRIMARY KEY AUTOINCREMENT |
| timestamp | TIMESTAMP NOT NULL |
| level | TEXT — 'INFO', 'WARNING', 'ERROR' |
| event_type | TEXT — 'scrape', 'api_call', 'poster_fetch', 'pdf_export', 'user_action', 'error' |
| source | TEXT |
| entity_key | TEXT — nullable |
| message | TEXT |
| success | INTEGER — 0/1 |

### `user_preferences`
| Column | Type & Notes |
|---|---|
| id | INTEGER PRIMARY KEY AUTOINCREMENT |
| user_uuid | TEXT NOT NULL — anonymous UUID from browser localStorage (see Section 3.6) |
| pref_key | TEXT — e.g. 'currency', 'country_c1', 'theme', 'default_content_type' |
| pref_value | TEXT |
| updated_at | TIMESTAMP |

### `watchlist`
| Column | Type & Notes |
|---|---|
| id | INTEGER PRIMARY KEY AUTOINCREMENT |
| user_uuid | TEXT NOT NULL — from browser localStorage |
| entity_id | INTEGER NOT NULL |
| entity_type | TEXT NOT NULL — 'movie', 'tv_series', 'anime', 'western_animation', 'cartoon' |
| added_at | TIMESTAMP NOT NULL |
| milestone_target | REAL — nullable; user-set gross/score milestone to track |
| notes | TEXT — nullable; user notes |

### `db_version`
| Column | Type & Notes |
|---|---|
| id | INTEGER PRIMARY KEY AUTOINCREMENT |
| version | INTEGER NOT NULL — current schema version number |
| applied_at | TIMESTAMP NOT NULL |
| description | TEXT — human-readable migration description |

### `match_overrides`

| Column | Type & Notes |
|---|---|
| id | INTEGER PRIMARY KEY AUTOINCREMENT |
| source_title | TEXT NOT NULL — the title string from the source that needs overriding |
| source | TEXT NOT NULL — 'bom', 'sacnilk', 'jikan', 'anilist', 'tvmaze' |
| target_title_normalized | TEXT NOT NULL — the correct normalized title to map to |
| target_entity_type | TEXT — 'movie', 'tv_series', 'anime', 'western_animation', 'cartoon' |
| notes | TEXT — human-readable reason for the override |
| created_at | TIMESTAMP |

---

## 18. Data Refresh & Caching Policy

| Policy | Detail |
|---|---|
| Session Cache | Each scraped/API-fetched entity cached for the session duration. Same entity not re-fetched within same session. |
| No Spam Refresh | Users cannot manually trigger a refresh of the same view/entity within a session. No refresh button on data views. |
| New Entity = New Fetch | Navigating to any different movie, series, anime, or franchise triggers a fresh fetch if not already in SQLite. |
| Between Sessions | Scrape cache entries (`scrape_cache`) expire on new session start. User preferences persist indefinitely via anonymous cookie UUID (see Section 3.6). |
| SQLite Persistence | Data from prior sessions remains as fallback. If live fetch fails, most recent SQLite data served with "Using cached data from [date]" notice. |
| Cold Start / Seed DB | On startup, if `cinestats.db` does not exist, `init_db.py` copies `seed.db` (a pre-warmed snapshot committed to the repo) as the starting database. This ensures the Home tab is immediately populated with baseline data after a fresh Streamlit Cloud deployment. |
| Data Cutoff Label | "Data current as of [date]" on all data views. Cutoff: if all timezones have passed midnight (UTC vs UTC-12), yesterday is used; otherwise day before yesterday. |
| Exchange Rates | Fetched once per session at startup. Session state only, not persisted to SQLite. |

---

## 19. API Rate Limits

CineStats enforces rate limits in code via a shared `RateLimiter` singleton. Each source has its own independent per-domain token-bucket queue.

| Source | Limit | Enforcement |
|---|---|---|
| Jikan API (MAL) | 3 req/sec, 60 req/min | Hard limit. Per-domain token bucket algorithm. Strictest individual source limit. |
| AniList GraphQL | 90 req/min | Per-domain tracking. Burst allowed up to 90 then throttled. |
| TVMaze API | 20 req/10 sec (unauth) | Per-domain tracking in RateLimiter. |
| TMDB API | ~40 req/10 sec | Per-domain tracking in RateLimiter. |
| BOM / Sacnilk (scraping) | Min 2 sec between requests to same domain | Enforced via sleep() in scraper modules. No concurrent same-domain requests. |
| Wikipedia (scraping) | Min 2 sec between requests | Same as BOM/Sacnilk. |
| Exchange Rate API | 1 call/session | No special throttling needed. |
| Global Policy | Each source has its own independent rate-limit queue | When multiple sources are active simultaneously, each is throttled independently — TMDB requests proceed at TMDB's limit even while Jikan is throttled at 3 req/sec. No global floor is applied across sources. |

---

## 20. Functional Requirements

Formal requirements using SHALL notation. Priority: **M** = Must Have, **S** = Should Have, **C** = Could Have.

| ID | Requirement | Priority |
|---|---|---|
| FR-01 | The system SHALL display a fully populated Home tab on first load without user input. | M |
| FR-02 | The Home tab SHALL show Currently in Theatres with movie poster cards and gross data. | M |
| FR-03 | The Home tab SHALL show Currently Airing split by content type; empty types hidden. | M |
| FR-04 | The Home tab SHALL show Trending This Week from external signals only; categories hidden if no signal. | M |
| FR-05 | The Home tab SHALL show an On This Day preview with a link to the full On This Day tab. | M |
| FR-06 | The Home tab SHALL show Top of Year for each content type with charts and tables; empty types hidden. | M |
| FR-07 | The Home tab SHALL show a What's New section from recent app_log entries. | S |
| FR-08 | The system SHALL provide a jump-to-section anchor nav at the top of the Home tab. | M |
| FR-09 | The system SHALL provide tabs for Movies, TV Series, Animated Shows, Compare, On This Day, Search, and Settings. | M |
| FR-10 | The Movies tab SHALL support browsing with filters including genre drawer, year, origin country, language, verdict. | M |
| FR-11 | The system SHALL support a three-level franchise hierarchy: Series, Sub-Franchise, Parent Franchise. | M |
| FR-12 | Parallel franchise entries SHALL be labelled with relationship tags: Original, Reboot, Continuation, Spin-off, Parallel Entry, Remake. | M |
| FR-13 | The Animated Shows tab SHALL contain sub-sections for Anime, Western Animation, and Cartoons. | M |
| FR-14 | The Anime sub-section SHALL have demographic sub-tabs (Shounen, Shoujo, Seinen, Josei, Kodomomuke). No selection shows all. | M |
| FR-15 | The Anime sub-section SHALL have origin country sub-tabs (Japan, Korea, China, India, Other). Multiple selectable simultaneously. | M |
| FR-16 | Anime detail SHALL offer four structural views: Cour, Season, Story Arc, Episode. Unavailable views SHALL be hidden. | M |
| FR-17 | A Flattened View toggle SHALL appear on anime detail only when split seasons or split cours exist. | M |
| FR-18 | Cartoons SHALL support age rating filters for both US (TV-Y, TV-Y7, TV-G, TV-PG) and India (U, U/A 7+, U/A 13+) rating systems. | M |
| FR-19 | Kodomomuke content SHALL be tagged and appear in both Anime and Cartoons sub-sections. | M |
| FR-20 | The Compare tab SHALL support within-category comparison of up to 10 entities. | M |
| FR-21 | The Compare tab SHALL support opt-in cross-category comparison of TV Series, Anime, Western Animation, and Cartoons. Movies/franchises excluded. | M |
| FR-22 | Cross-category compare SHALL display a prominent amber visual warning about metric comparability. | M |
| FR-23 | Missing metrics in cross-category compare SHALL display as N/A. | M |
| FR-24 | The system SHALL support saving comparisons to SQLite with auto-generated, user-editable names. | M |
| FR-25 | The On This Day tab SHALL function as a full date browser: single date and date range modes. | M |
| FR-26 | Date range mode SHALL include a toggle between "Released in range" and "Airing during range". | M |
| FR-27 | The system SHALL provide unified search across all content types with a content type pre-filter. | M |
| FR-28 | Content type badges in search results SHALL only appear when multiple content types are shown. | M |
| FR-29 | A visible note on the Search page SHALL explain how multi-type search and badges work. | M |
| FR-30 | The system SHALL provide an advanced search panel with year range, country, language, score range, gross range, status, and studio filters. | M |
| FR-31 | Every data view SHALL be PDF-exportable with full sections, embedded charts, and metadata. | M |
| FR-32 | PDF metadata SHALL include: data date range, sources, exchange rate, country lens, N/A explanations, generation timestamp, CineStats version. | M |
| FR-33 | Poster CDN URLs SHALL be resolved for all content types and passed to the browser for async rendering. No image bytes SHALL be downloaded by the Python backend during normal browsing. A CSS `onerror` fallback SHALL display a styled placeholder for broken image URLs. | M |
| FR-34 | All poster URL resolution attempts (source lookup success/failure per entity) SHALL be logged to app_log. | M |
| FR-35 | The currency selector SHALL support USD, INR, EUR, GBP, JPY, AED, AUD, CAD, SGD. | M |
| FR-36 | Worldwide gross SHALL always show USD as primary figure. | M |
| FR-37 | The country lens SHALL support Global + up to 3 additional countries (C1, C2, C3). | M |
| FR-38 | Currency, country lens, and all user preferences SHALL be saved in SQLite keyed by an anonymous browser UUID (see Section 3.6) and restored on subsequent visits. | M |
| FR-39 | The system SHALL NOT re-scrape or re-fetch the same entity within the same session. | M |
| FR-40 | All data views SHALL display "Data current as of [date]". Data is always 1–2 days prior to current date. | M |
| FR-41 | All API rate limits SHALL be enforced in code via independent per-domain token-bucket queues. No global floor SHALL be applied across sources. | M |
| FR-42 | The expandable sections setting SHALL allow per-section threshold and default state config. Saved in SQLite. | M |
| FR-43 | Anime detail SHALL show staff and credits including Japanese and English dub voice cast in expandable sub-sections. | M |
| FR-44 | All detail views SHALL show a Similar Titles section with 4–6 suggestions. | S |
| FR-45 | The system SHALL log all scrape, API, poster, error, PDF export, and user action events to app_log. | M |
| FR-46 | The system SHALL provide a genre filter modal drawer in all tabs that support filtering. | M |
| FR-47 | All list views SHALL support a compact/comfortable table view toggle. | S |
| FR-48 | The system SHALL show a Watchlist feature with milestone display. Stored in SQLite keyed by user UUID. | S |
| FR-49 | The system SHALL generate and persist an anonymous UUID v4 in browser localStorage on first visit, and use it as the identity key for all user-specific SQLite data. | M |
| FR-50 | All paginated list views SHALL track pagination state (current page, page size) in `st.session_state` with Previous/Next navigation and configurable page sizes (12/24/48). | M |
| FR-51 | The system SHALL include a pre-warmed `seed.db` in the repository. On cold start (no `cinestats.db` found), `init_db.py` SHALL copy `seed.db` as the starting database to ensure the Home tab is immediately functional. | M |
| FR-52 | The Home tab SHALL show a Daily / Weekend Movers section displaying the top 5 gainers and top 5 losers among currently running films, with absolute and percentage gross change, refreshed on session load. | S |
| FR-53 | The Movie Detail View SHALL show a Clash Analyzer section when other films share the same release date (±1 day), displaying side-by-side opening performance and verdict outcomes. | S |
| FR-54 | The Movie Detail View SHALL show a Verdict Context section comparing the film's verdict to others in its language, genre, and franchise. | S |
| FR-55 | The system SHALL provide genre and studio aggregate roll-up views with Plotly charts, accessible as sub-views from the Movies tab. | C |
| FR-56 | The system SHALL allow CSV export of any data table via a download button. | C |

---

## 21. Non-Functional Requirements

| ID | Category | Requirement |
|---|---|---|
| NFR-01 | Performance | Home tab SHALL complete initial render from cached SQLite data within 3 seconds on standard broadband. |
| NFR-02 | Performance | Live scrape/API operations SHALL complete within 15 seconds per source. Loading spinner with contextual message shown. |
| NFR-03 | Performance | PDF generation SHALL complete within 15 seconds for any single entity or comparison report. |
| NFR-04 | Reliability | On scrape/API failure, system SHALL fall back to most recent SQLite data with "Using cached data from [date]" notice. App SHALL NOT crash. |
| NFR-05 | Reliability | If exchange rate API unavailable, hardcoded approximate rates SHALL be used with a visible warning. |
| NFR-06 | Reliability | If kaleido fails during PDF export, PDF SHALL be generated without charts with a metadata note. |
| NFR-07 | Usability | All charts SHALL include titles, axis labels, and hover tooltips. |
| NFR-08 | Usability | All monetary figures SHALL clearly state their currency and unit. |
| NFR-09 | Usability | Missing data SHALL display as "N/A" or "Data unavailable". No blank cells or unhandled exceptions shown to users. |
| NFR-10 | Usability | The application SHALL be fully navigable without any onboarding documentation. |
| NFR-11 | Compatibility | Application SHALL render correctly on Chrome, Firefox, and Safari (latest 2 major versions) at 1024px width and above. |
| NFR-12 | Scalability | SQLite SHALL remain performant up to 100,000 content records and 1,000,000 daily performance rows. |
| NFR-13 | Maintainability | Each scraper/client module SHALL be independently replaceable without modifying business logic or UI layers. |
| NFR-14 | Maintainability | All colour and style constants SHALL be centralised in theme.py. |
| NFR-15 | Maintainability | All API rate limits SHALL be defined as constants in rate_limits.py. No hardcoded delay values elsewhere. |
| NFR-16 | Legal | Minimum 2-second delay between consecutive HTTP requests to the same domain SHALL be enforced in all scrapers. |
| NFR-17 | Security | The TMDB API key SHALL be stored in Streamlit secrets only. Never hardcoded or logged. |
| NFR-18 | Resilience | The system SHALL include a pre-warmed `seed.db` in the repository. On cold start, `init_db.py` SHALL copy it as the starting database so the Home tab renders immediately. |
| NFR-19 | Resilience | All poster images SHALL be rendered browser-side from CDN URLs. The Python backend SHALL NOT download image bytes during normal page rendering to avoid blocking the synchronous Streamlit execution model. |
| NFR-20 | Privacy | The anonymous user UUID stored in browser localStorage SHALL be a random UUID v4 with no correlation to any personal data. |

---

## 22. UI/UX Design Specification

### 22.1 Dark Mode (Primary)

| Element | Value |
|---|---|
| Main Canvas | `#0F172A` — deep navy-black |
| Cards / Panels | `#1E293B` with 1px `#334155` border. 8px border-radius. |
| Primary Accent | `#3B82F6` (blue) — CTAs, active nav, links, chart highlights |
| Secondary Accent | `#8B5CF6` (purple) — franchise/series elements |
| Positive | `#10B981` (green) — Blockbuster/Hit verdicts, positive movers |
| Negative | `#EF4444` (red) — Flop/Disaster verdicts, negative movers |
| Anime Accent | `#F59E0B` (amber) — anime score cards and demographic badges |
| Text Primary | `#F1F5F9` |
| Text Secondary | `#94A3B8` |
| Sidebar | `#1E293B` background. Active tab: `#3B82F6` left border + slightly lighter background. |
| Charts | `plotly_dark` template. Consistent colour sequence across all charts. |

### 22.2 Light Mode

| Element | Value |
|---|---|
| Main Canvas | `#F8FAFC` |
| Cards / Panels | `#FFFFFF` with 1px `#E2E8F0` border and soft box shadow |
| Primary Accent | `#2563EB` |
| Section Headers | Subtle gradient: `#EFF6FF` to `#DBEAFE` |
| Text Primary | `#0F172A` |
| Text Secondary | `#64748B` |
| Sidebar | White. Active tab: `#2563EB` left border + `#EFF6FF` background. |
| Charts | Custom light template: white background, `#E2E8F0` grid lines. |

### 22.3 Component Patterns

| Component | Spec |
|---|---|
| Content Cards | Poster (or fallback), title, year, key metric, content type badge (when multi-type), verdict/score badge. Hover: slight border glow. |
| Stat Cards | Large bold metric, label below, thin coloured top border (blue=global, amber=India/anime, green=positive). |
| Verdict Badges | Pill: Blockbuster/All-Time Blockbuster=green, Hit/Super Hit=teal, Average=amber, Flop/Disaster=red. |
| Content Type Badges | Small pill: Movie=blue, TV=indigo, Anime=amber, Western Animation=purple, Cartoon=pink, Franchise=teal. |
| Breadcrumb | Text nav at top of all detail views: e.g. Home > Movies > Spider-Man Franchise > MCU Spider-Man > No Way Home. |
| Loading State | Streamlit spinner with contextual message (e.g. "Fetching anime data from AniList…"). |
| Empty State | Styled card with content-type icon and human-readable message. |
| Error Banner | Red alert banner with message and "Use cached data" fallback button. |
| Cross-Category Warning | Amber banner with warning icon. |
| Data Cutoff Label | Subtle grey label in page header: "Data current as of [date]". |
| Poster Fallback | Grey box, content-type icon centred, "Poster not found". |

### 22.4 Genre Filter Drawer

- Modal drawer sliding in from the right when user clicks the "Genre" filter button. Not embedded in the sidebar.
- Multi-select checkboxes grouped by category (e.g. for anime: Action, Romance, Slice of Life, Isekai, Mecha, Psychological, etc.).
- "Clear All" and "Apply" buttons at the bottom. Applied genres shown as removable chips below the filter row.

### 22.5 Advanced Search

- Collapsible panel below search bar on Search tab.
- Contains: year range slider, origin country multi-select, language multi-select, score/rating range slider, gross range slider (movies), status toggle, network/studio text filter.
- Genre filter via genre drawer button within the panel. All filters combinable. Applied filters shown as removable chips above results.

---

## 23. Scraper & API Contract

### 23.1 Contract Rules

- Each module exposes a single public function: `fetch(entity_key: str) -> pd.DataFrame | dict`.
- Returned DataFrames always contain all defined columns even if values are NaN for missing fields.
- All string fields stripped and normalised. No currency symbols in numeric fields. Monetary fields as Python `float`. Date fields as Python `date` objects.
- On any failure, module raises `FetchException` with a human-readable message. Partial data never returned silently.
- Each module has a `SOURCE_NAME` constant used by RateLimiter and scrape_cache.

### 23.2 Key Output Schemas

| Module | Key Output Fields |
|---|---|
| bom_scraper | title_normalized, title_display, release_date, worldwide_gross_usd, domestic_gross_usd, foreign_gross_usd, opening_weekend_usd, theater_count, days_in_release |
| sacnilk_scraper | title_normalized, title_display, release_date, language, india_net_cr, india_gross_cr, verdict, days_in_release |
| tmdb_client | tmdb_id, title, origin_country, language, genre_ids, poster_url, backdrop_url, runtime_mins, cast, crew |
| jikan_client | mal_id, title_romaji, title_english, title_native, mal_score, mal_rank, mal_popularity, mal_members, mal_favourites, episodes, status, demographic, genres, studio, source, season, year, cover_image_url, episode_list |
| anilist_client | anilist_id, title_romaji, title_english, title_native, anilist_score, anilist_popularity, anilist_trending, episodes, format, season, studio, cover_image_url |
| tvmaze_client | tvmaze_id, name, network, genre, status, premiere_date, episodes (list: air_date, season, episode, title) |
| wikipedia_tv_scraper | series_title, season, episode, air_date, viewership_millions |

---

## 24. Error Handling & Graceful Degradation

| Failure Scenario | User-Visible Behaviour | Technical Handling |
|---|---|---|
| Scrape/API fails | Red alert banner: "Could not fetch fresh data. Showing last available data from [date]." | FetchException caught. Falls back to SQLite. Logged to app_log. |
| No cached data and fetch fails | Empty-state card: "No data available for this title yet. Try again later." | Empty DataFrame returned. Empty state component rendered. |
| Exchange rate API unavailable | Warning label: "Using approximate rates. Live rates unavailable." | Hardcoded fallback rates from constants.py used. |
| Partial data (one source missing) | Data from available source shown. Info badge: "India data unavailable" or "Global data unavailable". Missing fields as N/A. | Partial match object returned. UI renders available fields only. |
| Poster CDN URL broken / unreachable | Styled placeholder: "Poster not found" rendered via CSS `onerror` handler in the browser. | Browser handles the failure natively. No Python backend involvement during browsing. For PDF export, a single server-side download attempt (5s timeout) is made; on failure, placeholder embedded. Failure logged to app_log. |
| PDF chart export (kaleido) fails | PDF generated without charts. Metadata note: "Charts unavailable at time of export." | Exception caught in PDFReportBuilder. Proceeds without chart images. |
| SQLite write contention | Transparent — slight delay. | WAL mode. 3 retries at 200ms backoff before raising internal error. |
| TV/anime data unavailable | Fields as "Data unavailable". Charts requiring missing data hidden with notice. | Zero-length DataFrames handled in all chart components. |
| Rate limit hit | Loading spinner shown. Request queued automatically. | RateLimiter queues excess requests. If wait >30s, FetchException raised and fallback triggered. |

---

## 25. Logging Strategy

| Event Type | Logged Fields |
|---|---|
| Scrape Events | Source, entity_key, success/failure, rows returned, duration_ms, error message if failed. |
| API Call Events | Source, endpoint, entity_key, status_code, success/failure, duration_ms. |
| Poster URL Resolution Events | Source (TMDB/AniList/Jikan), entity_id, success/failure of URL lookup, resolved URL or error message. Browser-side rendering outcomes are not logged server-side. |
| PDF Export Events | Report type, entity name(s), page count, duration_ms, success/failure. |
| Rate Limit Events | Source, timestamp, queue depth at time of throttle. |
| Error Events | Module, error type, stack trace summary, entity_key if applicable. |
| User Action Events | Action type (search, compare_add, save_comparison, tab_navigate), content type, entity_key. No PII. |
| Log Retention | app_log not pruned automatically. `prune_log(days=90)` utility function available but not scheduled. |
| Log Viewer | Accessible from Settings tab. Shows recent errors and warnings for the operator. |

---

## 26. Unit Testing Strategy

### 26.1 Tooling

- **Framework**: `unittest` (Python stdlib).
- **Mocking**: `unittest.mock.patch` and `MagicMock` for HTTP calls, API responses, SQLite writes.
- **Test data**: HTML fixtures in `tests/fixtures/html/` and JSON fixtures in `tests/fixtures/json/`.
- **Run command**: `python -m unittest discover tests/`

### 26.2 Coverage by Module

| Module | Test File | Key Test Cases |
|---|---|---|
| bom_scraper | test_bom_scraper.py | Valid HTML parses correctly; malformed HTML raises FetchException; currency symbols stripped; all columns present; date fields are date objects. |
| sacnilk_scraper | test_sacnilk_scraper.py | India Net and verdict parse correctly; missing verdict handled; title normalised; FetchException on HTTP error. |
| jikan_client | test_jikan_client.py | MAL fields parsed from JSON fixture; demographic tag assigned; rate limit enforced (mock timer); FetchException on 429 response. |
| anilist_client | test_anilist_client.py | GraphQL response parsed; AniList score and popularity extracted; cover image URL returned; FetchException on error response. |
| tvmaze_client | test_tvmaze_client.py | Series metadata parsed; episode list with correct types; series-not-found handled gracefully. |
| tmdb_client | test_tmdb_client.py | Poster URL returned correctly; origin country extracted; API key not logged; FetchException on 401. |
| title_matcher | test_title_matcher.py | Exact match = confidence 1.0; fuzzy match within threshold succeeds; below threshold no match; date mismatch beyond window no match. |
| franchise_grouper | test_franchise_grouper.py | Films grouped correctly; override table overrides auto-grouping; parallel entries get correct relationship_tag; parent franchise aggregates correctly. |
| anime_structurer | test_anime_structurer.py | Split season detected correctly; flattened view combines parts; cour boundaries correct; arc episode ranges correct; unavailable views return empty. |
| predictor_engine | test_predictor_engine.py | Projection within expected range for known inputs; zero opening weekend handled; confidence interval returned. |
| currency_converter | test_currency_converter.py | Correct conversion USD-to-INR; identity when currencies match; fallback rate used when live rate absent; worldwide gross always USD primary. |
| pdf_report_builder | test_pdf_report_builder.py | Output is valid PDF bytes; expected section titles present; handles empty DataFrame; metadata section present; chart-less PDF when kaleido fails. |
| rate_limiter | test_rate_limiter.py | Jikan limit (3/sec) enforced; AniList limit (90/min) enforced; global floor applies when multiple sources active; queue wait timeout triggers FetchException. |
| init_db | test_init_db.py | All expected tables exist post-init; upsert does not duplicate; schema version recorded; WAL mode enabled. |

### 26.3 Coverage Targets

- Scraper/API client parsing functions: **100%** line coverage.
- Business logic (matcher, grouper, structurer, predictor, calculator): **90%** line coverage.
- Database layer (init, upsert, cache, log): **85%** line coverage.
- PDF builder, rate limiter, currency converter: **80%** line coverage.
- Streamlit UI components: excluded from unit testing, verified by manual review.

---

## 27. Build Plan & Milestones

| Phase | Milestone | Deliverables |
|---|---|---|
| 1 | Project Setup | Repo structure, requirements.txt, theme.py, rate_limits.py, constants.py, init_db.py (full schema), test skeleton. |
| 2 | Movie Scrapers | bom_scraper.py, sacnilk_scraper.py, title_matcher.py with full unit tests, HTML fixtures, RateLimiter skeleton. |
| 3 | Media & Metadata APIs | tmdb_client.py, jikan_client.py, anilist_client.py, exchange_rate_client.py. Poster retry logic. Full unit tests with JSON fixtures. |
| 4 | TV & Wikipedia | tvmaze_client.py, wikipedia_tv_scraper.py. Full unit tests. |
| 5 | Business Logic | franchise_grouper.py, anime_structurer.py, predictor_engine.py, clash_detector.py, mover_calculator.py, currency_converter.py, similar_title_recommender.py. Full unit tests. |
| 6 | DB & Logging | init_db.py finalised, upsert helpers, app_log writer, user_preferences CRUD, saved_comparisons CRUD. Full unit tests. |
| 7 | Home Tab | home.py: all sections, jump-to-section nav, dark mode, charts, PDF export button. |
| 8 | Movies Tab | movies.py: list/grid/table, filters, genre drawer. movie_detail.py: all stat cards, charts, regional breakdown, predictor, credits, similar titles, franchise link. Franchise/sub-franchise/parent franchise views. |
| 9 | TV Series Tab | tv_series.py: list, filters. tv_detail.py: season/episode tables, viewership/rating charts, credits, similar titles. |
| 10 | Animated Shows Tab | animated_shows.py: Anime (all 4 views, flattened toggle, demographic + origin sub-tabs, intra-series compare, voice cast credits), Western Animation, Cartoons (age filter, Kodomomuke tag). |
| 11 | On This Day Tab | on_this_day.py: single date + date range mode, released/airing toggle, all content types, categorised cards. |
| 12 | Compare Tab | compare.py: within-category (all types), cross-category (opt-in, warning, shared+specific metrics), saved comparisons CRUD. |
| 13 | Search | search.py: unified search, pre-filter, badges, note, advanced search panel, genre drawer, recent searches, live search fallback. |
| 14 | PDF Export | pdf_report_builder.py: all report types, kaleido charts, metadata section. pdf_button.py component. Unit tests. |
| 15 | Settings & Preferences | settings.py: currency, country lens, default content type, theme toggle, expandable sections config, PDF default, log viewer. All preferences to SQLite. |
| 16 | Light Mode | Implement full light mode colour scheme and Plotly light template across all pages and components. |
| 17 | Polish & Error Handling | Empty states, error banners, loading spinners, poster fallbacks, all graceful degradation flows. Full test suite passing. Manual UI review. |
| 18 | Deployment | Deploy to Streamlit Community Cloud. README with local setup. requirements.txt freeze. TMDB API key in Cloud secrets. |

---

## 28. Configuration & Environment Setup

### 28.1 Repository Structure

```
cinestats/
├── app.py                          # Streamlit entry point
├── requirements.txt                # Pinned dependencies
├── cinestats.db                    # SQLite database (gitignored)
├── seed.db                         # Pre-warmed SQLite snapshot (committed to repo; copied to cinestats.db on cold start)
├── theme.py                        # Centralised colour/style constants
├── rate_limits.py                  # All API rate limit constants
├── constants.py                    # Fallback exchange rates, config values
├── src/
│   ├── scrapers/
│   │   ├── bom_scraper.py
│   │   ├── sacnilk_scraper.py
│   │   └── wikipedia_tv_scraper.py
│   ├── clients/
│   │   ├── tmdb_client.py
│   │   ├── jikan_client.py
│   │   ├── anilist_client.py
│   │   ├── tvmaze_client.py
│   │   └── exchange_rate_client.py
│   ├── logic/
│   │   ├── franchise_grouper.py
│   │   ├── anime_structurer.py
│   │   ├── title_matcher.py
│   │   ├── predictor_engine.py
│   │   ├── clash_detector.py
│   │   ├── mover_calculator.py
│   │   ├── currency_converter.py
│   │   ├── similar_title_recommender.py
│   │   └── pdf_report_builder.py
│   ├── db/
│   │   ├── init_db.py
│   │   ├── upsert_helpers.py
│   │   ├── cache_helpers.py
│   │   ├── log_helpers.py
│   │   └── preference_helpers.py
│   └── rate_limiter.py
├── pages/
│   ├── home.py
│   ├── movies.py
│   ├── tv_series.py
│   ├── animated_shows.py
│   ├── compare.py
│   ├── on_this_day.py
│   ├── search.py
│   └── settings.py
├── components/
│   ├── content_card.py
│   ├── stat_bar.py
│   ├── chart_wrapper.py
│   ├── pdf_button.py
│   ├── genre_drawer.py
│   ├── poster.py
│   ├── franchise_tree.py
│   ├── breadcrumb.py
│   └── anime_view_selector.py
├── tests/
│   ├── fixtures/
│   │   ├── html/                   # HTML fixtures for scraper tests
│   │   └── json/                   # JSON fixtures for API client tests
│   └── [test files mirroring src/]
├── .streamlit/
│   ├── config.toml                 # Streamlit theme and server config
│   └── secrets.toml                # TMDB API key (local dev only, gitignored)
```

### 28.2 Key Dependencies

| Package | Purpose |
|---|---|
| streamlit | UI framework |
| pandas | Data processing |
| requests | HTTP scraping |
| beautifulsoup4 + lxml | HTML parsing |
| rapidfuzz | Fuzzy title matching |
| plotly | Interactive charts |
| kaleido | Plotly PNG export for PDF |
| reportlab | PDF generation |
| Pillow | Poster image handling for PDF embedding |
| streamlit-local-storage | Browser localStorage access for anonymous user UUID persistence (Section 3.6) |

### 28.3 Streamlit Config (`.streamlit/config.toml`)

```toml
[theme]
base = "dark"
primaryColor = "#3B82F6"
backgroundColor = "#0F172A"
secondaryBackgroundColor = "#1E293B"
textColor = "#F1F5F9"
```

### 28.4 Local Development Setup

```bash
# 1. Clone and enter the repo
git clone https://github.com/[user]/cinestats.git && cd cinestats

# 2. Create and activate virtual environment
python -m venv .venv && source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add TMDB API key
echo 'TMDB_API_KEY = "your_key_here"' > .streamlit/secrets.toml

# 5. Initialise the database (copies seed.db → cinestats.db if absent, then runs migrations)
python src/db/init_db.py

# 6. Run the app
streamlit run app.py

# 7. Run unit tests
python -m unittest discover tests/
```

---

## 29. Legal & Ethical Considerations

- **Personal and Educational Use Only.** No commercial redistribution of scraped or API data.
- **Robots.txt Compliance**: All scrapers check and respect `robots.txt` before initiating requests.
- **Rate Limiting**: Minimum 2-second delay between consecutive requests to the same domain. No concurrent same-domain scraping.
- **API Terms of Service**: All APIs used within published free-tier terms. No keys sold or shared.
- **User-Agent Headers**: `CineStats-Bot/1.0 (personal project; non-commercial)` on all scraper requests.
- **No Login Circumvention**: No bypassing of authentication, CAPTCHA, paywalls, or access controls.
- **No PII Collection**: No personally identifiable information collected, stored, or transmitted.
- **No Commercial Redistribution**: Data used solely within CineStats. Not sold, published via API, or shared externally.
- **Monetisation**: Free forever. No advertising. No sponsored content. No data monetisation.
- **TMDB API Key**: In Streamlit secrets only. Never hardcoded, logged, or exposed in the UI.
- **Accessibility**: The application is English-only (no internationalisation framework). Basic keyboard navigability is provided by Streamlit's default components. ARIA labels and screen reader support are deferred to the v3.0+ roadmap (Section 31.3). The application targets sighted desktop users at 1024px+ width.
- **Language**: All UI text, labels, and data are in English. No multi-language support is planned for v1.0.

---

## 29.1 Data Retention Policy

| Policy | Detail |
|---|---|
| Scraped Content | Retained indefinitely in SQLite. No automatic pruning of movie, TV, or anime data tables. |
| App Log | Not pruned automatically. A `prune_log(days=90)` utility function is available in `log_helpers.py` but not scheduled. Operators may run it manually. |
| Scrape Cache | Expires per-session. Old session entries remain in SQLite but are functionally inert. A `prune_cache(days=7)` utility removes stale entries. |
| User Preferences | Retained indefinitely, keyed by `user_uuid`. No automatic cleanup. |
| Saved Comparisons | Retained indefinitely. Users may delete individually or clear all via the Compare tab. |
| Seed DB | `seed.db` is a static snapshot and is never modified at runtime. Updated manually by the developer and re-committed to the repo. |

---

## 30. Known Limitations

| Area | Limitation | Impact |
|---|---|---|
| Anime viewership | Japanese broadcast ratings (Video Research Ltd.) are paywalled. No anime broadcast viewership numbers are publicly accessible. | Anime shows scores and popularity metrics only. No viewership figures. |
| Streaming viewership | Netflix, Prime, Disney+, Crunchyroll do not publish comprehensive viewership data. | Streaming viewership not tracked. Only linear TV viewership (where available via Wikipedia) shown. |
| Indian TV ratings | BARC India TRP/TVR not publicly accessible. | Indian TV series show IMDb rating and episode count only. No viewership figures. |
| UK/international TV ratings | BARB and equivalent bodies do not publish granular per-episode data freely. | International TV viewership available only where Wikipedia episode tables exist. |
| Cartoon/kids viewership | Nielsen children's viewership data for kids channels is paywalled. | Cartoon detail shows IMDb rating and episode count only for most titles. |
| Western Animation viewership | Only shows with Wikipedia episode tables have viewership data. | Viewership available for subset of major US Western Animation titles only. |
| Crunchyroll popularity | No public API or structured popularity data. Scraping would potentially violate ToS. | Crunchyroll popularity not tracked in CineStats. |
| BOM market coverage | BOM does not have comprehensive data for all countries. | Country lens may show N/A for countries where BOM coverage is sparse. |
| India regional TV | BARC regional channel data not available. | No viewership data for regional Indian language TV series. |
| SQLite on Streamlit Cloud | Streamlit Community Cloud does not guarantee persistent disk storage. Database may reset on redeployment. | A pre-warmed `seed.db` is committed to the repo and copied to `cinestats.db` on cold start, ensuring the app is immediately functional after redeployment. User-specific data (saved comparisons, watchlists, preferences) may still be lost. |
| Concurrent users | SQLite WAL mode supports limited concurrency. Not suitable for high-concurrency production deployment. | CineStats is designed for personal/small-group use. |
| Exchange rates | Indicative only, fetched once per session. Not financial-grade. | Currency conversions are for reference only. Native currency figures are always authoritative. |
| Anime franchise grouping | Automated grouping for complex parallel franchises may misgroup some entries. | Manual override table corrects known mismatches. |
| Data cutoff | All data is 1–2 days prior to current date. Current-day figures never shown. | Most recent data always labelled with cutoff date. |

---

## 31. Future Scope & Roadmap

### 31.1 Near-Term (v1.1 – v1.3)

- **TMDB for anime**: supplement AniList/Jikan with TMDB metadata for richer genre tags and additional posters.
- **Automated Daily Data Refresh**: GitHub Actions scheduled job to update SQLite daily.
- **Milestone Banners**: achievement banners when a film crosses a configurable gross threshold.

### 31.2 Medium-Term (v2.0)

- **OTT Tracking**: track when movies move to streaming; display OTT release dates alongside theatrical data.
- **Predictive Analytics**: ML-based gross trajectory prediction.
- **Historical Archive**: year-on-year comparison tools going back 10+ years.
- **Anime Episode Discussion Links**: link to MAL episode discussion pages from episode detail.

### 31.3 Long-Term (v3.0+)

- **User Accounts**: persistent cross-session watchlists and personalised dashboards with authentication.
- **Social Sentiment Correlation**: correlate IMDb/RT/MAL score movements with box office or viewership trends.
- **Mobile-Optimised Layout**: responsive design for mobile screen widths.
- **PostgreSQL Migration**: replace SQLite for production-grade multi-user deployment.
- **Public API**: read-only REST API exposing CineStats aggregated data under a Creative Commons licence.
- **Keyboard Navigation**: tab-through sidebar and enter-to-select for accessibility.

---

## 32. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| BOM or Sacnilk HTML structure changes | High | Scrapers break; no fresh movie data. | Modular scrapers. Output schema validation. HTML fixture unit tests detect structural changes early. SQLite fallback. |
| Jikan API deprecation or breaking change | Medium | Anime MAL data unavailable. | AniList is a full independent fallback for most anime data. Pin Jikan API version. Monitor Jikan changelog. |
| TMDB API key expiry or quota exceeded | Low | No posters; metadata gaps. | Poster fallback renders gracefully. Free tier generous for personal use. Quota monitored via app_log. |
| Wikipedia TV table structure changes | High | Viewership scrape failures. | Schema validation on all parsed tables. FetchException on parse failure. Falls back to N/A. |
| Streamlit Cloud SQLite reset on redeployment | Medium | Loss of saved comparisons and cache. | Pre-warmed `seed.db` committed to repo ensures app starts with baseline data. `init_db.py` detects missing `cinestats.db` and copies from `seed.db` automatically. v2+ migration to PostgreSQL planned. |
| kaleido PDF chart export fails on Cloud | Medium | PDFs missing charts. | PDF generated without charts with metadata note. Pin kaleido version. Unit tested. |
| Rate limit violations leading to IP ban | Low (with mitigations) | Source site blocks CineStats. | Strict RateLimiter in code. Session cache prevents repeat fetches. Conservative scraper delays. |
| Anime franchise auto-grouping errors | Medium | Incorrect franchise associations. | Manual override table for known complex franchises. Uncertain matches flagged with confidence badge. |
| Exchange rate API unavailable | Low | Incorrect currency display. | Hardcoded approximate fallback. Visible warning. No feature blocked. |
| Streamlit Community Cloud cold start | Medium | Slow first session load. | `seed.db` ensures Home tab data is available immediately. No live scraping required for initial render. Loading spinner shown for supplementary data. |
| Scraping from shared Streamlit Cloud IPs | Medium | BOM/Wikipedia bot-detection blocks CineStats IP. | Session cache prevents repeat fetches. Conservative 2s delay enforced. `seed.db` pre-populates baseline data so live scraping is supplementary, not critical-path. v1.1 roadmap includes GitHub Actions for offline scraping. |

---

## 33. Changelog

> This is the initial release document. There are no prior versions.

| Version | Date | Notes |
|---|---|---|
| v1.0 | Initial Release | First complete project requirements and technical specification for CineStats. Covers all modules: Movies, TV Series, Animated Shows (Anime, Western Animation, Cartoons), Compare, On This Day, Search, Settings, and Home tab. Full DB schema, API contracts, rate limit policy, functional and non-functional requirements, unit testing strategy, build plan, and known limitations. |

---

## 34. Glossary

| Term | Definition |
|---|---|
| India Net | Box office collections in India after deducting GST and entertainment tax. The standard industry metric for Indian films. |
| India Gross | Total box office collections in India before tax deductions. |
| Worldwide Gross | Total global box office revenue in USD across all territories. |
| Verdict | Indian film industry shorthand for commercial performance: All-Time Blockbuster, Blockbuster, Super Hit, Hit, Average, Flop, Disaster. |
| Cour | A Japanese broadcasting term for a 13-episode anime block airing over approximately 3 months (one broadcast season). Many anime are split into multiple cours within a production season. |
| Cours | Plural of cour. A two-cour anime runs for approximately 26 episodes over 6 months. |
| Story Arc | A named narrative sequence within an anime series, spanning multiple episodes. May not align with season or cour boundaries (e.g. the Chimera Ant Arc in Hunter x Hunter). |
| Split Season | When an anime season is broadcast in two or more separate parts with a gap between them, often listed as separate MAL entries (e.g. Attack on Titan Final Season Part 1, Part 2, The Final Chapters). |
| Flattened View | CineStats feature that combines all parts of a split season into a single unified entry for easier viewing. |
| Shounen | Anime demographic targeting young male audiences (roughly 12–18). Genre associations: action, adventure, friendship. Examples: Naruto, One Piece, Demon Slayer. |
| Shoujo | Anime demographic targeting young female audiences. Genre associations: romance, drama, magical girl. Examples: Sailor Moon, Fruits Basket. |
| Seinen | Anime demographic targeting adult male audiences (18+). Often more mature themes. Examples: Vinland Saga, Berserk, Ghost in the Shell. |
| Josei | Anime demographic targeting adult female audiences (18+). Examples: Nana, Chihayafuru, Paradise Kiss. |
| Kodomomuke | Anime targeted at young children. Examples: Doraemon, Pokémon, Digimon. In CineStats, Kodomomuke content appears in both the Anime and Cartoons sub-sections. |
| Donghua | Chinese animated series and films (e.g. Fog Hill of Five Elements, The King's Avatar). Tracked under Animated Shows with origin country filter set to China. |
| MAL | MyAnimeList — the largest anime and manga database and community site. MAL Score, Rank, Popularity, Members, and Favourites are key metrics. |
| Jikan API | An unofficial free REST API for MyAnimeList data. Used by CineStats to fetch MAL scores, rankings, and metadata. |
| AniList | A popular anime and manga tracking platform with a public GraphQL API. Provides AniList Score and Popularity metrics independent of MAL. |
| TVMaze | A free TV database API providing series metadata, episode listings, and network information. |
| TMDB | The Movie Database — a community-built movie and TV database with a free API. Used for posters, genre tags, cast, and crew. |
| BOM | Box Office Mojo — the primary global box office data aggregator, owned by IMDb/Amazon. |
| Sacnilk | Leading Indian box office tracking website covering Bollywood and all major regional film industries. |
| Country Lens | CineStats feature allowing users to configure up to 3 countries (alongside Global) whose specific performance data is shown as dedicated columns. |
| Parent Franchise | Top-level brand grouping parallel, rebooted, or spin-off sub-franchises. Example: "Spider-Man Franchise" as parent to MCU Spider-Man, Raimi Spider-Man, and Amazing Spider-Man as sub-franchises. |
| Sub-Franchise | A named branch within a Parent Franchise. Tagged with a relationship label: Original, Reboot, Continuation, Spin-off, Parallel Entry, or Remake. |
| Session Cache | A record in scrape_cache tracking what data has been fetched in the current Streamlit session, preventing the same entity from being re-fetched. |
| WAL Mode | Write-Ahead Logging — SQLite journaling mode that improves concurrent read/write performance. |
| Upsert | Database operation: INSERT if record does not exist, UPDATE if it does. SQLite: `INSERT OR REPLACE`. |
| kaleido | Python library enabling static PNG export of Plotly charts, used to embed charts in CineStats PDF reports. |
| ReportLab | Python library for programmatic PDF generation. |
| rapidfuzz | Python library for fast fuzzy string matching, used in the title matcher. |
| RateLimiter | CineStats internal module enforcing per-source API and scraping rate limits. The strictest applicable limit governs all concurrent operations. |
| FetchException | CineStats internal exception class raised by any scraper or API client on fetch failure. |
| AnimeStructurer | CineStats business logic module that organises raw anime episode data into cour, season, story arc, and episode views, and detects split seasons for the flattened view. |
| Data Cutoff | The date up to which CineStats data is current. Always 1–2 days prior to the current date. |
| BARC | Broadcast Audience Research Council India — measures TV ratings (TRP/TVR) in India. Data not publicly available. |
| Nielsen | US television audience measurement company. Most granular viewership data is paywalled. |
| Clash | Two or more films sharing the same theatrical release date and competing for audience share. CineStats detects clashes via the `ClashDetector` module with a ±1 day tolerance. |
| Holdover | A film's week-on-week retention of audience attendance. High holdover indicates strong word-of-mouth and sustained interest. |
| Domestic (US) | Box office collections specifically within the United States and Canada. |
| FetchException | CineStats internal exception class raised by any scraper or API client on fetch failure. Equivalent to `ScraperException` in earlier drafts. |

---

*End of Document — CineStats v1.0 Project Specification*
