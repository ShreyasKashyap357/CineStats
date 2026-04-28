import { useState, useEffect } from "react";
import { FolderHeart, Loader2, Link as LinkIcon, Film, Star, X, Image as ImageIcon, Calendar } from "lucide-react";

export default function Franchises() {
  const [category, setCategory] = useState("franchise");
  const [franchises, setFranchises] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  
  const [selectedFranchise, setSelectedFranchise] = useState<any>(null);
  const [movies, setMovies] = useState<any[]>([]);
  const [loadingMovies, setLoadingMovies] = useState(false);
  const [moviePage, setMoviePage] = useState(0);
  const [moviesPerPage, setMoviesPerPage] = useState(10);
  const [selectedMovie, setSelectedMovie] = useState<any>(null);

  const loadFranchises = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/franchises/list/${category}`);
      const data = await res.json();
      setFranchises(data);
    } catch (e) {
      console.error(e);
      setFranchises([]);
    }
    setLoading(false);
  };

  // Auto-load when category changes
  useEffect(() => {
    setFranchises([]);
    setSelectedFranchise(null);
    setMovies([]);
    loadFranchises();
  }, [category]);

  const loadMovies = async (f: any) => {
    setSelectedFranchise(f);
    setMoviePage(0);
    setLoadingMovies(true);
    try {
      const res = await fetch(`http://localhost:8000/api/franchises/detail?url=${encodeURIComponent(f.url)}`);
      const data = await res.json();
      setMovies(data.movies || []);
    } catch (e) {
      console.error(e);
    }
    setLoadingMovies(false);
  };

  return (
    <div className="max-w-7xl mx-auto pb-12">
      {/* Modern Header */}
      <header className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-3 rounded-2xl bg-linear-to-br from-pink-100 to-rose-100 dark:from-pink-500/20 dark:to-rose-500/20 border border-pink-200 dark:border-pink-500/30 shadow-lg shadow-pink-500/10">
            <FolderHeart className="w-8 h-8 text-pink-600 dark:text-pink-400" />
          </div>
          <div>
            <h2 className="text-4xl font-black text-slate-900 dark:text-slate-100 tracking-tight">Franchise Explorer</h2>
            <p className="text-slate-600 dark:text-slate-400 mt-1">Discover global Brands, Franchises, and Genres from Box Office Mojo.</p>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Left Panel: Master List */}
        <div>
          <div className="flex gap-2 mb-6">
            {["franchise", "brand", "genre"].map(c => (
              <button 
                key={c}
                onClick={() => setCategory(c)}
                className={`px-4 py-2.5 rounded-xl text-sm font-bold capitalize transition-all duration-300 ${category === c ? 'bg-linear-to-r from-pink-500 to-rose-500 text-white shadow-lg shadow-pink-500/25' : 'bg-slate-100 dark:bg-slate-800/50 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700/50 border border-slate-200 dark:border-slate-700/50'}`}
              >
                {c}s
              </button>
            ))}
            <button 
              onClick={loadFranchises}
              disabled={loading}
              className="ml-auto px-4 py-2.5 bg-linear-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-xl text-sm font-bold flex items-center gap-2 transition-all shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 hover:-translate-y-0.5 disabled:opacity-50"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Fetch List"}
            </button>
          </div>

          <div className="bg-white dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-200 dark:border-slate-700/50 shadow-xl shadow-black/5 dark:shadow-black/10 overflow-hidden max-h-175">
            {franchises.length > 0 ? (
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-100 dark:bg-slate-900/80 sticky top-0 z-10">
                  <tr>
                    <th className="p-4 font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider text-xs">Name</th>
                    <th className="p-4 font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider text-xs">Releases</th>
                    <th className="p-4 text-right font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider text-xs">Total Gross</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 dark:divide-slate-700/30">
                  {franchises.map((f, i) => (
                    <tr 
                      key={i} 
                      onClick={() => loadMovies(f)}
                      className={`cursor-pointer transition-all duration-300 ${selectedFranchise?.url === f.url ? 'bg-pink-100 dark:bg-pink-500/10 border-l-4 border-l-pink-500' : 'hover:bg-slate-100 dark:hover:bg-slate-700/30'}`}
                    >
                      <td className="p-4 font-bold text-slate-900 dark:text-slate-100">{f.name}</td>
                      <td className="p-4 text-slate-600 dark:text-slate-400">{f.releases}</td>
                      <td className="p-4 text-right font-mono text-emerald-600 dark:text-emerald-400 font-bold">{f.total_gross}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="h-64 flex flex-col items-center justify-center text-slate-500 gap-4">
                <div className="p-6 rounded-3xl bg-slate-100 dark:bg-slate-800/30 border border-slate-200 dark:border-slate-700/30">
                  <FolderHeart className="w-12 h-12 text-slate-400 dark:text-slate-600" />
                </div>
                <p>Click "Fetch List" to load {category}s.</p>
              </div>
            )}
          </div>
        </div>

        {/* Right Panel: Franchise Detail */}
        <div>
          <div className="bg-white dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-200 dark:border-slate-700/50 shadow-xl shadow-black/5 dark:shadow-black/10 h-full flex flex-col overflow-hidden">
            {selectedFranchise ? (
              <>
                <div className="p-6 bg-linear-to-br from-pink-100 to-rose-50 dark:from-pink-500/20 dark:to-rose-500/10 border-b border-slate-200 dark:border-slate-700/50">
                  <h3 className="text-2xl font-black text-slate-900 dark:text-slate-100 mb-2 tracking-tight">{selectedFranchise.name}</h3>
                  <div className="flex flex-wrap gap-4 text-sm text-slate-600 dark:text-slate-400">
                    <span className="bg-slate-100 dark:bg-slate-800/50 px-3 py-1 rounded-full border border-slate-200 dark:border-slate-700/30">{selectedFranchise.releases} Movies</span>
                    <span className="bg-slate-100 dark:bg-slate-800/50 px-3 py-1 rounded-full border border-slate-200 dark:border-slate-700/30 text-emerald-600 dark:text-emerald-400 font-bold">Total: {selectedFranchise.total_gross}</span>
                    <span className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800/50 px-3 py-1 rounded-full border border-slate-200 dark:border-slate-700/30"><Star className="w-4 h-4 text-amber-400 fill-current"/> Top: {selectedFranchise.top_release}</span>
                  </div>
                </div>

                <div className="flex-1 overflow-y-auto custom-scrollbar p-6">
                  {loadingMovies ? (
                    <div className="h-full flex items-center justify-center">
                      <div className="flex flex-col items-center gap-4">
                        <Loader2 className="w-10 h-10 animate-spin text-pink-500" />
                        <p className="text-slate-500 animate-pulse">Loading movies...</p>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="space-y-3">
                        {movies.slice(moviePage * moviesPerPage, (moviePage + 1) * moviesPerPage).map((m, i) => (
                          <div 
                            key={i} 
                            onClick={() => setSelectedMovie(m)}
                            className="flex justify-between items-center p-4 bg-slate-50 dark:bg-slate-900/50 backdrop-blur-sm rounded-xl border border-slate-200 dark:border-slate-700/50 hover:border-pink-400/30 dark:hover:border-pink-500/30 transition-all duration-300 group cursor-pointer"
                          >
                            <div className="flex items-center gap-3">
                              <Film className="w-5 h-5 text-slate-400 dark:text-slate-500 group-hover:text-pink-500 dark:group-hover:text-pink-400 transition-colors" />
                              <div>
                                <div className="font-bold text-slate-900 dark:text-slate-100">{m.title}</div>
                                <div className="text-xs text-slate-500">{m.release_date || 'Unknown Year'}</div>
                              </div>
                            </div>
                            <div className="font-mono text-emerald-600 dark:text-emerald-400 font-bold">{m.gross}</div>
                          </div>
                        ))}
                      </div>
                      
                      {/* Pagination Controls */}
                      {movies.length > moviesPerPage && (
                        <div className="mt-6 flex items-center justify-between pt-4 border-t border-slate-200 dark:border-slate-700/30">
                          <div className="flex items-center gap-2">
                            <span className="text-sm text-slate-600 dark:text-slate-400">Show:</span>
                            {[5, 10, 15, 20, 25].map(size => (
                              <button
                                key={size}
                                onClick={() => { setMoviesPerPage(size); setMoviePage(0); }}
                                className={`px-3 py-1 rounded-lg text-sm font-medium transition-all ${moviesPerPage === size ? 'bg-pink-100 dark:bg-pink-500/20 text-pink-700 dark:text-pink-400 border border-pink-300 dark:border-pink-500/30' : 'bg-slate-100 dark:bg-slate-800/50 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-200 dark:hover:bg-slate-700/50 border border-slate-200 dark:border-slate-700/30'}`}
                              >
                                {size}
                              </button>
                            ))}
                          </div>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => setMoviePage(Math.max(0, moviePage - 1))}
                              disabled={moviePage === 0}
                              className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800/50 hover:bg-slate-200 dark:hover:bg-slate-700/50 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 border border-slate-200 dark:border-slate-700/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                            >
                              ←
                            </button>
                            <span className="text-sm text-slate-600 dark:text-slate-400">
                              {moviePage + 1} / {Math.ceil(movies.length / moviesPerPage)}
                            </span>
                            <button
                              onClick={() => setMoviePage(Math.min(Math.ceil(movies.length / moviesPerPage) - 1, moviePage + 1))}
                              disabled={moviePage >= Math.ceil(movies.length / moviesPerPage) - 1}
                              className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800/50 hover:bg-slate-200 dark:hover:bg-slate-700/50 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 border border-slate-200 dark:border-slate-700/30 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                            >
                              →
                            </button>
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </>
            ) : (
              <div className="h-full flex flex-col items-center justify-center text-slate-500 gap-4 min-h-125">
                <div className="p-8 rounded-3xl bg-slate-100 dark:bg-slate-800/30 border border-slate-200 dark:border-slate-700/30">
                  <LinkIcon className="w-16 h-16 text-slate-400 dark:text-slate-600" />
                </div>
                <p className="text-lg">Select a franchise to view its cinematic universe.</p>
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Movie Detail Modal */}
      {selectedMovie && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-100 flex items-center justify-center p-4 animate-fade-in" onClick={() => setSelectedMovie(null)}>
          <div className="bg-white dark:bg-slate-900/95 backdrop-blur-xl rounded-3xl border border-slate-200 dark:border-slate-700/50 shadow-2xl shadow-black/50 w-full max-w-2xl relative" onClick={e => e.stopPropagation()}>
            <button 
              onClick={() => setSelectedMovie(null)}
              className="absolute top-4 right-4 p-2.5 bg-slate-100 dark:bg-slate-800/80 backdrop-blur-sm rounded-full hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white z-20 border border-slate-200 dark:border-slate-700/50 hover:border-slate-300 dark:hover:border-slate-600 transition-all"
              title="Close movie details"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="p-8">
              <h3 className="text-3xl font-black text-slate-900 dark:text-slate-100 mb-2 tracking-tight">{selectedMovie.title}</h3>
              <div className="flex items-center gap-4 text-sm text-slate-600 dark:text-slate-400 mb-6">
                {selectedMovie.release_date && (
                  <span className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800/50 px-2.5 py-1 rounded-full border border-slate-200 dark:border-slate-700/30">
                    <Calendar className="w-4 h-4" /> {selectedMovie.release_date}
                  </span>
                )}
                <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-slate-800/50 px-2.5 py-1 rounded-full border border-emerald-200 dark:border-slate-700/30 font-bold">
                  {selectedMovie.gross}
                </span>
              </div>

              <div className="bg-slate-50 dark:bg-slate-800/30 rounded-2xl border border-slate-200 dark:border-slate-700/30 p-6 text-center">
                <p className="text-slate-600 dark:text-slate-400 text-sm">This movie is part of the {selectedFranchise?.name} franchise.</p>
                <p className="text-slate-500 dark:text-slate-500 text-xs mt-2">For full details, search for this movie in the Movies section.</p>
              </div>

              <button
                onClick={() => { window.location.href = `/search?q=${encodeURIComponent(selectedMovie.title)}`; setSelectedMovie(null); }}
                className="mt-6 w-full bg-linear-to-r from-pink-600 to-rose-600 hover:from-pink-500 hover:to-rose-500 text-white py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-all shadow-lg shadow-pink-500/20 hover:shadow-pink-500/40 hover:-translate-y-0.5"
              >
                Search in Movies
                <Film className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
