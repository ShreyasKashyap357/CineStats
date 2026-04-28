import { useState, useEffect } from "react";
import { Heart, Trash2, Edit2, X, Check, Film, Tv, Star, Clock, Loader2 } from "lucide-react";

export default function Watchlist() {
  const [watchlist, setWatchlist] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingMilestone, setEditingMilestone] = useState<number | null>(null);
  const [milestoneInput, setMilestoneInput] = useState("");

  const fetchWatchlist = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/watchlist/");
      const data = await res.json();
      setWatchlist(data.items || []);
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchWatchlist();
  }, []);

  const removeFromWatchlist = async (itemId: number) => {
    try {
      await fetch(`http://localhost:8000/api/watchlist/remove/${itemId}`, { method: "DELETE" });
      setWatchlist(prev => prev.filter(item => item.id !== itemId));
    } catch (e) {
      console.error(e);
    }
  };

  const startEditingMilestone = (item: any) => {
    setEditingMilestone(item.id);
    setMilestoneInput(item.milestone || "");
  };

  const saveMilestone = async (itemId: number) => {
    try {
      await fetch(`http://localhost:8000/api/watchlist/milestone/${itemId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(milestoneInput)
      });
      setWatchlist(prev => prev.map(item => 
        item.id === itemId ? { ...item, milestone: milestoneInput } : item
      ));
      setEditingMilestone(null);
    } catch (e) {
      console.error(e);
    }
  };

  const cancelEditing = () => {
    setEditingMilestone(null);
    setMilestoneInput("");
  };

  const getContentTypeIcon = (type: string) => {
    switch (type) {
      case "movie": return Film;
      case "tv": return Tv;
      case "anime": return Star;
      default: return Film;
    }
  };

  const getContentTypeColor = (type: string) => {
    switch (type) {
      case "movie": return "text-blue-400 bg-blue-500/20 border-blue-500/30";
      case "tv": return "text-purple-400 bg-purple-500/20 border-purple-500/30";
      case "anime": return "text-amber-400 bg-amber-500/20 border-amber-500/30";
      default: return "text-slate-400 bg-slate-500/20 border-slate-500/30";
    }
  };

  return (
    <div className="max-w-7xl mx-auto pb-12">
      {/* Header */}
      <header className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-3 rounded-2xl bg-linear-to-br from-rose-100 to-pink-100 dark:from-rose-500/20 dark:to-pink-500/20 border border-rose-200 dark:border-rose-500/30 shadow-lg shadow-rose-500/10">
            <Heart className="w-8 h-8 text-rose-600 dark:text-rose-400" />
          </div>
          <div>
            <h2 className="text-4xl font-black text-slate-900 dark:text-slate-100 tracking-tight">Watchlist</h2>
            <p className="text-slate-600 dark:text-slate-400 mt-1">Track movies, TV series, and anime you want to watch.</p>
          </div>
        </div>
      </header>

      {loading ? (
        <div className="h-96 flex items-center justify-center">
          <div className="flex flex-col items-center gap-4">
            <Loader2 className="w-10 h-10 animate-spin text-rose-500" />
            <p className="text-slate-500 animate-pulse">Loading watchlist...</p>
          </div>
        </div>
      ) : watchlist.length === 0 ? (
        <div className="h-64 flex flex-col items-center justify-center text-slate-500 gap-4">
          <div className="p-8 rounded-3xl bg-slate-100 dark:bg-slate-800/30 border border-slate-200 dark:border-slate-700/30">
            <Heart className="w-16 h-16 text-slate-400 dark:text-slate-600" />
          </div>
          <p className="text-lg">Your watchlist is empty.</p>
          <p className="text-sm text-slate-600">Add movies, TV series, or anime from their detail pages.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {watchlist.map((item) => {
            const Icon = getContentTypeIcon(item.content_type);
            return (
              <div key={item.id} className="bg-white dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-700/50 shadow-xl shadow-black/5 dark:shadow-black/10 group hover:border-rose-400/40 dark:hover:border-rose-500/40 transition-all">
                <div className="flex">
                  {/* Poster */}
                  <div className="w-1/3 aspect-2/3 bg-slate-200 dark:bg-slate-900 overflow-hidden">
                    {item.poster_url ? (
                      <img src={item.poster_url} alt={item.title} className="w-full h-full object-cover object-top" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-slate-400 dark:text-slate-600">
                        <Icon className="w-8 h-8" />
                      </div>
                    )}
                  </div>

                  {/* Content */}
                  <div className="flex-1 p-4 flex flex-col">
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <span className={`px-2 py-1 rounded-lg text-xs font-bold uppercase ${getContentTypeColor(item.content_type)}`}>
                        {item.content_type}
                      </span>
                      <button
                        onClick={() => removeFromWatchlist(item.id)}
                        className="p-1.5 rounded-lg bg-slate-100 dark:bg-slate-900/50 hover:bg-rose-100 dark:hover:bg-rose-500/20 text-slate-500 dark:text-slate-400 hover:text-rose-500 dark:hover:text-rose-400 transition-colors"
                        title="Remove from watchlist"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>

                    <h3 className="font-bold text-slate-900 dark:text-slate-100 text-sm line-clamp-2 mb-2">{item.title}</h3>

                    {/* Milestone */}
                    <div className="mt-auto">
                      {editingMilestone === item.id ? (
                        <div className="flex gap-2">
                          <input
                            type="text"
                            value={milestoneInput}
                            onChange={e => setMilestoneInput(e.target.value)}
                            placeholder="e.g. Episode 5, Season 2"
                            className="flex-1 bg-slate-100 dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-lg px-2 py-1 text-xs text-slate-800 dark:text-slate-200"
                            autoFocus
                          />
                          <button
                            onClick={() => saveMilestone(item.id)}
                            className="p-1.5 rounded-lg bg-emerald-100 dark:bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 hover:bg-emerald-200 dark:hover:bg-emerald-500/30"
                            title="Save milestone"
                          >
                            <Check className="w-4 h-4" />
                          </button>
                          <button
                            onClick={cancelEditing}
                            className="p-1.5 rounded-lg bg-slate-100 dark:bg-slate-900/50 text-slate-500 dark:text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-700/30"
                            title="Cancel editing"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      ) : (
                        <div className="flex items-center justify-between">
                          {item.milestone ? (
                            <div className="flex items-center gap-1.5 text-xs text-slate-600 dark:text-slate-400">
                              <Clock className="w-3 h-3" />
                              <span>{item.milestone}</span>
                            </div>
                          ) : (
                            <span className="text-xs text-slate-500">No milestone set</span>
                          )}
                          <button
                            onClick={() => startEditingMilestone(item)}
                            className="p-1.5 rounded-lg bg-slate-100 dark:bg-slate-900/50 hover:bg-rose-100 dark:hover:bg-rose-500/20 text-slate-500 dark:text-slate-400 hover:text-rose-500 dark:hover:text-rose-400 transition-colors"
                            title="Edit milestone"
                          >
                            <Edit2 className="w-3 h-3" />
                          </button>
                        </div>
                      )}
                    </div>

                    {/* Added date */}
                    <div className="mt-2 text-xs text-slate-500">
                      Added {new Date(item.added_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
