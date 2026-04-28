import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import Home from "./pages/Home";
import Movies from "./pages/Movies";
import Compare from "./pages/Compare";
import Settings from "./pages/Settings";
import Search from "./pages/Search";
import Records from "./pages/Records";
import Franchises from "./pages/Franchises";
import DiscoverView from "./pages/DiscoverView";
import TVSeries from "./pages/TVSeries";
import Anime from "./pages/Anime";
import Watchlist from "./pages/Watchlist";
import WesternAnimation from "./pages/WesternAnimation";
import Cartoons from "./pages/Cartoons";
import OnThisDay from "./pages/OnThisDay";
import About from "./pages/About";
import { Film, Home as HomeIcon, Settings as SettingsIcon, BarChart2, Tv, Menu, ChevronLeft, Search as SearchIcon, Calendar, TrendingUp, Activity, PlayCircle, Star, Trophy, FolderHeart, Flame, Sun, Moon, Heart, Clapperboard, Baby, Info } from "lucide-react";

export default function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved !== null ? JSON.parse(saved) : true;
  });

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(isDarkMode));
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  // Listen for storage events from other tabs/components (e.g., Settings page)
  useEffect(() => {
    const handleStorage = (e: StorageEvent) => {
      if (e.key === 'darkMode' && e.newValue !== null) {
        setIsDarkMode(JSON.parse(e.newValue));
      }
    };
    window.addEventListener('storage', handleStorage);
    return () => window.removeEventListener('storage', handleStorage);
  }, []);

  const Placeholder = ({ title }: { title: string }) => (
    <div className="p-8">
      <h2 className="text-3xl font-bold flex items-center gap-3">{title}</h2>
      <p className="text-gray-400 mt-2">Coming soon to the SPA migration (Phase 3 Records Expansion).</p>
    </div>
  );

  return (
    <BrowserRouter>
      <AppContent 
        isDarkMode={isDarkMode} 
        setIsDarkMode={setIsDarkMode} 
        isSidebarOpen={isSidebarOpen} 
        setIsSidebarOpen={setIsSidebarOpen} 
      />
    </BrowserRouter>
  );
}

