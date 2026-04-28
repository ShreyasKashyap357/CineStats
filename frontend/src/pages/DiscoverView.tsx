import { useState, useEffect } from "react";
import { Loader2, Image as ImageIcon, X, Star, Calendar, Plus } from "lucide-react";

interface DiscoverProps {
  title: string;
  endpoint: string;
  icon: React.ReactNode;
  isSidebarOpen?: boolean;
}

export default function DiscoverView({ title, endpoint, icon, isSidebarOpen = true }: DiscoverProps) {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState<any>(null);
  const [tracking, setTracking] = useState(false);

  // Close modal on route change
  useEffect(() => {
    setSelectedItem(null);
  }, [endpoint]);

  useEffect(() => {
    setLoading(true);
    fetch(`http://localhost:8000/api/discover/${endpoint}`)
      .then(res => res.json())
      .then(data => {
        setItems(data.results || []);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [endpoint]);

  const handleTrack = async (item: any) => {
    setTracking(true);
    try {
      const res = await fetch(`http://localhost:8000/api/search/track`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tmdb_id: item.tmdb_id })
      });
      if (res.ok) {
        // Reload the items to update tracked status
        fetch(`http://localhost:8000/api/discover/${endpoint}`)
          .then(res => res.json())
          .then(data => {
            setItems(data.results || []);
          });
      }
    } catch (e) {
      console.error(e);
    }
    setTracking(false);
  };

  return (
    <div className="max-w-7xl mx-auto pb-12">
      {/* Modern Header */}
      <header className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-3 rounded-2xl bg-linear-to-br from-blue-100 to-cyan-100 dark:from-blue-500/20 dark:to-cyan-500/20 border border-blue-200 dark:border-blue-500/30 shadow-lg shadow-blue-500/10">
            {icon}
          </div>
          <div>
            <h2 className="text-4xl font-black text-slate-900 dark:text-slate-100 tracking-tight">{title}</h2>
            <p className="text-slate-600 dark:text-slate-400 mt-1">Explore the latest updates and trending media.</p>
          </div>
        </div>
      </header>

      {loading ? (
        <div className="h-64 flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="w-10 h-10 animate-spin text-blue-500" />
            <p className="text-slate-500 animate-pulse">Loading content...</p>
          </div>
        </div>
      ) : items.length > 0 ? (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
          {items.map((item, idx) => (
            <div 
              key={idx} 
              onClick={() => setSelectedItem(item)}
              className="group cursor-pointer relative rounded-2xl overflow-hidden shadow-lg border border-slate-200 dark:border-slate-700/50 hover:border-blue-400/50 dark:hover:border-blue-500/50 hover:shadow-2xl hover:shadow-blue-500/20 transition-all duration-300 hover:-translate-y-2"
            >
              <div className="aspect-2/3 bg-slate-100 dark:bg-slate-800/50 flex items-center justify-center overflow-hidden">
                {item.poster_url ? (
                  <img src={item.poster_url} alt={item.title || item.title_display} className="w-full h-full object-cover object-top group-hover:scale-105 transition-transform duration-500" loading="lazy" />
                ) : (
                  <ImageIcon className="w-12 h-12 text-slate-400 dark:text-slate-600" />
                )}
              </div>
              
              {/* Always visible full details */}
              <div className="absolute inset-0 bg-linear-to-t from-slate-900 via-slate-900/95 to-transparent p-3 flex flex-col justify-end">
                <h3 className="font-bold text-slate-100 text-xs line-clamp-2 leading-tight mb-1.5">{item.title || item.title_display}</h3>
                
                {/* Year */}
                {item.release_date && (
                  <div className="text-xs text-slate-400 mb-1.5">
                    {item.release_date.split('-')[0] || "TBA"}
                  </div>
                )}
                
                {/* Rating or Gross */}
                <div className="flex justify-between items-center mb-1.5">
                  {item.vote_average ? (
                    <span className="text-xs font-bold text-amber-400 bg-amber-400/20 px-2 py-0.5 rounded-md">★ {item.vote_average.toFixed(1)}</span>
                  ) : item.worldwide_gross_usd ? (
                    <span className="text-xs font-bold text-emerald-400 bg-emerald-400/20 px-2 py-0.5 rounded-md">${(item.worldwide_gross_usd/1000000).toFixed(1)}M</span>
                  ) : null}
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-slate-100 dark:bg-slate-800/30 rounded-2xl border border-slate-200 dark:border-slate-700/50 border-dashed h-64 flex flex-col items-center justify-center text-slate-500">
          <p className="text-lg">No data available for {title} right now.</p>
        </div>
      )}

      {/* Modern Detail Modal */}
      {selectedItem && (
        <div className="absolute inset-0 bg-black/80 backdrop-blur-sm z-[100] flex items-center justify-center p-4 animate-fade-in" onClick={() => setSelectedItem(null)}>
          <div className="bg-white dark:bg-slate-900/95 backdrop-blur-xl rounded-3xl border border-slate-200 dark:border-slate-700/50 shadow-2xl shadow-black/50 w-full max-w-3xl flex flex-col md:flex-row overflow-hidden relative max-h-[90vh]" onClick={e => e.stopPropagation()}>
            {/* Ambient Glow */}
            <div className="absolute -top-32 -right-32 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
            
            <button onClick={() => setSelectedItem(null)} title="Close modal"
              className="absolute top-4 right-4 p-2.5 bg-slate-100 dark:bg-slate-800/80 backdrop-blur-sm rounded-full hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white z-20 border border-slate-200 dark:border-slate-700/50 hover:border-slate-300 dark:hover:border-slate-600 transition-all">
              <X className="w-5 h-5" />
            </button>

            <div className="w-full md:w-48 bg-slate-100 dark:bg-slate-800/30 relative overflow-hidden shrink-0">
              {selectedItem.poster_url ? (
                <img src={selectedItem.poster_url} alt={selectedItem.title || selectedItem.title_display} className="w-full h-auto object-contain" />
              ) : (
                <div className="w-full h-48 flex items-center justify-center text-slate-400 dark:text-slate-700"><ImageIcon className="w-16 h-16 opacity-50" /></div>
              )}
            </div>

            <div className="flex-1 p-6 overflow-y-auto custom-scrollbar relative z-10">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider bg-slate-100 dark:bg-slate-800/50 px-2.5 py-1 rounded-full border border-slate-200 dark:border-slate-700/30">
                  {selectedItem.media_type === "tv" ? "TV Series" : "Movie"}
                </span>
              </div>
              
              <h2 className="text-3xl font-black text-slate-900 dark:text-slate-100 mb-2 tracking-tight">{selectedItem.title || selectedItem.title_display}</h2>
              
              <div className="flex items-center gap-4 text-sm text-slate-600 dark:text-slate-400 mb-4">
                {selectedItem.release_date && (
                  <span className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800/50 px-2.5 py-1 rounded-full border border-slate-200 dark:border-slate-700/30"><Calendar className="w-4 h-4" /> {selectedItem.release_date}</span>
                )}
                {selectedItem.vote_average && (
                  <span className="flex items-center gap-1 text-amber-500 dark:text-amber-400 bg-slate-100 dark:bg-slate-800/50 px-2.5 py-1 rounded-full border border-slate-200 dark:border-slate-700/30"><Star className="w-4 h-4 fill-current" /> {selectedItem.vote_average.toFixed?.(1) || selectedItem.vote_average}</span>
                )}
              </div>
              
              {selectedItem.overview && (
                <p className="text-slate-600 dark:text-slate-300 text-sm leading-relaxed mb-6 line-clamp-6">{selectedItem.overview}</p>
              )}

              {(selectedItem.worldwide_gross_usd || selectedItem.india_net_cr) && (
                <div className="flex gap-4 mb-6">
                  {selectedItem.worldwide_gross_usd && (
                    <div className="bg-slate-100 dark:bg-slate-800/50 backdrop-blur-sm px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700/50">
                      <span className="text-xs text-slate-500 uppercase tracking-wider">WW Gross</span>
                      <p className="text-emerald-600 dark:text-emerald-400 font-bold">${(selectedItem.worldwide_gross_usd / 1000000).toFixed(1)}M</p>
                    </div>
                  )}
                  {selectedItem.india_net_cr && (
                    <div className="bg-slate-100 dark:bg-slate-800/50 backdrop-blur-sm px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700/50">
                      <span className="text-xs text-slate-500 uppercase tracking-wider">India Net</span>
                      <p className="text-amber-600 dark:text-amber-400 font-bold">₹{selectedItem.india_net_cr} Cr</p>
                    </div>
                  )}
                </div>
              )}

              {/* Track button - only show if not tracked (no id) */}
              {!selectedItem.id && selectedItem.tmdb_id && (
                <button
                  onClick={() => handleTrack(selectedItem)}
                  disabled={tracking}
                  className="bg-linear-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-all shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 disabled:opacity-50 hover:-translate-y-0.5"
                >
                  {tracking ? <Loader2 className="w-5 h-5 animate-spin" /> : <Plus className="w-5 h-5" />}
                  {tracking ? "Ingesting..." : "Track in CineStats"}
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
