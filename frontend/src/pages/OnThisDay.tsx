import { useState, useEffect } from "react";
import { Calendar, Clock, Loader2, Download, Filter, ChevronLeft, ChevronRight, Film, Tv, Star, Zap } from "lucide-react";

export default function OnThisDay() {
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [isDateRange, setIsDateRange] = useState(false);
  const [startDate, setStartDate] = useState(new Date());
  const [endDate, setEndDate] = useState(new Date());
  const [mode, setMode] = useState<"released" | "airing">("released");
  const [contentTypeFilter, setContentTypeFilter] = useState<string[]>(["movies", "tv", "anime"]);
  const [results, setResults] = useState<any>({});
  const [loading, setLoading] = useState(false);

  const contentTypes = [
    { id: "movies", name: "Movies", icon: Film },
    { id: "tv", name: "TV Series", icon: Tv },
    { id: "anime", name: "Anime", icon: Star },
  ];

  const formatDate = (date: Date) => {
    return date.toISOString().split('T')[0];
  };

  const fetchOnThisDay = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (isDateRange) {
        params.append("start_date", formatDate(startDate));
        params.append("end_date", formatDate(endDate));
        params.append("mode", mode);
      } else {
        params.append("date", formatDate(selectedDate));
      }
      contentTypeFilter.forEach(type => params.append("content_type", type));

      const res = await fetch(`http://localhost:8000/api/on-this-day?${params.toString()}`);
      const data = await res.json();
      setResults(data);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchOnThisDay();
  }, [selectedDate, isDateRange, startDate, endDate, mode, contentTypeFilter]);

  const toggleContentType = (type: string) => {
    setContentTypeFilter(prev =>
      prev.includes(type) ? prev.filter(t => t !== type) : [...prev, type]
    );
  };

  const moveDate = (days: number) => {
    const newDate = new Date(selectedDate);
    newDate.setDate(newDate.getDate() + days);
    setSelectedDate(newDate);
  };

  return (
    <div className="max-w-7xl mx-auto pb-12">
      {/* Header */}
      <header className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-3 rounded-2xl bg-linear-to-br from-purple-100 to-pink-100 dark:from-purple-500/20 dark:to-pink-500/20 border border-purple-200 dark:border-purple-500/30 shadow-lg shadow-purple-500/10">
            <Calendar className="w-8 h-8 text-purple-600 dark:text-purple-400" />
          </div>
          <div>
            <h2 className="text-4xl font-black text-slate-900 dark:text-slate-100 tracking-tight">On This Day</h2>
            <p className="text-slate-600 dark:text-slate-400 mt-1">Explore content released on specific dates throughout history.</p>
          </div>
        </div>
      </header>

      {/* Controls */}
      <div className="bg-white dark:bg-slate-800/50 backdrop-blur-sm p-6 rounded-2xl border border-slate-200 dark:border-slate-700/50 shadow-xl shadow-black/5 dark:shadow-black/10 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Date Picker */}
          <div>
            <label className="text-xs text-slate-600 dark:text-slate-400 mb-2 block font-semibold">Date Mode</label>
            <div className="flex gap-2">
              <button
                onClick={() => setIsDateRange(false)}
                className={`flex-1 p-3 rounded-xl font-bold text-sm transition-all ${!isDateRange ? 'bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400 border border-purple-300 dark:border-purple-500/30' : 'bg-slate-100 dark:bg-slate-900/50 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700/30'}`}
              >
                Single Date
              </button>
              <button
                onClick={() => setIsDateRange(true)}
                className={`flex-1 p-3 rounded-xl font-bold text-sm transition-all ${isDateRange ? 'bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400 border border-purple-300 dark:border-purple-500/30' : 'bg-slate-100 dark:bg-slate-900/50 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700/30'}`}
              >
                Date Range
              </button>
            </div>
          </div>

          {/* Single Date */}
          {!isDateRange && (
            <div>
              <label className="text-xs text-slate-600 dark:text-slate-400 mb-2 block font-semibold">Select Date</label>
              <div className="flex items-center gap-2">
                <button onClick={() => moveDate(-1)} className="p-2 rounded-lg bg-slate-100 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700/30 hover:bg-slate-200 dark:hover:bg-slate-700/30 text-slate-500 dark:text-slate-400">
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <input
                  type="date"
                  value={formatDate(selectedDate)}
                  onChange={e => setSelectedDate(new Date(e.target.value))}
                  className="flex-1 bg-slate-100 dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-xl p-3 text-sm text-slate-800 dark:text-slate-200"
                />
                <button onClick={() => moveDate(1)} className="p-2 rounded-lg bg-slate-100 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700/30 hover:bg-slate-200 dark:hover:bg-slate-700/30 text-slate-500 dark:text-slate-400">
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}

          {/* Date Range */}
          {isDateRange && (
            <>
              <div>
                <label className="text-xs text-slate-600 dark:text-slate-400 mb-2 block font-semibold">Start Date</label>
                <input
                  type="date"
                  value={formatDate(startDate)}
                  onChange={e => setStartDate(new Date(e.target.value))}
                  className="w-full bg-slate-100 dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-xl p-3 text-sm text-slate-800 dark:text-slate-200"
                />
              </div>
              <div>
                <label className="text-xs text-slate-600 dark:text-slate-400 mb-2 block font-semibold">End Date</label>
                <input
                  type="date"
                  value={formatDate(endDate)}
                  onChange={e => setEndDate(new Date(e.target.value))}
                  className="w-full bg-slate-100 dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-xl p-3 text-sm text-slate-800 dark:text-slate-200"
                />
              </div>
            </>
          )}

          {/* Mode Toggle (Date Range Only) */}
          {isDateRange && (
            <div>
              <label className="text-xs text-slate-600 dark:text-slate-400 mb-2 block font-semibold">Mode</label>
              <div className="flex gap-2">
                <button
                  onClick={() => setMode("released")}
                  className={`flex-1 p-3 rounded-xl font-bold text-sm transition-all ${mode === "released" ? 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400 border border-blue-300 dark:border-blue-500/30' : 'bg-slate-100 dark:bg-slate-900/50 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700/30'}`}
                >
                  Released
                </button>
                <button
                  onClick={() => setMode("airing")}
                  className={`flex-1 p-3 rounded-xl font-bold text-sm transition-all ${mode === "airing" ? 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400 border border-blue-300 dark:border-blue-500/30' : 'bg-slate-100 dark:bg-slate-900/50 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700/30'}`}
                >
                  Airing
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Content Type Filter */}
        <div className="mt-6 pt-6 border-t border-slate-200 dark:border-slate-700/50">
          <label className="text-xs text-slate-600 dark:text-slate-400 mb-3 block font-semibold">Content Types</label>
          <div className="flex flex-wrap gap-3">
            {contentTypes.map(type => {
              const Icon = type.icon;
              return (
                <button
                  key={type.id}
                  onClick={() => toggleContentType(type.id)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl font-bold text-sm transition-all ${contentTypeFilter.includes(type.id) ? 'bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400 border border-purple-300 dark:border-purple-500/30' : 'bg-slate-100 dark:bg-slate-900/50 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700/30'}`}
                >
                  <Icon className="w-4 h-4" />
                  {type.name}
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Results */}
      {loading ? (
        <div className="h-96 flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="w-10 h-10 animate-spin text-purple-500" />
            <p className="text-slate-500 animate-pulse">Loading data...</p>
          </div>
        </div>
      ) : (
        <div className="space-y-8">
          {contentTypeFilter.includes("movies") && results.movies && results.movies.length > 0 && (
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-xl bg-blue-100 dark:bg-blue-500/20 border border-blue-300 dark:border-blue-500/30">
                  <Film className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100">Movies</h3>
                <span className="text-slate-500 text-sm">({results.movies.length} results)</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
                {results.movies.map((movie: any) => (
                  <div key={movie.id} className="bg-white dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-700/50 hover:border-blue-400/40 dark:hover:border-blue-500/40 transition-all cursor-pointer group">
                    <div className="aspect-2/3 bg-slate-100 dark:bg-slate-900 overflow-hidden">
                      {movie.poster_url ? (
                        <img src={movie.poster_url} alt={movie.title_display} className="w-full h-full object-cover object-top group-hover:scale-105 transition-transform duration-500" />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-slate-400 dark:text-slate-600">
                          <Film className="w-8 h-8" />
                        </div>
                      )}
                    </div>
                    <div className="p-3">
                      <h4 className="font-bold text-sm text-slate-900 dark:text-slate-100 line-clamp-2 group-hover:text-blue-500 dark:group-hover:text-blue-400 transition-colors">{movie.title_display}</h4>
                      <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{movie.release_date?.split('-')[0]}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {contentTypeFilter.includes("tv") && results.tv && results.tv.length > 0 && (
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-xl bg-purple-100 dark:bg-purple-500/20 border border-purple-300 dark:border-purple-500/30">
                  <Tv className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100">TV Series</h3>
                <span className="text-slate-500 text-sm">({results.tv.length} results)</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
                {results.tv.map((series: any) => (
                  <div key={series.id} className="bg-white dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-700/50 hover:border-purple-400/40 dark:hover:border-purple-500/40 transition-all cursor-pointer group">
                    <div className="aspect-2/3 bg-slate-100 dark:bg-slate-900 overflow-hidden">
                      {series.poster_url ? (
                        <img src={series.poster_url} alt={series.name} className="w-full h-full object-cover object-top group-hover:scale-105 transition-transform duration-500" />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-slate-400 dark:text-slate-600">
                          <Tv className="w-8 h-8" />
                        </div>
                      )}
                    </div>
                    <div className="p-3">
                      <h4 className="font-bold text-sm text-slate-900 dark:text-slate-100 line-clamp-2 group-hover:text-purple-500 dark:group-hover:text-purple-400 transition-colors">{series.name}</h4>
                      <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{series.premiere?.split('-')[0] || series.first_aired?.split('-')[0]}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {contentTypeFilter.includes("anime") && results.anime && results.anime.length > 0 && (
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-xl bg-amber-100 dark:bg-amber-500/20 border border-amber-300 dark:border-amber-500/30">
                  <Star className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                </div>
                <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100">Anime</h3>
                <span className="text-slate-500 text-sm">({results.anime.length} results)</span>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
                {results.anime.map((anime: any) => (
                  <div key={anime.id} className="bg-white dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-700/50 hover:border-amber-400/40 dark:hover:border-amber-500/40 transition-all cursor-pointer group">
                    <div className="aspect-2/3 bg-slate-100 dark:bg-slate-900 overflow-hidden">
                      {anime.poster_url ? (
                        <img src={anime.poster_url} alt={anime.title_english || anime.title_normalized} className="w-full h-full object-cover object-top group-hover:scale-105 transition-transform duration-500" />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-slate-400 dark:text-slate-600">
                          <Star className="w-8 h-8" />
                        </div>
                      )}
                    </div>
                    <div className="p-3">
                      <h4 className="font-bold text-sm text-slate-900 dark:text-slate-100 line-clamp-2 group-hover:text-amber-500 dark:group-hover:text-amber-400 transition-colors">{anime.title_english || anime.title_normalized}</h4>
                      <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{anime.season_year || anime.aired?.split('-')[0]}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {!loading && Object.keys(results).length === 0 && (
            <div className="h-64 flex flex-col items-center justify-center text-slate-500 gap-4">
              <div className="p-8 rounded-3xl bg-slate-100 dark:bg-slate-800/30 border border-slate-200 dark:border-slate-700/30">
                <Calendar className="w-16 h-16 text-slate-400 dark:text-slate-600" />
              </div>
              <p className="text-lg">No content found for the selected date(s).</p>
              <p className="text-sm text-slate-600">Try adjusting the date range or content type filters.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
