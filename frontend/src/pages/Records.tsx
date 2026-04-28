import { useState, useEffect } from "react";
import { Trophy, Globe, Loader2, PlayCircle, Star, Filter, RefreshCw, Trash2, Calendar, TrendingUp, Clock, CalendarDays, BarChart3, Award, Zap } from "lucide-react";

export default function Records() {
  const [savedRecords, setSavedRecords] = useState<any[]>([]);
  const [activeRecordId, setActiveRecordId] = useState<number | null>(null);
  const [entries, setEntries] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [scraping, setScraping] = useState(false);

  const [activeTab, setActiveTab] = useState<"bom" | "sacnilk">("bom");
  const [bomCategory, setBomCategory] = useState("chart-links");
  const [sacnilkCategory, setSacnilkCategory] = useState("box-office-records/Highest_Day_Wise_Collection_List");

  // BOM parameter states
  const [bomYear, setBomYear] = useState(new Date().getFullYear());
  const [bomView, setBomView] = useState("year");
  const [bomInterval, setBomInterval] = useState("");
  const [bomByType, setBomByType] = useState("year");
  const [bomValue, setBomValue] = useState("");
  const [bomGrossesOption, setBomGrossesOption] = useState("totalGrosses");
  const [bomReleaseScale, setBomReleaseScale] = useState("all");
  const [bomDateStr, setBomDateStr] = useState("");
  const [bomHoliday, setBomHoliday] = useState("");

  useEffect(() => {
    fetchRecords();
  }, []);

  const fetchRecords = async () => {
    const res = await fetch("http://localhost:8000/api/records/list");
    const data = await res.json();
    setSavedRecords(data);
    if (data.length > 0 && !activeRecordId) {
      loadEntries(data[0].id);
    }
  };

  const loadEntries = async (id: number) => {
    setActiveRecordId(id);
    setLoading(true);
    const res = await fetch(`http://localhost:8000/api/records/${id}`);
    const data = await res.json();
    setEntries(data);
    setLoading(false);
  };

  const handleBOMScrape = async () => {
    setScraping(true);
    try {
      let url = `http://localhost:8000/api/records/bom/${bomCategory}`;
      const params = new URLSearchParams();
      
      if (bomCategory === "daily") {
        params.append("year", bomYear.toString());
        params.append("view", bomView);
        if (bomInterval) params.append("interval", bomInterval);
      } else if (bomCategory === "weekend" || bomCategory === "weekly") {
        if (bomByType) params.append("by_type", bomByType);
        if (bomValue) params.append("value", bomValue);
      } else if (bomCategory === "monthly" || bomCategory === "quarterly") {
        if (bomByType) params.append("by_type", bomByType);
        if (bomValue) params.append("value", bomValue);
        params.append("grosses_option", bomGrossesOption);
        params.append("release_scale", bomReleaseScale);
      } else if (bomCategory === "yearly") {
        params.append("view", bomView);
        if (bomYear) params.append("year", bomYear.toString());
        if (bomInterval) params.append("interval", bomInterval);
      } else if (bomCategory === "season") {
        if (bomByType) params.append("by_type", bomByType);
        if (bomValue) params.append("value", bomValue);
        if (bomYear) params.append("year", bomYear.toString());
        params.append("grosses_option", bomGrossesOption);
      } else if (bomCategory === "holiday") {
        if (bomByType) params.append("by_type", bomByType);
        if (bomYear) params.append("year", bomYear.toString());
        if (bomHoliday) params.append("holiday", bomHoliday);
      } else if (bomCategory === "calendar" && bomDateStr) {
        params.append("date_str", bomDateStr);
      }
      
      if (params.toString()) url += `?${params.toString()}`;
      
      const res = await fetch(url);
      const data = await res.json();
      
      // Store as a record
      const recordRes = await fetch("http://localhost:8000/api/records/scrape?source=bom&category=bom-" + bomCategory + "&path=" + bomCategory);
      if (recordRes.ok) {
        await fetchRecords();
      }
    } catch (e) {
      console.error(e);
    }
    setScraping(false);
  };

  const handleSacnilkScrape = async () => {
    setScraping(true);
    try {
      const res = await fetch(`http://localhost:8000/api/records/scrape?source=sacnilk&category=${sacnilkCategory}`);
      if (res.ok) {
        await fetchRecords();
      }
    } catch (e) {
      console.error(e);
    }
    setScraping(false);
  };

  const clearRecords = async () => {
    if (!confirm("Are you sure you want to delete all saved records? This cannot be undone.")) return;
    try {
      const res = await fetch("http://localhost:8000/api/records/clear", { method: "DELETE" });
      if (res.ok) {
        setSavedRecords([]);
        setEntries([]);
        setActiveRecordId(null);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const bomCategories = [
    { id: "chart-links", name: "Chart Links", icon: Globe, description: "All-time chart sub-links" },
    { id: "calendar", name: "Release Calendar", icon: Calendar, description: "Upcoming releases" },
    { id: "calendar-changes", name: "Calendar Changes", icon: CalendarDays, description: "Release date changes" },
    { id: "showdowns", name: "Showdowns", icon: Zap, description: "Box office showdowns" },
    { id: "daily", name: "Daily Views", icon: Clock, description: "Daily earnings by date" },
    { id: "weekend", name: "Weekend Views", icon: TrendingUp, description: "Weekend rankings" },
    { id: "weekly", name: "Weekly Views", icon: BarChart3, description: "Weekly rankings" },
    { id: "monthly", name: "Monthly Views", icon: Calendar, description: "Monthly rankings" },
    { id: "quarterly", name: "Quarterly Views", icon: Award, description: "Quarterly rankings" },
    { id: "yearly", name: "Yearly Views", icon: Trophy, description: "Yearly rankings" },
    { id: "season", name: "Season Views", icon: CalendarDays, description: "Season rankings" },
    { id: "holiday-list", name: "Holiday List", icon: Calendar, description: "Available holidays" },
    { id: "holiday", name: "Holiday Views", icon: Star, description: "Holiday rankings" },
  ];

  const renderBOMParams = () => {
    switch (bomCategory) {
      case "daily":
        return (
          <div className="space-y-3">
            <div>
              <label className="text-xs text-slate-600 dark:text-slate-400 mb-1 block">Year</label>
              <input 
                type="number" 
                value={bomYear}
                onChange={e => setBomYear(parseInt(e.target.value))}
                className="w-full bg-white dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-lg p-2 text-sm text-slate-800 dark:text-slate-200"
              />
            </div>
            <div>
              <label className="text-xs text-slate-600 dark:text-slate-400 mb-1 block">View Type</label>
              <select 
                value={bomView}
                onChange={e => setBomView(e.target.value)}
                className="w-full bg-white dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-lg p-2 text-sm text-slate-800 dark:text-slate-200"
              >
                <option value="year">Year</option>
                <option value="season">Season</option>
                <option value="quarter">Quarter</option>
                <option value="month">Month</option>
                <option value="holiday">Holiday</option>
                <option value="cumulative">Cumulative</option>
              </select>
            </div>
            {(bomView === "season" || bomView === "cumulative") && (
              <div>
                <label className="text-xs text-slate-600 dark:text-slate-400 mb-1 block">Interval</label>
                <input 
                  type="text"
                  value={bomInterval}
                  onChange={e => setBomInterval(e.target.value)}
                  placeholder={bomView === "season" ? "winter, spring, summer, fall" : "year_to_date or cumulative_march"}
                  className="w-full bg-white dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-lg p-2 text-sm text-slate-800 dark:text-slate-200"
                />
              </div>
            )}
          </div>
        );
      case "weekend":
      case "weekly":
        return (
          <div className="space-y-3">
            <div>
              <label className="text-xs text-slate-600 dark:text-slate-400 mb-1 block">By Type</label>
              <select 
                value={bomByType}
                onChange={e => setBomByType(e.target.value)}
                className="w-full bg-white dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-lg p-2 text-sm text-slate-800 dark:text-slate-200"
              >
                <option value="year">By Year</option>
                <option value="week">By Week</option>
              </select>
            </div>
            {bomByType === "week" && (
              <div>
                <label className="text-xs text-slate-600 dark:text-slate-400 mb-1 block">Week Number (1-53)</label>
                <input 
                  type="number"
                  value={bomValue}
                  onChange={e => setBomValue(e.target.value)}
                  className="w-full bg-white dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-lg p-2 text-sm text-slate-800 dark:text-slate-200"
                />
              </div>
            )}
            {bomByType === "year" && (
              <div>
                <label className="text-xs text-slate-600 dark:text-slate-400 mb-1 block">Year</label>
                <input 
                  type="number"
                  value={bomValue}
                  onChange={e => setBomValue(e.target.value)}
                  className="w-full bg-white dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-lg p-2 text-sm text-slate-800 dark:text-slate-200"
                />
              </div>
            )}
          </div>
        );
      case "monthly":
      case "quarterly":
        return (
          <div className="space-y-3">
            <div>
              <label className="text-xs text-slate-600 dark:text-slate-400 mb-1 block">By Type</label>
              <select 
                value={bomByType}
                onChange={e => setBomByType(e.target.value)}
                className="w-full bg-white dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-lg p-2 text-sm text-slate-800 dark:text-slate-200"
              >
                <option value="month">By Month</option>
                <option value="year">By Year</option>
                <option value="to-date">To Date</option>
              </select>
            </div>
            {bomByType !== "to-date" && (
              <div>
                <label className="text-xs text-slate-600 dark:text-slate-400 mb-1 block">Value</label>
                <input 
                  type="text"
                  value={bomValue}
                  onChange={e => setBomValue(e.target.value)}
                  placeholder={bomByType === "month" ? "february, march..." : "2024, 2025..."}
                  className="w-full bg-white dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-lg p-2 text-sm text-slate-800 dark:text-slate-200"
                />
              </div>
            )}
            {bomByType === "to-date" && (
              <div>
                <label className="text-xs text-slate-600 dark:text-slate-400 mb-1 block">Year</label>
                <input 
                  type="number"
                  value={bomValue}
                  onChange={e => setBomValue(e.target.value)}
                  className="w-full bg-white dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-lg p-2 text-sm text-slate-800 dark:text-slate-200"
                />
              </div>
            )}
            <div>
              <label className="text-xs text-slate-600 dark:text-slate-400 mb-1 block">Grosses Option</label>
              <select 
                value={bomGrossesOption}
                onChange={e => setBomGrossesOption(e.target.value)}
                className="w-full bg-white dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-lg p-2 text-sm text-slate-800 dark:text-slate-200"
              >
                <option value="totalGrosses">Total Grosses</option>
                <option value="calendarGrosses">Calendar Grosses</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-600 dark:text-slate-400 mb-1 block">Release Scale</label>
              <select 
                value={bomReleaseScale}
                onChange={e => setBomReleaseScale(e.target.value)}
                className="w-full bg-white dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-lg p-2 text-sm text-slate-800 dark:text-slate-200"
              >
                <option value="all">All</option>
                <option value="wide">Wide</option>
                <option value="limited">Limited</option>
              </select>
            </div>
          </div>
        );
      case "yearly":
        return (
          <div className="space-y-3">
            <div>
              <label className="text-xs text-slate-600 dark:text-slate-400 mb-1 block">View</label>
              <select 
                value={bomView}
                onChange={e => setBomView(e.target.value)}
                className="w-full bg-white dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-lg p-2 text-sm text-slate-800 dark:text-slate-200"
              >
                <option value="overview">Overview</option>
                <option value="ytd">YTD Comparison</option>
              </select>
            </div>
            {bomView === "ytd" && (
              <>
                <div>
                  <label className="text-xs text-slate-600 dark:text-slate-400 mb-1 block">Year</label>
                  <input 
                    type="number"
                    value={bomYear}
                    onChange={e => setBomYear(parseInt(e.target.value))}
                    className="w-full bg-white dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-lg p-2 text-sm text-slate-800 dark:text-slate-200"
                  />
                </div>
                <div>
                  <label className="text-xs text-slate-600 dark:text-slate-400 mb-1 block">Interval (optional)</label>
                  <input 
                    type="text"
                    value={bomInterval}
                    onChange={e => setBomInterval(e.target.value)}
                    placeholder="year_to_date or cumulative_march"
                    className="w-full bg-white dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-lg p-2 text-sm text-slate-800 dark:text-slate-200"
                  />
                </div>
              </>
            )}
          </div>
        );
      case "season":
        return (
          <div className="space-y-3">
            <div>
              <label className="text-xs text-slate-600 dark:text-slate-400 mb-1 block">By Type</label>
              <select 
                value={bomByType}
                onChange={e => setBomByType(e.target.value)}
                className="w-full bg-white dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-lg p-2 text-sm text-slate-800 dark:text-slate-200"
              >
                <option value="season">By Season</option>
                <option value="year">By Year</option>
                <option value="to-date">To Date</option>
              </select>
            </div>
            {bomByType === "season" && (
              <div>
                <label className="text-xs text-slate-600 dark:text-slate-400 mb-1 block">Season</label>
                <select 
                  value={bomValue}
                  onChange={e => setBomValue(e.target.value)}
                  className="w-full bg-white dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-lg p-2 text-sm text-slate-800 dark:text-slate-200"
                >
                  <option value="winter">Winter</option>
                  <option value="spring">Spring</option>
                  <option value="summer">Summer</option>
                  <option value="fall">Fall</option>
                </select>
              </div>
            )}
            {(bomByType === "year" || bomByType === "to-date") && (
              <div>
                <label className="text-xs text-slate-600 dark:text-slate-400 mb-1 block">Year</label>
                <input 
                  type="number"
                  value={bomYear}
                  onChange={e => setBomYear(parseInt(e.target.value))}
                  className="w-full bg-white dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-lg p-2 text-sm text-slate-800 dark:text-slate-200"
                />
              </div>
            )}
            <div>
              <label className="text-xs text-slate-600 dark:text-slate-400 mb-1 block">Grosses Option</label>
              <select 
                value={bomGrossesOption}
                onChange={e => setBomGrossesOption(e.target.value)}
                className="w-full bg-white dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-lg p-2 text-sm text-slate-800 dark:text-slate-200"
              >
                <option value="calendarGrosses">Calendar Grosses</option>
                <option value="totalGrosses">Total Grosses</option>
              </select>
            </div>
          </div>
        );
      case "holiday":
        return (
          <div className="space-y-3">
            <div>
              <label className="text-xs text-slate-600 dark:text-slate-400 mb-1 block">By Type</label>
              <select 
                value={bomByType}
                onChange={e => setBomByType(e.target.value)}
                className="w-full bg-white dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-lg p-2 text-sm text-slate-800 dark:text-slate-200"
              >
                <option value="year">By Year</option>
                <option value="holiday">By Holiday</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-600 dark:text-slate-400 mb-1 block">Year</label>
              <input 
                type="number"
                value={bomYear}
                onChange={e => setBomYear(parseInt(e.target.value))}
                className="w-full bg-white dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-lg p-2 text-sm text-slate-800 dark:text-slate-200"
              />
            </div>
            {bomByType === "holiday" && (
              <div>
                <label className="text-xs text-slate-600 dark:text-slate-400 mb-1 block">Holiday</label>
                <input 
                  type="text"
                  value={bomHoliday}
                  onChange={e => setBomHoliday(e.target.value)}
                  placeholder="e.g., easter_sunday"
                  className="w-full bg-white dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-lg p-2 text-sm text-slate-800 dark:text-slate-200"
                />
              </div>
            )}
          </div>
        );
      case "calendar":
        return (
          <div>
            <label className="text-xs text-slate-600 dark:text-slate-400 mb-1 block">Date (YYYY-MM-DD, optional)</label>
            <input 
              type="text"
              value={bomDateStr}
              onChange={e => setBomDateStr(e.target.value)}
              placeholder="2025-03-01"
              className="w-full bg-white dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-lg p-2 text-sm text-slate-800 dark:text-slate-200"
            />
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="max-w-7xl mx-auto pb-12">
      {/* Modern Header */}
      <header className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-3 rounded-2xl bg-amber-100 dark:bg-amber-500/20 border border-amber-200 dark:border-amber-500/30 shadow-sm">
            <Trophy className="w-8 h-8 text-amber-600 dark:text-amber-400" />
          </div>
          <div>
            <h2 className="text-4xl font-black text-slate-900 dark:text-slate-100 tracking-tight">Hall of Fame</h2>
            <p className="text-slate-600 dark:text-slate-400 mt-1">Global and Regional Box Office Records.</p>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar Controls */}
        <div className="space-y-6">
          {/* Source Tabs */}
          <div className="bg-white dark:bg-slate-800/50 p-2 rounded-2xl border border-slate-200 dark:border-slate-700/50 shadow-sm">
            <div className="flex gap-2">
              <button
                onClick={() => setActiveTab("bom")}
                className={`flex-1 p-3 rounded-xl font-bold text-sm transition-all flex items-center justify-center gap-2 ${activeTab === "bom" ? 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400 border border-blue-200 dark:border-blue-500/30' : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700/30'}`}
              >
                <Globe className="w-4 h-4" />
                BOM
              </button>
              <button
                onClick={() => setActiveTab("sacnilk")}
                className={`flex-1 p-3 rounded-xl font-bold text-sm transition-all flex items-center justify-center gap-2 ${activeTab === "sacnilk" ? 'bg-amber-100 dark:bg-amber-500/20 text-amber-700 dark:text-amber-400 border border-amber-200 dark:border-amber-500/30' : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700/30'}`}
              >
                <Star className="w-4 h-4 fill-current" />
                Sacnilk
              </button>
            </div>
          </div>

          {/* BOM Categories */}
          {activeTab === "bom" && (
            <div className="bg-white dark:bg-slate-800/50 p-4 rounded-2xl border border-slate-200 dark:border-slate-700/50 shadow-sm">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-1 h-5 bg-linear-to-b from-blue-500 to-cyan-500 rounded-full" />
                <h3 className="font-bold text-lg text-slate-900 dark:text-slate-100">BOM Categories</h3>
              </div>
              <div className="grid grid-cols-2 gap-2 max-h-80 overflow-y-auto custom-scrollbar pr-2">
                {bomCategories.map(cat => {
                  const Icon = cat.icon;
                  return (
                    <button
                      key={cat.id}
                      onClick={() => setBomCategory(cat.id)}
                      className={`p-3 rounded-xl text-left transition-all ${bomCategory === cat.id ? 'bg-blue-100 dark:bg-blue-500/20 border border-blue-200 dark:border-blue-500/30' : 'bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700/30 hover:border-slate-300 dark:hover:border-slate-600'}`}
                    >
                      <Icon className={`w-5 h-5 mb-1 ${bomCategory === cat.id ? 'text-blue-600 dark:text-blue-400' : 'text-slate-500'}`} />
                      <div className="text-xs font-bold text-slate-700 dark:text-slate-200">{cat.name}</div>
                      <div className="text-[10px] text-slate-500 truncate">{cat.description}</div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Parameters */}
          <div className="bg-white dark:bg-slate-800/50 p-4 rounded-2xl border border-slate-200 dark:border-slate-700/50 shadow-sm">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-1 h-5 bg-linear-to-b from-purple-500 to-pink-500 rounded-full" />
              <h3 className="font-bold text-lg text-slate-900 dark:text-slate-100">Parameters</h3>
            </div>
            {activeTab === "bom" ? renderBOMParams() : (
              <div className="space-y-3">
                <select 
                  className="w-full bg-slate-50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700/50 rounded-xl p-3 text-sm text-slate-700 dark:text-slate-200 outline-none transition-all"
                  value={sacnilkCategory}
                  onChange={e => setSacnilkCategory(e.target.value)}
                >
                  <optgroup label="All-Time Records">
                    <option value="box-office-records/Top_Grossing_Indian_Movies_Of_All_Time">Top Grossing All-Time</option>
                    <option value="box-office-records/Highest_Day_Wise_Collection_List">Highest Day-Wise</option>
                    <option value="box-office-records/Highest_Week_Wise_Collection_List">Highest Week-Wise</option>
                    <option value="box-office-records/Highest_Month_Wise_Collection_List">Highest Month-Wise</option>
                    <option value="box-office-records/Highest_Year_Wise_Collection_List">Highest Year-Wise</option>
                  </optgroup>
                  <optgroup label="Regional Records">
                    <option value="box-office-records/tollywood">Tollywood Records</option>
                    <option value="box-office-records/kollywood">Kollywood Records</option>
                    <option value="box-office-records/mollywood">Mollywood Records</option>
                    <option value="box-office-records/sandalwood">Sandalwood Records</option>
                    <option value="box-office-records/punjabi">Punjabi Records</option>
                    <option value="box-office-records/marathi">Marathi Records</option>
                    <option value="box-office-records/bengali">Bengali Records</option>
                  </optgroup>
                  <optgroup label="Bollywood Clubs">
                    <option value="box-office-records/Bollywood_100_Cr_Club_All_Time">100 Cr Club</option>
                    <option value="box-office-records/Bollywood_200_Cr_Club_All_Time">200 Cr Club</option>
                    <option value="box-office-records/Bollywood_300_Cr_Club_All_Time">300 Cr Club</option>
                    <option value="box-office-records/Bollywood_400_Cr_Club_All_Time">400 Cr Club</option>
                    <option value="box-office-records/Bollywood_500_Cr_Club_All_Time">500 Cr Club</option>
                    <option value="box-office-records/Bollywood_1000_Cr_Club_All_Time">1000 Cr Club</option>
                  </optgroup>
                  <optgroup label="Fastest Milestones">
                    <option value="box-office-records/Bollywood_Fastest_10_Cr_Collection_Movies">Fastest 10 Cr</option>
                    <option value="box-office-records/Bollywood_Fastest_25_Cr_Collection_Movies">Fastest 25 Cr</option>
                    <option value="box-office-records/Bollywood_Fastest_50_Cr_Collection_Movies">Fastest 50 Cr</option>
                    <option value="box-office-records/Bollywood_Fastest_100_Cr_Collection_Movies">Fastest 100 Cr</option>
                    <option value="box-office-records/Bollywood_Fastest_200_Cr_Collection_Movies">Fastest 200 Cr</option>
                    <option value="box-office-records/Bollywood_Fastest_300_Cr_Collection_Movies">Fastest 300 Cr</option>
                    <option value="box-office-records/Bollywood_Fastest_500_Cr_Collection_Movies">Fastest 500 Cr</option>
                    <option value="box-office-records/Bollywood_Fastest_1000_Cr_Collection_Movies">Fastest 1000 Cr</option>
                  </optgroup>
                  <optgroup label="Yearly Collections">
                    <option value="news/Box_Office_Collection_2024">2024 Collection</option>
                    <option value="news/Box_Office_Collection_2025">2025 Collection</option>
                    <option value="news/South_Indian_Movies_Box_Office_Collection_2024">South Indian 2024</option>
                  </optgroup>
                  <optgroup label="Opening Records">
                    <option value="box-office-records/Highest_Opening_Day_Collection_List">Highest Opening Day</option>
                    <option value="box-office-records/Highest_Opening_Weekend_Collection_List">Highest Opening Weekend</option>
                    <option value="box-office-records/Highest_Opening_Week_Collection_List">Highest Opening Week</option>
                  </optgroup>
                </select>
              </div>
            )}

            <button 
              onClick={activeTab === "bom" ? handleBOMScrape : handleSacnilkScrape}
              disabled={scraping}
              className="w-full mt-4 bg-linear-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white p-3 rounded-xl font-bold text-sm transition-all shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 flex items-center justify-center gap-2 disabled:opacity-50 hover:-translate-y-0.5"
            >
              {scraping ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
              Pull Live Data
            </button>
          </div>

          {/* Saved Records */}
          <div className="bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700/50 shadow-sm overflow-hidden">
            <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-900/50 border-b border-slate-200 dark:border-slate-700/50">
              <div className="flex items-center gap-2">
                <div className="w-1 h-5 bg-linear-to-b from-amber-500 to-yellow-500 rounded-full" />
                <h3 className="font-bold text-lg text-slate-900 dark:text-slate-100">Saved Records</h3>
              </div>
              {savedRecords.length > 0 && (
                <button
                  onClick={clearRecords}
                  className="p-2 rounded-lg bg-rose-50 dark:bg-red-500/10 hover:bg-rose-100 dark:hover:bg-red-500/20 text-rose-600 dark:text-red-400 hover:text-rose-700 dark:hover:text-red-300 border border-rose-200 dark:border-red-500/20 transition-all"
                  title="Clear all records"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>
            <div className="max-h-48 overflow-y-auto custom-scrollbar">
              {savedRecords.map(r => (
                <button 
                  key={r.id}
                  onClick={() => loadEntries(r.id)}
                  className={`w-full text-left p-3 text-sm font-semibold border-b border-slate-200 dark:border-slate-700/30 transition-all flex items-center gap-2 ${activeRecordId === r.id ? 'bg-blue-50 dark:bg-blue-500/10 text-blue-700 dark:text-blue-400 border-l-4 border-l-blue-500' : 'hover:bg-slate-100 dark:hover:bg-slate-700/30 text-slate-700 dark:text-slate-300'}`}
                >
                  {r.source === 'bom' ? <Globe className="w-3 h-3 shrink-0 text-slate-500 dark:text-slate-400" /> : <Star className="w-3 h-3 shrink-0 text-amber-500 dark:text-amber-400 fill-current" />}
                  <span className="truncate">{r.title}</span>
                </button>
              ))}
              {savedRecords.length === 0 && <div className="p-4 text-sm text-slate-500">No records saved yet.</div>}
            </div>
          </div>
        </div>

        {/* Record Entries Table */}
        <div className="lg:col-span-3">
          <div className="bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700/50 shadow-sm overflow-hidden">
            {loading ? (
              <div className="h-96 flex items-center justify-center">
                <div className="flex flex-col items-center gap-4">
                  <Loader2 className="w-10 h-10 animate-spin text-amber-500" />
                  <p className="text-slate-500 animate-pulse">Loading records...</p>
                </div>
              </div>
            ) : entries.length > 0 ? (
              <div className="overflow-x-auto custom-scrollbar max-h-[600px]">
                <table className="w-full text-left">
                  <thead className="bg-slate-100 dark:bg-slate-900/80 sticky top-0 z-10 shadow-sm text-slate-600 dark:text-slate-400">
                    <tr>
                      <th className="p-4 w-20 text-center font-bold uppercase text-xs tracking-wider">#</th>
                      <th className="p-4 font-bold uppercase text-xs tracking-wider">Movie Title</th>
                      {(() => {
                        try {
                          const firstMetrics = JSON.parse(entries[0].primary_value);
                          if (typeof firstMetrics === 'object' && firstMetrics !== null) {
                            return Object.keys(firstMetrics).map(k => (
                              <th key={k} className="p-4 text-right uppercase text-xs font-bold tracking-wider">{k}</th>
                            ));
                          }
                        } catch(e) {}
                        return <th className="p-4 text-right uppercase text-xs font-bold tracking-wider">Collection</th>;
                      })()}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200 dark:divide-slate-700/30">
                    {entries.map((e, idx) => {
                      let parsedMetrics = null;
                      try {
                        parsedMetrics = JSON.parse(e.primary_value);
                      } catch(err) {}

                      return (
                        <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors">
                          <td className="p-4 text-center font-black text-slate-500">{e.rank || idx + 1}</td>
                          <td className="p-4 font-bold text-slate-900 dark:text-slate-100 flex items-center gap-3 whitespace-nowrap">
                            {idx < 3 && <Trophy className={`w-5 h-5 shrink-0 ${idx === 0 ? 'text-amber-500' : idx === 1 ? 'text-slate-400' : 'text-amber-600'}`} />}
                            {e.movie_title}
                          </td>
                          {parsedMetrics && typeof parsedMetrics === 'object' ? (
                            Object.values(parsedMetrics).map((v: any, i) => (
                              <td key={i} className="p-4 text-right font-mono text-emerald-600 dark:text-emerald-400 font-bold whitespace-nowrap">
                                {typeof v === 'number' ? `₹${v} Cr` : v}
                              </td>
                            ))
                          ) : (
                            <td className="p-4 text-right font-mono text-emerald-600 dark:text-emerald-400 font-bold whitespace-nowrap">{e.primary_value}</td>
                          )}
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="h-96 flex items-center justify-center text-slate-500 flex-col gap-4">
                <div className="p-8 rounded-3xl bg-slate-100 dark:bg-slate-800/30 border border-slate-200 dark:border-slate-700/30">
                  <PlayCircle className="w-16 h-16 text-slate-400 dark:text-slate-600" />
                </div>
                <p className="text-lg text-slate-600">Select a record from the sidebar to view its leaderboard.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
