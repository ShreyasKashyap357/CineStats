import { useState, useEffect } from "react";
import { Tv, Search, Loader2, X, Plus, Play, Calendar, Star, Trash2, Image as ImageIcon, ChevronLeft, ChevronRight, RefreshCw, Filter, X as CloseIcon, Download } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from "recharts";
import TableToggle from "../components/TableToggle";
import DataCutoffLabel from "../components/DataCutoffLabel";

export default function TVSeries() {
  const [series, setSeries] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [perPage, setPerPage] = useState(25);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [scraping, setScraping] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('grid');
  const [showFilterDrawer, setShowFilterDrawer] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [originCountry, setOriginCountry] = useState<string>('');
  const [network, setNetwork] = useState<string>('');
  const [yearMin, setYearMin] = useState<string>('');
  const [yearMax, setYearMax] = useState<string>('');
  const [genre, setGenre] = useState<string>('');
  const [availableStatuses, setAvailableStatuses] = useState<string[]>([]);
  const [availableNetworks, setAvailableNetworks] = useState<string[]>([]);
  const [availableGenres, setAvailableGenres] = useState<string[]>([]);
  const [availableCountries, setAvailableCountries] = useState<string[]>([]);
  const [expandedSeasons, setExpandedSeasons] = useState<Set<number>>(new Set());
  
  const [selectedSeries, setSelectedSeries] = useState<any>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [similarSeries, setSimilarSeries] = useState<any[]>([]);
  const [loadingSimilar, setLoadingSimilar] = useState(false);
  const [showSearchModal, setShowSearchModal] = useState(false);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);

  const fetchSeries = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        limit: perPage.toString(),
        offset: (page * perPage).toString()
      });
      if (statusFilter) params.append('status', statusFilter);
      if (originCountry) params.append('origin_country', originCountry);
      if (network) params.append('network', network);
      if (yearMin) params.append('year_min', yearMin);
      if (yearMax) params.append('year_max', yearMax);
      if (genre) params.append('genre', genre);
      
      const res = await fetch(`http://localhost:8000/api/tv/?${params.toString()}`);
      const data = await res.json();
      setSeries(data.items || []);
      setTotal(data.total || 0);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  const fetchFilterOptions = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/tv/?limit=1000`);
      const data = await res.json();
      const statuses = new Set<string>();
      const networks = new Set<string>();
      const genres = new Set<string>();
      const countries = new Set<string>();
      
      data.items?.forEach((s: any) => {
        if (s.status) statuses.add(s.status);
        if (s.network) networks.add(s.network);
        if (s.genre) s.genre.split(',').forEach((g: string) => genres.add(g.trim()));
        if (s.origin_country) countries.add(s.origin_country);
      });
      
      setAvailableStatuses(Array.from(statuses).sort());
      setAvailableNetworks(Array.from(networks).sort());
      setAvailableGenres(Array.from(genres).sort());
      setAvailableCountries(Array.from(countries).sort());
    } catch (e) { console.error(e); }
  };

  const clearFilters = () => {
    setStatusFilter('');
    setOriginCountry('');
    setNetwork('');
    setYearMin('');
    setYearMax('');
    setGenre('');
    setPage(0);
  };

  const hasActiveFilters = statusFilter || originCountry || network || yearMin || yearMax || genre;

  useEffect(() => { fetchSeries(); fetchFilterOptions(); }, [page, perPage, statusFilter, originCountry, network, yearMin, yearMax, genre]);
  const totalPages = Math.ceil(total / perPage);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery) return;
    
    setSearchLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/tv/search?query=${encodeURIComponent(searchQuery)}`);
      const data = await res.json();
      setSearchResults(data.results || []);
    } catch (e) { 
      console.error(e);
      setSearchResults([]);
    }
    setSearchLoading(false);
  };

  const handleAddSeries = async (seriesId: number) => {
    setScraping(true);
    try {
      const res = await fetch(`http://localhost:8000/api/tv/scrape?id=${seriesId}`, { method: "POST" });
      if (res.ok) {
        setShowSearchModal(false);
        setSearchResults([]);
        setSearchQuery("");
        setTimeout(fetchSeries, 3000);
      }
    } catch (e) { console.error(e); }
    setScraping(false);
  };

  const loadDetail = async (id: number) => {
    setDetailLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/tv/${id}`);
      const data = await res.json();
      
      const chartData = data.episodes.map((ep: any) => ({
        name: `S${ep.season}E${ep.episode}`,
        viewers: ep.viewership_millions,
        title: ep.title,
        rating: ep.rating
      })).filter((ep: any) => ep.viewers != null);
      
      data.chartData = chartData;
      setSelectedSeries(data);
      fetchSimilar(id);
    } catch (e) { console.error(e); }
    setDetailLoading(false);
  };

  const fetchSimilar = async (id: number) => {
    setLoadingSimilar(true);
    try {
      const res = await fetch(`http://localhost:8000/api/tv/${id}/similar`);
      const data = await res.json();
      setSimilarSeries(data.similar || []);
    } catch (err) {
      console.error(err);
      setSimilarSeries([]);
    }
    setLoadingSimilar(false);
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this TV series from the database?")) return;
    setDeleting(true);
    try {
      const res = await fetch(`http://localhost:8000/api/tv/${id}`, { method: "DELETE" });
      if (res.ok) {
        setSelectedSeries(null);
        fetchSeries();
      }
    } catch (e) { console.error(e); }
    setDeleting(false);
  };

  const handleRefresh = async (id: number) => {
    setRefreshing(true);
    try {
      const res = await fetch(`http://localhost:8000/api/tv/${id}/refresh`, { method: "POST" });
      if (res.ok) {
        loadDetail(id);
      }
    } catch (e) { console.error(e); }
    setRefreshing(false);
  };

  return (
    <div className="max-w-7xl mx-auto pb-12">
      {/* Modern Header */}
      <header className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-3 rounded-2xl bg-linear-to-br from-purple-100 to-pink-100 dark:from-purple-500/20 dark:to-pink-500/20 border border-purple-200 dark:border-purple-500/30 shadow-lg shadow-purple-500/10">
            <Tv className="w-8 h-8 text-purple-600 dark:text-purple-400" />
          </div>
          <div>
            <h2 className="text-4xl font-black text-slate-900 dark:text-slate-100 tracking-tight">TV Series Database</h2>
            <div className="flex items-center gap-3 mt-1">
              <span className="text-slate-600 dark:text-slate-400 text-sm flex items-center gap-2">
                {total.toLocaleString()} series tracked via TVMaze + Wikipedia
                <span className="inline-flex h-2 w-2 rounded-full bg-purple-500 animate-pulse" />
              </span>
            </div>
            <DataCutoffLabel />
          </div>
        </div>
      </header>

      {/* Modern Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-3">
          {/* Filter Toggle */}
          <button 
            onClick={() => setShowFilterDrawer(true)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl transition-all duration-300 ${hasActiveFilters ? 'bg-linear-to-r from-purple-600 to-pink-600 text-white shadow-lg shadow-purple-500/25' : 'bg-slate-100 dark:bg-slate-800/50 text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-100 border border-slate-200 dark:border-slate-700/50 hover:border-slate-400 dark:hover:border-slate-600'}`}
          >
            <Filter className="w-4 h-4" />
            <span className="font-semibold">{hasActiveFilters ? `Filters (${[statusFilter, originCountry, network, yearMin, yearMax, genre].filter(Boolean).length})` : 'Filters'}</span>
          </button>

          {/* View Mode Toggle */}
          <TableToggle viewMode={viewMode} onViewModeChange={setViewMode} />

          {/* Per Page Selector */}
          {total > 50 && (
            <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800/50 rounded-xl px-3 py-1.5 border border-slate-200 dark:border-slate-700/50">
              <span className="text-slate-500 text-xs font-medium uppercase tracking-wider">Per page</span>
              {[10, 15, 25, 50, 100].map(n => (
                <button key={n} onClick={() => { setPerPage(n); setPage(0); }}
                  className={`px-2.5 py-1 rounded-lg text-sm font-bold transition-all duration-300 ${perPage === n ? 'bg-purple-600 text-white shadow-md' : 'text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700/50'}`}>
                  {n}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Search & Add Button */}
        <button
          onClick={() => setShowSearchModal(true)}
          className="bg-linear-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white px-5 py-2.5 rounded-xl text-sm font-bold flex items-center gap-2 transition-all duration-300 shadow-lg shadow-purple-500/20 hover:shadow-purple-500/40 hover:-translate-y-0.5"
        >
          <Search className="w-4 h-4" />
          Search & Add Show
        </button>
      </div>

      {/* Modern Filter Drawer */}
      {showFilterDrawer && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex justify-end animate-slide-in-right">
          <div className="bg-slate-900/95 backdrop-blur-xl w-96 h-full p-6 border-l border-slate-700/50 overflow-y-auto shadow-2xl">
            <div className="flex justify-between items-center mb-8">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-purple-500/20 border border-purple-500/30">
                  <Filter className="w-5 h-5 text-purple-400" />
                </div>
                <h3 className="text-xl font-black text-slate-100">Advanced Filters</h3>
              </div>
              <button onClick={() => setShowFilterDrawer(false)} className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-all" aria-label="Close filters">
                <CloseIcon className="w-6 h-6" />
              </button>
            </div>
            
            <div className="space-y-6">
              {/* Status */}
              <div>
                <label className="flex items-center gap-2 text-sm font-bold text-slate-300 mb-2 uppercase tracking-wider">
                  <Play className="w-4 h-4 text-slate-500" /> Status
                </label>
                <select 
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="w-full bg-slate-800/50 border border-slate-700/50 rounded-xl px-4 py-3 text-slate-200 focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 outline-none transition-all"
                  title="Status Filter"
                >
                  <option value="">All Statuses</option>
                  {availableStatuses.map(status => (
                    <option key={status} value={status}>{status}</option>
                  ))}
                </select>
              </div>

              {/* Origin Country */}
              <div>
                <label className="flex items-center gap-2 text-sm font-bold text-slate-300 mb-2 uppercase tracking-wider">
                  <span className="text-slate-500">🌍</span> Origin Country
                </label>
                <select 
                  value={originCountry}
                  onChange={(e) => setOriginCountry(e.target.value)}
                  className="w-full bg-slate-800/50 border border-slate-700/50 rounded-xl px-4 py-3 text-slate-200 focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 outline-none transition-all"
                  title="Country Filter"
                >
                  <option value="">All Countries</option>
                  {availableCountries.map(country => (
                    <option key={country} value={country}>{country}</option>
                  ))}
                </select>
              </div>

              {/* Network */}
              <div>
                <label className="flex items-center gap-2 text-sm font-bold text-slate-300 mb-2 uppercase tracking-wider">
                  <span className="text-slate-500">📡</span> Network
                </label>
                <select 
                  value={network}
                  onChange={(e) => setNetwork(e.target.value)}
                  className="w-full bg-slate-800/50 border border-slate-700/50 rounded-xl px-4 py-3 text-slate-200 focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 outline-none transition-all"
                  title="Network Filter"
                >
                  <option value="">All Networks</option>
                  {availableNetworks.map(net => (
                    <option key={net} value={net}>{net}</option>
                  ))}
                </select>
              </div>

              {/* Year Range */}
              <div>
                <label className="flex items-center gap-2 text-sm font-bold text-slate-300 mb-2 uppercase tracking-wider">
                  <Calendar className="w-4 h-4 text-slate-500" /> Year Range
                </label>
                <div className="flex gap-3">
                  <input 
                    type="number"
                    placeholder="From"
                    value={yearMin}
                    onChange={(e) => setYearMin(e.target.value)}
                    className="w-1/2 bg-slate-800/50 border border-slate-700/50 rounded-xl px-4 py-3 text-slate-200 focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 outline-none transition-all placeholder:text-slate-600"
                  />
                  <input 
                    type="number"
                    placeholder="To"
                    value={yearMax}
                    onChange={(e) => setYearMax(e.target.value)}
                    className="w-1/2 bg-slate-800/50 border border-slate-700/50 rounded-xl px-4 py-3 text-slate-200 focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 outline-none transition-all placeholder:text-slate-600"
                  />
                </div>
              </div>

              {/* Genre */}
              <div>
                <label className="flex items-center gap-2 text-sm font-bold text-slate-300 mb-2 uppercase tracking-wider">
                  <Star className="w-4 h-4 text-slate-500" /> Genre
                </label>
                <select 
                  value={genre}
                  onChange={(e) => setGenre(e.target.value)}
                  className="w-full bg-slate-800/50 border border-slate-700/50 rounded-xl px-4 py-3 text-slate-200 focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 outline-none transition-all"
                  title="Genre Filter"
                >
                  <option value="">All Genres</option>
                  {availableGenres.map(g => (
                    <option key={g} value={g}>{g}</option>
                  ))}
                </select>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 pt-6 border-t border-slate-700/50">
                <button 
                  onClick={() => { clearFilters(); setPage(0); }}
                  className="flex-1 bg-slate-800/50 hover:bg-slate-700/50 text-slate-300 px-4 py-3 rounded-xl font-bold transition-all border border-slate-700/50"
                >
                  Clear All
                </button>
                <button 
                  onClick={() => { setPage(0); setShowFilterDrawer(false); }}
                  className="flex-1 bg-linear-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white px-4 py-3 rounded-xl font-bold transition-all shadow-lg shadow-purple-500/20 hover:shadow-purple-500/40 hover:-translate-y-0.5"
                >
                  Apply Filters
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="h-64 flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="w-10 h-10 animate-spin text-purple-500" />
            <p className="text-slate-500 animate-pulse">Loading series...</p>
          </div>
        </div>
      ) : (
        <>
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-5">
              {series.map(s => (
                <div 
                  key={s.id} 
                  onClick={() => loadDetail(s.id)}
                  className="group bg-slate-800/50 backdrop-blur-sm rounded-2xl overflow-hidden border border-slate-700/50 shadow-lg hover:shadow-2xl hover:border-purple-500/40 transition-all duration-300 cursor-pointer hover:-translate-y-2 flex flex-col"
                >
                  <div className="relative aspect-2/3 w-full bg-slate-900/80 overflow-hidden">
                    {s.poster_url || s.poster || s.poster_path || s.image_url ? (
                      <img 
                        src={s.poster_url || s.poster || s.poster_path || s.image_url} 
                        alt={s.name}
                        className="w-full h-full object-cover object-top group-hover:scale-110 transition-transform duration-500" 
                        loading="lazy" 
                      />
                    ) : (
                      <div className="w-full h-full flex flex-col items-center justify-center text-slate-600 gap-2">
                        <ImageIcon className="w-10 h-10" />
                        <span className="text-xs">No Poster</span>
                      </div>
                    )}
                    {/* Shimmer Overlay */}
                    <div className="absolute inset-0 bg-linear-to-t from-slate-900/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                    {s.status && (
                      <div className={`absolute top-2 right-2 backdrop-blur-md px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider border ${s.status === 'Running' ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-rose-500/20 text-rose-400 border-rose-500/30'}`}>
                        {s.status}
                      </div>
                    )}
                  </div>
                  
                  <div className="p-3 flex flex-col flex-1 bg-slate-800/30">
                    <h3 className="font-bold text-sm leading-tight mb-1 line-clamp-2 group-hover:text-purple-400 transition-colors">{s.name}</h3>
                    <p className="text-xs text-slate-400 mb-2 flex items-center gap-1.5">
                      <Calendar className="w-3 h-3" />
                      {s.premiere?.split("-")[0] || s.first_aired?.split("-")[0] || "?"} • {s.origin_country || "Unknown"}
                    </p>
                    <div className="flex justify-between items-center text-[11px] text-slate-400 mt-auto pt-2 border-t border-slate-700/50">
                      <span className="font-mono text-slate-500">{s.network || "?"}</span>
                      <span className="flex items-center gap-1 text-amber-400 font-bold"><Star className="w-3 h-3 fill-current"/> {s.avg_rating || "N/A"}</span>
                    </div>
                  </div>
                </div>
              ))}
              {series.length === 0 && (
                <div className="col-span-full h-64 flex flex-col items-center justify-center text-slate-500 gap-4">
                  <div className="p-6 rounded-3xl bg-slate-800/30 border border-slate-700/30">
                    <Tv className="w-16 h-16 text-slate-600" />
                  </div>
                  <p className="text-lg">No TV Series tracked yet.</p>
                  <p className="text-sm text-slate-600">Add one from the search bar above!</p>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700/50 overflow-hidden">
              <table className="w-full">
                <thead className="bg-slate-900/80 border-b border-slate-700/50">
                  <tr>
                    <th className="text-left p-4 text-sm font-bold text-slate-300 uppercase tracking-wider">Title</th>
                    <th className="text-left p-4 text-sm font-bold text-slate-300 uppercase tracking-wider">Network</th>
                    <th className="text-left p-4 text-sm font-bold text-slate-300 uppercase tracking-wider">Status</th>
                    <th className="text-left p-4 text-sm font-bold text-slate-300 uppercase tracking-wider">Premiere</th>
                    <th className="text-right p-4 text-sm font-bold text-slate-300 uppercase tracking-wider">Rating</th>
                    <th className="text-right p-4 text-sm font-bold text-slate-300 uppercase tracking-wider">Seasons</th>
                  </tr>
                </thead>
                <tbody>
                  {series.map(s => (
                    <tr 
                      key={s.id}
                      onClick={() => loadDetail(s.id)}
                      className="border-b border-slate-700/30 hover:bg-slate-700/30 cursor-pointer transition-colors"
                    >
                      <td className="p-4">
                        <div className="flex items-center gap-3">
                          {s.poster_url ? (
                            <img src={s.poster_url} alt={s.name} className="w-10 h-15 object-cover rounded-lg shadow-md" />
                          ) : (
                            <div className="w-10 h-15 bg-slate-700/50 rounded-lg flex items-center justify-center">
                              <ImageIcon className="w-5 h-5 text-slate-500" />
                            </div>
                          )}
                          <span className="font-bold text-slate-100">{s.name}</span>
                        </div>
                      </td>
                      <td className="p-4 text-sm text-slate-400">{s.network || "Unknown"}</td>
                      <td className="p-4">
                        {s.status ? (
                          <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border ${s.status === 'Running' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'}`}>
                            {s.status}
                          </span>
                        ) : (
                          <span className="text-slate-500 text-sm">-</span>
                        )}
                      </td>
                      <td className="p-4 text-sm text-slate-400">{s.premiere_date || "N/A"}</td>
                      <td className="p-4 text-right text-sm text-amber-400 font-bold">
                        {s.avg_rating ? `${s.avg_rating}/10` : "-"}
                      </td>
                      <td className="p-4 text-right text-sm text-slate-400">
                        {s.total_seasons || "-"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {series.length === 0 && (
                <div className="h-64 flex flex-col items-center justify-center text-slate-500 gap-4">
                  <div className="p-6 rounded-3xl bg-slate-800/30 border border-slate-700/30">
                    <Tv className="w-16 h-16 text-slate-600" />
                  </div>
                  <p className="text-lg">No TV Series tracked yet.</p>
                  <p className="text-sm text-slate-600">Add one from the search bar above!</p>
                </div>
              )}
            </div>
          )}
          
          {totalPages > 1 && (
            <div className="flex justify-center items-center gap-4 mt-8">
              <button onClick={() => setPage(Math.max(0, page - 1))} disabled={page === 0}
                className="flex items-center gap-1 bg-slate-800/50 border border-slate-700/50 hover:bg-slate-700/50 hover:border-purple-500/30 text-slate-300 px-4 py-2.5 rounded-xl disabled:opacity-30 transition-all duration-300">
                <ChevronLeft className="w-5 h-5" />
                <span className="hidden sm:inline font-bold">Previous</span>
              </button>
              <span className="text-slate-400 text-sm font-medium">
                Page <span className="text-slate-100 font-black text-lg">{page + 1}</span> of <span className="text-slate-100 font-black text-lg">{totalPages}</span>
              </span>
              <button onClick={() => setPage(Math.min(totalPages - 1, page + 1))} disabled={page >= totalPages - 1}
                className="flex items-center gap-1 bg-slate-800/50 border border-slate-700/50 hover:bg-slate-700/50 hover:border-purple-500/30 text-slate-300 px-4 py-2.5 rounded-xl disabled:opacity-30 transition-all duration-300">
                <span className="hidden sm:inline font-bold">Next</span>
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          )}
        </>
      )}

      {/* Modern Detail Modal */}
      {selectedSeries && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-slate-900/95 backdrop-blur-xl rounded-3xl border border-slate-700/50 shadow-2xl shadow-black/50 w-full max-w-5xl max-h-[90vh] flex flex-col overflow-hidden relative">
            {/* Ambient Glow */}
            <div className="absolute -top-32 -right-32 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />
            <div className="absolute -bottom-32 -left-32 w-64 h-64 bg-pink-500/10 rounded-full blur-3xl pointer-events-none" />
            
            <button onClick={() => setSelectedSeries(null)} title="Close modal"
              className="absolute top-4 right-4 p-2.5 bg-slate-800/80 backdrop-blur-sm rounded-full hover:bg-slate-700 text-slate-400 hover:text-white transition-all z-10 border border-slate-700/50 hover:border-slate-600">
              <X className="w-5 h-5" />
            </button>

            {detailLoading ? (
              <div className="h-96 flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                  <Loader2 className="w-10 h-10 animate-spin text-purple-500" />
                  <p className="text-slate-500 animate-pulse">Loading details...</p>
                </div>
              </div>
            ) : (
              <>
                <div className="flex flex-col md:flex-row border-b border-slate-700/50 bg-slate-800/30">
                  <div className="md:w-1/4 bg-slate-900/50 relative overflow-hidden">
                    {selectedSeries.poster_url || selectedSeries.poster || selectedSeries.poster_path || selectedSeries.image_url ? (
                      <img 
                        src={selectedSeries.poster_url || selectedSeries.poster || selectedSeries.poster_path || selectedSeries.image_url} 
                        alt={selectedSeries.name} 
                        className="w-full h-full object-cover" 
                      />
                    ) : (
                      <div className="w-full h-48 md:h-full flex items-center justify-center text-slate-700 bg-slate-900/50">
                        <ImageIcon className="w-20 h-20 opacity-50" />
                      </div>
                    )}
                    {/* Poster Gradient Overlay */}
                    <div className="absolute inset-0 bg-linear-to-t from-slate-900/60 via-transparent to-transparent" />
                  </div>
                  <div className="md:w-3/4 p-8 flex flex-col justify-center relative z-10">
                    <div className="flex flex-wrap items-center gap-4 mb-3">
                      <h2 className="text-4xl font-black text-slate-100 tracking-tight">{selectedSeries.name}</h2>
                      <span className={`px-3 py-1.5 rounded-full text-xs font-black uppercase tracking-wider border ${selectedSeries.status === 'Running' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'}`}>
                        {selectedSeries.status}
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-6 text-sm text-slate-400 mt-2 mb-6">
                      <span className="flex items-center gap-2 bg-slate-800/50 px-3 py-1.5 rounded-full border border-slate-700/30"><Play className="w-4 h-4 text-slate-500"/> {selectedSeries.network}</span>
                      <span className="flex items-center gap-2 bg-slate-800/50 px-3 py-1.5 rounded-full border border-slate-700/30"><Calendar className="w-4 h-4 text-slate-500"/> {selectedSeries.premiere_date}</span>
                      <span className="flex items-center gap-2 bg-slate-800/50 px-3 py-1.5 rounded-full border border-slate-700/30"><Star className="w-4 h-4 text-amber-400 fill-current"/> {selectedSeries.avg_rating} / 10</span>
                    </div>
                    
                    <div className="flex flex-wrap items-center gap-3 mt-auto">
                      <button onClick={() => handleRefresh(selectedSeries.id)} disabled={refreshing}
                        className="flex items-center gap-2 bg-blue-500/20 hover:bg-blue-500 text-blue-400 hover:text-white px-5 py-2.5 rounded-xl text-sm font-bold transition-all duration-300 border border-blue-500/30 disabled:opacity-50 hover:-translate-y-0.5">
                        {refreshing ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
                        Refresh Data
                      </button>
                      <button onClick={() => handleDelete(selectedSeries.id)} disabled={deleting}
                        className="flex items-center gap-2 bg-rose-500/20 hover:bg-rose-500 text-rose-400 hover:text-white px-5 py-2.5 rounded-xl text-sm font-bold transition-all duration-300 border border-rose-500/30 disabled:opacity-50 hover:-translate-y-0.5">
                        {deleting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
                        Delete TV Series
                      </button>
                      <button onClick={() => window.open(`http://localhost:8000/api/tv/${selectedSeries.id}/pdf`, '_blank')}
                        className="flex items-center gap-2 bg-emerald-500/20 hover:bg-emerald-500 text-emerald-400 hover:text-white px-5 py-2.5 rounded-xl text-sm font-bold transition-all duration-300 border border-emerald-500/30 hover:-translate-y-0.5">
                        <Download className="w-4 h-4" />
                        Export PDF
                      </button>
                    </div>
                  </div>
                </div>

                <div className="flex-1 overflow-y-auto custom-scrollbar p-8">
                  {/* Season Overview */}
                  {selectedSeries.episodes && selectedSeries.episodes.length > 0 && (() => {
                    const seasonData: any = {};
                    selectedSeries.episodes.forEach((ep: any) => {
                      if (!seasonData[ep.season]) {
                        seasonData[ep.season] = { episodes: [], ratings: [], dates: [] };
                      }
                      seasonData[ep.season].episodes.push(ep);
                      if (ep.rating) seasonData[ep.season].ratings.push(parseFloat(ep.rating));
                      if (ep.air_date) seasonData[ep.season].dates.push(ep.air_date);
                    });
                    
                    const seasons = Object.keys(seasonData).map(season => ({
                      season,
                      episodeCount: seasonData[season].episodes.length,
                      avgRating: seasonData[season].ratings.length > 0 
                        ? (seasonData[season].ratings.reduce((a: number, b: number) => a + b, 0) / seasonData[season].ratings.length).toFixed(1)
                        : '-',
                      firstAir: seasonData[season].dates.length > 0 ? seasonData[season].dates[0] : '-',
                      lastAir: seasonData[season].dates.length > 0 ? seasonData[season].dates[seasonData[season].dates.length - 1] : '-'
                    })).sort((a, b) => parseInt(a.season) - parseInt(b.season));
                    
                    return (
                      <div className="mb-8">
                        <div className="flex items-center gap-3 mb-4">
                          <div className="w-1 h-6 bg-linear-to-b from-purple-500 to-pink-500 rounded-full" />
                          <h3 className="text-xl font-black text-slate-100">Season Overview</h3>
                        </div>
                        <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700/50 overflow-hidden">
                          <table className="w-full text-left text-sm">
                            <thead className="bg-slate-900/80">
                              <tr>
                                <th className="p-4 font-bold text-slate-300 uppercase tracking-wider text-xs">Season</th>
                                <th className="p-4 text-right font-bold text-slate-300 uppercase tracking-wider text-xs">Episodes</th>
                                <th className="p-4 text-right font-bold text-slate-300 uppercase tracking-wider text-xs">Avg Rating</th>
                                <th className="p-4 font-bold text-slate-300 uppercase tracking-wider text-xs">First Air Date</th>
                                <th className="p-4 font-bold text-slate-300 uppercase tracking-wider text-xs">Last Air Date</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-700/30">
                              {seasons.map((s: any) => (
                                <tr key={s.season} className="hover:bg-slate-700/30 transition-colors">
                                  <td className="p-4 font-bold text-slate-100">Season {s.season}</td>
                                  <td className="p-4 text-right text-slate-400">{s.episodeCount}</td>
                                  <td className="p-4 text-right text-amber-400 font-bold">{s.avgRating}</td>
                                  <td className="p-4 text-slate-400">{s.firstAir}</td>
                                  <td className="p-4 text-slate-400">{s.lastAir}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </div>
                    );
                  })()}

                  {selectedSeries.chartData && selectedSeries.chartData.length > 0 ? (
                    <div className="mb-12">
                      <div className="flex items-center gap-3 mb-6">
                        <div className="w-1 h-6 bg-linear-to-b from-blue-500 to-cyan-500 rounded-full" />
                        <h3 className="text-xl font-black text-slate-100">US Viewership (Millions)</h3>
                      </div>
                      <div className="h-75 w-full bg-slate-900/50 rounded-2xl p-4 border border-slate-700/50">
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={selectedSeries.chartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                            <XAxis dataKey="name" stroke="#9CA3AF" fontSize={12} tickLine={false} axisLine={false} minTickGap={30} />
                            <YAxis stroke="#9CA3AF" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `${value}M`} />
                            <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '0.5rem', color: '#fff' }} labelStyle={{ color: '#9CA3AF', fontWeight: 'bold', marginBottom: '0.25rem' }} formatter={(value: number) => [`${value}M Viewers`, 'US Ratings']} />
                            <Line type="monotone" dataKey="viewers" stroke="#8B5CF6" strokeWidth={3} dot={{ fill: '#8B5CF6', strokeWidth: 2, r: 4 }} activeDot={{ r: 6, fill: '#fff', stroke: '#8B5CF6' }} />
                          </LineChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-slate-800/30 p-6 rounded-2xl border border-slate-700/50 border-dashed text-center mb-8">
                      <p className="text-slate-500">Wikipedia US Viewership data not found for this series.</p>
                    </div>
                  )}

                  {/* Rating Chart */}
                  {selectedSeries.episodes && selectedSeries.episodes.length > 0 && (() => {
                    const ratingData = selectedSeries.episodes
                      .filter((ep: any) => ep.rating)
                      .map((ep: any) => ({
                        name: `S${ep.season}E${ep.episode}`,
                        rating: parseFloat(ep.rating)
                      }));
                    
                    if (ratingData.length === 0) return null;
                    
                    return (
                      <div className="mb-12">
                        <div className="flex items-center gap-3 mb-6">
                          <div className="w-1 h-6 bg-linear-to-b from-amber-500 to-yellow-500 rounded-full" />
                          <h3 className="text-xl font-black text-slate-100">Episode Ratings</h3>
                        </div>
                        <div className="h-75 w-full bg-slate-900/50 rounded-2xl p-4 border border-slate-700/50">
                          <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={ratingData}>
                              <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                              <XAxis dataKey="name" stroke="#9CA3AF" fontSize={10} tickLine={false} axisLine={false} interval={Math.ceil(ratingData.length / 20)} />
                              <YAxis stroke="#9CA3AF" fontSize={12} tickLine={false} axisLine={false} domain={[0, 10]} />
                              <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '0.5rem', color: '#fff' }} labelStyle={{ color: '#9CA3AF', fontWeight: 'bold', marginBottom: '0.25rem' }} formatter={(value: number) => [`${value}/10`, 'Rating']} />
                              <Bar dataKey="rating" fill="#F59E0B" radius={[4, 4, 0, 0]} />
                            </BarChart>
                          </ResponsiveContainer>
                        </div>
                      </div>
                    );
                  })()}

                  {/* Season Comparison Chart */}
                  {selectedSeries.episodes && selectedSeries.episodes.length > 0 && (() => {
                    const seasonData: any = {};
                    selectedSeries.episodes.forEach((ep: any) => {
                      if (!seasonData[ep.season]) {
                        seasonData[ep.season] = { ratings: [], viewers: [] };
                      }
                      if (ep.rating) seasonData[ep.season].ratings.push(parseFloat(ep.rating));
                      if (ep.viewership_millions) seasonData[ep.season].viewers.push(parseFloat(ep.viewership_millions));
                    });
                    
                    const comparisonData = Object.keys(seasonData).map(season => ({
                      season: `Season ${season}`,
                      avgRating: seasonData[season].ratings.length > 0 
                        ? (seasonData[season].ratings.reduce((a: number, b: number) => a + b, 0) / seasonData[season].ratings.length).toFixed(2)
                        : 0,
                      avgViewers: seasonData[season].viewers.length > 0
                        ? (seasonData[season].viewers.reduce((a: number, b: number) => a + b, 0) / seasonData[season].viewers.length).toFixed(2)
                        : 0
                    })).sort((a, b) => parseInt(a.season.replace('Season ', '')) - parseInt(b.season.replace('Season ', '')));
                    
                    if (comparisonData.length < 2) return null;
                    
                    return (
                      <div className="mb-12">
                        <div className="flex items-center gap-3 mb-6">
                          <div className="w-1 h-6 bg-linear-to-b from-cyan-500 to-teal-500 rounded-full" />
                          <h3 className="text-xl font-black text-slate-100">Season Comparison</h3>
                        </div>
                        <div className="h-75 w-full bg-slate-900/50 rounded-2xl p-4 border border-slate-700/50">
                          <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={comparisonData}>
                              <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                              <XAxis dataKey="season" stroke="#9CA3AF" fontSize={12} tickLine={false} axisLine={false} />
                              <YAxis stroke="#9CA3AF" fontSize={12} tickLine={false} axisLine={false} />
                              <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151', borderRadius: '0.5rem', color: '#fff' }} labelStyle={{ color: '#9CA3AF', fontWeight: 'bold', marginBottom: '0.25rem' }} />
                              <Bar dataKey="avgRating" fill="#8B5CF6" name="Avg Rating" radius={[4, 4, 0, 0]} />
                              <Bar dataKey="avgViewers" fill="#10B981" name="Avg Viewers (M)" radius={[4, 4, 0, 0]} />
                            </BarChart>
                          </ResponsiveContainer>
                        </div>
                      </div>
                    );
                  })()}

                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-1 h-6 bg-linear-to-b from-indigo-500 to-violet-500 rounded-full" />
                    <h3 className="text-xl font-black text-slate-100">Episode Guide</h3>
                  </div>
                  {selectedSeries.episodes && selectedSeries.episodes.length > 0 && (() => {
                    const seasonGroups: any = {};
                    selectedSeries.episodes.forEach((ep: any) => {
                      if (!seasonGroups[ep.season]) {
                        seasonGroups[ep.season] = [];
                      }
                      seasonGroups[ep.season].push(ep);
                    });
                    
                    const seasons = Object.keys(seasonGroups).sort((a, b) => parseInt(a) - parseInt(b));
                    
                    return (
                      <div className="space-y-4">
                        {seasons.map((season) => {
                          const isExpanded = expandedSeasons.has(parseInt(season));
                          const toggleSeason = () => {
                            const newExpanded = new Set(expandedSeasons);
                            if (isExpanded) {
                              newExpanded.delete(parseInt(season));
                            } else {
                              newExpanded.add(parseInt(season));
                            }
                            setExpandedSeasons(newExpanded);
                          };
                          
                          return (
                            <div key={season} className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700/50 overflow-hidden">
                              <button 
                                onClick={toggleSeason}
                                className="w-full p-4 flex items-center justify-between bg-slate-800/50 hover:bg-slate-700/50 transition-all group"
                              >
                                <span className="font-bold text-slate-100 flex items-center gap-2">
                                  Season {season} 
                                  <span className="text-xs bg-slate-700/50 px-2 py-0.5 rounded-full text-slate-400">{seasonGroups[season].length} episodes</span>
                                </span>
                                <ChevronLeft className={`w-5 h-5 text-slate-400 transition-transform duration-300 group-hover:text-slate-200 ${isExpanded ? 'rotate-90' : ''}`} />
                              </button>
                              {isExpanded && (
                                <div className="overflow-hidden border-t border-slate-700/30">
                                  <table className="w-full text-left text-sm">
                                    <thead className="bg-slate-900/50">
                                      <tr>
                                        <th className="p-4 font-bold text-slate-400 uppercase tracking-wider text-xs">Episode</th>
                                        <th className="p-4 font-bold text-slate-400 uppercase tracking-wider text-xs">Title</th>
                                        <th className="p-4 text-right font-bold text-slate-400 uppercase tracking-wider text-xs">Air Date</th>
                                        <th className="p-4 text-right font-bold text-slate-400 uppercase tracking-wider text-xs">Rating</th>
                                      </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-700/30">
                                      {seasonGroups[season].map((ep: any, i: number) => (
                                        <tr key={i} className="hover:bg-slate-700/30 transition-colors">
                                          <td className="p-4 font-mono text-slate-400 font-bold whitespace-nowrap">E{ep.episode}</td>
                                          <td className="p-4 font-bold text-slate-100">{ep.title}</td>
                                          <td className="p-4 text-right text-slate-500 whitespace-nowrap">{ep.air_date}</td>
                                          <td className="p-4 text-right font-mono text-amber-400 font-bold">{ep.rating ? ep.rating : '-'}</td>
                                        </tr>
                                      ))}
                                    </tbody>
                                  </table>
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    );
                  })()}

                  {/* Staff & Credits */}
                  {(selectedSeries.director || selectedSeries.producer || selectedSeries.studio || selectedSeries.cast_json) && (
                    <div className="mt-8">
                      <div className="flex items-center gap-3 mb-4">
                        <div className="w-1 h-6 bg-linear-to-b from-rose-500 to-pink-500 rounded-full" />
                        <h3 className="text-xl font-black text-slate-100">Staff & Credits</h3>
                      </div>
                      <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-700/50 p-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          {selectedSeries.director && (
                            <div>
                              <h4 className="text-sm font-bold text-slate-400 mb-1 uppercase tracking-wider">Director</h4>
                              <p className="text-slate-100 font-semibold">{selectedSeries.director}</p>
                            </div>
                          )}
                          {selectedSeries.producer && (
                            <div>
                              <h4 className="text-sm font-bold text-slate-400 mb-1 uppercase tracking-wider">Producer</h4>
                              <p className="text-slate-100 font-semibold">{selectedSeries.producer}</p>
                            </div>
                          )}
                          {selectedSeries.studio && (
                            <div>
                              <h4 className="text-sm font-bold text-slate-400 mb-1 uppercase tracking-wider">Studio</h4>
                              <p className="text-slate-100 font-semibold">{selectedSeries.studio}</p>
                            </div>
                          )}
                        </div>
                        {selectedSeries.cast_json && (() => {
                          try {
                            const cast = typeof selectedSeries.cast_json === 'string' 
                              ? JSON.parse(selectedSeries.cast_json) 
                              : selectedSeries.cast_json;
                            if (Array.isArray(cast) && cast.length > 0) {
                              return (
                                <div className="mt-6 pt-6 border-t border-slate-700/50">
                                  <h4 className="text-sm font-bold text-slate-400 mb-3 uppercase tracking-wider">Cast</h4>
                                  <div className="flex flex-wrap gap-2">
                                    {cast.map((actor: string, i: number) => (
                                      <span key={i} className="bg-slate-700/50 text-slate-300 px-3 py-1.5 rounded-full text-sm font-medium border border-slate-600/30">
                                        {actor}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              );
                            }
                          } catch (e) {
                            return null;
                          }
                        })()}
                      </div>
                    </div>
                  )}

                  {/* Modern Similar Titles */}
                  <div className="mt-8">
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-1 h-6 bg-linear-to-b from-emerald-500 to-teal-500 rounded-full" />
                      <h3 className="text-xl font-black text-slate-100">Similar Titles</h3>
                      <span className="text-xs text-slate-500 bg-slate-800/50 px-3 py-1 rounded-full border border-slate-700/30">From TMDB</span>
                    </div>
                    {loadingSimilar ? (
                      <div className="flex items-center justify-center h-32 bg-slate-800/30 rounded-2xl border border-slate-700/30">
                        <Loader2 className="w-8 h-8 animate-spin text-purple-500" />
                      </div>
                    ) : similarSeries.length > 0 ? (
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        {similarSeries.map((series: any) => (
                          <div key={series.tmdb_id} className="group bg-slate-800/50 backdrop-blur-sm p-3 rounded-2xl border border-slate-700/50 hover:border-purple-500/40 hover:-translate-y-1 transition-all duration-300">
                            {series.poster_url_card ? (
                              <img src={series.poster_url_card} alt={series.title} className="w-full h-32 object-cover rounded-xl mb-3 shadow-lg group-hover:scale-105 transition-transform duration-300" />
                            ) : (
                              <div className="w-full h-32 bg-slate-700/50 rounded-xl mb-3 flex items-center justify-center">
                                <ImageIcon className="w-10 h-10 text-slate-500" />
                              </div>
                            )}
                            <p className="font-bold text-slate-100 text-sm truncate group-hover:text-purple-400 transition-colors">{series.title}</p>
                            <p className="text-xs text-slate-400">{series.first_air_date || "TBA"}</p>
                            {series.vote_average && (
                              <p className="text-sm text-amber-400 mt-1 flex items-center gap-1 font-bold">
                                <Star className="w-3 h-3 fill-current" /> {series.vote_average.toFixed(1)}
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
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* Search Modal */}
      {showSearchModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[100] flex items-center justify-center p-4 animate-fade-in" onClick={() => setShowSearchModal(false)}>
          <div className="bg-slate-900/95 backdrop-blur-xl rounded-3xl border border-slate-700/50 shadow-2xl shadow-black/50 w-full max-w-lg relative" onClick={e => e.stopPropagation()}>
            <button 
              onClick={() => setShowSearchModal(false)}
              className="absolute top-4 right-4 p-2.5 bg-slate-800/80 backdrop-blur-sm rounded-full hover:bg-slate-700 text-slate-400 hover:text-white z-20 border border-slate-700/50 hover:border-slate-600 transition-all"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="p-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 rounded-2xl bg-linear-to-br from-purple-500/20 to-pink-500/20 border border-purple-500/30 shadow-lg shadow-purple-500/10">
                  <Search className="w-6 h-6 text-purple-400" />
                </div>
                <div>
                  <h3 className="text-2xl font-black text-slate-100 tracking-tight">Search TV Series</h3>
                  <p className="text-slate-400 text-sm mt-1">Search TVMaze database and add to your collection</p>
                </div>
              </div>

              <form onSubmit={handleSearch} className="space-y-4">
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                  <input
                    type="text"
                    placeholder="Search TVMaze..."
                    className="w-full bg-slate-800/50 border border-slate-700/50 rounded-xl pl-12 pr-4 py-3.5 text-base text-slate-200 focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50 outline-none transition-all duration-300 placeholder:text-slate-600"
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    autoFocus
                  />
                </div>
                <button
                  type="submit"
                  disabled={searchLoading}
                  className="w-full bg-linear-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white py-3.5 rounded-xl font-bold flex items-center justify-center gap-2 disabled:opacity-50 transition-all duration-300 shadow-lg shadow-purple-500/20 hover:shadow-purple-500/40 hover:-translate-y-0.5"
                >
                  {searchLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
                  {searchLoading ? "Searching..." : "Search"}
                </button>
              </form>

              {/* Search Results */}
              {searchResults.length > 0 && (
                <div className="mt-6 space-y-3 max-h-96 overflow-y-auto custom-scrollbar">
                  <h4 className="text-sm font-bold text-slate-400 uppercase tracking-wider">Results</h4>
                  {searchResults.map((series: any) => (
                    <div
                      key={series.id}
                      onClick={() => { loadDetail(series.id); setShowSearchModal(false); }}
                      className="flex items-center gap-4 p-3 bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-700/50 hover:border-purple-500/30 transition-all duration-300 cursor-pointer group"
                    >
                      {series.image && (
                        <img src={series.image.medium || series.image.original} alt={series.name} className="w-16 h-24 object-cover rounded-lg shadow-md" />
                      )}
                      <div className="flex-1 min-w-0">
                        <div className="font-bold text-slate-100 truncate">{series.name}</div>
                        <div className="text-xs text-slate-500 mt-1">{series.network?.name || 'Unknown Network'}</div>
                        <div className="text-xs text-slate-500">{series.premiered?.split('-')[0] || 'Unknown Year'}</div>
                      </div>
                      <button
                        onClick={(e) => { e.stopPropagation(); handleAddSeries(series.id); }}
                        disabled={scraping}
                        className="p-2 bg-purple-500/20 hover:bg-purple-500/30 text-purple-400 rounded-lg border border-purple-500/30 transition-all disabled:opacity-50"
                        title="Add to collection"
                      >
                        <Plus className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {searchResults.length === 0 && !searchLoading && searchQuery && (
                <div className="mt-6 text-center text-slate-500 text-sm">
                  No results found. Try a different search term.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
