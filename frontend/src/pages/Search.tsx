import { useState, useEffect } from "react";
import { Search as SearchIcon, Loader2, Database, Film, Tv, Flame, X, Plus } from "lucide-react";
import { useLocation } from "react-router-dom";

export default function Search() {
  const location = useLocation();
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [searched, setSearched] = useState(false);
  
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [tracking, setTracking] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const q = params.get("q");
    if (q) {
      setQuery(q);
      executeSearch(q);
    }
  }, [location.search]);

  const executeSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    setSearched(true);
    try {
      const res = await fetch(`http://localhost:8000/api/search?query=${encodeURIComponent(searchQuery)}`);
      const data = await res.json();
      setResults(data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  const handleSearch = () => {
    executeSearch(query);
  };

  const handleTrack = async (item: any) => {
    setTracking(true);
    try {
      let endpoint = "";
      let payload = {};

      if (item.source.startsWith("tmdb_movie")) {
        // Deep Scrape TMDB Movie (Needs a new endpoint or fallback to BOM/Sacnilk search)
        endpoint = "http://localhost:8000/api/scraper/search-and-scrape";
        payload = { module: item.title }; // We pass title to deep scrape
      } else if (item.source.startsWith("tmdb_tv")) {
        endpoint = `http://localhost:8000/api/tv/scrape?query=${encodeURIComponent(item.title)}`;
      } else if (item.source === "jikan_anime") {
        endpoint = `http://localhost:8000/api/anime/scrape?query=${encodeURIComponent(item.title)}`;
      }

      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: Object.keys(payload).length ? JSON.stringify(payload) : null
      });

      if (res.ok) {
        alert(`${item.title} is now tracking! Background job started.`);
        setSelectedItem(null);
      } else {
        alert(`Failed to track ${item.title}`);
      }
    } catch (e) {
      console.error(e);
    }
    setTracking(false);
  };

  const renderIcon = (source: string) => {
    if (source.includes("movie")) return <Film className="w-4 h-4 text-blue-400" />;
    if (source.includes("tv")) return <Tv className="w-4 h-4 text-purple-400" />;
    if (source.includes("anime")) return <Flame className="w-4 h-4 text-orange-400" />;
    return <Database className="w-4 h-4 text-green-400" />;
  };

  const localResults = results.filter(r => r.source.startsWith("local"));
  const remoteResults = results.filter(r => !r.source.startsWith("local"));

  return (
    <div className="max-w-6xl mx-auto pb-12">
      {/* Modern Header */}
      <header className="text-center mb-12">
        <div className="flex items-center justify-center gap-3 mb-2">
          <div className="p-3 rounded-2xl bg-linear-to-br from-blue-100 to-cyan-100 dark:from-blue-500/20 dark:to-cyan-500/20 border border-blue-200 dark:border-blue-500/30 shadow-lg shadow-blue-500/10">
            <SearchIcon className="w-8 h-8 text-blue-600 dark:text-blue-400" />
          </div>
        </div>
        <h2 className="text-4xl font-black text-slate-900 dark:text-slate-100 tracking-tight mb-4">Global Search Engine</h2>
        <p className="text-slate-600 dark:text-slate-400">Search TMDB, AniList, and your local database all at once.</p>
      </header>

      {/* Modern Search Bar */}
      <div className="bg-white dark:bg-slate-800/50 backdrop-blur-sm p-2 rounded-2xl shadow-xl shadow-black/10 dark:shadow-black/20 border border-slate-200 dark:border-slate-700/50 flex items-center mb-8">
        <SearchIcon className="w-6 h-6 text-slate-400 ml-4 mr-2" />
        <input 
          type="text" 
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSearch()}
          placeholder="Search for movies, TV series, or anime..."
          className="bg-transparent border-none outline-none flex-1 text-xl text-slate-900 dark:text-slate-100 placeholder-slate-400 dark:placeholder-slate-500"
        />
        <button 
          onClick={handleSearch}
          className="bg-linear-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white px-8 py-3 rounded-xl font-bold transition-all shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 disabled:opacity-50 hover:-translate-y-0.5"
          disabled={loading}
        >
          {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : "Search"}
        </button>
      </div>

      {searched && (
        <div className="space-y-12">
          
          {/* External Ingestion Results */}
          <div>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-1 h-6 bg-linear-to-b from-blue-500 to-cyan-500 rounded-full" />
              <h3 className="text-xl font-black text-slate-900 dark:text-slate-100">Web Results</h3>
              <span className="text-xs text-slate-600 dark:text-slate-500 bg-slate-100 dark:bg-slate-800/50 px-3 py-1 rounded-full border border-slate-200 dark:border-slate-700/30">Click to Add</span>
            </div>
            {remoteResults.length > 0 ? (
              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
                {remoteResults.map((r, i) => (
                  <div 
                    key={i} 
                    onClick={() => setSelectedItem(r)}
                    className="group bg-white dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl overflow-hidden shadow-lg border border-slate-200 dark:border-slate-700/50 hover:border-blue-400/40 dark:hover:border-blue-500/40 transition-all duration-300 cursor-pointer hover:-translate-y-1"
                  >
                    <div className="aspect-2/3 bg-slate-100 dark:bg-slate-900/50 w-full relative overflow-hidden">
                      {r.poster ? (
                        <img src={r.poster} alt={r.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-slate-400 dark:text-slate-600"><Film className="w-12 h-12" /></div>
                      )}
                      <div className="absolute top-2 left-2 bg-black/60 backdrop-blur-sm px-2.5 py-1 rounded-lg text-xs font-black flex items-center gap-1.5 border border-slate-600/50">
                        {renderIcon(r.source)}
                        {r.source.replace("tmdb_", "").replace("jikan_", "").toUpperCase()}
                      </div>
                    </div>
                    <div className="p-4 bg-slate-50 dark:bg-slate-800/30">
                      <h4 className="font-bold text-sm text-slate-900 dark:text-slate-100 line-clamp-1 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">{r.title}</h4>
                      <p className="text-xs text-slate-500 mt-1">{r.year}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-slate-500 text-center py-8 bg-slate-100 dark:bg-slate-800/30 rounded-2xl border border-slate-200 dark:border-slate-700/30">No external results found.</div>
            )}
          </div>

          {/* Local DB Results */}
          <div>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-1 h-6 bg-linear-to-b from-emerald-500 to-teal-500 rounded-full" />
              <h3 className="text-xl font-black text-slate-900 dark:text-slate-100">Tracked in CineStats</h3>
            </div>
            {localResults.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {localResults.map((r, i) => (
                  <div key={i} className="group bg-white dark:bg-slate-800/50 backdrop-blur-sm border border-slate-200 dark:border-slate-700/50 rounded-xl p-4 flex justify-between items-center hover:border-emerald-400/30 dark:hover:border-emerald-500/30 transition-all duration-300 cursor-pointer hover:-translate-y-0.5">
                    <div className="flex items-center gap-3">
                      {renderIcon(r.source)}
                      <div>
                        <h4 className="font-bold text-sm text-slate-900 dark:text-slate-100">{r.title}</h4>
                        <p className="text-xs text-slate-500">{r.year}</p>
                      </div>
                    </div>
                    {r.gross && <div className="text-emerald-600 dark:text-emerald-400 font-bold text-sm">{r.gross}</div>}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-slate-500 text-center py-8 bg-slate-100 dark:bg-slate-800/30 rounded-2xl border border-slate-200 dark:border-slate-700/30">Not tracking any items matching this query.</div>
            )}
          </div>

        </div>
      )}

      {/* Modern Detail Modal */}
      {selectedItem && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fade-in">
          <div className="bg-white dark:bg-slate-900/95 backdrop-blur-xl rounded-3xl border border-slate-200 dark:border-slate-700/50 shadow-2xl shadow-black/50 w-full max-w-3xl flex flex-col md:flex-row overflow-hidden relative">
            {/* Ambient Glow */}
            <div className="absolute -top-32 -right-32 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
            
            <button 
              onClick={() => setSelectedItem(null)} title="Close modal"
              className="absolute top-4 right-4 p-2.5 bg-slate-100 dark:bg-slate-800/80 backdrop-blur-sm rounded-full hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white z-20 border border-slate-200 dark:border-slate-700/50 hover:border-slate-300 dark:hover:border-slate-600 transition-all"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="w-full md:w-1/3 bg-slate-100 dark:bg-slate-800/30 relative hidden md:block overflow-hidden">
              {selectedItem.poster ? (
                <img src={selectedItem.poster} alt={selectedItem.title} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-slate-400 dark:text-slate-700"><Film className="w-24 h-24 opacity-50" /></div>
              )}
              {/* Poster Gradient Overlay */}
              <div className="absolute inset-0 bg-linear-to-t from-slate-900/60 via-transparent to-transparent dark:from-slate-900/60" />
            </div>

            <div className="w-full md:w-2/3 p-8 flex flex-col relative z-10">
              <div className="flex items-center gap-2 mb-2">
                {renderIcon(selectedItem.source)}
                <span className="text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider bg-slate-100 dark:bg-slate-800/50 px-2.5 py-1 rounded-full border border-slate-200 dark:border-slate-700/30">
                  {selectedItem.source.replace("tmdb_", "").replace("jikan_", "")}
                </span>
              </div>
              
              <h2 className="text-3xl font-black text-slate-900 dark:text-slate-100 mb-2 tracking-tight">{selectedItem.title}</h2>
              <p className="text-blue-600 dark:text-blue-400 font-bold mb-6">{selectedItem.year}</p>
              
              <p className="text-slate-600 dark:text-slate-300 text-sm leading-relaxed mb-8 line-clamp-6">
                {selectedItem.overview || "No synopsis available."}
              </p>

              <div className="mt-auto flex gap-4">
                <button 
                  onClick={() => handleTrack(selectedItem)}
                  disabled={tracking}
                  className="flex-1 bg-linear-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-all shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 disabled:opacity-50 hover:-translate-y-0.5"
                >
                  {tracking ? <Loader2 className="w-5 h-5 animate-spin" /> : <Plus className="w-5 h-5" />}
                  {tracking ? "Ingesting..." : "Track in CineStats"}
                </button>
              </div>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}
