import { useState, useEffect } from "react";
import { Search, Loader2, X, Plus, Star, Users, Flame, Info, Trash2, ChevronLeft, ChevronRight, Filter } from "lucide-react";
import DataCutoffLabel from "../components/DataCutoffLabel";

export default function Anime() {
  const [animeList, setAnimeList] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [perPage, setPerPage] = useState(25);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [scraping, setScraping] = useState(false);
  const [deleting, setDeleting] = useState(false);
  
  // Demographic and origin country filters
  const [selectedDemographics, setSelectedDemographics] = useState<string[]>([]);
  const [selectedOrigins, setSelectedOrigins] = useState<string[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  
  const [selectedAnime, setSelectedAnime] = useState<any>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [arcs, setArcs] = useState<any[]>([]);
  const [adminMode, setAdminMode] = useState(false);
  const [newArc, setNewArc] = useState({ arc_name: "", episode_start: "", episode_end: "" });
  const [showSearchModal, setShowSearchModal] = useState(false);
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);

  const demographics = [
    { id: "shounen", name: "Shounen", description: "Young male audiences" },
    { id: "shoujo", name: "Shoujo", description: "Young female audiences" },
    { id: "seinen", name: "Seinen", description: "Adult male audiences" },
    { id: "josei", name: "Josei", description: "Adult female audiences" },
    { id: "kids", name: "Kodomomuke", description: "Children" }
  ];

  const origins = ["Japan", "Korea", "China", "India", "Other"];

  const fetchAnime = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/anime/?limit=${perPage}&offset=${page * perPage}`);
      const data = await res.json();
      setAnimeList(data.items || []);
      setTotal(data.total || 0);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  useEffect(() => { fetchAnime(); }, [page, perPage]);
  const totalPages = Math.ceil(total / perPage);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery) return;
    
    setSearchLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/anime/search?query=${encodeURIComponent(searchQuery)}`);
      const data = await res.json();
      setSearchResults(data.results || []);
    } catch (e) { 
      console.error(e);
      setSearchResults([]);
    }
    setSearchLoading(false);
  };

  const handleAddAnime = async (animeId: number) => {
    setScraping(true);
    try {
      const res = await fetch(`http://localhost:8000/api/anime/scrape?id=${animeId}`, { method: "POST" });
      if (res.ok) {
        setShowSearchModal(false);
        setSearchResults([]);
        setSearchQuery("");
        setTimeout(fetchAnime, 3000);
      }
    } catch (e) { console.error(e); }
    setScraping(false);
  };

  const loadDetail = async (id: number) => {
    setDetailLoading(true);
    setAdminMode(false);
    try {
      const res = await fetch(`http://localhost:8000/api/anime/${id}`);
      const data = await res.json();
      setSelectedAnime(data);
      
      const arcsRes = await fetch(`http://localhost:8000/api/anime/${id}/arcs`);
      const arcsData = await arcsRes.json();
      setArcs(arcsData);
    } catch (e) { console.error(e); }
    setDetailLoading(false);
  };

  const handleAddArc = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newArc.arc_name || !newArc.episode_start || !newArc.episode_end) return;
    
    try {
      const res = await fetch(`http://localhost:8000/api/anime/${selectedAnime.id}/arcs`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          arc_name: newArc.arc_name,
          episode_start: parseInt(newArc.episode_start),
          episode_end: parseInt(newArc.episode_end)
        })
      });
      if (res.ok) {
        setNewArc({ arc_name: "", episode_start: "", episode_end: "" });
        const arcsRes = await fetch(`http://localhost:8000/api/anime/${selectedAnime.id}/arcs`);
        setArcs(await arcsRes.json());
      }
    } catch (e) { console.error(e); }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this Anime from the database?")) return;
    setDeleting(true);
    try {
      const res = await fetch(`http://localhost:8000/api/anime/${id}`, { method: "DELETE" });
      if (res.ok) {
        setSelectedAnime(null);
        fetchAnime();
      }
    } catch (e) { console.error(e); }
    setDeleting(false);
  };

  return (
    <div className="max-w-7xl mx-auto pb-12">
      {/* Modern Header */}
      <header className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-3 rounded-2xl bg-linear-to-br from-orange-100 to-red-100 dark:from-orange-500/20 dark:to-red-500/20 border border-orange-200 dark:border-orange-500/30 shadow-lg shadow-orange-500/10">
            <Flame className="w-8 h-8 text-orange-600 dark:text-orange-400" />
          </div>
          <div>
            <h2 className="text-4xl font-black text-slate-900 dark:text-slate-100 tracking-tight">Animated Shows Database</h2>
            <div className="flex items-center gap-3 mt-1">
              <span className="text-slate-600 dark:text-slate-400 text-sm flex items-center gap-2">
                {total.toLocaleString()} anime tracked via MyAnimeList and AniList
                <span className="inline-flex h-2 w-2 rounded-full bg-orange-500 animate-pulse" />
              </span>
            </div>
            <DataCutoffLabel />
          </div>
        </div>
      </header>

      {/* Modern Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        {total > 50 && (
          <div className="flex items-center gap-2 bg-white dark:bg-slate-800/50 rounded-xl px-3 py-1.5 border border-slate-200 dark:border-slate-700/50 shadow-sm">
            <span className="text-slate-500 text-xs font-medium uppercase tracking-wider">Per page</span>
            {[10, 15, 25, 50, 100].map(n => (
              <button key={n} onClick={() => { setPerPage(n); setPage(0); }}
                className={`px-2.5 py-1 rounded-lg text-sm font-bold transition-all duration-300 ${perPage === n ? 'bg-orange-500 text-white shadow-md' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700/50'}`}>
                {n}
              </button>
            ))}
          </div>
        )}
        
        <div className="flex items-center gap-3 ml-auto">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`px-4 py-2.5 rounded-xl text-sm font-bold flex items-center gap-2 transition-all duration-300 ${showFilters ? 'bg-orange-500 text-white shadow-md' : 'bg-white dark:bg-slate-800/50 text-slate-700 dark:text-slate-400 border border-slate-200 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/50'}`}
          >
            <Filter className="w-4 h-4" />
            Filters
            {selectedDemographics.length > 0 || selectedOrigins.length > 0 && (
              <span className="bg-orange-500 text-white text-xs px-1.5 py-0.5 rounded-full">
                {selectedDemographics.length + selectedOrigins.length}
              </span>
            )}
          </button>
          <button
            onClick={() => setShowSearchModal(true)}
            className="bg-linear-to-r from-orange-500 to-red-500 hover:from-orange-400 hover:to-red-400 text-white px-5 py-2.5 rounded-xl text-sm font-bold flex items-center gap-2 transition-all duration-300 shadow-lg shadow-orange-500/20 hover:shadow-orange-500/40 hover:-translate-y-0.5"
          >
            <Search className="w-4 h-4" />
            Search & Add Anime
          </button>
        </div>
      </div>

      {/* Filter Panel */}
      {showFilters && (
        <div className="bg-white dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-slate-200 dark:border-slate-700/50 shadow-xl shadow-black/5 dark:shadow-black/10 mb-6 animate-in slide-in-from-top-2 duration-300">
          <div className="mb-4">
            <h4 className="text-sm font-bold text-slate-700 dark:text-slate-300 mb-3 uppercase tracking-wider">Demographics</h4>
            <div className="flex flex-wrap gap-2">
              {demographics.map(demo => (
                <button
                  key={demo.id}
                  onClick={() => setSelectedDemographics(prev =>
                    prev.includes(demo.id) ? prev.filter(d => d !== demo.id) : [...prev, demo.id]
                  )}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${selectedDemographics.includes(demo.id) ? 'bg-orange-100 text-orange-700 dark:bg-orange-500/20 dark:text-orange-400 border border-orange-300 dark:border-orange-500/30' : 'bg-slate-100 dark:bg-slate-900/50 text-slate-600 dark:text-slate-400 border border-slate-300 dark:border-slate-700/50 hover:border-slate-400 dark:hover:border-slate-600'}`}
                  title={demo.description}
                >
                  {demo.name}
                </button>
              ))}
            </div>
          </div>
          
          <div>
            <h4 className="text-sm font-bold text-slate-700 dark:text-slate-300 mb-3 uppercase tracking-wider">Origin Country</h4>
            <div className="flex flex-wrap gap-2">
              {origins.map(origin => (
                <button
                  key={origin}
                  onClick={() => setSelectedOrigins(prev =>
                    prev.includes(origin) ? prev.filter(o => o !== origin) : [...prev, origin]
                  )}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${selectedOrigins.includes(origin) ? 'bg-purple-100 text-purple-700 dark:bg-purple-500/20 dark:text-purple-400 border border-purple-300 dark:border-purple-500/30' : 'bg-slate-100 dark:bg-slate-900/50 text-slate-600 dark:text-slate-400 border border-slate-300 dark:border-slate-700/50 hover:border-slate-400 dark:hover:border-slate-600'}`}
                >
                  {origin}
                </button>
              ))}
            </div>
          </div>
          
          {(selectedDemographics.length > 0 || selectedOrigins.length > 0) && (
            <button
              onClick={() => { setSelectedDemographics([]); setSelectedOrigins([]); }}
              className="mt-4 text-xs text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 underline"
            >
              Clear all filters
            </button>
          )}
        </div>
      )}

      {loading ? (
        <div className="h-64 flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="w-10 h-10 animate-spin text-orange-500" />
            <p className="text-slate-600 dark:text-slate-500 animate-pulse">Loading anime...</p>
          </div>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
            {animeList.map(a => (
              <div 
                key={a.id} 
                onClick={() => loadDetail(a.id)}
                className="group bg-white dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl overflow-hidden shadow-xl shadow-black/5 dark:shadow-black/10 border border-slate-200 dark:border-slate-700/50 hover:border-orange-400/40 dark:hover:border-orange-500/40 transition-all duration-300 cursor-pointer hover:-translate-y-2 relative flex flex-col"
              >
                <div className="aspect-2/3 bg-slate-100 dark:bg-slate-900/80 w-full relative overflow-hidden">
                  {a.poster_url && <img src={a.poster_url} alt={a.title_english || a.title_normalized} className="w-full h-full object-cover object-top group-hover:scale-105 transition-transform duration-500" loading="lazy" />}
                  {/* Shimmer Overlay */}
                  <div className="absolute inset-0 bg-linear-to-t from-slate-900/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  <div className="absolute top-2 right-2 bg-black/60 backdrop-blur-md text-white px-2.5 py-1 rounded-full text-xs font-black flex items-center gap-1 border border-slate-600/50">
                    <Star className="w-3 h-3 text-amber-400 fill-current" /> {a.anilist_score ? (a.anilist_score / 10).toFixed(1) : a.mal_score}
                  </div>
                </div>
                <div className="p-3 flex-1 flex flex-col bg-slate-50 dark:bg-slate-800/30">
                  <h3 className="font-bold text-sm line-clamp-2 group-hover:text-orange-500 dark:group-hover:text-orange-400 transition-colors leading-tight text-slate-900 dark:text-slate-100">{a.title_english || a.title_normalized}</h3>
                  <div className="flex justify-between items-center mt-auto pt-2 text-[11px] text-slate-500 dark:text-slate-400 border-t border-slate-200 dark:border-slate-700/50">
                    <span className="font-mono text-slate-400 dark:text-slate-500">{a.episodes ? `${a.episodes} EPs` : '?'}</span>
                    <span>{a.season_year || ''}</span>
                  </div>
                </div>
              </div>
            ))}
            {animeList.length === 0 && (
              <div className="col-span-full h-64 flex flex-col items-center justify-center text-slate-500 gap-4">
                <div className="p-6 rounded-3xl bg-slate-100 dark:bg-slate-800/30 border border-slate-200 dark:border-slate-700/30">
                  <Flame className="w-16 h-16 text-slate-400" />
                </div>
                <p className="text-lg text-slate-700 dark:text-slate-500">No Anime tracked yet.</p>
                <p className="text-sm text-slate-500">Add one from the search bar above!</p>
              </div>
            )}
          </div>

          {totalPages > 1 && (
            <div className="flex justify-center items-center gap-4 mt-8">
              <button onClick={() => setPage(Math.max(0, page - 1))} disabled={page === 0}
                className="flex items-center gap-1 bg-white dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/50 hover:border-orange-400/30 dark:hover:border-orange-500/30 text-slate-700 dark:text-slate-300 px-4 py-2.5 rounded-xl disabled:opacity-30 transition-all duration-300">
                <ChevronLeft className="w-5 h-5" />
                <span className="hidden sm:inline font-bold">Previous</span>
              </button>
              <span className="text-slate-500 dark:text-slate-400 text-sm font-medium">
                Page <span className="text-slate-900 dark:text-slate-100 font-black text-lg">{page + 1}</span> of <span className="text-slate-900 dark:text-slate-100 font-black text-lg">{totalPages}</span>
              </span>
              <button onClick={() => setPage(Math.min(totalPages - 1, page + 1))} disabled={page >= totalPages - 1}
                className="flex items-center gap-1 bg-white dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50 hover:bg-slate-50 dark:hover:bg-slate-700/50 hover:border-orange-400/30 dark:hover:border-orange-500/30 text-slate-700 dark:text-slate-300 px-4 py-2.5 rounded-xl disabled:opacity-30 transition-all duration-300">
                <span className="hidden sm:inline font-bold">Next</span>
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          )}
        </>
      )}

      {/* Modern Detail Modal */}
      {selectedAnime && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-white dark:bg-slate-900/95 backdrop-blur-xl rounded-3xl border border-slate-200 dark:border-slate-700/50 shadow-2xl shadow-black/50 w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden relative">
            {/* Ambient Glow */}
            <div className="absolute -top-32 -right-32 w-64 h-64 bg-orange-500/10 rounded-full blur-3xl pointer-events-none" />
            <div className="absolute -bottom-32 -left-32 w-64 h-64 bg-red-500/10 rounded-full blur-3xl pointer-events-none" />
            
            <button onClick={() => setSelectedAnime(null)} title="Close modal"
              className="absolute top-4 right-4 p-2.5 bg-slate-100 dark:bg-slate-800/80 backdrop-blur-sm rounded-full hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all z-20 border border-slate-200 dark:border-slate-700/50 hover:border-slate-300 dark:hover:border-slate-600">
              <X className="w-5 h-5" />
            </button>

            {detailLoading ? (
              <div className="h-96 flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                  <Loader2 className="w-10 h-10 animate-spin text-orange-500" />
                  <p className="text-slate-500 animate-pulse">Loading details...</p>
                </div>
              </div>
            ) : (
              <div className="flex flex-col md:flex-row h-full overflow-y-auto custom-scrollbar">
                {/* Left side: Poster */}
                <div className="w-full md:w-1/3 bg-slate-100 dark:bg-slate-800/30 relative">
                  {selectedAnime.poster_url && <img src={selectedAnime.poster_url} alt={selectedAnime.title_english || selectedAnime.title_normalized} className="w-full h-full object-cover opacity-80" />}
                  <div className="absolute inset-0 bg-linear-to-t from-slate-900 via-slate-900/40 to-transparent"></div>
                  <div className="absolute bottom-0 left-0 p-6 w-full">
                    <h2 className="text-3xl font-black text-white leading-tight drop-shadow-lg tracking-tight">{selectedAnime.title_english || selectedAnime.title_normalized}</h2>
                    <p className="text-sm text-slate-200 dark:text-slate-300 mt-2 font-mono drop-shadow-md">{selectedAnime.title_japanese}</p>
                    <div className="flex flex-wrap gap-2 mt-4">
                      {selectedAnime.genre && selectedAnime.genre.split(',').map((g: string, i: number) => (
                        <span key={i} className="px-2.5 py-1 bg-slate-900/80 dark:bg-slate-800/80 backdrop-blur-sm border border-slate-600/50 rounded-full text-xs text-slate-200 dark:text-slate-300 font-medium">{g.trim()}</span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Right side: Stats */}
                <div className="w-full md:w-2/3 p-8 relative z-10">
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="bg-slate-50 dark:bg-slate-800/50 backdrop-blur-sm p-4 rounded-2xl border border-slate-200 dark:border-slate-700/50">
                      <div className="text-xs text-slate-500 dark:text-slate-500 uppercase tracking-wider font-bold mb-1">Studio</div>
                      <div className="text-lg font-black text-slate-900 dark:text-slate-100">{selectedAnime.studio || "Unknown"}</div>
                    </div>
                    <div className="bg-slate-50 dark:bg-slate-800/50 backdrop-blur-sm p-4 rounded-2xl border border-slate-200 dark:border-slate-700/50">
                      <div className="text-xs text-slate-500 dark:text-slate-500 uppercase tracking-wider font-bold mb-1">Source Material</div>
                      <div className="text-lg font-black text-slate-900 dark:text-slate-100">{selectedAnime.source_material || "Original"}</div>
                    </div>
                    <div className="bg-slate-50 dark:bg-slate-800/50 backdrop-blur-sm p-4 rounded-2xl border border-slate-200 dark:border-slate-700/50">
                      <div className="text-xs text-slate-500 dark:text-slate-500 uppercase tracking-wider font-bold mb-1">Status</div>
                      <div className="text-lg font-black text-slate-900 dark:text-slate-100">{selectedAnime.status || "Unknown"}</div>
                    </div>
                    <div className="bg-slate-50 dark:bg-slate-800/50 backdrop-blur-sm p-4 rounded-2xl border border-slate-200 dark:border-slate-700/50">
                      <div className="text-xs text-slate-500 dark:text-slate-500 uppercase tracking-wider font-bold mb-1">Episodes</div>
                      <div className="text-lg font-black text-slate-900 dark:text-slate-100">{selectedAnime.episodes || "?"} EPs</div>
                    </div>
                  </div>

                  <div className="mb-8">
                    <button onClick={() => handleDelete(selectedAnime.id)} disabled={deleting}
                      className="flex items-center gap-2 bg-rose-100 dark:bg-rose-500/20 hover:bg-rose-200 dark:hover:bg-rose-500 text-rose-600 dark:text-rose-400 hover:text-rose-700 dark:hover:text-white px-5 py-2.5 rounded-xl text-sm font-bold transition-all duration-300 border border-rose-200 dark:border-rose-500/30 disabled:opacity-50 hover:-translate-y-0.5">
                      {deleting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
                      Delete Anime
                    </button>
                  </div>

                  <div className="flex items-center gap-3 mb-4 mt-8">
                    <div className="w-1 h-6 bg-linear-to-b from-indigo-500 to-violet-500 rounded-full" />
                    <h3 className="text-xl font-black text-slate-900 dark:text-slate-100">Story Arcs</h3>
                    <button 
                      onClick={() => setAdminMode(!adminMode)}
                      className="ml-auto text-xs font-bold text-slate-500 hover:text-orange-500 dark:hover:text-orange-400 uppercase flex items-center gap-1 px-3 py-1.5 rounded-full bg-slate-100 dark:bg-slate-800/50 hover:bg-slate-200 dark:hover:bg-slate-700/50 transition-all border border-slate-200 dark:border-slate-700/30"
                    >
                      <Plus className="w-3 h-3"/> Admin Mode
                    </button>
                  </div>

                  {adminMode && (
                    <form onSubmit={handleAddArc} className="mb-6 bg-slate-50 dark:bg-slate-800/30 p-4 rounded-2xl border border-dashed border-slate-300 dark:border-slate-600/50 flex gap-2">
                      <input 
                        required type="text" placeholder="Arc Name (e.g. Wano Arc)" 
                        className="bg-white dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50 px-3 py-2 rounded-xl text-sm flex-1 outline-none focus:border-orange-500/50 transition-all text-slate-900 dark:text-slate-200 placeholder:text-slate-400 dark:placeholder:text-slate-600"
                        value={newArc.arc_name} onChange={e => setNewArc({...newArc, arc_name: e.target.value})}
                      />
                      <input 
                        required type="number" placeholder="Start Ep" 
                        className="bg-white dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50 px-3 py-2 rounded-xl text-sm w-24 outline-none focus:border-orange-500/50 transition-all text-slate-900 dark:text-slate-200 placeholder:text-slate-400 dark:placeholder:text-slate-600"
                        value={newArc.episode_start} onChange={e => setNewArc({...newArc, episode_start: e.target.value})}
                      />
                      <input 
                        required type="number" placeholder="End Ep" 
                        className="bg-white dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50 px-3 py-2 rounded-xl text-sm w-24 outline-none focus:border-orange-500/50 transition-all text-slate-900 dark:text-slate-200 placeholder:text-slate-400 dark:placeholder:text-slate-600"
                        value={newArc.episode_end} onChange={e => setNewArc({...newArc, episode_end: e.target.value})}
                      />
                      <button type="submit" className="bg-linear-to-r from-orange-500 to-red-500 hover:from-orange-400 hover:to-red-400 text-white px-4 py-2 rounded-xl text-sm font-bold transition-all shadow-md">Add</button>
                    </form>
                  )}

                  {arcs.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-8">
                      {arcs.map(arc => (
                        <div key={arc.id} className="bg-slate-50 dark:bg-slate-800/50 backdrop-blur-sm border border-slate-200 dark:border-slate-700/50 p-3 rounded-xl flex justify-between items-center hover:border-orange-400/30 dark:hover:border-orange-500/30 transition-all">
                          <span className="font-bold text-sm text-slate-800 dark:text-slate-200">{arc.arc_name}</span>
                          <span className="text-xs bg-slate-200 dark:bg-slate-900/80 px-2.5 py-1 rounded-full text-orange-600 dark:text-orange-400 font-mono font-bold">Eps {arc.episode_start}-{arc.episode_end}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-slate-500 text-sm mb-8 italic bg-slate-50 dark:bg-slate-800/30 p-4 rounded-xl border border-slate-200 dark:border-slate-700/30">No story arcs defined yet. Toggle Admin Mode to add some.</div>
                  )}

                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-1 h-6 bg-linear-to-b from-blue-500 to-cyan-500 rounded-full" />
                    <h3 className="text-xl font-black text-slate-900 dark:text-slate-100">Community Analytics</h3>
                  </div>
                  
                  {/* MAL vs AniList Comparison */}
                  <div className="space-y-4">
                    
                    {/* MyAnimeList */}
                    <div className="flex flex-col bg-blue-50 dark:bg-blue-900/20 backdrop-blur-sm border border-blue-200 dark:border-blue-500/20 rounded-2xl p-5">
                      <div className="flex items-center gap-2 mb-3">
                        <div className="bg-blue-600 text-white text-xs font-black px-2 py-1 rounded-md">MAL</div>
                        <span className="font-bold text-blue-700 dark:text-blue-400">MyAnimeList Metrics</span>
                      </div>
                      <div className="grid grid-cols-3 gap-4">
                        <div>
                          <div className="text-xs text-blue-600/60 dark:text-blue-300/60 mb-1 uppercase tracking-wider">Score</div>
                          <div className="text-2xl font-black text-slate-900 dark:text-white flex items-center gap-1"><Star className="w-5 h-5 text-amber-400 fill-current" /> {selectedAnime.mal_score || "-"}</div>
                        </div>
                        <div>
                          <div className="text-xs text-blue-600/60 dark:text-blue-300/60 mb-1 uppercase tracking-wider">Global Rank</div>
                          <div className="text-xl font-black text-slate-900 dark:text-white">#{selectedAnime.mal_rank || "-"}</div>
                        </div>
                        <div>
                          <div className="text-xs text-blue-600/60 dark:text-blue-300/60 mb-1 uppercase tracking-wider">Members</div>
                          <div className="text-xl font-black text-slate-900 dark:text-white flex items-center gap-2"><Users className="w-4 h-4 text-blue-600 dark:text-blue-400"/> {(selectedAnime.mal_members / 1000).toFixed(1)}K</div>
                        </div>
                      </div>
                    </div>

                    {/* AniList */}
                    <div className="flex flex-col bg-slate-50 dark:bg-slate-800/50 backdrop-blur-sm border border-slate-200 dark:border-slate-700/50 rounded-2xl p-5">
                      <div className="flex items-center gap-2 mb-3">
                        <div className="bg-slate-700 text-white text-xs font-black px-2 py-1 rounded-md">AL</div>
                        <span className="font-bold text-slate-700 dark:text-slate-300">AniList Metrics</span>
                      </div>
                      <div className="grid grid-cols-3 gap-4">
                        <div>
                          <div className="text-xs text-slate-500 dark:text-slate-400 mb-1 uppercase tracking-wider">Average Score</div>
                          <div className="text-2xl font-black text-slate-900 dark:text-white">{selectedAnime.anilist_score ? `${selectedAnime.anilist_score}%` : "-"}</div>
                        </div>
                        <div>
                          <div className="text-xs text-slate-500 dark:text-slate-400 mb-1 uppercase tracking-wider">Popularity</div>
                          <div className="text-xl font-black text-slate-900 dark:text-white flex items-center gap-2"><Flame className="w-4 h-4 text-orange-500 dark:text-orange-400" /> {selectedAnime.anilist_popularity ? (selectedAnime.anilist_popularity / 1000).toFixed(1) + 'K' : "-"}</div>
                        </div>
                        <div>
                          <div className="text-xs text-slate-500 dark:text-slate-400 mb-1 uppercase tracking-wider">Demographic</div>
                          <div className="text-lg font-black text-slate-900 dark:text-white">{selectedAnime.demographic || "-"}</div>
                        </div>
                      </div>
                    </div>

                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Search Modal */}
      {showSearchModal && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[100] flex items-center justify-center p-4 animate-fade-in" onClick={() => setShowSearchModal(false)}>
          <div className="bg-white dark:bg-slate-900/95 backdrop-blur-xl rounded-3xl border border-slate-200 dark:border-slate-700/50 shadow-2xl shadow-black/50 w-full max-w-lg relative" onClick={e => e.stopPropagation()}>
            <button 
              onClick={() => setShowSearchModal(false)}
              className="absolute top-4 right-4 p-2.5 bg-slate-100 dark:bg-slate-800/80 backdrop-blur-sm rounded-full hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white z-20 border border-slate-200 dark:border-slate-700/50 hover:border-slate-300 dark:hover:border-slate-600 transition-all"
              title="Close search"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="p-8">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-3 rounded-2xl bg-linear-to-br from-orange-100 to-red-100 dark:from-orange-500/20 dark:to-red-500/20 border border-orange-200 dark:border-orange-500/30 shadow-lg shadow-orange-500/10">
                  <Search className="w-6 h-6 text-orange-600 dark:text-orange-400" />
                </div>
                <div>
                  <h3 className="text-2xl font-black text-slate-900 dark:text-slate-100 tracking-tight">Search Anime</h3>
                  <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">Search AniList / MAL database and add to your collection</p>
                </div>
              </div>

              <form onSubmit={handleSearch} className="space-y-4">
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
                  <input
                    type="text"
                    placeholder="Search AniList / MAL..."
                    className="w-full bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50 rounded-xl pl-12 pr-4 py-3.5 text-base text-slate-900 dark:text-slate-200 focus:ring-2 focus:ring-orange-500/50 focus:border-orange-500/50 outline-none transition-all duration-300 placeholder:text-slate-400 dark:placeholder:text-slate-600"
                    value={searchQuery}
                    onChange={e => setSearchQuery(e.target.value)}
                    autoFocus
                  />
                </div>
                <button
                  type="submit"
                  disabled={searchLoading}
                  className="w-full bg-linear-to-r from-orange-500 to-red-500 hover:from-orange-400 hover:to-red-400 text-white py-3.5 rounded-xl font-bold flex items-center justify-center gap-2 disabled:opacity-50 transition-all duration-300 shadow-lg shadow-orange-500/20 hover:shadow-orange-500/40 hover:-translate-y-0.5"
                >
                  {searchLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Search className="w-5 h-5" />}
                  {searchLoading ? "Searching..." : "Search"}
                </button>
              </form>

              {/* Search Results */}
              {searchResults.length > 0 && (
                <div className="mt-6 space-y-3 max-h-96 overflow-y-auto custom-scrollbar">
                  <h4 className="text-sm font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Results</h4>
                  {searchResults.map((anime: any) => (
                    <div
                      key={anime.id}
                      onClick={() => { loadDetail(anime.id); setShowSearchModal(false); }}
                      className="flex items-center gap-4 p-3 bg-slate-50 dark:bg-slate-800/50 backdrop-blur-sm rounded-xl border border-slate-200 dark:border-slate-700/50 hover:border-orange-400/30 dark:hover:border-orange-500/30 transition-all duration-300 cursor-pointer group"
                    >
                      {anime.cover_image && (
                        <img src={anime.cover_image} alt={anime.title} className="w-16 h-24 object-cover rounded-lg shadow-md" />
                      )}
                      <div className="flex-1 min-w-0">
                        <div className="font-bold text-slate-900 dark:text-slate-100 truncate">{anime.title}</div>
                        <div className="text-xs text-slate-500 mt-1">{anime.studio || 'Unknown Studio'}</div>
                        <div className="text-xs text-slate-500">{anime.format || 'Unknown Format'}</div>
                      </div>
                      <button
                        onClick={(e) => { e.stopPropagation(); handleAddAnime(anime.id); }}
                        disabled={scraping}
                        className="p-2 bg-orange-100 dark:bg-orange-500/20 hover:bg-orange-200 dark:hover:bg-orange-500/30 text-orange-600 dark:text-orange-400 rounded-lg border border-orange-200 dark:border-orange-500/30 transition-all disabled:opacity-50"
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
