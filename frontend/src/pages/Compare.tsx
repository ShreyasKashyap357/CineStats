import { useState, useEffect, useMemo } from "react";
import { Search, Plus, X, BarChart2, TrendingUp, Calendar, Info } from "lucide-react";
// User must install recharts via: npm install recharts
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from "recharts";

export default function Compare() {
  const [allMovies, setAllMovies] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [comparedMovies, setComparedMovies] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    fetch("http://localhost:8000/api/movies?limit=200")
      .then(res => res.json())
      .then(data => setAllMovies(data))
      .catch(err => console.error(err));
  }, []);

  useEffect(() => {
    const fetchSelected = async () => {
      const fetches = selectedIds.map(id => fetch(`http://localhost:8000/api/movies/${id}`).then(r => r.json()));
      const results = await Promise.all(fetches);
      setComparedMovies(results);
    };
    fetchSelected();
  }, [selectedIds]);

  const toggleMovie = (id: number) => {
    if (selectedIds.includes(id)) {
      setSelectedIds(selectedIds.filter(i => i !== id));
    } else if (selectedIds.length < 5) {
      setSelectedIds([...selectedIds, id]);
    }
  };

  const filteredMovies = allMovies.filter(m => m.title_display.toLowerCase().includes(search.toLowerCase()) && !selectedIds.includes(m.id));

  // --- Graph Data Prep ---
  // We align all movies by "Day X" from their daily_performance array
  const dayWiseData = useMemo(() => {
    const data: any[] = [];
    const maxDays = Math.max(...comparedMovies.map(m => m.daily_performance?.length || 0), 0);
    
    for (let i = 0; i < maxDays; i++) {
      const row: any = { day: `Day ${i + 1}` };
      comparedMovies.forEach(m => {
        if (m.daily_performance && m.daily_performance[i]) {
          // Some days are formatted "Day 1", some just "1", we map by index
          row[`${m.title_display} (Net)`] = m.daily_performance[i].daily_india_net_cr || 0;
          row[`${m.title_display} (Cumulative)`] = m.daily_performance[i].cumulative_india_net_cr || 0;
        }
      });
      data.push(row);
    }
    return data;
  }, [comparedMovies]);

  const colors = ["#3b82f6", "#10b981", "#f97316", "#ec4899", "#8b5cf6"];

  return (
    <div className="max-w-7xl mx-auto pb-12">
      {/* Modern Header */}
      <header className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-3 rounded-2xl bg-linear-to-br from-blue-100 to-cyan-100 dark:from-blue-500/20 dark:to-cyan-500/20 border border-blue-200 dark:border-blue-500/30 shadow-lg shadow-blue-500/10">
            <BarChart2 className="w-8 h-8 text-blue-600 dark:text-blue-400" />
          </div>
          <div>
            <h2 className="text-4xl font-black text-slate-900 dark:text-slate-100 tracking-tight">Compare Media</h2>
            <p className="text-slate-600 dark:text-slate-400 mt-1">Select up to 5 movies to compare their financial trajectories side-by-side.</p>
          </div>
        </div>
      </header>

      {/* Modern Selector Section */}
      <div className="bg-white dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-slate-200 dark:border-slate-700/50 shadow-xl shadow-black/5 dark:shadow-black/10 mb-8">
        <div className="flex flex-wrap gap-3 items-center">
          {comparedMovies.map((m, i) => (
            <div key={m.id} className="group bg-slate-100 dark:bg-slate-900/80 border border-slate-300 dark:border-slate-600/50 rounded-full px-4 py-2.5 flex items-center gap-3 shadow-lg hover:border-blue-400 dark:hover:border-slate-500 transition-all duration-300">
              <div className="w-3 h-3 rounded-full shadow-lg" style={{ "--dot-color": colors[i], backgroundColor: "var(--dot-color)", boxShadow: "0 0 8px var(--dot-color)" } as React.CSSProperties}></div>
              <span className="font-bold text-slate-800 dark:text-slate-200">{m.title_display}</span>
              <button 
                onClick={() => toggleMovie(m.id)} 
                className="p-1 rounded-full text-slate-500 hover:text-red-500 hover:bg-red-500/10 transition-all duration-300"
                title="Remove"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ))}
          
          {selectedIds.length < 5 && (
            <div className="relative flex-1 min-w-[300px]">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
              <input 
                type="text" 
                placeholder="Search movies to add..." 
                className="w-full bg-white dark:bg-slate-900/80 border border-slate-300 dark:border-slate-700/50 rounded-full pl-12 pr-4 py-3 text-slate-900 dark:text-slate-200 focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 outline-none transition-all duration-300 placeholder:text-slate-400 dark:placeholder:text-slate-600"
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
              {search && (
                <div className="absolute top-14 left-0 right-0 bg-white dark:bg-slate-800/95 backdrop-blur-xl border border-slate-200 dark:border-slate-700/50 rounded-2xl shadow-2xl shadow-black/10 dark:shadow-black/50 max-h-72 overflow-y-auto z-50">
                  {filteredMovies.map(m => (
                    <button 
                      key={m.id}
                      onClick={() => { toggleMovie(m.id); setSearch(""); }}
                      className="w-full text-left px-4 py-3 hover:bg-slate-100 dark:hover:bg-slate-700/50 flex justify-between items-center border-b border-slate-100 dark:border-slate-700/30 transition-colors group"
                    >
                      <div>
                        <div className="font-bold text-slate-900 dark:text-slate-200 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">{m.title_display}</div>
                        <div className="text-xs text-slate-500">{m.release_date?.split('-')[0]} • {m.origin_country || "Unknown"}</div>
                      </div>
                      <div className="p-2 rounded-full bg-blue-100 dark:bg-blue-500/20 text-blue-600 dark:text-blue-400 group-hover:bg-blue-500 group-hover:text-white transition-all">
                        <Plus className="w-4 h-4" />
                      </div>
                    </button>
                  ))}
                  {filteredMovies.length === 0 && <div className="p-6 text-center text-slate-500">No movies found in database.</div>}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {comparedMovies.length > 0 ? (
        <div className="bg-white dark:bg-slate-800/50 backdrop-blur-sm rounded-2xl border border-slate-200 dark:border-slate-700/50 shadow-xl shadow-black/5 dark:shadow-black/10 overflow-hidden">
          {/* Modern Tabs */}
          <div className="flex border-b border-slate-200 dark:border-slate-700/50 bg-slate-50 dark:bg-slate-900/30">
            {[
              { id: 'overview', label: 'Overview', icon: Info },
              { id: 'day_number', label: 'By Day #', icon: Calendar },
              { id: 'visuals', label: 'Visual Trends', icon: TrendingUp },
            ].map((tab) => (
              <button 
                key={tab.id}
                onClick={() => setActiveTab(tab.id)} 
                className={`flex items-center gap-2 px-6 py-4 font-bold text-sm transition-all duration-300 ${activeTab === tab.id ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-500 bg-white dark:bg-slate-800/50' : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800/30'}`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
          </div>

          <div className="p-6">
            {activeTab === "overview" && (
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="border-b border-slate-200 dark:border-slate-700/50">
                      <th className="p-4 text-slate-600 dark:text-slate-400 font-bold uppercase tracking-wider text-sm w-1/4">Metric</th>
                      {comparedMovies.map((m, i) => <th key={i} className="p-4 font-black text-lg" style={{ "--header-color": colors[i], color: "var(--header-color)" } as React.CSSProperties}>{m.title_display}</th>)}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 dark:divide-slate-700/30">
                    <tr className="hover:bg-slate-50 dark:hover:bg-slate-700/20 transition-colors">
                      <td className="p-4 text-slate-600 dark:text-slate-400 flex items-center gap-2"><Calendar className="w-4 h-4 text-slate-500"/> Release Date</td>
                      {comparedMovies.map((m, i) => <td key={i} className="p-4 text-slate-800 dark:text-slate-200">{m.release_date || "N/A"}</td>)}
                    </tr>
                    <tr className="hover:bg-slate-50 dark:hover:bg-slate-700/20 transition-colors">
                      <td className="p-4 text-slate-600 dark:text-slate-400 flex items-center gap-2"><Info className="w-4 h-4 text-slate-500"/> Verdict</td>
                      {comparedMovies.map((m, i) => <td key={i} className="p-4 text-emerald-600 dark:text-emerald-400 font-bold">{m.verdict || "N/A"}</td>)}
                    </tr>
                    <tr className="bg-slate-50 dark:bg-slate-900/30">
                      <td className="p-4 text-slate-700 dark:text-slate-300 font-bold uppercase tracking-wider text-xs">Worldwide Summary</td>
                      {comparedMovies.map((m, i) => <td key={i} className="p-4"></td>)}
                    </tr>
                    <tr className="hover:bg-slate-50 dark:hover:bg-slate-700/20 transition-colors">
                      <td className="p-4 text-slate-600 dark:text-slate-400">Worldwide Gross</td>
                      {comparedMovies.map((m, i) => <td key={i} className="p-4 font-black text-slate-900 dark:text-slate-100">${((m.worldwide_gross_usd || 0)/1000000).toFixed(2)}M</td>)}
                    </tr>
                    <tr className="hover:bg-slate-50 dark:hover:bg-slate-700/20 transition-colors">
                      <td className="p-4 text-slate-600 dark:text-slate-400">Domestic Gross</td>
                      {comparedMovies.map((m, i) => <td key={i} className="p-4 text-slate-800 dark:text-slate-200">${((m.domestic_gross_usd || 0)/1000000).toFixed(2)}M</td>)}
                    </tr>
                    <tr className="hover:bg-slate-50 dark:hover:bg-slate-700/20 transition-colors">
                      <td className="p-4 text-slate-600 dark:text-slate-400">Foreign Gross</td>
                      {comparedMovies.map((m, i) => <td key={i} className="p-4 text-slate-800 dark:text-slate-200">${((m.foreign_gross_usd || 0)/1000000).toFixed(2)}M</td>)}
                    </tr>
                    <tr className="bg-slate-50 dark:bg-slate-900/30">
                      <td className="p-4 text-slate-700 dark:text-slate-300 font-bold uppercase tracking-wider text-xs">India Summary</td>
                      {comparedMovies.map((m, i) => <td key={i} className="p-4"></td>)}
                    </tr>
                    <tr className="hover:bg-slate-50 dark:hover:bg-slate-700/20 transition-colors">
                      <td className="p-4 text-slate-600 dark:text-slate-400">India Net</td>
                      {comparedMovies.map((m, i) => <td key={i} className="p-4 text-blue-600 dark:text-blue-400 font-bold">₹{m.india_net_cr || "0"} Cr</td>)}
                    </tr>
                    <tr className="hover:bg-slate-50 dark:hover:bg-slate-700/20 transition-colors">
                      <td className="p-4 text-slate-600 dark:text-slate-400">India Gross</td>
                      {comparedMovies.map((m, i) => <td key={i} className="p-4 text-blue-600 dark:text-blue-400 font-bold">₹{m.india_gross_cr || "0"} Cr</td>)}
                    </tr>
                    <tr className="hover:bg-slate-50 dark:hover:bg-slate-700/20 transition-colors">
                      <td className="p-4 text-slate-600 dark:text-slate-400">Total Shows</td>
                      {comparedMovies.map((m, i) => <td key={i} className="p-4 text-slate-800 dark:text-slate-200">{m.total_shows_sacnilk?.toLocaleString() || "0"}</td>)}
                    </tr>
                  </tbody>
                </table>
              </div>
            )}

            {activeTab === "day_number" && (
              <div className="overflow-x-auto custom-scrollbar max-h-150">
                <table className="w-full text-left text-sm">
                  <thead className="bg-slate-100 dark:bg-slate-900/80 sticky top-0 z-10 shadow-lg">
                    <tr>
                      <th className="p-4 text-slate-600 dark:text-slate-400 font-bold uppercase tracking-wider text-xs border-b border-slate-200 dark:border-slate-700/50">Day</th>
                      {comparedMovies.map((m, i) => <th key={i} className="p-4 border-b border-slate-200 dark:border-slate-700/50 font-bold" style={{ "--header-color": colors[i], color: "var(--header-color)" } as React.CSSProperties}>{m.title_display} (Net)</th>)}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 dark:divide-slate-700/30">
                    {dayWiseData.map((row, i) => (
                      <tr key={i} className="hover:bg-slate-50 dark:hover:bg-slate-700/20 transition-colors">
                        <td className="p-4 font-bold text-slate-700 dark:text-slate-300">{row.day}</td>
                        {comparedMovies.map((m, colIdx) => (
                          <td key={colIdx} className="p-4 font-mono text-slate-800 dark:text-slate-200">
                            {row[`${m.title_display} (Net)`] ? `₹${row[`${m.title_display} (Net)`]} Cr` : "-"}
                          </td>
                        ))}
                      </tr>
                    ))}
                    {dayWiseData.length === 0 && (
                      <tr><td colSpan={6} className="p-8 text-center text-slate-500">No daily performance data available for selected movies.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            )}

            {activeTab === "visuals" && (
              <div className="space-y-12">
                <div>
                  <h3 className="text-xl font-black mb-6 flex items-center gap-2 text-slate-900 dark:text-slate-100">
                    <TrendingUp className="w-5 h-5 text-emerald-600 dark:text-emerald-400" /> Cumulative Gross Collection (₹ Cr)
                  </h3>
                  <div className="h-96 w-full bg-white dark:bg-slate-900/50 backdrop-blur-sm rounded-2xl p-4 border border-slate-200 dark:border-slate-700/50 shadow-inner">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={dayWiseData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                        <defs>
                          {comparedMovies.map((m, i) => (
                            <linearGradient key={m.id} id={`colorUv${i}`} x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor={colors[i]} stopOpacity={0.8}/>
                              <stop offset="95%" stopColor={colors[i]} stopOpacity={0}/>
                            </linearGradient>
                          ))}
                        </defs>
                        <XAxis dataKey="day" stroke="#94a3b8" tick={{fill: '#64748b'}} />
                        <YAxis stroke="#94a3b8" tick={{fill: '#64748b'}} />
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                        <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', color: '#1e293b' }} itemStyle={{ fontWeight: 'bold' }} />
                        <Legend />
                        {comparedMovies.map((m, i) => (
                          <Area 
                            key={m.id} 
                            type="monotone" 
                            dataKey={`${m.title_display} (Cumulative)`} 
                            stroke={colors[i]} 
                            fillOpacity={1} 
                            fill={`url(#colorUv${i})`} 
                            strokeWidth={3}
                            dot={false}
                          />
                        ))}
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div>
                  <h3 className="text-xl font-black mb-6 flex items-center gap-2 text-slate-900 dark:text-slate-100">
                    <BarChart2 className="w-5 h-5 text-blue-600 dark:text-blue-400" /> Day-wise Net Collection (₹ Cr)
                  </h3>
                  <div className="h-96 w-full bg-white dark:bg-slate-900/50 backdrop-blur-sm rounded-2xl p-4 border border-slate-200 dark:border-slate-700/50 shadow-inner">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={dayWiseData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                        <XAxis dataKey="day" stroke="#94a3b8" tick={{fill: '#64748b'}} />
                        <YAxis stroke="#94a3b8" tick={{fill: '#64748b'}} />
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
                        <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e2e8f0', color: '#1e293b' }} />
                        <Legend />
                        {comparedMovies.map((m, i) => (
                          <Line 
                            key={m.id} 
                            type="monotone" 
                            dataKey={`${m.title_display} (Net)`} 
                            stroke={colors[i]} 
                            strokeWidth={3}
                            dot={{ r: 3, fill: colors[i], strokeWidth: 0 }}
                            activeDot={{ r: 6 }}
                          />
                        ))}
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="bg-white dark:bg-slate-800/30 backdrop-blur-sm rounded-2xl border border-slate-200 dark:border-slate-700/50 border-dashed h-64 flex flex-col items-center justify-center text-slate-500">
          <div className="p-4 rounded-2xl bg-slate-100 dark:bg-slate-800/50 mb-4">
            <BarChart2 className="w-12 h-12 text-slate-400" />
          </div>
          <p className="text-lg font-medium text-slate-700 dark:text-slate-500">Select a movie from the search bar above to begin comparing.</p>
          <p className="text-sm text-slate-500 dark:text-slate-600 mt-2">Compare up to 5 movies side-by-side</p>
        </div>
      )}
    </div>
  );
}
