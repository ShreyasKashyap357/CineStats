import { useState, useEffect } from "react";
import { Tv, Loader2, Filter, Star, Calendar, Shield, Baby } from "lucide-react";
import DataCutoffLabel from "../components/DataCutoffLabel";

export default function Cartoons() {
  const [cartoonList, setCartoonList] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [perPage, setPerPage] = useState(25);
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(true);
  const [selectedCartoon, setSelectedCartoon] = useState<any>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedAgeRating, setSelectedAgeRating] = useState<string[]>([]);
  const [selectedStudio, setSelectedStudio] = useState<string[]>([]);

  const ageRatings = ["TV-Y", "TV-Y7", "TV-G", "TV-PG", "TV-14", "All Ages", "Kids", "Family"];
  const studios = ["Cartoon Network", "Nickelodeon", "Disney Channel", "PBS Kids", "Netflix", "Other"];

  const fetchCartoons = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/tv/?limit=${perPage}&offset=${page * perPage}&cartoon=true`);
      const data = await res.json();
      setCartoonList(data.items || []);
      setTotal(data.total || 0);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  useEffect(() => { fetchCartoons(); }, [page, perPage]);
  const totalPages = Math.ceil(total / perPage);

  const loadDetail = async (id: number) => {
    setDetailLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/tv/${id}`);
      const data = await res.json();
      setSelectedCartoon(data);
    } catch (e) { console.error(e); }
    setDetailLoading(false);
  };

  return (
    <div className="max-w-7xl mx-auto pb-12">
      {/* Header */}
      <header className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-3 rounded-2xl bg-linear-to-br from-pink-100 to-rose-100 dark:from-pink-500/20 dark:to-rose-500/20 border border-pink-200 dark:border-pink-500/30 shadow-lg shadow-pink-500/10">
            <Tv className="w-8 h-8 text-pink-600 dark:text-pink-400" />
          </div>
          <div>
            <h2 className="text-4xl font-black text-slate-900 dark:text-slate-100 tracking-tight">Cartoons</h2>
            <p className="text-slate-600 dark:text-slate-400 mt-1">Children's animated series and family-friendly cartoons.</p>
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
                className={`px-2.5 py-1 rounded-lg text-sm font-bold transition-all duration-300 ${perPage === n ? 'bg-pink-500 text-white shadow-md' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700/50'}`}>
                {n}
              </button>
            ))}
          </div>
        )}
        
        <div className="flex items-center gap-3 ml-auto">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`px-4 py-2.5 rounded-xl text-sm font-bold flex items-center gap-2 transition-all duration-300 ${showFilters ? 'bg-pink-500 text-white shadow-md' : 'bg-slate-100 dark:bg-slate-800/50 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700/50 hover:bg-slate-200 dark:hover:bg-slate-700/50'}`}
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
            <h4 className="text-sm font-bold text-slate-700 dark:text-slate-300 mb-3 uppercase tracking-wider flex items-center gap-2">
              <Shield className="w-4 h-4" />
              Age Rating
            </h4>
            <div className="flex flex-wrap gap-2">
              {ageRatings.map(rating => (
                <button
                  key={rating}
                  onClick={() => setSelectedAgeRating(prev =>
                    prev.includes(rating) ? prev.filter(r => r !== rating) : [...prev, rating]
                  )}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${selectedAgeRating.includes(rating) ? 'bg-pink-100 dark:bg-pink-500/20 text-pink-700 dark:text-pink-400 border border-pink-300 dark:border-pink-500/30' : 'bg-slate-100 dark:bg-slate-900/50 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700/50 hover:border-slate-400 dark:hover:border-slate-600'}`}
                >
                  {rating}
                </button>
              ))}
            </div>
          </div>
          
          <div>
            <h4 className="text-sm font-bold text-slate-700 dark:text-slate-300 mb-3 uppercase tracking-wider">Studio/Network</h4>
            <div className="flex flex-wrap gap-2">
              {studios.map(studio => (
                <button
                  key={studio}
                  onClick={() => setSelectedStudio(prev =>
                    prev.includes(studio) ? prev.filter(s => s !== studio) : [...prev, studio]
                  )}
                  className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${selectedStudio.includes(studio) ? 'bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400 border border-purple-300 dark:border-purple-500/30' : 'bg-slate-100 dark:bg-slate-900/50 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700/50 hover:border-slate-400 dark:hover:border-slate-600'}`}
                >
                  {studio}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {loading ? (
        <div className="h-64 flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="w-10 h-10 animate-spin text-pink-500" />
            <p className="text-slate-500 animate-pulse">Loading cartoons...</p>
          </div>
        </div>
      ) : cartoonList.length === 0 ? (
        <div className="h-64 flex flex-col items-center justify-center text-slate-500 gap-4">
          <div className="p-8 rounded-3xl bg-slate-100 dark:bg-slate-800/30 border border-slate-200 dark:border-slate-700/30">
            <Baby className="w-16 h-16 text-slate-400 dark:text-slate-600" />
          </div>
          <p className="text-lg">No cartoons found.</p>
          <p className="text-sm text-slate-600">Try adjusting filters or check back later.</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-5 gap-6">
            {cartoonList.map((series) => (
              <div 
                key={series.id} 
                onClick={() => loadDetail(series.id)}
                className="group bg-white dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl overflow-hidden shadow-xl border border-slate-200 dark:border-slate-700/50 hover:border-pink-400/40 dark:hover:border-pink-500/40 transition-all duration-300 cursor-pointer hover:-translate-y-2 relative flex flex-col"
              >
                <div className="aspect-2/3 bg-slate-100 dark:bg-slate-900/80 w-full relative overflow-hidden">
                  {series.poster_url ? (
                    <img src={series.poster_url} alt={series.name} className="w-full h-full object-cover object-top group-hover:scale-105 transition-transform duration-500" loading="lazy" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-slate-400 dark:text-slate-600">
                      <Tv className="w-8 h-8" />
                    </div>
                  )}
                  {series.vote_average && (
                    <div className="absolute top-2 right-2 bg-black/60 backdrop-blur-md text-white px-2.5 py-1 rounded-full text-xs font-black flex items-center gap-1 border border-slate-600/50">
                      <Star className="w-3 h-3 text-amber-400 fill-current" /> {series.vote_average.toFixed(1)}
                    </div>
                  )}
                </div>
                <div className="p-3 flex-1 flex flex-col bg-slate-50 dark:bg-slate-800/30">
                  <h3 className="font-bold text-slate-900 dark:text-slate-100 text-sm line-clamp-2 mb-2 group-hover:text-pink-500 dark:group-hover:text-pink-400 transition-colors">{series.name}</h3>
                  <div className="mt-auto flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
                    <Calendar className="w-3 h-3" />
                    {series.premiere?.split('-')[0] || series.first_aired?.split('-')[0] || "Unknown"}
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
      {selectedCartoon && (
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-300" 
          onClick={() => setSelectedCartoon(null)}
        >
          <div 
            className="bg-white dark:bg-slate-900 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-slate-200 dark:border-slate-700/50 shadow-2xl"
            onClick={e => e.stopPropagation()}
          >
            {detailLoading ? (
              <div className="h-64 flex items-center justify-center">
                <Loader2 className="w-8 h-8 animate-spin text-pink-500" />
              </div>
            ) : (
              <div className="p-6">
                <div className="flex gap-6 mb-6">
                  {selectedCartoon.poster_url && (
                    <img src={selectedCartoon.poster_url} alt={selectedCartoon.name} className="w-32 h-48 object-cover rounded-xl" />
                  )}
                  <div className="flex-1">
                    <h3 className="text-2xl font-bold text-slate-900 dark:text-slate-100 mb-2">{selectedCartoon.name}</h3>
                    {selectedCartoon.premiere && (
                      <p className="text-slate-500 dark:text-slate-400 text-sm mb-2">{selectedCartoon.premiere}</p>
                    )}
                    {selectedCartoon.overview && (
                      <p className="text-slate-600 dark:text-slate-300 text-sm line-clamp-4">{selectedCartoon.overview}</p>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => setSelectedCartoon(null)}
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