function AppContent({ isDarkMode, setIsDarkMode, isSidebarOpen, setIsSidebarOpen }: { 
  isDarkMode: boolean; 
  setIsDarkMode: (v: boolean) => void; 
  isSidebarOpen: boolean; 
  setIsSidebarOpen: (v: boolean) => void;
}) {
  const location = useLocation();
  const isActive = (path: string) => location.pathname === path;

  return (
    <div className={`flex h-screen font-sans ${isDarkMode ? 'bg-slate-950 text-slate-100' : 'bg-[#F9FAFB] text-slate-900'}`}>
      {/* Modern Glassmorphism Sidebar */}
      <nav className={`${isSidebarOpen ? 'w-64' : 'w-20'} ${isDarkMode ? 'bg-slate-900/80 border-slate-800' : 'bg-white border-slate-200'} backdrop-blur-xl flex flex-col border-r shadow-[0_1px_3px_rgba(0,0,0,0.04)] transition-all duration-500 ease-out relative z-20`}>
        <button 
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          className="absolute -right-3 top-8 bg-linear-to-br from-blue-500 to-indigo-600 rounded-full p-1.5 shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50 hover:scale-110 transition-all duration-300 z-50 hidden md:block group"
        >
          {isSidebarOpen ? <ChevronLeft className="w-4 h-4 text-white group-hover:-translate-x-0.5 transition-transform" /> : <Menu className="w-4 h-4 text-white group-hover:translate-x-0.5 transition-transform" />}
        </button>
          
          <div className="flex-1 overflow-y-auto overflow-x-hidden custom-scrollbar flex flex-col w-full">
            {/* Logo Section */}
            <div className={`p-6 mb-4 flex items-center gap-3 transition-all duration-300 ${!isSidebarOpen && 'justify-center'}`}>
              <div className="relative">
                <div className="absolute inset-0 bg-linear-to-br from-blue-500 to-indigo-600 rounded-xl blur-lg opacity-40" />
                <div className="relative bg-linear-to-br from-blue-500 to-indigo-600 rounded-xl p-2 shadow-lg">
                  <Film className="text-white w-5 h-5" />
                </div>
              </div>
              {isSidebarOpen && <h1 className="text-2xl font-bold bg-linear-to-br from-blue-400 via-indigo-400 to-purple-400 text-transparent bg-clip-text whitespace-nowrap tracking-tight">CineStats</h1>}
            </div>
          
          <div className="flex flex-col gap-1 px-3 text-sm">
            {/* NavLink component for consistent active states */}
            <Link to="/" className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative overflow-hidden ${isActive('/') ? (isDarkMode ? 'bg-blue-500/10 text-blue-400' : 'bg-blue-50 text-blue-700 border border-blue-100') : (isDarkMode ? 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/50' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100')}`} title="Dashboard">
              <HomeIcon className={`w-5 h-5 transition-transform duration-200 group-hover:scale-110 ${isActive('/') && 'text-blue-500'}`} /> 
              {isSidebarOpen && <span className="whitespace-nowrap font-medium">Home</span>}
              {isActive('/') && <div className="absolute left-0 w-1 h-6 bg-linear-to-b from-blue-400 to-indigo-500 rounded-r-full" />}
            </Link>
            <Link to="/search" className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative overflow-hidden ${isActive('/search') ? (isDarkMode ? 'bg-blue-500/10 text-blue-400' : 'bg-blue-50 text-blue-700 border border-blue-100') : (isDarkMode ? 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/50' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100')}`} title="Global Search">
              <SearchIcon className={`w-5 h-5 transition-transform duration-200 group-hover:scale-110 ${isActive('/search') && 'text-blue-500'}`} /> 
              {isSidebarOpen && <span className="whitespace-nowrap font-medium">Global Search</span>}
              {isActive('/search') && <div className="absolute left-0 w-1 h-6 bg-linear-to-b from-blue-400 to-indigo-500 rounded-r-full" />}
            </Link>
            <Link to="/movies" className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative overflow-hidden ${isActive('/movies') ? (isDarkMode ? 'bg-blue-500/10 text-blue-400' : 'bg-blue-50 text-blue-700 border border-blue-100') : (isDarkMode ? 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/50' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100')}`} title="Movies">
              <Film className={`w-5 h-5 transition-transform duration-200 group-hover:scale-110 ${isActive('/movies') && 'text-blue-500'}`} /> 
              {isSidebarOpen && <span className="whitespace-nowrap font-medium">Movies</span>}
              {isActive('/movies') && <div className="absolute left-0 w-1 h-6 bg-linear-to-b from-blue-400 to-indigo-500 rounded-r-full" />}
            </Link>
            <Link to="/compare" className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative overflow-hidden ${isActive('/compare') ? (isDarkMode ? 'bg-blue-500/10 text-blue-400' : 'bg-blue-50 text-blue-700 border border-blue-100') : (isDarkMode ? 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/50' : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100')}`} title="Compare Media">
              <BarChart2 className={`w-5 h-5 transition-transform duration-200 group-hover:scale-110 ${isActive('/compare') && 'text-blue-500'}`} /> 
              {isSidebarOpen && <span className="whitespace-nowrap font-medium">Compare</span>}
              {isActive('/compare') && <div className="absolute left-0 w-1 h-6 bg-linear-to-b from-blue-400 to-indigo-500 rounded-r-full" />}
            </Link>
            <Link to="/watchlist" className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative overflow-hidden ${isActive('/watchlist') ? (isDarkMode ? 'bg-rose-500/10 text-rose-400' : 'bg-rose-50 text-rose-600') : (isDarkMode ? 'text-slate-400 hover:text-rose-400 hover:bg-rose-500/5' : 'text-slate-600 hover:text-rose-600 hover:bg-rose-50/50')}`} title="Watchlist">
              <Heart className={`w-5 h-5 transition-transform duration-200 group-hover:scale-110 ${isActive('/watchlist') ? 'text-rose-500' : 'text-rose-400'}`} /> 
              {isSidebarOpen && <span className="whitespace-nowrap font-medium">Watchlist</span>}
              {isActive('/watchlist') && <div className="absolute left-0 w-1 h-6 bg-linear-to-b from-rose-400 to-pink-500 rounded-r-full" />}
            </Link>
            
            {isSidebarOpen && <div className={`text-[10px] font-bold uppercase tracking-[0.2em] mt-6 mb-3 px-3 ${isDarkMode ? 'text-slate-500' : 'text-slate-400'}`}>Discover</div>}
            
            <Link to="/records" className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative overflow-hidden ${isActive('/records') ? (isDarkMode ? 'bg-amber-500/10 text-amber-400' : 'bg-amber-50 text-amber-600') : (isDarkMode ? 'text-slate-400 hover:text-amber-400 hover:bg-amber-500/5' : 'text-slate-600 hover:text-amber-600 hover:bg-amber-50/50')}`} title="Hall of Fame">
              <Trophy className={`w-5 h-5 transition-transform duration-200 group-hover:scale-110 ${isActive('/records') ? 'text-amber-500' : 'text-amber-400'}`} /> 
              {isSidebarOpen && <span className="whitespace-nowrap font-medium">Hall of Fame</span>}
              {isActive('/records') && <div className="absolute left-0 w-1 h-6 bg-linear-to-b from-amber-400 to-orange-500 rounded-r-full" />}
            </Link>
            <Link to="/franchises" className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative overflow-hidden ${isActive('/franchises') ? (isDarkMode ? 'bg-pink-500/10 text-pink-400' : 'bg-pink-50 text-pink-600') : (isDarkMode ? 'text-slate-400 hover:text-pink-400 hover:bg-pink-500/5' : 'text-slate-600 hover:text-pink-600 hover:bg-pink-50/50')}`} title="Franchises">
              <FolderHeart className={`w-5 h-5 transition-transform duration-200 group-hover:scale-110 ${isActive('/franchises') ? 'text-pink-500' : 'text-pink-400'}`} /> 
              {isSidebarOpen && <span className="whitespace-nowrap font-medium">Franchises</span>}
              {isActive('/franchises') && <div className="absolute left-0 w-1 h-6 bg-linear-to-b from-pink-400 to-rose-500 rounded-r-full" />}
            </Link>
            
            <Link to="/in-theatres" className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative overflow-hidden ${isActive('/in-theatres') ? (isDarkMode ? 'bg-red-500/10 text-red-400' : 'bg-red-50 text-red-600') : (isDarkMode ? 'text-slate-400 hover:text-red-400 hover:bg-red-500/5' : 'text-slate-600 hover:text-red-600 hover:bg-red-50/50')}`} title="In Theatres">
              <PlayCircle className="w-5 h-5 text-red-400 transition-transform duration-200 group-hover:scale-110" /> 
              {isSidebarOpen && <span className="whitespace-nowrap font-medium">In Theatres</span>}
              {isActive('/in-theatres') && <div className="absolute left-0 w-1 h-6 bg-linear-to-b from-red-400 to-rose-500 rounded-r-full" />}
            </Link>
            <Link to="/airing" className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative overflow-hidden ${isActive('/airing') ? (isDarkMode ? 'bg-purple-500/10 text-purple-400' : 'bg-purple-50 text-purple-600') : (isDarkMode ? 'text-slate-400 hover:text-purple-400 hover:bg-purple-500/5' : 'text-slate-600 hover:text-purple-600 hover:bg-purple-50/50')}`} title="Airing">
              <Tv className="w-5 h-5 text-purple-400 transition-transform duration-200 group-hover:scale-110" /> 
              {isSidebarOpen && <span className="whitespace-nowrap font-medium">Airing</span>}
              {isActive('/airing') && <div className="absolute left-0 w-1 h-6 bg-linear-to-b from-purple-400 to-violet-500 rounded-r-full" />}
            </Link>
            <Link to="/trending" className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative overflow-hidden ${isActive('/trending') ? (isDarkMode ? 'bg-orange-500/10 text-orange-400' : 'bg-orange-50 text-orange-600') : (isDarkMode ? 'text-slate-400 hover:text-orange-400 hover:bg-orange-500/5' : 'text-slate-600 hover:text-orange-600 hover:bg-orange-50/50')}`} title="Trending">
              <TrendingUp className="w-5 h-5 text-orange-400 transition-transform duration-200 group-hover:scale-110" /> 
              {isSidebarOpen && <span className="whitespace-nowrap font-medium">Trending</span>}
              {isActive('/trending') && <div className="absolute left-0 w-1 h-6 bg-linear-to-b from-orange-400 to-amber-500 rounded-r-full" />}
            </Link>
            <Link to="/movers" className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative overflow-hidden ${isActive('/movers') ? (isDarkMode ? 'bg-emerald-500/10 text-emerald-400' : 'bg-emerald-50 text-emerald-600') : (isDarkMode ? 'text-slate-400 hover:text-emerald-400 hover:bg-emerald-500/5' : 'text-slate-600 hover:text-emerald-600 hover:bg-emerald-50/50')}`} title="Movers">
              <Activity className="w-5 h-5 text-emerald-400 transition-transform duration-200 group-hover:scale-110" /> 
              {isSidebarOpen && <span className="whitespace-nowrap font-medium">Movers</span>}
              {isActive('/movers') && <div className="absolute left-0 w-1 h-6 bg-linear-to-b from-emerald-400 to-green-500 rounded-r-full" />}
            </Link>
            <Link to="/on-this-day" className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative overflow-hidden ${isActive('/on-this-day') ? (isDarkMode ? 'bg-sky-500/10 text-sky-400' : 'bg-sky-50 text-sky-600') : (isDarkMode ? 'text-slate-400 hover:text-sky-400 hover:bg-sky-500/5' : 'text-slate-600 hover:text-sky-600 hover:bg-sky-50/50')}`} title="On This Day">
              <Calendar className="w-5 h-5 text-sky-400 transition-transform duration-200 group-hover:scale-110" /> 
              {isSidebarOpen && <span className="whitespace-nowrap font-medium">On This Day</span>}
              {isActive('/on-this-day') && <div className="absolute left-0 w-1 h-6 bg-linear-to-b from-sky-400 to-blue-500 rounded-r-full" />}
            </Link>
            <Link to="/top-of-year" className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative overflow-hidden ${isActive('/top-of-year') ? (isDarkMode ? 'bg-yellow-500/10 text-yellow-400' : 'bg-yellow-50 text-yellow-600') : (isDarkMode ? 'text-slate-400 hover:text-yellow-400 hover:bg-yellow-500/5' : 'text-slate-600 hover:text-yellow-600 hover:bg-yellow-50/50')}`} title="Top of Year">
              <Star className="w-5 h-5 text-yellow-400 transition-transform duration-200 group-hover:scale-110" /> 
              {isSidebarOpen && <span className="whitespace-nowrap font-medium">Top of Year</span>}
              {isActive('/top-of-year') && <div className="absolute left-0 w-1 h-6 bg-linear-to-b from-yellow-400 to-amber-500 rounded-r-full" />}
            </Link>
            
            {isSidebarOpen && <div className={`text-[10px] font-bold uppercase tracking-[0.2em] mt-6 mb-3 px-3 ${isDarkMode ? 'text-slate-500' : 'text-slate-400'}`}>Databases</div>}
            
            <Link to="/tv" className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative overflow-hidden ${isActive('/tv') ? (isDarkMode ? 'bg-purple-500/10 text-purple-400' : 'bg-purple-50 text-purple-600') : (isDarkMode ? 'text-slate-400 hover:text-purple-400 hover:bg-purple-500/5' : 'text-slate-600 hover:text-purple-600 hover:bg-purple-50/50')}`} title="TV Series">
              <Tv className="w-5 h-5 text-purple-400 transition-transform duration-200 group-hover:scale-110" /> 
              {isSidebarOpen && <span className="whitespace-nowrap font-medium">TV Series</span>}
              {isActive('/tv') && <div className="absolute left-0 w-1 h-6 bg-linear-to-b from-purple-400 to-violet-500 rounded-r-full" />}
            </Link>
            <Link to="/animated" className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative overflow-hidden ${isActive('/animated') ? (isDarkMode ? 'bg-orange-500/10 text-orange-400' : 'bg-orange-50 text-orange-600') : (isDarkMode ? 'text-slate-400 hover:text-orange-400 hover:bg-orange-500/5' : 'text-slate-600 hover:text-orange-600 hover:bg-orange-50/50')}`} title="Animated Shows">
              <Flame className="w-5 h-5 text-orange-400 transition-transform duration-200 group-hover:scale-110" /> 
              {isSidebarOpen && <span className="whitespace-nowrap font-medium">Anime</span>}
              {isActive('/animated') && <div className="absolute left-0 w-1 h-6 bg-linear-to-b from-orange-400 to-amber-500 rounded-r-full" />}
            </Link>
            <Link to="/western" className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative overflow-hidden ${isActive('/western') ? (isDarkMode ? 'bg-cyan-500/10 text-cyan-400' : 'bg-cyan-50 text-cyan-600') : (isDarkMode ? 'text-slate-400 hover:text-cyan-400 hover:bg-cyan-500/5' : 'text-slate-600 hover:text-cyan-600 hover:bg-cyan-50/50')}`} title="Western Animation">
              <Clapperboard className={`w-5 h-5 transition-transform duration-200 group-hover:scale-110 ${isActive('/western') ? 'text-cyan-500' : 'text-cyan-400'}`} /> 
              {isSidebarOpen && <span className="whitespace-nowrap font-medium">Western</span>}
              {isActive('/western') && <div className="absolute left-0 w-1 h-6 bg-linear-to-b from-cyan-400 to-blue-500 rounded-r-full" />}
            </Link>
            <Link to="/cartoons" className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative overflow-hidden ${isActive('/cartoons') ? (isDarkMode ? 'bg-green-500/10 text-green-400' : 'bg-green-50 text-green-600') : (isDarkMode ? 'text-slate-400 hover:text-green-400 hover:bg-green-500/5' : 'text-slate-600 hover:text-green-600 hover:bg-green-50/50')}`} title="Cartoons">
              <Baby className={`w-5 h-5 transition-transform duration-200 group-hover:scale-110 ${isActive('/cartoons') ? 'text-green-500' : 'text-green-400'}`} /> 
              {isSidebarOpen && <span className="whitespace-nowrap font-medium">Cartoons</span>}
              {isActive('/cartoons') && <div className="absolute left-0 w-1 h-6 bg-linear-to-b from-green-400 to-emerald-500 rounded-r-full" />}
            </Link>
            
            <div className="flex-grow min-h-4"></div>
            
            {/* Modern Dark Mode Toggle */}
            <button 
              onClick={() => setIsDarkMode(!isDarkMode)}
              className={`flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-300 mt-auto mb-2 group ${isDarkMode ? 'hover:bg-slate-800 border-t border-slate-800 pt-4' : 'hover:bg-slate-100 border-t border-slate-200 pt-4'}`}
              title="Toggle Dark Mode"
            >
              <div className={`relative w-10 h-6 rounded-full transition-colors duration-300 ${isDarkMode ? 'bg-slate-700' : 'bg-slate-200'} flex items-center px-1`}>
                <div className={`w-4 h-4 rounded-full transition-all duration-300 ${isDarkMode ? 'translate-x-4 bg-yellow-400 shadow-lg shadow-yellow-400/50' : 'translate-x-0 bg-white shadow-md'}`}>
                  {isDarkMode ? <Sun className="w-2.5 h-2.5 text-yellow-700 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" /> : <Moon className="w-2.5 h-2.5 text-slate-600 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />}
                </div>
              </div>
              {isSidebarOpen && <span className="whitespace-nowrap font-medium text-sm">{isDarkMode ? 'Dark' : 'Light'}</span>}
            </button>
            
            <Link to="/about" className={`flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group relative overflow-hidden ${isActive('/about') ? (isDarkMode ? 'bg-blue-500/10 text-blue-400' : 'bg-blue-50 text-blue-600') : (isDarkMode ? 'text-slate-400 hover:text-blue-400 hover:bg-blue-500/5' : 'text-slate-600 hover:text-blue-600 hover:bg-blue-50/50')}`} title="About">
              <Info className={`w-5 h-5 transition-transform duration-200 group-hover:scale-110 ${isActive('/about') ? 'text-blue-500' : 'text-blue-400'}`} /> 
              {isSidebarOpen && <span className="whitespace-nowrap font-medium">About</span>}
              {isActive('/about') && <div className="absolute left-0 w-1 h-6 bg-linear-to-b from-blue-400 to-indigo-500 rounded-r-full" />}
            </Link>
            
            <Link to="/settings" className={`flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200 group relative overflow-hidden mb-4 ${isActive('/settings') ? (isDarkMode ? 'bg-slate-500/10 text-slate-300' : 'bg-slate-100 text-slate-700') : (isDarkMode ? 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50' : 'text-slate-600 hover:text-slate-800 hover:bg-slate-100')}`} title="Settings">
              <SettingsIcon className="w-5 h-5 transition-transform duration-200 group-hover:scale-110 group-hover:rotate-90" /> 
              {isSidebarOpen && <span className="whitespace-nowrap font-medium text-sm">Settings</span>}
              {isActive('/settings') && <div className="absolute left-0 w-1 h-6 bg-linear-to-b from-slate-400 to-slate-500 rounded-r-full" />}
            </Link>
          </div>
          </div>
        </nav>

        {/* Modern Main Content Area */}
        <main className={`flex-1 overflow-auto relative ${isDarkMode ? 'bg-slate-950' : 'bg-[#F9FAFB]'}`}>
          {/* Soft neutral background for light mode */}
          <div className={`absolute inset-0 pointer-events-none ${isDarkMode ? 'bg-linear-to-br from-blue-500/5 via-transparent to-purple-500/5' : 'bg-[#F9FAFB]'}`} />
          <div className="relative z-10 p-8">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/search" element={<Search />} />
              <Route path="/movies" element={<Movies />} />
              <Route path="/compare" element={<Compare />} />
              <Route path="/records" element={<Records />} />
              <Route path="/franchises" element={<Franchises />} />
              
              {/* Phase 4 Discover Hub */}
              <Route path="/in-theatres" element={<DiscoverView title="In Theatres" endpoint="in-theatres" icon={<PlayCircle className="w-8 h-8 text-red-400" />} isSidebarOpen={isSidebarOpen} />} />
              <Route path="/airing" element={<DiscoverView title="Airing" endpoint="airing" icon={<Tv className="w-8 h-8 text-purple-400" />} isSidebarOpen={isSidebarOpen} />} />
              <Route path="/trending" element={<DiscoverView title="Trending" endpoint="trending" icon={<TrendingUp className="w-8 h-8 text-orange-400" />} isSidebarOpen={isSidebarOpen} />} />
              <Route path="/movers" element={<DiscoverView title="Movers" endpoint="movers" icon={<Activity className="w-8 h-8 text-emerald-400" />} isSidebarOpen={isSidebarOpen} />} />
              <Route path="/on-this-day" element={<OnThisDay />} />
              <Route path="/top-of-year" element={<DiscoverView title="Top of Year" endpoint="top-of-year" icon={<Star className="w-8 h-8 text-amber-400" />} isSidebarOpen={isSidebarOpen} />} />
              
              <Route path="/tv" element={<TVSeries />} />
              <Route path="/animated" element={<Anime />} />
              <Route path="/western" element={<WesternAnimation />} />
              <Route path="/cartoons" element={<Cartoons />} />
              <Route path="/watchlist" element={<Watchlist />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/about" element={<About />} />
            </Routes>
          </div>
        </main>
      </div>
  );
}
