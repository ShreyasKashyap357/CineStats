import { useState, useEffect } from "react";
import { X, TrendingUp, Globe, MapPin, Calendar, Film, Loader2, RefreshCw, Trash2, Image as ImageIcon, ChevronLeft, ChevronRight, Filter, X as CloseIcon, Download, Star } from "lucide-react";
import GenreDrawer from "../components/GenreDrawer";
import TableToggle from "../components/TableToggle";
import DataCutoffLabel from "../components/DataCutoffLabel";

export default function Movies() {
  const [movies, setMovies] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [perPage, setPerPage] = useState(25);
  const [page, setPage] = useState(0);
  const [selectedMovie, setSelectedMovie] = useState<any>(null);
  const [deleting, setDeleting] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [clashes, setClashes] = useState<any[]>([]);
  const [loadingClashes, setLoadingClashes] = useState(false);
  const [verdictContext, setVerdictContext] = useState<any[]>([]);
  const [loadingVerdictContext, setLoadingVerdictContext] = useState(false);
  const [onThisDay, setOnThisDay] = useState<any[]>([]);
  const [loadingOnThisDay, setLoadingOnThisDay] = useState(false);
  const [similarMovies, setSimilarMovies] = useState<any[]>([]);
  const [loadingSimilar, setLoadingSimilar] = useState(false);
  const [franchiseHierarchy, setFranchiseHierarchy] = useState<any>(null);
  const [loadingFranchise, setLoadingFranchise] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('grid');
  const [genreFilter, setGenreFilter] = useState<string>('');
  const [showGenreDrawer, setShowGenreDrawer] = useState(false);
  const [availableGenres, setAvailableGenres] = useState<string[]>([]);
  const [yearMin, setYearMin] = useState<string>('');
  const [yearMax, setYearMax] = useState<string>('');
  const [originCountry, setOriginCountry] = useState<string>('');
  const [language, setLanguage] = useState<string>('');
  const [verdict, setVerdict] = useState<string>('');
  const [minGross, setMinGross] = useState<string>('');
  const [availableVerdicts, setAvailableVerdicts] = useState<string[]>([]);
  const [availableCountries, setAvailableCountries] = useState<string[]>([]);

  const fetchMovies = async () => {
    try {
      const params = new URLSearchParams({
        limit: perPage.toString(),
        offset: (page * perPage).toString()
      });
      if (genreFilter) params.append('genre', genreFilter);
      if (yearMin) params.append('year_min', yearMin);
      if (yearMax) params.append('year_max', yearMax);
      if (originCountry) params.append('origin_country', originCountry);
      if (language) params.append('language', language);
      if (verdict) params.append('verdict', verdict);
      if (minGross) params.append('min_gross_usd', (parseFloat(minGross) * 1000000).toString());
      
      const res = await fetch(`http://localhost:8000/api/movies/?${params.toString()}`);
      const data = await res.json();
      setMovies(data.items || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchFilterOptions = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/movies/?limit=1000`);
      const data = await res.json();
      const genres = new Set<string>();
      const verdicts = new Set<string>();
      const countries = new Set<string>();
      
      data.items?.forEach((m: any) => {
        if (m.genre) {
          m.genre.split(',').forEach((g: string) => genres.add(g.trim()));
        }
        if (m.verdict) verdicts.add(m.verdict);
        if (m.origin_country) countries.add(m.origin_country);
      });
      
      setAvailableGenres(Array.from(genres).sort());
      setAvailableVerdicts(Array.from(verdicts).sort());
      setAvailableCountries(Array.from(countries).sort());
    } catch (err) {
      console.error(err);
    }
  };

  const clearFilters = () => {
    setGenreFilter('');
    setYearMin('');
    setYearMax('');
    setOriginCountry('');
    setLanguage('');
    setVerdict('');
    setMinGross('');
    setPage(0);
  };

  const fetchClashes = async (movieId: number) => {
    setLoadingClashes(true);
    try {
      const res = await fetch(`http://localhost:8000/api/movies/${movieId}/clashes`);
      const data = await res.json();
      setClashes(data.clashes || []);
    } catch (err) {
      console.error(err);
      setClashes([]);
    }
    setLoadingClashes(false);
  };

  const fetchVerdictContext = async (movieId: number) => {
    setLoadingVerdictContext(true);
    try {
      const res = await fetch(`http://localhost:8000/api/movies/${movieId}/verdict-context`);
      const data = await res.json();
      setVerdictContext(data.similar || []);
    } catch (err) {
      console.error(err);
      setVerdictContext([]);
    }
    setLoadingVerdictContext(false);
  };

  const fetchOnThisDay = async (movieId: number) => {
    setLoadingOnThisDay(true);
    try {
      const res = await fetch(`http://localhost:8000/api/movies/${movieId}/on-this-day`);
      const data = await res.json();
      setOnThisDay(data.same_day || []);
    } catch (err) {
      console.error(err);
      setOnThisDay([]);
    }
    setLoadingOnThisDay(false);
  };

  const fetchSimilar = async (movieId: number) => {
    setLoadingSimilar(true);
    try {
      const res = await fetch(`http://localhost:8000/api/movies/${movieId}/similar`);
      const data = await res.json();
      setSimilarMovies(data.similar || []);
    } catch (err) {
      console.error(err);
      setSimilarMovies([]);
    }
    setLoadingSimilar(false);
  };

  const fetchFranchiseHierarchy = async (movieId: number) => {
    setLoadingFranchise(true);
    try {
      const res = await fetch(`http://localhost:8000/api/movies/${movieId}/franchise-hierarchy`);
      const data = await res.json();
      setFranchiseHierarchy(data);
    } catch (err) {
      console.error(err);
      setFranchiseHierarchy(null);
    }
    setLoadingFranchise(false);
  };

  const hasActiveFilters = genreFilter || yearMin || yearMax || originCountry || language || verdict || minGross;

  useEffect(() => { fetchMovies(); fetchFilterOptions(); }, [page, perPage, genreFilter, yearMin, yearMax, originCountry, language, verdict, minGross]);

  const totalPages = Math.ceil(total / perPage);

  const openMovie = async (movie: any) => {
    try {
      const res = await fetch(`http://localhost:8000/api/movies/${movie.id}`);
      const data = await res.json();
      setSelectedMovie(data);
      fetchClashes(movie.id);
      fetchVerdictContext(movie.id);
      fetchOnThisDay(movie.id);
      fetchSimilar(movie.id);
      fetchFranchiseHierarchy(movie.id);
    } catch (e) {
      console.error(e);
      setSelectedMovie(movie);
    }
  };

  const handleRefresh = async (movieId: number) => {
    setRefreshing(true);
    try {
      const res = await fetch(`http://localhost:8000/api/movies/${movieId}/refresh`, { method: "POST" });
      const data = await res.json();
      if (data.status === "success") {
        // Re-fetch detail
        const res2 = await fetch(`http://localhost:8000/api/movies/${movieId}`);
        setSelectedMovie(await res2.json());
        fetchMovies(); // refresh list too
      }
    } catch (e) { console.error(e); }
    setRefreshing(false);
  };

  const handleDelete = async (movieId: number) => {
    if (!confirm("Are you sure you want to delete this movie from the database?")) return;
    setDeleting(true);
    try {
      const res = await fetch(`http://localhost:8000/api/movies/${movieId}`, { method: "DELETE" });
      if (res.ok) {
        setSelectedMovie(null);
        fetchMovies();
      }
    } catch (e) { console.error(e); }
    setDeleting(false);
  };

  const getVerdictColor = (verdict: string) => {
    const colors: Record<string, string> = {
      'Blockbuster': 'from-emerald-500/20 to-emerald-600/10 border-emerald-500/30 text-emerald-400',
      'Super Hit': 'from-green-500/20 to-green-600/10 border-green-500/30 text-green-400',
      'Hit': 'from-lime-500/20 to-lime-600/10 border-lime-500/30 text-lime-400',
      'Average': 'from-yellow-500/20 to-yellow-600/10 border-yellow-500/30 text-yellow-400',
      'Flop': 'from-red-500/20 to-red-600/10 border-red-500/30 text-red-400',
      'Disaster': 'from-rose-500/20 to-rose-600/10 border-rose-500/30 text-rose-400',
    };
    return colors[verdict] || 'from-slate-500/20 to-slate-600/10 border-slate-500/30 text-slate-400';
  };

  return (
    <div className="max-w-7xl mx-auto pb-12">
      {/* Modern Header with Glassmorphism */}
      <header className="mb-8 flex flex-col md:flex-row md:justify-between md:items-end gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-3 rounded-2xl bg-linear-to-br from-blue-500/20 to-indigo-500/20 border border-blue-500/30 shadow-lg shadow-blue-500/10">
              <Film className="w-8 h-8 text-blue-400" />
            </div>
            <div>
              <h2 className="text-4xl font-black text-slate-900 dark:text-slate-100 tracking-tight">Movie Database</h2>
              <p className="text-slate-500 dark:text-slate-400 text-sm mt-1 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                {total.toLocaleString()} movies tracked
              </p>
              <DataCutoffLabel />
            </div>
          </div>
        </div>
        
        {/* Controls */}
        <div className="flex items-center gap-3 flex-wrap">
          {/* Filter Button */}
          <button 
            onClick={() => setShowGenreDrawer(true)}
            className={`group flex items-center gap-2 px-4 py-2.5 rounded-xl transition-all duration-300 ${hasActiveFilters ? 'bg-linear-to-r from-blue-500 to-indigo-600 text-white shadow-lg shadow-blue-500/25' : 'bg-slate-800/80 text-slate-400 hover:text-slate-200 border border-slate-700/50 hover:border-slate-600'} backdrop-blur-sm`}
          >
            <Filter className="w-4 h-4 group-hover:scale-110 transition-transform" />
            <span className="font-medium">
              {hasActiveFilters ? `Filters (${[genreFilter, yearMin, yearMax, originCountry, language, verdict, minGross].filter(Boolean).length})` : 'Filters'}
            </span>
          </button>
          
          {/* View Mode Toggle */}
          <TableToggle viewMode={viewMode} onViewModeChange={setViewMode} />
          
          {/* Per Page Selector */}
          {total > 50 && (
            <div className="flex items-center gap-2 bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm rounded-xl p-1 border border-slate-200 dark:border-slate-700/50 shadow-sm">
              <span className="text-xs font-medium text-slate-500 px-2">Show</span>
              {[10, 25, 50, 100].map(n => (
                <button 
                  key={n} 
                  onClick={() => { setPerPage(n); setPage(0); }}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-300 ${perPage === n ? 'bg-blue-500 text-white shadow-md' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700/50'}`}
                >
                  {n}
                </button>
              ))}
            </div>
          )}
        </div>
      </header>

      {/* Modern Filter Drawer */}
      {showGenreDrawer && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex justify-end animate-in fade-in duration-300">
          <div className="bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl w-96 h-full p-6 border-l border-slate-200 dark:border-slate-700/50 overflow-y-auto shadow-2xl animate-in slide-in-from-right duration-300">
            {/* Header */}
            <div className="flex justify-between items-center mb-8">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-linear-to-br from-blue-500/20 to-indigo-500/20 border border-blue-500/30">
                  <Filter className="w-5 h-5 text-blue-400" />
                </div>
                <h3 className="text-xl font-black text-slate-900 dark:text-slate-100">Filters</h3>
              </div>
              <button 
                onClick={() => setShowGenreDrawer(false)} 
                className="p-2 rounded-xl bg-slate-200/80 dark:bg-slate-800/80 hover:bg-slate-300/80 dark:hover:bg-slate-700/80 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all duration-300 border border-slate-200 dark:border-slate-700/50 hover:border-slate-400 dark:hover:border-slate-600"
                title="Close filters"
              >
                <CloseIcon className="w-5 h-5" />
              </button>
            </div>
            
            <div className="space-y-6">
              {/* Genre */}
              <div className="group">
                <label className="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-2 flex items-center gap-2">
                  <Film className="w-4 h-4 text-slate-500" /> Genre
                </label>
                <select 
                  title="Select Genre"
                  value={genreFilter}
                  onChange={(e) => setGenreFilter(e.target.value)}
                  className="w-full bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/50 rounded-xl px-4 py-3 text-slate-900 dark:text-slate-200 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 outline-none transition-all duration-300 appearance-none cursor-pointer hover:bg-slate-200 dark:hover:bg-slate-800"
                >
                  <option value="">All Genres</option>
                  {availableGenres.map(genre => (
                    <option key={genre} value={genre}>{genre}</option>
                  ))}
                </select>
              </div>

              {/* Year Range */}
              <div>
                <label className="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-2 flex items-center gap-2">
                  <Calendar className="w-4 h-4 text-slate-500" /> Year Range
                </label>
                <div className="flex gap-3">
                  <input 
                    type="number"
                    placeholder="From"
                    value={yearMin}
                    onChange={(e) => setYearMin(e.target.value)}
                    className="w-1/2 bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/50 rounded-xl px-4 py-3 text-slate-900 dark:text-slate-200 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 outline-none transition-all duration-300 placeholder:text-slate-500 dark:placeholder:text-slate-600"
                  />
                  <input 
                    type="number"
                    placeholder="To"
                    value={yearMax}
                    onChange={(e) => setYearMax(e.target.value)}
                    className="w-1/2 bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/50 rounded-xl px-4 py-3 text-slate-900 dark:text-slate-200 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 outline-none transition-all duration-300 placeholder:text-slate-500 dark:placeholder:text-slate-600"
                  />
                </div>
              </div>

              {/* Origin Country */}
              <div>
                <label className="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-2 flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-slate-500" /> Origin Country
                </label>
                <select 
                  title="Select Origin Country"
                  value={originCountry}
                  onChange={(e) => setOriginCountry(e.target.value)}
                  className="w-full bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/50 rounded-xl px-4 py-3 text-slate-900 dark:text-slate-200 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 outline-none transition-all duration-300 appearance-none cursor-pointer hover:bg-slate-200 dark:hover:bg-slate-800"
                >
                  <option value="">All Countries</option>
                  {availableCountries.map(country => (
                    <option key={country} value={country}>{country}</option>
                  ))}
                </select>
              </div>

              {/* Language */}
              <div>
                <label className="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-2 flex items-center gap-2">
                  <Globe className="w-4 h-4 text-slate-500" /> Language
                </label>
                <input 
                  type="text"
                  placeholder="e.g., English, Hindi"
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/50 rounded-xl px-4 py-3 text-slate-900 dark:text-slate-200 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 outline-none transition-all duration-300 placeholder:text-slate-500 dark:placeholder:text-slate-600"
                />
              </div>

              {/* Verdict */}
              <div>
                <label className="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-2 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-slate-500" /> Verdict
                </label>
                <select 
                  title="Select Verdict"
                  value={verdict}
                  onChange={(e) => setVerdict(e.target.value)}
                  className="w-full bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/50 rounded-xl px-4 py-3 text-slate-900 dark:text-slate-200 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 outline-none transition-all duration-300 appearance-none cursor-pointer hover:bg-slate-200 dark:hover:bg-slate-800"
                >
                  <option value="">All Verdicts</option>
                  {availableVerdicts.map(v => (
                    <option key={v} value={v}>{v}</option>
                  ))}
                </select>
              </div>

              {/* Minimum Gross */}
              <div>
                <label className="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-2 flex items-center gap-2">
                  <Globe className="w-4 h-4 text-slate-500" /> Min WW Gross (Millions USD)
                </label>
                <input 
                  type="number"
                  placeholder="e.g., 100"
                  value={minGross}
                  onChange={(e) => setMinGross(e.target.value)}
                  className="w-full bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/50 rounded-xl px-4 py-3 text-slate-900 dark:text-slate-200 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 outline-none transition-all duration-300 placeholder:text-slate-500 dark:placeholder:text-slate-600"
                />
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 pt-6 border-t border-slate-200 dark:border-slate-700/50">
                <button 
                  onClick={() => { clearFilters(); setPage(0); }}
                  className="flex-1 bg-slate-200 dark:bg-slate-800 hover:bg-slate-300 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 px-4 py-3 rounded-xl transition-all duration-300 font-medium border border-slate-200 dark:border-slate-700/50 hover:border-slate-400 dark:hover:border-slate-600"
                >
                  Clear All
                </button>
                <button 
                  onClick={() => { setPage(0); setShowGenreDrawer(false); }}
                  className="flex-1 bg-linear-to-r from-blue-500 to-indigo-600 hover:from-blue-400 hover:to-indigo-500 text-white px-4 py-3 rounded-xl transition-all duration-300 font-bold shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40"
                >
                  Apply Filters
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {viewMode === 'grid' ? (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-5">
          {movies.map((m: any) => (
            <div 
              key={m.id} 
              onClick={() => openMovie(m)}
              className="group bg-white dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-700/30 shadow-lg shadow-black/10 dark:shadow-black/20 hover:shadow-2xl hover:shadow-blue-500/10 hover:border-blue-500/40 hover:-translate-y-2 hover:scale-[1.02] transition-all duration-500 cursor-pointer flex flex-col"
            >
              {/* Poster Section */}
              <div className="relative aspect-2/3 w-full bg-slate-200 dark:bg-slate-900 overflow-hidden">
                {m.poster_url ? (
                  <img 
                    src={m.poster_url} 
                    alt={m.title_display}
                    className="w-full h-full object-cover object-top group-hover:scale-110 transition-transform duration-700 group-hover:brightness-75" 
                    loading="lazy" 
                  />
                ) : (
                  <div className="w-full h-full flex flex-col items-center justify-center text-slate-500 dark:text-slate-600 gap-3">
                    <div className="w-16 h-16 rounded-2xl bg-slate-300/50 dark:bg-slate-700/50 flex items-center justify-center">
                      <ImageIcon className="w-8 h-8 text-slate-400 dark:text-slate-500" />
                    </div>
                    <span className="text-xs font-medium text-slate-600 dark:text-slate-400">No Poster</span>
                  </div>
                )}
                
                {/* Shimmer overlay on hover */}
                <div className="absolute inset-0 bg-linear-to-tr from-transparent via-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                
                {/* Verdict Badge */}
                {m.verdict && (
                  <div className={`absolute top-3 right-3 bg-linear-to-r ${getVerdictColor(m.verdict)} px-3 py-1.5 rounded-full text-xs font-bold backdrop-blur-sm shadow-lg`}>
                    {m.verdict}
                  </div>
                )}
              </div>
              
              {/* Content Section */}
              <div className="p-4 flex-1 flex flex-col">
                <h3 className="font-bold text-sm leading-tight mb-2 line-clamp-2 text-slate-900 dark:text-slate-100 group-hover:text-blue-500 dark:group-hover:text-blue-400 transition-colors">{m.title_display}</h3>
                <p className="text-xs text-slate-600 dark:text-slate-400 mb-3 flex items-center gap-1.5">
                  <Calendar className="w-3 h-3" />
                  {m.release_date?.split("-")[0]} • {m.origin_country || "Unknown"}
                </p>
                <div className="mt-auto flex justify-between items-center text-xs bg-slate-100 dark:bg-slate-900/50 rounded-xl p-2.5 border border-slate-200 dark:border-slate-700/30">
                  <span className="text-slate-600 dark:text-slate-500 font-medium">WW Gross</span>
                  <span className="font-black text-emerald-600 dark:text-emerald-400">${((m.worldwide_gross_usd || 0)/1000000).toFixed(1)}M</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-200 dark:border-slate-700/50 overflow-hidden shadow-xl shadow-black/10">
          <table className="w-full">
            <thead className="bg-slate-100 dark:bg-slate-900/80 border-b border-slate-200 dark:border-slate-700/50">
              <tr>
                <th className="text-left p-4 text-sm font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">Title</th>
                <th className="text-left p-4 text-sm font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">Release Date</th>
                <th className="text-left p-4 text-sm font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">Country</th>
                <th className="text-left p-4 text-sm font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">Verdict</th>
                <th className="text-right p-4 text-sm font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">WW Gross</th>
                <th className="text-right p-4 text-sm font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider">India Net</th>
              </tr>
            </thead>
            <tbody>
              {movies.map((m: any) => (
                <tr 
                  key={m.id}
                  onClick={() => openMovie(m)}
                  className="border-b border-slate-200 dark:border-slate-700/30 hover:bg-slate-100 dark:hover:bg-slate-700/30 cursor-pointer transition-all duration-300 group"
                >
                  <td className="p-4">
                    <div className="flex items-center gap-4">
                      {m.poster_url ? (
                        <img src={m.poster_url} alt={m.title_display} className="w-12 h-16 object-cover rounded-xl shadow-lg group-hover:scale-105 transition-transform duration-300" />
                      ) : (
                        <div className="w-12 h-16 bg-slate-300/50 dark:bg-slate-700/50 rounded-xl flex items-center justify-center">
                          <ImageIcon className="w-5 h-5 text-slate-400 dark:text-slate-500" />
                        </div>
                      )}
                      <span className="font-bold text-slate-900 dark:text-slate-100 group-hover:text-blue-500 dark:group-hover:text-blue-400 transition-colors">{m.title_display}</span>
                    </div>
                  </td>
                  <td className="p-4 text-sm text-slate-600 dark:text-slate-400">{m.release_date || "N/A"}</td>
                  <td className="p-4 text-sm text-slate-600 dark:text-slate-400">{m.origin_country || "Unknown"}</td>
                  <td className="p-4">
                    {m.verdict ? (
                      <span className={`px-3 py-1.5 bg-linear-to-r ${getVerdictColor(m.verdict)} rounded-full text-xs font-bold border`}>
                        {m.verdict}
                      </span>
                    ) : (
                      <span className="text-slate-500 text-sm">-</span>
                    )}
                  </td>
                  <td className="p-4 text-right text-sm font-bold text-emerald-600 dark:text-emerald-400">
                    ${((m.worldwide_gross_usd || 0)/1000000).toFixed(1)}M
                  </td>
                  <td className="p-4 text-right text-sm font-bold text-orange-500 dark:text-orange-400">
                    {m.india_net_cr ? `₹${m.india_net_cr}Cr` : "-"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modern Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-4 mt-10">
          <button 
            onClick={() => setPage(Math.max(0, page - 1))} 
            disabled={page === 0}
            className="flex items-center gap-2 bg-white dark:bg-slate-800/80 backdrop-blur-sm hover:bg-slate-100 dark:hover:bg-slate-700/80 text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white px-4 py-3 rounded-xl disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-300 border border-slate-200 dark:border-slate-700/50 hover:border-slate-400 dark:hover:border-slate-600"
          >
            <ChevronLeft className="w-5 h-5" />
            <span className="hidden sm:inline font-medium">Previous</span>
          </button>
          
          <div className="flex items-center gap-2 bg-white dark:bg-slate-800/50 backdrop-blur-sm rounded-xl px-6 py-3 border border-slate-200 dark:border-slate-700/30">
            <span className="text-slate-500 dark:text-slate-400 text-sm">Page</span>
            <span className="text-slate-900 dark:text-white font-black text-lg">{page + 1}</span>
            <span className="text-slate-500 dark:text-slate-400 text-sm">of</span>
            <span className="text-slate-900 dark:text-white font-black text-lg">{totalPages}</span>
          </div>
          
          <button 
            onClick={() => setPage(Math.min(totalPages - 1, page + 1))} 
            disabled={page >= totalPages - 1}
            className="flex items-center gap-2 bg-white dark:bg-slate-800/80 backdrop-blur-sm hover:bg-slate-100 dark:hover:bg-slate-700/80 text-slate-700 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white px-4 py-3 rounded-xl disabled:opacity-30 disabled:cursor-not-allowed transition-all duration-300 border border-slate-200 dark:border-slate-700/50 hover:border-slate-400 dark:hover:border-slate-600"
          >
            <span className="hidden sm:inline font-medium">Next</span>
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
      )}

      {/* Modern Detail Modal */}
      {selectedMovie && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex justify-center items-start overflow-y-auto p-4 md:p-10 animate-in fade-in duration-300">
          <div className="bg-white dark:bg-slate-900/95 backdrop-blur-xl w-full max-w-5xl rounded-3xl shadow-2xl shadow-black/50 overflow-hidden relative border border-slate-200 dark:border-slate-700/50 mt-10 mb-10 animate-in zoom-in-95 duration-300">
            {/* Ambient glow effects */}
            <div className="absolute -top-20 -right-20 w-40 h-40 bg-blue-500/20 rounded-full blur-3xl pointer-events-none" />
            <div className="absolute -bottom-20 -left-20 w-40 h-40 bg-indigo-500/20 rounded-full blur-3xl pointer-events-none" />
            
            {/* Close Button */}
            <button 
              onClick={() => setSelectedMovie(null)}
              className="absolute top-4 right-4 p-2.5 bg-slate-200 dark:bg-slate-800/80 hover:bg-slate-300 dark:hover:bg-slate-700/80 backdrop-blur-sm rounded-full text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white z-20 transition-all duration-300 hover:rotate-90 border border-slate-200 dark:border-slate-700/50 hover:border-slate-400 dark:hover:border-slate-500/50 shadow-lg"
              title="Close"
            >
              <X className="w-6 h-6" />
            </button>
            
            <div className="flex flex-col md:flex-row relative z-10">
              {/* Modal Poster */}
              <div className="md:w-2/5 bg-slate-200 dark:bg-slate-800/50 relative overflow-hidden flex items-center justify-center">
                {selectedMovie.poster_url ? (
                  <img 
                    src={selectedMovie.poster_url} 
                    alt={selectedMovie.title_display} 
                    className="w-full h-full object-contain max-h-[500px] md:max-h-[600px]" 
                  />
                ) : (
                  <div className="w-full h-80 md:h-full flex flex-col items-center justify-center text-slate-500 dark:text-slate-600 gap-3">
                    <div className="w-24 h-24 rounded-3xl bg-slate-300/50 dark:bg-slate-700/50 flex items-center justify-center">
                      <ImageIcon className="w-12 h-12 text-slate-400 dark:text-slate-500" />
                    </div>
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-400">No Poster Available</span>
                  </div>
                )}
                {/* Gradient overlay */}
                <div className="absolute inset-0 bg-linear-to-t from-white via-transparent to-transparent md:bg-linear-to-r md:from-transparent md:to-white/20 dark:from-slate-900 dark:to-transparent dark:md:from-transparent dark:md:to-slate-900/20 pointer-events-none" />
              </div>
              
              {/* Modal Data */}
              <div className="md:w-3/5 p-8">
                {/* Title Section */}
                <h2 className="text-4xl md:text-5xl font-black text-white mb-4 leading-tight">{selectedMovie.title_display}</h2>
                
                {/* Meta Tags */}
                <div className="flex flex-wrap gap-3 text-sm mb-6 pb-6 border-b border-slate-700/50">
                  <span className="flex items-center gap-2 bg-slate-800/50 px-3 py-1.5 rounded-lg text-slate-400 border border-slate-700/30">
                    <Calendar className="w-4 h-4 text-slate-500" /> 
                    {selectedMovie.release_date || "Unknown"}
                  </span>
                  <span className="flex items-center gap-2 bg-slate-800/50 px-3 py-1.5 rounded-lg text-slate-400 border border-slate-700/30">
                    <MapPin className="w-4 h-4 text-slate-500" /> 
                    {selectedMovie.origin_country || "Unknown"}
                  </span>
                  {selectedMovie.verdict && (
                    <span className={`bg-linear-to-r ${getVerdictColor(selectedMovie.verdict)} px-3 py-1.5 rounded-lg text-xs font-bold border`}>
                      {selectedMovie.verdict}
                    </span>
                  )}
                </div>

                {/* Director / Studio / Producer */}
                {(selectedMovie.director || selectedMovie.studio || selectedMovie.producer) && (
                  <div className="grid grid-cols-2 gap-4 mb-6 text-sm">
                    {selectedMovie.director && (
                      <div className="bg-slate-800/30 p-3 rounded-xl border border-slate-700/30">
                        <span className="text-slate-500 text-xs uppercase font-bold tracking-wider">Director</span>
                        <p className="text-white font-semibold">{selectedMovie.director}</p>
                      </div>
                    )}
                    {selectedMovie.studio && (
                      <div className="bg-slate-800/30 p-3 rounded-xl border border-slate-700/30">
                        <span className="text-slate-500 text-xs uppercase font-bold tracking-wider">Studio</span>
                        <p className="text-white font-semibold">{selectedMovie.studio}</p>
                      </div>
                    )}
                    {selectedMovie.producer && (
                      <div className="col-span-2 bg-slate-800/30 p-3 rounded-xl border border-slate-700/30">
                        <span className="text-slate-500 text-xs uppercase font-bold tracking-wider">Producer</span>
                        <p className="text-white">{selectedMovie.producer}</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Cast Section */}
                {selectedMovie.cast && selectedMovie.cast.length > 0 && (
                  <div className="mb-6">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-1 h-6 bg-linear-to-b from-pink-500 to-rose-500 rounded-full" />
                      <h3 className="text-xl font-black text-slate-100">Cast</h3>
                      <span className="text-xs text-slate-500 bg-slate-800/50 px-3 py-1 rounded-full border border-slate-700/30">{selectedMovie.cast.length} actors</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {selectedMovie.cast.slice(0, 8).map((actor: string, idx: number) => (
                        <span key={idx} className="bg-slate-800/50 px-3 py-1.5 rounded-lg text-sm text-slate-300 border border-slate-700/30 hover:border-pink-500/30 hover:bg-slate-800/80 transition-all">
                          {actor}
                        </span>
                      ))}
                      {selectedMovie.cast.length > 8 && (
                        <span className="bg-slate-800/30 px-3 py-1.5 rounded-lg text-sm text-slate-500 border border-slate-700/30">
                          +{selectedMovie.cast.length - 8} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
                
                {/* Stats Grid */}
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
                  <div className="bg-linear-to-br from-emerald-500/10 to-emerald-600/5 p-5 rounded-2xl border border-emerald-500/20 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-20 h-20 bg-emerald-500/10 rounded-full blur-2xl group-hover:bg-emerald-500/20 transition-colors" />
                    <p className="text-emerald-400/80 text-xs uppercase font-bold tracking-wider mb-1 flex items-center gap-2">
                      <Globe className="w-4 h-4" /> Worldwide
                    </p>
                    <p className="text-2xl font-black text-emerald-400">${((selectedMovie.worldwide_gross_usd || 0)/1000000).toFixed(2)}M</p>
                  </div>
                  <div className="bg-linear-to-br from-blue-500/10 to-blue-600/5 p-5 rounded-2xl border border-blue-500/20 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-20 h-20 bg-blue-500/10 rounded-full blur-2xl group-hover:bg-blue-500/20 transition-colors" />
                    <p className="text-blue-400/80 text-xs uppercase font-bold tracking-wider mb-1 flex items-center gap-2">
                      <MapPin className="w-4 h-4" /> Domestic
                    </p>
                    <p className="text-2xl font-black text-blue-400">${((selectedMovie.domestic_gross_usd || 0)/1000000).toFixed(2)}M</p>
                  </div>
                  <div className="bg-linear-to-br from-orange-500/10 to-orange-600/5 p-5 rounded-2xl border border-orange-500/20 relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-20 h-20 bg-orange-500/10 rounded-full blur-2xl group-hover:bg-orange-500/20 transition-colors" />
                    <p className="text-orange-400/80 text-xs uppercase font-bold tracking-wider mb-1 flex items-center gap-2">
                      <TrendingUp className="w-4 h-4" /> India Net
                    </p>
                    <p className="text-2xl font-black text-orange-400">₹{selectedMovie.india_net_cr || "0"} Cr</p>
                  </div>
                  {selectedMovie.total_shows_sacnilk && (
                    <div className="bg-linear-to-br from-purple-500/10 to-purple-600/5 p-5 rounded-2xl border border-purple-500/20 relative overflow-hidden group">
                      <div className="absolute top-0 right-0 w-20 h-20 bg-purple-500/10 rounded-full blur-2xl group-hover:bg-purple-500/20 transition-colors" />
                      <p className="text-purple-400/80 text-xs uppercase font-bold tracking-wider mb-1 flex items-center gap-2">
                        <Film className="w-4 h-4" /> Total Shows
                      </p>
                      <p className="text-2xl font-black text-purple-400">{selectedMovie.total_shows_sacnilk.toLocaleString()}</p>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                <div className="flex flex-wrap gap-3 mb-8">
                  <button 
                    onClick={() => handleRefresh(selectedMovie.id)} 
                    disabled={refreshing}
                    className="flex items-center gap-2 bg-linear-to-r from-blue-500 to-indigo-600 hover:from-blue-400 hover:to-indigo-500 text-white px-5 py-3 rounded-xl text-sm font-bold transition-all duration-300 disabled:opacity-50 shadow-lg shadow-blue-500/25 hover:shadow-blue-500/40 hover:-translate-y-0.5"
                  >
                    {refreshing ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
                    Refresh from TMDB
                  </button>
                  <button 
                    onClick={() => handleDelete(selectedMovie.id)} 
                    disabled={deleting}
                    className="flex items-center gap-2 bg-linear-to-r from-red-500/20 to-red-600/20 hover:from-red-500 hover:to-red-600 text-red-400 hover:text-white px-5 py-3 rounded-xl text-sm font-bold transition-all duration-300 border border-red-500/30 disabled:opacity-50 hover:-translate-y-0.5"
                  >
                    {deleting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
                    Delete
                  </button>
                  <button 
                    onClick={() => window.open(`http://localhost:8000/api/movies/${selectedMovie.id}/pdf`, '_blank')}
                    className="flex items-center gap-2 bg-linear-to-r from-emerald-500/20 to-emerald-600/20 hover:from-emerald-500 hover:to-emerald-600 text-emerald-400 hover:text-white px-5 py-3 rounded-xl text-sm font-bold transition-all duration-300 border border-emerald-500/30 hover:-translate-y-0.5"
                  >
                    <Download className="w-4 h-4" />
                    Export PDF
                  </button>
                </div>

                {/* Modern Clash Analyzer */}
                <div className="mb-8">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-1 h-6 bg-linear-to-b from-red-500 to-orange-500 rounded-full" />
                    <h3 className="text-xl font-black text-slate-100">Clash Analyzer</h3>
                  </div>
                  {loadingClashes ? (
                    <div className="flex items-center justify-center h-32 bg-slate-800/30 rounded-2xl border border-slate-700/30">
                      <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                    </div>
                  ) : clashes.length > 0 ? (
                    <div className="space-y-3">
                      {clashes.map((clash: any) => (
                        <div key={clash.id} className="group bg-slate-800/50 backdrop-blur-sm p-4 rounded-2xl border border-slate-700/50 flex items-center justify-between hover:border-slate-600 transition-all duration-300">
                          <div className="flex items-center gap-4">
                            {clash.poster_url ? (
                              <img src={clash.poster_url} alt={clash.title_display} className="w-14 h-20 object-cover rounded-xl shadow-lg group-hover:scale-105 transition-transform duration-300" />
                            ) : (
                              <div className="w-14 h-20 bg-slate-700/50 rounded-xl flex items-center justify-center">
                                <ImageIcon className="w-6 h-6 text-slate-500" />
                              </div>
                            )}
                            <div>
                              <p className="font-bold text-slate-100 group-hover:text-blue-400 transition-colors">{clash.title_display}</p>
                              <p className="text-sm text-slate-400">{clash.release_date}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <span className={`px-3 py-1.5 rounded-full text-xs font-bold ${clash.clash_type === 'direct_clash' ? 'bg-linear-to-r from-red-500/20 to-rose-500/20 text-red-400 border border-red-500/30' : 'bg-linear-to-r from-orange-500/20 to-amber-500/20 text-orange-400 border border-orange-500/30'}`}>
                              {clash.clash_type === 'direct_clash' ? 'Direct Clash' : 'Release Clash'}
                            </span>
                            <p className="text-sm font-bold text-emerald-400 mt-2">${((clash.worldwide_gross_usd || 0)/1000000).toFixed(1)}M</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="bg-slate-800/30 rounded-2xl border border-slate-700/30 p-6 text-center">
                      <p className="text-slate-500 text-sm">No clashing movies found within 14 days.</p>
                    </div>
                  )}
                </div>

                {/* Modern Verdict Context */}
                {selectedMovie.verdict && (
                  <div className="mb-8">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-1 h-6 bg-linear-to-b from-blue-500 to-indigo-500 rounded-full" />
                      <h3 className="text-xl font-black text-slate-100">Verdict Context</h3>
                      <span className="text-xs text-slate-500 bg-slate-800/50 px-3 py-1 rounded-full border border-slate-700/30">{verdictContext.length} movies</span>
                    </div>
                    {loadingVerdictContext ? (
                      <div className="flex items-center justify-center h-32 bg-slate-800/30 rounded-2xl border border-slate-700/30">
                        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                      </div>
                    ) : verdictContext.length > 0 ? (
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        {verdictContext.map((movie: any) => (
                          <div key={movie.id} className="group bg-slate-800/50 backdrop-blur-sm p-3 rounded-2xl border border-slate-700/50 cursor-pointer hover:border-blue-500/40 hover:-translate-y-1 transition-all duration-300" onClick={() => openMovie(movie)}>
                            {movie.poster_url ? (
                              <img src={movie.poster_url} alt={movie.title_display} className="w-full h-32 object-cover rounded-xl mb-3 shadow-lg group-hover:scale-105 transition-transform duration-300" />
                            ) : (
                              <div className="w-full h-32 bg-slate-700/50 rounded-xl mb-3 flex items-center justify-center">
                                <ImageIcon className="w-10 h-10 text-slate-500" />
                              </div>
                            )}
                            <p className="font-bold text-slate-100 text-sm truncate group-hover:text-blue-400 transition-colors">{movie.title_display}</p>
                            <p className="text-xs text-slate-400">{movie.release_date}</p>
                            <p className="text-sm font-bold text-emerald-400 mt-1">${((movie.worldwide_gross_usd || 0)/1000000).toFixed(1)}M</p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="bg-slate-800/30 rounded-2xl border border-slate-700/30 p-6 text-center">
                        <p className="text-slate-500 text-sm">No other movies with verdict "{selectedMovie.verdict}" found.</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Modern On This Day Context */}
                {selectedMovie.release_date && (
                  <div className="mb-8">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-1 h-6 bg-linear-to-b from-amber-500 to-yellow-500 rounded-full" />
                      <h3 className="text-xl font-black text-slate-100">On This Day</h3>
                      <span className="text-xs text-slate-500 bg-slate-800/50 px-3 py-1 rounded-full border border-slate-700/30">{onThisDay.length} releases</span>
                    </div>
                    {loadingOnThisDay ? (
                      <div className="flex items-center justify-center h-32 bg-slate-800/30 rounded-2xl border border-slate-700/30">
                        <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                      </div>
                    ) : onThisDay.length > 0 ? (
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        {onThisDay.map((movie: any) => (
                          <div key={movie.id} className="group bg-slate-800/50 backdrop-blur-sm p-3 rounded-2xl border border-slate-700/50 cursor-pointer hover:border-amber-500/40 hover:-translate-y-1 transition-all duration-300" onClick={() => openMovie(movie)}>
                            {movie.poster_url ? (
                              <img src={movie.poster_url} alt={movie.title_display} className="w-full h-32 object-cover rounded-xl mb-3 shadow-lg group-hover:scale-105 transition-transform duration-300" />
                            ) : (
                              <div className="w-full h-32 bg-slate-700/50 rounded-xl mb-3 flex items-center justify-center">
                                <ImageIcon className="w-10 h-10 text-slate-500" />
                              </div>
                            )}
                            <p className="font-bold text-slate-100 text-sm truncate group-hover:text-amber-400 transition-colors">{movie.title_display}</p>
                            <p className="text-xs text-slate-400">{movie.release_date}</p>
                            <p className="text-sm font-bold text-emerald-400 mt-1">${((movie.worldwide_gross_usd || 0)/1000000).toFixed(1)}M</p>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="bg-slate-800/30 rounded-2xl border border-slate-700/30 p-6 text-center">
                        <p className="text-slate-500 text-sm">No other movies released on this date found.</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Modern Similar Titles */}
                <div className="mb-8">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-1 h-6 bg-linear-to-b from-purple-500 to-pink-500 rounded-full" />
                    <h3 className="text-xl font-black text-slate-100">Similar Titles</h3>
                    <span className="text-xs text-slate-500 bg-slate-800/50 px-3 py-1 rounded-full border border-slate-700/30">From TMDB</span>
                  </div>
                  {loadingSimilar ? (
                    <div className="flex items-center justify-center h-32 bg-slate-800/30 rounded-2xl border border-slate-700/30">
                      <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                    </div>
                  ) : similarMovies.length > 0 ? (
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                      {similarMovies.map((movie: any) => (
                        <div 
                          key={movie.tmdb_id} 
                          onClick={() => window.location.href = `/search?q=${encodeURIComponent(movie.title)}`}
                          className="group bg-slate-800/50 backdrop-blur-sm p-3 rounded-2xl border border-slate-700/50 hover:border-purple-500/40 hover:-translate-y-1 transition-all duration-300 cursor-pointer"
                        >
                          {movie.poster_url_card ? (
                            <img src={movie.poster_url_card} alt={movie.title} className="w-full h-32 object-cover rounded-xl mb-3 shadow-lg group-hover:scale-105 transition-transform duration-300" />
                          ) : (
                            <div className="w-full h-32 bg-slate-700/50 rounded-xl mb-3 flex items-center justify-center">
                              <ImageIcon className="w-10 h-10 text-slate-500" />
                            </div>
                          )}
                          <p className="font-bold text-slate-100 text-sm truncate group-hover:text-purple-400 transition-colors">{movie.title}</p>
                          <p className="text-xs text-slate-400">{movie.release_date || "TBA"}</p>
                          {movie.vote_average && (
                            <p className="text-sm text-amber-400 mt-1 flex items-center gap-1">
                              <Star className="w-3 h-3 fill-current" /> {movie.vote_average.toFixed(1)}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="bg-slate-800/30 rounded-2xl border border-slate-700/30 p-6 text-center">
                      <p className="text-slate-500 text-sm">No similar titles found from TMDB.</p>
                    </div>
                  )}
                </div>

                {/* Modern Franchise Hierarchy */}
                {loadingFranchise ? (
                  <div className="mb-8">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-1 h-6 bg-linear-to-b from-cyan-500 to-teal-500 rounded-full" />
                      <h3 className="text-xl font-black text-slate-100">Franchise Hierarchy</h3>
                    </div>
                    <div className="flex items-center justify-center h-32 bg-slate-800/30 rounded-2xl border border-slate-700/30">
                      <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                    </div>
                  </div>
                ) : franchiseHierarchy && (franchiseHierarchy.parent_franchise || franchiseHierarchy.sub_franchises.length > 0 || franchiseHierarchy.current_franchises.length > 0) ? (
                  <div className="mb-8">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-1 h-6 bg-linear-to-b from-cyan-500 to-teal-500 rounded-full" />
                      <h3 className="text-xl font-black text-slate-100">Franchise Hierarchy</h3>
                    </div>
                    
                    {franchiseHierarchy.parent_franchise && franchiseHierarchy.parent_franchise.length > 0 && (
                      <div className="mb-4">
                        <h4 className="text-sm font-bold text-slate-400 mb-3 uppercase tracking-wider">Parent Franchise</h4>
                        <div className="space-y-2">
                          {franchiseHierarchy.parent_franchise.map((f: any) => (
                            <div key={f.id} className="bg-linear-to-r from-purple-500/10 to-purple-600/5 p-4 rounded-xl border border-purple-500/20">
                              <p className="font-bold text-white">{f.name}</p>
                              <p className="text-xs text-purple-400/80">{f.franchise_type}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {franchiseHierarchy.current_franchises && franchiseHierarchy.current_franchises.length > 0 && (
                      <div className="mb-4">
                        <h4 className="text-sm font-bold text-slate-400 mb-3 uppercase tracking-wider">Current Franchise(s)</h4>
                        <div className="space-y-2">
                          {franchiseHierarchy.current_franchises.map((f: any) => (
                            <div key={f.id} className="bg-linear-to-r from-blue-500/10 to-blue-600/5 p-4 rounded-xl border border-blue-500/20">
                              <p className="font-bold text-white">{f.name}</p>
                              <p className="text-xs text-blue-400/80">{f.franchise_type}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {franchiseHierarchy.sub_franchises && franchiseHierarchy.sub_franchises.length > 0 && (
                      <div className="mb-4">
                        <h4 className="text-sm font-bold text-slate-400 mb-3 uppercase tracking-wider">Sub-Franchises</h4>
                        <div className="space-y-2">
                          {franchiseHierarchy.sub_franchises.map((f: any) => (
                            <div key={f.id} className="bg-linear-to-r from-emerald-500/10 to-emerald-600/5 p-4 rounded-xl border border-emerald-500/20">
                              <p className="font-bold text-white">{f.name}</p>
                              <p className="text-xs text-emerald-400/80">{f.franchise_type}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : null}
                
                {/* Modern Regional Rollout Table */}
                {selectedMovie.rollouts && selectedMovie.rollouts.length > 0 && (
                  <div>
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-1 h-6 bg-linear-to-b from-pink-500 to-rose-500 rounded-full" />
                      <h3 className="text-xl font-black text-slate-100">Regional Rollouts</h3>
                      <span className="text-xs text-slate-500 bg-slate-800/50 px-3 py-1 rounded-full border border-slate-700/30">{selectedMovie.rollouts.length} markets</span>
                    </div>
                    <div className="max-h-96 overflow-y-auto pr-2 custom-scrollbar bg-slate-800/30 rounded-2xl border border-slate-700/30">
                      <table className="w-full text-left text-sm text-slate-300">
                        <thead className="bg-slate-900/80 text-slate-400 sticky top-0 z-10">
                          <tr>
                            <th className="p-4 rounded-tl-2xl font-bold uppercase tracking-wider text-xs">Market</th>
                            <th className="p-4 font-bold uppercase tracking-wider text-xs">Opening</th>
                            <th className="p-4 rounded-tr-2xl font-bold uppercase tracking-wider text-xs">Gross</th>
                          </tr>
                        </thead>
                        <tbody>
                          {selectedMovie.rollouts.map((r: any, idx: number) => (
                            <CountryRolloutRow key={idx} rollout={r} />
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function CountryRolloutRow({ rollout }: { rollout: any }) {
  const [expanded, setExpanded] = useState(false);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any[]>([]);

  const toggleExpand = async () => {
    if (!rollout.source_url) return;
    
    if (!expanded && data.length === 0) {
      setLoading(true);
      try {
        const res = await fetch(`http://localhost:8000/api/movies/country-rollout?url=${encodeURIComponent(rollout.source_url)}`);
        const json = await res.json();
        setData(json);
      } catch (e) {
        console.error(e);
      }
      setLoading(false);
    }
    setExpanded(!expanded);
  };

  return (
    <>
      <tr 
        onClick={toggleExpand} 
        className={`border-b border-slate-700/30 hover:bg-slate-700/30 transition-all duration-300 ${rollout.source_url ? 'cursor-pointer group' : ''}`}
      >
        <td className="p-4 font-bold text-slate-100 flex items-center gap-3">
          <MapPin className="w-4 h-4 text-slate-500 group-hover:text-blue-400 transition-colors" />
          {rollout.country_name}
          {rollout.source_url && (
            <span className={`text-xs px-2 py-1 rounded-full transition-all duration-300 ${expanded ? 'bg-slate-700 text-slate-300' : 'bg-blue-500/20 text-blue-400 group-hover:bg-blue-500 group-hover:text-white'}`}>
              {expanded ? 'Hide' : 'Drops'}
            </span>
          )}
        </td>
        <td className="p-4 text-slate-400">${rollout.opening_usd?.toLocaleString() || "-"}</td>
        <td className="p-4 text-emerald-400 font-bold">${rollout.gross_usd?.toLocaleString() || "-"}</td>
      </tr>
      
      {expanded && (
        <tr>
          <td colSpan={3} className="p-0 border-b border-slate-700/30">
            <div className="bg-slate-800/80 backdrop-blur-sm p-4 border-l-4 border-blue-500">
              {loading ? (
                <div className="flex items-center gap-2 text-sm text-blue-400 animate-pulse">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Fetching localized Box Office...
                </div>
              ) : data.length > 0 ? (
                <div className="max-h-48 overflow-y-auto custom-scrollbar">
                  <table className="w-full text-xs">
                    <thead className="text-slate-500 sticky top-0 bg-slate-800">
                      <tr><th className="py-2 text-left font-bold uppercase tracking-wider">Date</th><th className="py-2 text-right font-bold uppercase tracking-wider">Gross</th></tr>
                    </thead>
                    <tbody>
                      {data.map((d, i) => (
                        <tr key={i} className="border-b border-slate-700/20">
                          <td className="py-2 text-slate-300">{d.date}</td>
                          <td className="py-2 text-right text-slate-100 font-mono font-medium">{d.gross}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-sm text-gray-500">No detailed data available.</div>
              )}
            </div>
          </td>
        </tr>
      )}
    </>
  );
}
