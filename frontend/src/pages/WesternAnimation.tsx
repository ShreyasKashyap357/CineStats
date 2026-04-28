import { useState, useEffect } from "react";
import { Film, Loader2, Search, Filter, Star, Calendar, Globe } from "lucide-react";
import DataCutoffLabel from "../components/DataCutoffLabel";

export default function WesternAnimation() {
  const [westernList, setWesternList] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [perPage, setPerPage] = useState(25);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedWestern, setSelectedWestern] = useState<any>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedStudio, setSelectedStudio] = useState<string[]>([]);
  const [selectedDecade, setSelectedDecade] = useState<string[]>([]);

  const studios = ["Disney", "Pixar", "DreamWorks", "Illumination", "Sony Animation", "Warner Bros", "Other"];
  const decades = ["2020s", "2010s", "2000s", "1990s", "1980s", "1970s", "1960s", "1950s", "Earlier"];

  const fetchWestern = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/movies/?limit=${perPage}&offset=${page * perPage}&animation=true`);
      const data = await res.json();
      setWesternList(data.items || []);
      setTotal(data.total || 0);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  useEffect(() => { fetchWestern(); }, [page, perPage]);
  const totalPages = Math.ceil(total / perPage);

  const loadDetail = async (id: number) => {
    setDetailLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/movies/${id}`);
      const data = await res.json();
      setSelectedWestern(data);
    } catch (e) { console.error(e); }
    setDetailLoading(false);
  };

  return (
    <div className="max-w-7xl mx-auto pb-12">
      {/* Header */}
      <header className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-3 rounded-2xl bg-linear-to-br from-cyan-100 to-blue-100 dark:from-cyan-500/20 dark:to-blue-500/20 border border-cyan-200 dark:border-cyan-500/30 shadow-lg shadow-cyan-500/10">
            <Film className="w-8 h-8 text-cyan-600 dark:text-cyan-400" />
          </div>
          <div>
            <h2 className="text-4xl font-black text-slate-900 dark:text-slate-100 tracking-tight">Western Animation</h2>
            <p className="text-slate-600 dark:text-slate-400 mt-1">Animated films from Western studios and production houses.</p>
            <DataCutoffLabel />
          </div>
        </div>
      </header>

      {/* Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        {total > 50 && (
          <div className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800/50 rounded-xl px-3 py-1.5 border border-slate-200 dark:border-slate-700/50">
            <span className="text-slate-500 text-xs font-medium uppercase tracking-wider">Per page</span>
            {[10, 15, 25, 50, 100].map(n => (
              <button key={n} onClick={() => { setPerPage(n); setPage(0); }}
                className={`px-2.5 py-1 rounded-lg text-sm font-bold transition-all duration-300 ${perPage === n ? 'bg-cyan-500 text-white shadow-md' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700/50'}`}>
                {n}
              </button>
            ))}
          </div>
        )}
        
        <div className="flex items-center gap-3 ml-auto">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`px-4 py-2.5 rounded-xl text-sm font-bold flex items-center gap-2 transition-all duration-300 ${showFilters ? 'bg-cyan-500 text-white shadow-md' : 'bg-slate-100 dark:bg-slate-800/50 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700/50 hover:bg-slate-200 dark:hover:bg-slate-700/50'}`}
          >
            <Filter className="w-4 h-4" />
            Filters
          </button>
        </div>
      </div>

      {/* Filter Panel */}
      {showFilters && (
        <div className="bg-white dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-slate-200 dark:border-slate-700/50 shadow-xl shadow-black/5 dark:shadow-black/10 mb-6 animate-in slide-in-from-top-2 duration-300">
          <div className="mb-4">
            <h4 className="text-sm font-bold text-slate-700 dark:text-slate-300 mb-3 uppercase tracking-wider">Studio</h4>
            <div className="flex flex-wrap gap-2">
              {studios.map(studio => (
                <button
                  key={studio}
                  onClick={() => setSelectedStudio(prev =>
                    prev.includes(studio) ? prev.filter(s => s !== studio) : [...prev, studio]
                  )}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${selectedStudio.includes(studio) ? 'bg-cyan-100 dark:bg-cyan-500/20 text-cyan-700 dark:text-cyan-400 border border-cyan-300 dark:border-cyan-500/30' : 'bg-slate-100 dark:bg-slate-900/50 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700/50 hover:border-slate-400 dark:hover:border-slate-600'}`}
                >
                  {studio}
                </button>
              ))}
            </div>
          </div>
          
          <div>
            <h4 className="text-sm font-bold text-slate-700 dark:text-slate-300 mb-3 uppercase tracking-wider">Decade</h4>
            <div className="flex flex-wrap gap-2">
              {decades.map(decade => (
                <button
                  key={decade}
                  onClick={() => setSelectedDecade(prev =>
                    prev.includes(decade) ? prev.filter(d => d !== decade) : [...prev, decade]
                  )}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${selectedDecade.includes(decade) ? 'bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400 border border-purple-300 dark:border-purple-500/30' : 'bg-slate-100 dark:bg-slate-900/50 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700/50 hover:border-slate-400 dark:hover:border-slate-600'}`}
                >
                  {decade}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="h-64 flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="w-10 h-10 animate-spin text-cyan-500" />
            <p className="text-slate-500 animate-pulse">Loading Western animation...</p>
          </div>
        </div>
      ) : westernList.length === 0 ? (
        <div className="h-64 flex flex-col items-center justify-center text-slate-500 gap-4">
          <div className="p-8 rounded-3xl bg-slate-100 dark:bg-slate-800/30 border border-slate-200 dark:border-slate-700/30">
            <Film className="w-16 h-16 text-slate-400 dark:text-slate-600" />
          </div>
          <p className="text-lg">No Western animation found.</p>
          <p className="text-sm text-slate-600">Try adjusting filters or check back later.</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
            {westernList.map((movie) => (
              <div 
                key={movie.id} 
                onClick={() => loadDetail(movie.id)}
                className="group bg-white dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl overflow-hidden shadow-xl border border-slate-200 dark:border-slate-700/50 hover:border-cyan-400/40 dark:hover:border-cyan-500/40 transition-all duration-300 cursor-pointer hover:-translate-y-2 relative flex flex-col"
              >
                <div className="aspect-2/3 bg-slate-100 dark:bg-slate-900/80 w-full relative overflow-hidden">
                  {movie.poster_url ? (
                    <img src={movie.poster_url} alt={movie.title_display} className="w-full h-full object-cover object-top group-hover:scale-105 transition-transform duration-500" loading="lazy" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-slate-400 dark:text-slate-600">
                      <Film className="w-8 h-8" />
                    </div>
                  )}
                  {movie.vote_average && (
                    <div className="absolute top-2 right-2 bg-black/60 backdrop-blur-md text-white px-2.5 py-1 rounded-full text-xs font-black flex items-center gap-1 border border-slate-600/50">
                      <Star className="w-3 h-3 text-amber-400 fill-current" /> {movie.vote_average.toFixed(1)}
                    </div>
                  )}
                </div>
                <div className="p-3 flex-1 flex flex-col bg-slate-50 dark:bg-slate-800/30">
                  <h3 className="font-bold text-slate-900 dark:text-slate-100 text-sm line-clamp-2 mb-2 group-hover:text-cyan-500 dark:group-hover:text-cyan-400 transition-colors">{movie.title_display}</h3>
                  <div className="mt-auto flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                    <Calendar className="w-3 h-3" />
                    {movie.release_date?.split('-')[0] || "Unknown"}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-8">
              <button
                onClick={() => setPage(p => Math.max(0, p - 1))}
                disabled={page === 0}
                className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700/50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <span className="text-slate-600 dark:text-slate-400 text-sm">
                Page {page + 1} of {totalPages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
                disabled={page === totalPages - 1}
                className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/50 text-slate-600 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700/50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}

      {/* Detail Modal */}
      {selectedWestern && (
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-300" 
          onClick={() => setSelectedWestern(null)}
        >
          <div 
            className="bg-white dark:bg-slate-900 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-slate-200 dark:border-slate-700/50 shadow-2xl"
            onClick={e => e.stopPropagation()}
          >
            {detailLoading ? (
              <div className="h-64 flex items-center justify-center">
                <Loader2 className="w-8 h-8 animate-spin text-cyan-500" />
              </div>
            ) : (
              <div className="p-6">
                <div className="flex gap-6 mb-6">
                  {selectedWestern.poster_url && (
                    <img src={selectedWestern.poster_url} alt={selectedWestern.title_display} className="w-32 h-48 object-cover rounded-xl" />
                  )}
                  <div className="flex-1">
                    <h3 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-2">{selectedWestern.title_display}</h3>
                    {selectedWestern.release_date && (
                      <p className="text-slate-500 dark:text-slate-400 text-sm mb-2">{selectedWestern.release_date}</p>
                    )}
                    {selectedWestern.overview && (
                      <p className="text-slate-600 dark:text-slate-300 text-sm line-clamp-4">{selectedWestern.overview}</p>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => setSelectedWestern(null)}
                  className="w-full py-3 rounded-xl bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300 font-bold hover:bg-slate-300 dark:hover:bg-slate-700 transition-colors"
                >
                  Close
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
