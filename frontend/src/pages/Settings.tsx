import { useState, useEffect } from "react";
import { Server, RefreshCw, CheckCircle, AlertTriangle, DollarSign, Globe, Sun, Moon, Layers, Save, Trash2 } from "lucide-react";

export default function Settings() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<any>(null);
  
  // Settings state
  const [currency, setCurrency] = useState("INR");
  const [countryLens, setCountryLens] = useState(["Global", "India"]);
  const [theme, setTheme] = useState<"dark" | "light">(() => {
    const saved = localStorage.getItem('darkMode');
    return saved !== null ? (JSON.parse(saved) ? 'dark' : 'light') : 'dark';
  });
  const [expandableThreshold, setExpandableThreshold] = useState(5);
  const [pdfAlwaysExpanded, setPdfAlwaysExpanded] = useState(true);
  const [saved, setSaved] = useState(false);
  const [cleaning, setCleaning] = useState(false);
  const [showCleanupConfirm, setShowCleanupConfirm] = useState(false);
  const [cleanupResult, setCleanupResult] = useState<any>(null);

  const currencies = [
    { code: "USD", symbol: "$", name: "US Dollar" },
    { code: "INR", symbol: "₹", name: "Indian Rupee" },
    { code: "EUR", symbol: "€", name: "Euro" },
    { code: "GBP", symbol: "£", name: "British Pound" },
    { code: "JPY", symbol: "¥", name: "Japanese Yen" },
    { code: "AED", symbol: "د.إ", name: "UAE Dirham" },
    { code: "AUD", symbol: "A$", name: "Australian Dollar" },
    { code: "CAD", symbol: "C$", name: "Canadian Dollar" },
    { code: "SGD", symbol: "S$", name: "Singapore Dollar" },
  ];

  const countries = ["Global", "India", "USA", "UK", "China", "Japan", "South Korea", "France", "Germany", "Australia", "Canada", "Brazil", "Mexico", "Russia", "Italy", "Spain"];

  const triggerScrape = async (module: string) => {
    try {
      const res = await fetch("http://localhost:8000/api/scrape/trigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ module })
      });
      const data = await res.json();
      setJobId(data.job_id);
    } catch (e) {
      console.error(e);
      alert("Failed to connect to backend server");
    }
  };

  const saveSettings = async () => {
    try {
      // Update localStorage for App.tsx to pick up theme change
      localStorage.setItem('darkMode', JSON.stringify(theme === 'dark'));
      // Dispatch storage event to trigger App.tsx re-render
      window.dispatchEvent(new StorageEvent('storage', {
        key: 'darkMode',
        newValue: JSON.stringify(theme === 'dark')
      }));
      
      await fetch("http://localhost:8000/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          currency,
          country_lens: countryLens,
          theme,
          expandable_threshold: expandableThreshold,
          pdf_always_expanded: pdfAlwaysExpanded
        })
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (e) {
      console.error(e);
    }
  };

  const handleCleanup = async () => {
    setCleaning(true);
    try {
      const res = await fetch("http://localhost:8000/api/settings/cleanup", {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      const data = await res.json();
      setCleanupResult(data);
      setShowCleanupConfirm(false);
    } catch (e) {
      console.error(e);
      alert("Failed to cleanup database");
    } finally {
      setCleaning(false);
    }
  };

  useEffect(() => {
    if (!jobId) return;

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/scrape/status/${jobId}`);
        const data = await res.json();
        setJobStatus(data);
        
        if (data.status === "completed" || data.status === "failed") {
          clearInterval(interval);
        }
      } catch (e) {
        console.error("Polling error", e);
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [jobId]);

  // Apply theme to document
  useEffect(() => {
    if (theme === "light") {
      document.documentElement.classList.add("light");
      document.documentElement.classList.remove("dark");
    } else {
      document.documentElement.classList.add("dark");
      document.documentElement.classList.remove("light");
    }
  }, [theme]);

  const toggleCountry = (country: string) => {
    if (country === "Global") return; // Global always included
    setCountryLens(prev =>
      prev.includes(country) ? prev.filter(c => c !== country) : [...prev, country]
    );
  };

  return (
    <div className="max-w-4xl mx-auto mt-8 pb-12">
      {/* Modern Header with Green-Purple Gradient */}
      <header className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-3 rounded-2xl bg-linear-to-br from-emerald-100 via-green-100 to-purple-100 dark:from-emerald-900/30 dark:via-green-900/20 dark:to-purple-900/30 border border-emerald-200 dark:border-emerald-800 shadow-sm">
            <Server className="w-8 h-8 text-emerald-600 dark:text-emerald-400" />
          </div>
          <div>
            <h2 className="text-4xl font-black bg-linear-to-r from-emerald-600 via-green-600 to-purple-600 text-transparent bg-clip-text tracking-tight">Settings</h2>
            <p className="text-slate-500 text-sm mt-1">Customize your CineStats experience</p>
          </div>
        </div>
      </header>
      
      <div className="space-y-6">
        {/* Currency Settings - Green Accent */}
        <section className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200 dark:border-slate-700 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-[0_4px_16px_rgba(16,185,129,0.1)] transition-shadow">
          <div className="flex items-center gap-3 mb-5">
            <div className="p-2.5 rounded-xl bg-linear-to-br from-emerald-50 to-green-50 dark:bg-emerald-900/50 border border-emerald-200 dark:border-emerald-800">
              <DollarSign className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white">Currency</h3>
          </div>
          <div className="grid grid-cols-3 md:grid-cols-5 gap-3">
            {currencies.map(curr => (
              <button
                key={curr.code}
                onClick={() => setCurrency(curr.code)}
                className={`px-4 py-3 rounded-xl font-semibold text-sm transition-all border ${currency === curr.code ? 'bg-linear-to-r from-emerald-500 to-green-500 text-white border-emerald-500 shadow-md shadow-emerald-200' : 'bg-slate-50 dark:bg-slate-700 text-slate-700 dark:text-gray-300 border-slate-200 dark:border-slate-600 hover:border-emerald-400 hover:bg-emerald-50/50 dark:hover:bg-slate-600'}`}
              >
                <span className="mr-1">{curr.symbol}</span>{curr.code}
              </button>
            ))}
          </div>
        </section>

        {/* Country Lens Settings - Purple Accent */}
        <section className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200 dark:border-slate-700 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-[0_4px_16px_rgba(139,92,246,0.1)] transition-shadow">
          <div className="flex items-center gap-3 mb-3">
            <div className="p-2.5 rounded-xl bg-linear-to-br from-purple-50 to-violet-50 dark:bg-purple-900/50 border border-purple-200 dark:border-purple-800">
              <Globe className="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white">Country Lens</h3>
          </div>
          <p className="text-slate-600 dark:text-gray-400 text-sm mb-5 ml-14">Select up to 3 countries to highlight alongside global data. Global is always included.</p>
          <div className="grid grid-cols-3 md:grid-cols-5 gap-3 ml-14">
            {countries.map(country => (
              <button
                key={country}
                onClick={() => toggleCountry(country)}
                disabled={country === "Global"}
                className={`px-3 py-2.5 rounded-xl font-semibold text-sm transition-all border ${country === "Global" ? 'bg-linear-to-r from-purple-500 to-violet-500 text-white border-purple-500 shadow-md shadow-purple-200 cursor-default' : countryLens.includes(country) ? 'bg-linear-to-r from-purple-500 to-violet-500 text-white border-purple-500 shadow-md shadow-purple-200' : 'bg-slate-50 dark:bg-slate-700 text-slate-700 dark:text-gray-300 border-slate-200 dark:border-slate-600 hover:border-purple-400 hover:bg-purple-50/50 dark:hover:bg-slate-600'}`}
              >
                {country}
              </button>
            ))}
          </div>
        </section>

        {/* Theme Settings - Amber/Orange Accent */}
        <section className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200 dark:border-slate-700 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-[0_4px_16px_rgba(245,158,11,0.1)] transition-shadow">
          <div className="flex items-center gap-3 mb-5">
            <div className="p-2.5 rounded-xl bg-linear-to-br from-amber-50 to-orange-50 dark:bg-amber-900/50 border border-amber-200 dark:border-amber-800">
              {theme === "dark" ? <Moon className="w-6 h-6 text-amber-600 dark:text-amber-400" /> : <Sun className="w-6 h-6 text-amber-600 dark:text-amber-400" />}
            </div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white">Theme</h3>
          </div>
          <div className="flex gap-4">
            <button
              onClick={() => setTheme("dark")}
              className={`flex-1 px-4 py-4 rounded-xl font-semibold transition-all border flex items-center justify-center gap-2 ${theme === "dark" ? 'bg-linear-to-r from-slate-700 to-slate-800 text-white border-slate-600 shadow-md shadow-slate-200' : 'bg-slate-50 dark:bg-slate-700 text-slate-700 dark:text-gray-300 border-slate-200 dark:border-slate-600 hover:bg-slate-100 dark:hover:bg-slate-600'}`}
            >
              <Moon className="w-5 h-5" /> Dark Mode
            </button>
            <button
              onClick={() => setTheme("light")}
              className={`flex-1 px-4 py-4 rounded-xl font-semibold transition-all border flex items-center justify-center gap-2 ${theme === "light" ? 'bg-linear-to-r from-amber-400 to-orange-400 text-white border-amber-400 shadow-md shadow-amber-200' : 'bg-slate-50 dark:bg-slate-700 text-slate-700 dark:text-gray-300 border-slate-200 dark:border-slate-600 hover:bg-amber-50/50 dark:hover:bg-slate-600'}`}
            >
              <Sun className="w-5 h-5" /> Light Mode
            </button>
          </div>
        </section>

        {/* Expandable Sections Settings - Pink/Rose Accent */}
        <section className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200 dark:border-slate-700 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-[0_4px_16px_rgba(244,63,94,0.1)] transition-shadow">
          <div className="flex items-center gap-3 mb-5">
            <div className="p-2.5 rounded-xl bg-linear-to-br from-pink-50 to-rose-50 dark:bg-pink-900/50 border border-pink-200 dark:border-pink-800">
              <Layers className="w-6 h-6 text-pink-600 dark:text-pink-400" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white">Expandable Sections</h3>
          </div>
          <div className="space-y-6">
            <div>
              <label className="text-sm font-medium text-slate-700 dark:text-gray-300 mb-3 block">Auto-collapse threshold (lines)</label>
              <input
                type="range"
                min="3"
                max="20"
                value={expandableThreshold}
                onChange={e => setExpandableThreshold(parseInt(e.target.value))}
                className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-purple-600"
                title="Auto-collapse threshold"
              />
              <div className="flex justify-between text-xs text-slate-500 mt-2">
                <span>3 lines</span>
                <span className="font-bold text-purple-600 dark:text-purple-400">{expandableThreshold} lines</span>
                <span>20 lines</span>
              </div>
            </div>
            <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-700/50 rounded-xl border border-slate-200 dark:border-slate-700">
              <span className="text-sm font-medium text-slate-800 dark:text-gray-200">PDF: Always expand all sections</span>
              <button
                onClick={() => setPdfAlwaysExpanded(!pdfAlwaysExpanded)}
                className={`relative w-14 h-7 rounded-full transition-all ${pdfAlwaysExpanded ? 'bg-linear-to-r from-pink-500 to-rose-500 shadow-sm shadow-pink-200' : 'bg-slate-300 dark:bg-slate-600'}`}
                title="Toggle PDF always expanded"
              >
                <div className={`absolute top-1 left-1 w-5 h-5 rounded-full bg-white shadow-sm transition-all ${pdfAlwaysExpanded ? 'translate-x-7' : 'translate-x-0'}`} />
              </button>
            </div>
          </div>
        </section>

        {/* Manual Triggers - Cyan/Indigo Accent */}
        <section className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200 dark:border-slate-700 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-[0_4px_16px_rgba(6,182,212,0.1)] transition-shadow">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2.5 rounded-xl bg-linear-to-br from-cyan-50 to-indigo-50 dark:bg-cyan-900/50 border border-cyan-200 dark:border-cyan-800">
              <RefreshCw className="w-6 h-6 text-cyan-600 dark:text-cyan-400" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white">Manual Data Sync</h3>
          </div>
          <p className="text-slate-600 dark:text-gray-400 text-sm mb-6">Start a deep scrape to replenish the SQLite Database. The backend will queue the request.</p>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <button 
              onClick={() => triggerScrape("sacnilk")}
              className="px-6 py-4 bg-linear-to-r from-cyan-500 to-cyan-600 hover:from-cyan-400 hover:to-cyan-500 text-white rounded-xl font-semibold transition-all shadow-md shadow-cyan-200 hover:shadow-lg flex justify-center items-center gap-2"
            >
              <RefreshCw className="w-5 h-5" /> Scrape Sacnilk (Indian Box Office)
            </button>
            
            <button 
              onClick={() => triggerScrape("bom")}
              className="px-6 py-4 bg-linear-to-r from-indigo-500 to-violet-500 hover:from-indigo-400 hover:to-violet-400 text-white rounded-xl font-semibold transition-all shadow-md shadow-indigo-200 hover:shadow-lg flex justify-center items-center gap-2"
            >
              <RefreshCw className="w-5 h-5" /> Scrape Box Office Mojo (Global)
            </button>
          </div>

          {/* Polling UI */}
          {jobId && jobStatus && (
            <div className="mt-6 bg-slate-50 dark:bg-slate-700/50 rounded-xl p-5 border border-slate-200 dark:border-slate-700">
              <h4 className="font-bold text-lg flex items-center gap-3 mb-4">
                {jobStatus.status === "completed" ? <CheckCircle className="w-6 h-6 text-emerald-600" /> : 
                 jobStatus.status === "failed" ? <AlertTriangle className="w-6 h-6 text-rose-600" /> : 
                 <RefreshCw className="w-6 h-6 animate-spin text-blue-600" />}
                <span className="text-slate-900 dark:text-white">Job Status:</span>
                <span className={`uppercase text-xs px-3 py-1.5 rounded-full font-bold ${jobStatus.status === 'completed' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300' : jobStatus.status === 'failed' ? 'bg-rose-100 text-rose-800 dark:bg-rose-900/50 dark:text-rose-300' : 'bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300'}`}>{jobStatus.status}</span>
              </h4>
              
              <div className="w-full bg-slate-200 dark:bg-slate-800 rounded-full h-3 mb-3 overflow-hidden">
                <div 
                  className={`h-3 rounded-full transition-all duration-500 ${jobStatus.status === "failed" ? 'bg-rose-500' : 'bg-blue-500'}`} 
                  style={{ width: `${Math.max(jobStatus.progress_pct || 0, 5)}%` }}
                ></div>
              </div>
              
              <p className="text-slate-600 dark:text-gray-400 font-mono text-sm">{jobStatus.message || "Waiting in queue..."}</p>
            </div>
          )}
        </section>

        {/* Database Cleanup - Rose/Red Accent */}
        <section className="bg-white dark:bg-slate-800 rounded-2xl p-6 border border-slate-200 dark:border-slate-700 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-[0_4px_16px_rgba(244,63,94,0.1)] transition-shadow">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2.5 rounded-xl bg-linear-to-br from-rose-50 to-red-50 dark:bg-rose-900/50 border border-rose-200 dark:border-rose-800">
              <Trash2 className="w-6 h-6 text-rose-600 dark:text-rose-400" />
            </div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-white">Database Cleanup</h3>
          </div>
          <p className="text-slate-600 dark:text-gray-400 text-sm mb-6">Delete all data from the database except your settings. This action cannot be undone.</p>
          
          {cleanupResult && cleanupResult.status === "success" && (
            <div className="mb-4 bg-emerald-50 dark:bg-emerald-900/30 border border-emerald-200 dark:border-emerald-800 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
                <span className="font-bold text-emerald-800 dark:text-emerald-300">Cleanup Successful</span>
              </div>
              <div className="text-sm text-slate-700 dark:text-gray-300 space-y-1">
                {Object.entries(cleanupResult.deleted_counts || {}).map(([table, count]) => (
                  <div key={table} className="flex justify-between">
                    <span>{table}:</span>
                    <span className="font-mono">{String(count)} rows</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {!showCleanupConfirm ? (
            <button
              onClick={() => setShowCleanupConfirm(true)}
              className="w-full px-6 py-4 bg-rose-50 hover:bg-rose-100 dark:bg-rose-900/30 dark:hover:bg-rose-900/50 text-rose-700 dark:text-rose-400 border-2 border-rose-200 dark:border-rose-800 rounded-xl font-semibold transition-all flex items-center justify-center gap-2"
            >
              <Trash2 className="w-5 h-5" /> Clean Database
            </button>
          ) : (
            <div className="space-y-4">
              <div className="bg-rose-50 dark:bg-rose-900/30 border border-rose-200 dark:border-rose-800 rounded-xl p-4">
                <p className="text-rose-800 dark:text-rose-300 font-bold mb-2 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5" /> Warning
                </p>
                <p className="text-slate-700 dark:text-gray-300 text-sm">This will permanently delete all movies, TV series, anime, records, and other data. Your settings will be preserved.</p>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={() => setShowCleanupConfirm(false)}
                  disabled={cleaning}
                  className="flex-1 px-4 py-3 bg-slate-100 hover:bg-slate-200 dark:bg-slate-700 dark:hover:bg-slate-600 text-slate-800 dark:text-gray-200 rounded-xl font-semibold transition-all disabled:opacity-50"
                >
                  Cancel
                </button>
                <button
                  onClick={handleCleanup}
                  disabled={cleaning}
                  className="flex-1 px-4 py-3 bg-rose-600 hover:bg-rose-500 text-white rounded-xl font-semibold transition-all disabled:opacity-50 flex items-center justify-center gap-2 shadow-sm"
                >
                  {cleaning ? <RefreshCw className="w-5 h-5 animate-spin" /> : <Trash2 className="w-5 h-5" />}
                  {cleaning ? "Cleaning..." : "Confirm Cleanup"}
                </button>
              </div>
            </div>
          )}
        </section>

        {/* Save Button - Teal/Emerald Gradient */}
        <button
          onClick={saveSettings}
          className="w-full px-6 py-5 bg-linear-to-r from-teal-500 via-emerald-500 to-green-500 hover:from-teal-400 hover:via-emerald-400 hover:to-green-400 text-white rounded-xl font-bold text-lg transition-all shadow-lg shadow-emerald-200 hover:shadow-xl flex justify-center items-center gap-3"
        >
          {saved ? <CheckCircle className="w-6 h-6" /> : <Save className="w-6 h-6" />}
          {saved ? "Settings Saved!" : "Save Settings"}
        </button>
      </div>
    </div>
  );
}
