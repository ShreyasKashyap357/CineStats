# CineStats

**Global Movies, TV & Animation Analytics Tracker**

A modern, dark-mode-first web application for tracking box office performance, viewership, and ratings across Movies, TV Series, Anime, Western Animation, and Cartoons. Permanently free with no advertising and no paid tier.

---

## Overview

CineStats is an analytics dashboard that brings together data from multiple sources—Box Office Mojo, TMDB, MAL, AniList, TVMaze, and more—into a unified interface. Whether you're tracking the latest blockbuster's box office run, exploring anime by demographic, comparing TV series viewership, or discovering what released on this day in history, CineStats provides the tools you need.

### Key Features

- **Home Dashboard**: Fully populated on load with currently in theatres, currently airing, trending, top of year, and more
- **Movies**: Browse films with box office data, regional breakdowns, clash analysis, and franchise hierarchies
- **TV Series**: Track shows with season/episode data, viewership charts, and ratings
- **Animated Shows**: Dedicated sections for Anime (with demographic filters), Western Animation, and Cartoons
- **Compare**: Compare up to 10 entities within or across categories with visualizations
- **On This Day**: Browse content released on any date or date range
- **Search**: Unified search across all content types with advanced filters
- **Multi-Currency**: Display in USD, INR, EUR, GBP, JPY, and more with live exchange rates
- **Country Lens**: Highlight performance data for specific countries alongside global figures
- **PDF Export**: Export any view as a complete PDF report with full metadata
- **Dark/Light Mode**: Premium dark mode by default, modern light mode available
- **Free Forever**: No ads, no subscriptions, no paywalls

---

## Quick Start

### For Users (Just Want to Use It)

1. Visit the deployed application (link coming soon)
2. Start exploring—no account required

### For Developers (Run Locally)

#### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher (for the frontend)
- Git

#### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ShreyasKashyap357/CineStats.git
   cd CineStats
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up Streamlit secrets:
   - Create `.streamlit/secrets.toml` in the project root
   - Add your API keys (see [Configuration](#configuration) below)

5. Run the backend:
   ```bash
   streamlit run backend/main.py
   ```

#### Frontend Setup (Optional)

The frontend is a React + TypeScript + Vite application. If you want to run or develop the frontend separately:

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

4. Build for production:
   ```bash
   npm run build
   ```

---

## Configuration

### Required API Keys

Create a `.streamlit/secrets.toml` file in the project root with the following:

```toml
TMDB_API_KEY = "your_tmdb_api_key_here"
```

**How to get a TMDB API key:**
1. Go to [themoviedb.org](https://www.themoviedb.org/)
2. Sign up for a free account
3. Navigate to Settings → API → Create a new API key
4. Select "Developer" as the key type
5. Copy the key into your `secrets.toml`

### Optional Configuration

The application includes a pre-seeded database (`cinestats.db`) for immediate functionality. The database is automatically updated with fresh data from APIs and scrapers as you use the application.

---

## Project Structure

```
CineStats/
├── backend/              # Streamlit backend application
│   ├── api/             # API endpoint handlers
│   ├── database.py      # Database operations
│   ├── main.py          # Main Streamlit app entry point
│   └── orchestrator.py  # Data orchestration and caching
├── frontend/            # React + TypeScript frontend
│   ├── src/
│   │   ├── pages/      # Page components
│   │   ├── components/ # Reusable UI components
│   │   └── App.tsx     # Main app component
│   └── package.json
├── src/                 # Shared Python modules
│   ├── clients/        # API clients (TMDB, MAL, AniList, etc.)
│   ├── scrapers/       # Web scrapers (BOM, Sacnilk, etc.)
│   ├── logic/          # Business logic modules
│   └── db/             # Database helpers
├── tests/               # Unit tests
├── requirements.txt     # Python dependencies
├── cinestats.db        # SQLite database (pre-seeded)
└── README.md           # This file
```

---

## Technology Stack

### Backend
- **Streamlit**: Web application framework
- **Python 3.10+**: Core language
- **SQLite**: Local database
- **Pandas**: Data manipulation
- **Requests**: HTTP client
- **BeautifulSoup4**: Web scraping
- **RapidFuzz**: Fuzzy string matching
- **Plotly**: Interactive charts
- **ReportLab**: PDF generation
- **Kaleido**: Chart export for PDFs

### Frontend
- **React 18**: UI library
- **TypeScript**: Type safety
- **Vite**: Build tool
- **TailwindCSS**: Styling
- **Lucide React**: Icons

### Data Sources
- **TMDB API**: Movies, TV series, posters
- **Box Office Mojo**: Global box office data
- **Sacnilk**: Indian box office data
- **Jikan API**: MyAnimeList data
- **AniList GraphQL**: Anime metadata
- **TVMaze API**: TV series information
- **Wikipedia**: Episode tables
- **open.er-api.com**: Exchange rates

---

## Features in Detail

### Home Tab
The default landing page provides:
- Currently in theatres (movies running now)
- Currently airing (TV and animated shows)
- Daily/weekend movers (biggest gainers and losers)
- Trending this week
- On this day preview
- Top of year by content type
- What's new (recently added content)

### Movies Tab
- Browse and filter movies by year, country, language, genre, verdict
- Detailed movie view with box office charts, regional breakdowns
- Franchise hierarchy (Series → Sub-Franchise → Parent Franchise)
- Clash analysis for films released on the same date
- Opening vs lifetime projections

### TV Series Tab
- Browse TV series with filters
- Season and episode data
- Viewership and rating charts
- Staff and credits

### Animated Shows Tab
Three dedicated sub-sections:

**Anime**
- Demographic filters (Shounen, Shoujo, Seinen, Josei, Kids)
- Origin country filters (Japan, Korea, China, India, Other)
- Multiple structural views (Season, Cour, Story Arc, Episode)
- MAL and AniList scores, popularity, rankings

**Western Animation**
- Adult-targeted animated series
- IMDb ratings and episode counts
- Network and studio information

**Cartoons**
- Children's animated content
- Age rating filters (US TV-Y, TV-Y7, TV-G, TV-PG; Indian U, U/A)
- Kodomomuke (kids anime) tagged content

### Compare Tab
- Compare up to 10 entities
- Within-category comparison (movies with movies, anime with anime)
- Cross-category comparison (TV, Anime, Western Animation, Cartoons)
- Visual comparisons with charts and tables
- Save and load comparisons

### On This Day Tab
- Browse content released on any date
- Date range mode
- Filter by content type
- Export as PDF

### Search
- Unified search across all content types
- Advanced filters (year, country, genre, score, etc.)
- Recent searches
- Content type badges

### Settings
- Currency selector (USD, INR, EUR, GBP, JPY, and more)
- Country lens configuration (highlight specific countries)
- Theme toggle (dark/light mode)
- Expandable sections threshold
- PDF export settings
- Log viewer

---

## Data Policy

- **Data Freshness**: All data is 1-2 days prior to current date. A "Data current as of [date]" label is always shown.
- **Caching**: Session-based caching reduces API calls and improves performance.
- **Rate Limits**: Strict adherence to API rate limits to ensure responsible data access.
- **Privacy**: Anonymous user identity via UUID for preference persistence. No personal data collected.
- **Usage**: Personal and educational use only. No commercial redistribution.

---

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_anime_structurer.py
```

### Adding New Features

1. Backend changes go in `backend/` or `src/`
2. Frontend changes go in `frontend/src/`
3. API clients go in `src/clients/`
4. Scrapers go in `src/scrapers/`
5. Business logic goes in `src/logic/`

### Code Style

- Python: Follow PEP 8
- TypeScript: Follow ESLint configuration
- Commit messages: Use clear, descriptive messages

---

## Deployment

### Streamlit Community Cloud (Recommended)

1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Add secrets in Streamlit Cloud dashboard
4. Deploy

The application uses SQLite with a pre-seeded database for cold-start resilience. The database is automatically updated with fresh data as users interact with the application.

---

## Known Limitations

- **Indian TV Viewership**: BARC TRP/TVR data is not publicly accessible. Viewership for Indian TV series is shown as "Data unavailable" with IMDb ratings as the primary metric.
- **Real-time Data**: Data is 1-2 days old. No same-day or live data is displayed.
- **OTT Viewership**: Streaming platform viewership (Netflix, Disney+, etc.) is not included due to lack of public APIs.
- **Anime Movies**: Anime feature films are tracked in the Movies tab, not Animated Shows.

---

## Future Roadmap

- [ ] User accounts for personalized watchlists and preferences
- [ ] Mobile app (React Native)
- [ ] More data sources and integrations
- [ ] Advanced analytics and ML-based recommendations
- [ ] Social features (share comparisons, comments)
- [ ] API for third-party integrations

---

## Contributing

Contributions are welcome! If you'd like to contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure your code follows the project's style guidelines and includes appropriate tests.

---

## License

This project is for personal and educational use only. No commercial redistribution.

Data sources have their own terms of service:
- TMDB: [Terms of Use](https://www.themoviedb.org/documentation/api/terms-of-use)
- Box Office Mojo: [Terms of Service](https://www.boxofficemojo.com/)
- MyAnimeList: [Terms of Service](https://myanimelist.net/static/terms)
- AniList: [Terms of Service](https://anilist.co/terms)

---

## Acknowledgments

- **TMDB** for movie and TV data
- **Box Office Mojo** for box office figures
- **Sacnilk** for Indian box office data
- **MyAnimeList** and **AniList** for anime data
- **TVMaze** for TV series information
- **Wikipedia** for episode tables
- **Streamlit** for the web framework
- The open-source community for the tools and libraries that make this project possible

---

## Contact

For questions, issues, or suggestions, please open an issue on the GitHub[https://github.com/ShreyasKashyap357/CineStats] repo.

---

**Built with ❤️ for movie, TV, and animation enthusiasts everywhere**
