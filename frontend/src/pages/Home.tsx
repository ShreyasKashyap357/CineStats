import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Film, Loader2, TrendingUp, Calendar, Star, PlayCircle, Activity, Image as ImageIcon, ChevronRight, X, Tv, Clock, Download } from "lucide-react";

interface MediaItem {
  id?: number;
  tmdb_id?: string | number;
  title?: string;
  title_display?: string;
  release_date?: string;
  poster_url?: string;
  vote_average?: number;
  worldwide_gross_usd?: number;
  india_net_cr?: number;
  media_type?: string;
  franchise_id?: number;
  franchise_name?: string;
  cast_json?: string;
  origin_country?: string;
  overview?: string;
}

interface SectionProps {
  title: string;
  icon: React.ReactNode;
  items: MediaItem[];
  loading: boolean;
  linkTo: string;
  accentColor: string;
  onCardClick: (item: MediaItem) => void;
}

/* Modern Hero Section with glassmorphism and smooth animations */
function HeroSection({ items, loading, onSelectItem }: { items: MediaItem[]; loading: boolean; onSelectItem?: (item: MediaItem) => void }) {
  const [heroIdx, setHeroIdx] = useState(0);
  const [isTransitioning, setIsTransitioning] = useState(false);

  useEffect(() => {
    if (items.length === 0) return;
    const interval = setInterval(() => {
      setIsTransitioning(true);
      setTimeout(() => {
        setHeroIdx(prev => (prev + 1) % Math.min(items.length, 5));
        setIsTransitioning(false);
      }, 300);
    }, 6000);
    return () => clearInterval(interval);
  }, [items.length]);

  // Skeleton loader with shimmer effect
  if (loading) {
    return (
      <div className="h-[400px] rounded-3xl bg-slate-100 dark:bg-slate-800/50 flex items-center justify-center mb-12 border border-slate-200 dark:border-slate-700/30 overflow-hidden relative">
        {/* Shimmer effect */}
        <div className="absolute inset-0 bg-linear-to-r from-transparent via-white/5 to-transparent animate-[shimmer_2s_infinite]" />
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-12 h-12 animate-spin text-blue-500" />
          <span className="text-slate-500 dark:text-slate-500 text-sm font-medium">Loading featured content...</span>
        </div>
      </div>
    );
  }

  if (items.length === 0) return null;
  const hero = items[heroIdx % items.length];
  const heroTitle = hero?.title || hero?.title_display || "Untitled";

  return (
    <div className="relative h-[400px] rounded-3xl overflow-hidden mb-12 group shadow-2xl shadow-black/20">
      {/* Dynamic background with poster if available */}
      {hero?.poster_url ? (
        <div className="absolute inset-0">
          <img 
            src={hero.poster_url} 
            alt="" 
            className={`w-full h-full object-cover transition-all duration-700 ${isTransitioning ? 'scale-110 opacity-50' : 'scale-100 opacity-100'}`}
          />
          <div className="absolute inset-0 bg-linear-to-r from-white/95 via-white/80 to-transparent dark:from-slate-950/95 dark:via-slate-900/80 dark:to-transparent" />
          <div className="absolute inset-0 bg-linear-to-t from-white via-transparent to-white/20 dark:from-slate-950 dark:via-transparent dark:to-slate-900/20" />
        </div>
      ) : (
        <div className="absolute inset-0 bg-linear-to-br from-blue-600/20 via-indigo-600/20 to-purple-600/20" />
      )}
      
      {/* Glassmorphism content card */}
      <div className="relative z-10 h-full flex items-end p-8 md:p-12">
        <div className={`max-w-2xl transition-all duration-500 ${isTransitioning ? 'opacity-0 translate-y-4' : 'opacity-100 translate-y-0'}`}>
          {/* Tags */}
          <div className="flex items-center gap-3 mb-4">
            <span className="bg-linear-to-r from-blue-500 to-indigo-500 text-white text-xs font-bold px-4 py-1.5 rounded-full uppercase tracking-wider shadow-lg shadow-blue-500/30">
              {hero?.media_type === "tv" ? "TV Series" : "Movie"}
            </span>
            {hero?.vote_average && (
              <span className="bg-amber-100 dark:bg-amber-500/20 backdrop-blur-sm text-amber-700 dark:text-amber-400 text-xs font-bold px-3 py-1.5 rounded-full border border-amber-300 dark:border-amber-500/30 flex items-center gap-1">
                <Star className="w-3 h-3 fill-current" /> {hero.vote_average.toFixed?.(1) || hero.vote_average}
              </span>
            )}
          </div>
          
          {/* Title with text shadow for depth */}
          <h2 className="text-5xl md:text-6xl font-black text-slate-900 dark:text-white mb-4 drop-shadow-2xl max-w-3xl leading-tight">
            {heroTitle}
          </h2>
          
          {/* Meta info with icons */}
          <div className="flex items-center gap-6 text-sm text-slate-600 dark:text-slate-300 mb-6">
            {hero?.release_date && (
              <span className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-slate-500 dark:text-slate-400" />
                {hero.release_date}
              </span>
            )}
            {hero?.worldwide_gross_usd && (
              <span className="flex items-center gap-2 text-emerald-700 dark:text-emerald-400 font-bold bg-emerald-100 dark:bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-300 dark:border-emerald-500/20">
                <TrendingUp className="w-4 h-4" />
                ${(hero.worldwide_gross_usd / 1_000_000).toFixed(1)}M
              </span>
            )}
          </div>

          {/* CTA Button with hover glow */}
          <button
            onClick={() => onSelectItem?.(hero)}
            className="group/btn bg-linear-to-r from-blue-500 to-indigo-600 hover:from-blue-400 hover:to-indigo-500 text-white px-8 py-3 rounded-full font-bold text-sm shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50 transition-all hover:scale-105 flex items-center gap-2"
          >
            View Details
            <ChevronRight className="w-4 h-4 group-hover/btn:translate-x-1 transition-transform" />
          </button>
        </div>
      </div>

      {/* Modern Hero Dots with progress */}
      <div className="absolute bottom-6 right-8 flex gap-3 z-20">
        {items.slice(0, 5).map((_, i) => (
          <button
            key={i}
            onClick={() => {
              setIsTransitioning(true);
              setTimeout(() => {
                setHeroIdx(i);
                setIsTransitioning(false);
              }, 300);
            }}
            className="group/dot relative"
            aria-label={`Go to slide ${i + 1}`}
          >
            <div className={`h-1.5 rounded-full transition-all duration-500 ${i === heroIdx ? 'w-8 bg-blue-500' : 'w-1.5 bg-slate-400/50 dark:bg-slate-500/50 group-hover/dot:bg-slate-500 dark:group-hover/dot:bg-slate-400'}`} />
            {i === heroIdx && (
              <div className="absolute inset-0 h-1.5 rounded-full bg-blue-400/50 animate-pulse" />
            )}
          </button>
        ))}
      </div>
      
      {/* Ambient glow */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-linear-to-t from-white/50 to-transparent dark:from-slate-950/50 pointer-events-none" />
    </div>
  );
}

/* Modern Media Card with full details inline */
function MediaCard({ item, onClick }: { item: MediaItem; onClick: () => void }) {
  const title = item.title || item.title_display || "Untitled";
  
  // Parse cast from JSON if available
  let cast: string[] = [];
  try {
    if (item.cast_json) {
      cast = JSON.parse(item.cast_json);
    }
  } catch (e) {
    // Invalid JSON, ignore
  }
  const displayCast = cast.slice(0, 2).join(', ');
  
  return (
    <div
      onClick={onClick}
      className="group cursor-pointer relative rounded-2xl overflow-hidden shadow-lg shadow-black/10 dark:shadow-black/20 border border-slate-200 dark:border-slate-700/30 hover:border-blue-500/40 hover:shadow-2xl hover:shadow-blue-500/20 transition-all duration-500 hover:-translate-y-2 hover:scale-[1.02] bg-white dark:bg-slate-900/50 backdrop-blur-sm"
    >
      {/* Image container with aspect ratio */}
      <div className="aspect-2/3 bg-slate-200 dark:bg-slate-800 overflow-hidden relative">
        {item.poster_url ? (
          <img 
            src={item.poster_url} 
            alt={title} 
            className="w-full h-full object-cover object-top group-hover:scale-105 transition-transform duration-500" 
            loading="lazy" 
          />
        ) : (
          <div className="flex flex-col items-center justify-center gap-3 text-slate-500 dark:text-slate-600 h-full">
            <div className="w-16 h-16 rounded-2xl bg-slate-300/50 dark:bg-slate-700/50 flex items-center justify-center">
              <ImageIcon className="w-8 h-8 text-slate-400 dark:text-slate-500" />
            </div>
            <span className="text-xs font-medium text-slate-600 dark:text-slate-400">No Poster</span>
          </div>
        )}
      </div>

      {/* Always visible full details */}
      <div className="absolute inset-0 bg-linear-to-t from-white via-white/95 to-transparent dark:from-slate-950 dark:via-slate-950/95 dark:to-transparent p-3 flex flex-col justify-end">
        <h3 className="font-bold text-slate-900 dark:text-white text-xs line-clamp-2 leading-tight mb-1.5">{title}</h3>
        
        {/* Year and Country */}
        <div className="flex items-center gap-2 mb-1.5">
          {item.release_date && (
            <span className="text-xs text-slate-600 dark:text-slate-400 font-medium">{item.release_date.split('-')[0]}</span>
          )}
          {item.origin_country && (
            <span className="text-xs text-slate-500 dark:text-slate-500">• {item.origin_country}</span>
          )}
        </div>
        
        {/* Franchise badge */}
        {item.franchise_name && (
          <div className="text-xs text-pink-600 dark:text-pink-400 font-medium mb-1.5 truncate">
            {item.franchise_name}
          </div>
        )}
        
        {/* Rating or Gross */}
        <div className="flex justify-between items-center mb-1.5">
          {item.vote_average ? (
            <span className="text-xs font-bold text-amber-700 dark:text-amber-400 bg-amber-100 dark:bg-amber-500/20 backdrop-blur-sm px-2 py-0.5 rounded-full border border-amber-300 dark:border-amber-500/30 flex items-center gap-1">
              <Star className="w-3 h-3 fill-current" /> 
              {typeof item.vote_average === 'number' ? item.vote_average.toFixed(1) : item.vote_average}
            </span>
          ) : item.worldwide_gross_usd ? (
            <span className="text-xs font-bold text-emerald-700 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-500/20 backdrop-blur-sm px-2 py-0.5 rounded-full border border-emerald-300 dark:border-emerald-500/30">
              ${(item.worldwide_gross_usd / 1_000_000).toFixed(1)}M
            </span>
          ) : item.india_net_cr ? (
            <span className="text-xs font-bold text-orange-700 dark:text-orange-400 bg-orange-100 dark:bg-orange-500/20 backdrop-blur-sm px-2 py-0.5 rounded-full border border-orange-300 dark:border-orange-500/30">
              ₹{item.india_net_cr}Cr
            </span>
          ) : null}
        </div>
        
        {/* Cast */}
        {displayCast && (
          <div className="text-xs text-slate-600 dark:text-slate-400 truncate">
            {displayCast}
          </div>
        )}
      </div>
      
      {/* Corner accent */}
      <div className="absolute top-0 right-0 w-16 h-16 bg-linear-to-bl from-blue-500/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
    </div>
  );
}

/* Skeleton card for loading states */
function SkeletonCard() {
  return (
    <div className="rounded-2xl overflow-hidden bg-slate-200 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700/30 animate-pulse">
      <div className="aspect-2/3 bg-slate-300/50 dark:bg-slate-700/50" />
      <div className="p-3 space-y-2">
        <div className="h-4 bg-slate-300 dark:bg-slate-700 rounded w-3/4" />
        <div className="h-3 bg-slate-300 dark:bg-slate-700 rounded w-1/2" />
      </div>
    </div>
  );
}

/* Modern Home Section with enhanced header and skeleton loading */
function HomeSection({ title, icon, items, loading, linkTo, accentColor, onCardClick, sectionId }: SectionProps & { sectionId?: string }) {
  if (loading) {
    return (
      <div id={sectionId} className="mb-12">
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-slate-200 dark:bg-slate-800/50">{icon}</div>
            <h3 className="text-xl font-bold text-slate-700 dark:text-slate-200">{title}</h3>
          </div>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {[...Array(6)].map((_, i) => <SkeletonCard key={i} />)}
        </div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <section id={sectionId} className="mb-12 scroll-mt-28">
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-3">
            <div className={`p-2.5 rounded-xl bg-slate-200/80 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/50 shadow-lg ${accentColor}`}>
              {icon}
            </div>
            <div>
              <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100">{title}</h3>
              <p className="text-xs text-slate-500 dark:text-slate-500 font-medium">No items available</p>
            </div>
          </div>
          <Link 
            to={linkTo} 
            className={`group text-sm font-semibold flex items-center gap-1.5 px-4 py-2 rounded-full bg-slate-200/50 dark:bg-slate-800/50 hover:bg-slate-300/50 dark:hover:bg-slate-700/50 border border-slate-200 dark:border-slate-700/50 transition-all duration-300 ${accentColor}`}
          >
            View All 
            <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>
        <div className="bg-slate-100/50 dark:bg-slate-800/30 rounded-2xl border border-slate-200 dark:border-slate-700/30 border-dashed h-48 flex flex-col items-center justify-center text-slate-500">
          <p className="text-lg">No data available for {title} right now.</p>
          <p className="text-sm mt-2">Check back later or try refreshing the data.</p>
        </div>
      </section>
    );
  }

  return (
    <section id={sectionId} className="mb-12 scroll-mt-28">
      {/* Modern section header */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          <div className={`p-2.5 rounded-xl bg-slate-200/80 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700/50 shadow-lg ${accentColor}`}>
            {icon}
          </div>
          <div>
            <h3 className="text-xl font-bold text-slate-900 dark:text-slate-100">{title}</h3>
            <p className="text-xs text-slate-500 dark:text-slate-500 font-medium">{items.length} items</p>
          </div>
        </div>
        <Link 
          to={linkTo} 
          className={`group text-sm font-semibold flex items-center gap-1.5 px-4 py-2 rounded-full bg-slate-200/50 dark:bg-slate-800/50 hover:bg-slate-300/50 dark:hover:bg-slate-700/50 border border-slate-200 dark:border-slate-700/50 transition-all duration-300 ${accentColor}`}
        >
          View All 
          <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
        </Link>
      </div>
      
      {/* Enhanced grid with larger gap */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-5">
        {items.slice(0, 6).map((item, idx) => (
          <MediaCard
            key={idx}
            item={item}
            onClick={() => onCardClick(item)}
          />
        ))}
      </div>
    </section>
  );
}

export default function Home() {
  const [nowPlaying, setNowPlaying] = useState<MediaItem[]>([]);
  const [trending, setTrending] = useState<MediaItem[]>([]);
  const [airing, setAiring] = useState<MediaItem[]>([]);
  const [recent, setRecent] = useState<MediaItem[]>([]);
  const [topOfYear, setTopOfYear] = useState<MediaItem[]>([]);
  const [movers, setMovers] = useState<MediaItem[]>([]);
  const [onThisDay, setOnThisDay] = useState<MediaItem[]>([]);

  const [loadingNP, setLoadingNP] = useState(true);
  const [loadingFullDetails, setLoadingFullDetails] = useState(false);
  const [fullDetails, setFullDetails] = useState<any>(null);
  const [loadingTrend, setLoadingTrend] = useState(true);
  const [loadingAiring, setLoadingAiring] = useState(true);
  const [loadingRecent, setLoadingRecent] = useState(true);
  const [loadingTop, setLoadingTop] = useState(true);
  const [loadingMovers, setLoadingMovers] = useState(true);
  const [loadingOTD, setLoadingOTD] = useState(true);
  
  const [selectedItem, setSelectedItem] = useState<MediaItem | null>(null);

  const fetchSection = async (endpoint: string, setter: Function, loadingSetter: Function) => {
    try {
      const res = await fetch(`http://localhost:8000/api/discover/${endpoint}`);
      const data = await res.json();
      setter(data.results || []);
    } catch (e) {
      console.error(`Failed to fetch ${endpoint}:`, e);
      setter([]);
    }
    loadingSetter(false);
  };

  useEffect(() => {
    fetchSection("in-theatres", setNowPlaying, setLoadingNP);
    fetchSection("trending", setTrending, setLoadingTrend);
    fetchSection("airing", setAiring, setLoadingAiring);
    fetchSection("recent", setRecent, setLoadingRecent);
    fetchSection("top-of-year", setTopOfYear, setLoadingTop);
    fetchSection("movers", setMovers, setLoadingMovers);
    fetchSection("on-this-day", setOnThisDay, setLoadingOTD);
  }, []);

  const handleExportPDF = () => {
    window.print();
  };

  const fetchFullDetails = async (item: MediaItem) => {
    setLoadingFullDetails(true);
    try {
      const title = item.title || item.title_display || '';
      const res = await fetch(`http://localhost:8000/api/search?q=${encodeURIComponent(title)}`);
      const data = await res.json();
      if (data.results && data.results.length > 0) {
        setFullDetails(data.results[0]);
      }
    } catch (e) {
      console.error('Failed to fetch full details:', e);
    }
    setLoadingFullDetails(false);
  };

  return (
    <div className="max-w-7xl mx-auto pb-12">
      {/* Modern Glassmorphism Header */}
      <header className="mb-10 flex flex-col md:flex-row md:justify-between md:items-start gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="w-2 h-8 bg-linear-to-b from-blue-500 to-indigo-600 rounded-full" />
            <h1 className="text-5xl font-black bg-linear-to-r from-blue-400 via-indigo-400 to-purple-400 text-transparent bg-clip-text tracking-tight">
              CineStats Dashboard
            </h1>
          </div>
          <p className="text-slate-500 dark:text-slate-400 text-lg ml-5">
            Your high-fidelity entertainment analytics command center
          </p>
        </div>
        <button 
          onClick={handleExportPDF}
          className="group flex items-center gap-2 bg-slate-200/80 dark:bg-slate-800/80 hover:bg-slate-300/80 dark:hover:bg-slate-700/80 text-slate-700 dark:text-slate-300 px-5 py-2.5 rounded-xl border border-slate-200 dark:border-slate-700/50 backdrop-blur-sm transition-all duration-300 hover:shadow-lg hover:shadow-slate-500/10 hover:-translate-y-0.5"
          title="Export as PDF"
        >
          <Download className="w-4 h-4 group-hover:scale-110 transition-transform" />
          <span className="font-medium">Export PDF</span>
        </button>
      </header>

      {/* Modern Jump Navigation with Glassmorphism */}
      <nav className="mb-10 p-2 bg-white/60 dark:bg-slate-800/40 backdrop-blur-xl rounded-2xl border border-slate-200 dark:border-slate-700/30 shadow-xl shadow-black/5 sticky top-4 z-30">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm font-semibold text-slate-500 flex items-center gap-2 px-3 py-2">
            <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
            Quick Jump
          </span>
          <div className="h-6 w-px bg-slate-300 dark:bg-slate-700/50 mx-1" />
          {[
            { id: 'trending', label: 'Trending', color: 'text-orange-600 dark:text-orange-400', bg: 'from-orange-500/20 to-amber-500/20', border: 'border-orange-500/30' },
            { id: 'airing', label: 'Airing', color: 'text-purple-600 dark:text-purple-400', bg: 'from-purple-500/20 to-violet-500/20', border: 'border-purple-500/30' },
            { id: 'recent', label: "What's New", color: 'text-cyan-600 dark:text-cyan-400', bg: 'from-cyan-500/20 to-blue-500/20', border: 'border-cyan-500/30' },
            { id: 'now-playing', label: 'Now Playing', color: 'text-red-600 dark:text-red-400', bg: 'from-red-500/20 to-rose-500/20', border: 'border-red-500/30' },
            { id: 'top-year', label: 'Top of Year', color: 'text-amber-600 dark:text-amber-400', bg: 'from-amber-500/20 to-yellow-500/20', border: 'border-amber-500/30' },
            { id: 'movers', label: 'Movers', color: 'text-emerald-600 dark:text-emerald-400', bg: 'from-emerald-500/20 to-green-500/20', border: 'border-emerald-500/30' },
            { id: 'on-this-day', label: 'On This Day', color: 'text-sky-600 dark:text-sky-400', bg: 'from-sky-500/20 to-blue-500/20', border: 'border-sky-500/30' },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => document.getElementById(item.id)?.scrollIntoView({ behavior: 'smooth', block: 'start' })}
              className={`text-sm px-4 py-2 rounded-xl ${item.color} bg-linear-to-r ${item.bg} border ${item.border} hover:shadow-lg transition-all duration-300 hover:-translate-y-0.5 font-medium`}
            >
              {item.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Hero Carousel — Now Playing */}
      <HeroSection items={nowPlaying} loading={loadingNP} onSelectItem={setSelectedItem} />

      {/* Trending Section */}
      <HomeSection
        title="Trending Today"
        icon={<TrendingUp className="w-5 h-5 text-orange-400" />}
        items={trending}
        loading={loadingTrend}
        linkTo="/trending"
        accentColor="text-orange-400"
        onCardClick={setSelectedItem}
        sectionId="trending"
      />

      {/* Currently Airing */}
      <HomeSection
        title="Currently Airing"
        icon={<Tv className="w-5 h-5 text-purple-400" />}
        items={airing}
        loading={loadingAiring}
        linkTo="/trending"
        accentColor="text-purple-400"
        onCardClick={setSelectedItem}
        sectionId="airing"
      />

      {/* What's New */}
      <HomeSection
        title="What's New"
        icon={<Clock className="w-5 h-5 text-cyan-400" />}
        items={recent}
        loading={loadingRecent}
        linkTo="/movies"
        accentColor="text-cyan-400"
        onCardClick={setSelectedItem}
        sectionId="recent"
      />

      {/* Now Playing Grid */}
      <HomeSection
        title="Now Playing in Theatres"
        icon={<PlayCircle className="w-5 h-5 text-red-400" />}
        items={nowPlaying}
        loading={loadingNP}
        linkTo="/in-theatres"
        accentColor="text-red-400"
        onCardClick={setSelectedItem}
        sectionId="now-playing"
      />

      {/* Top of Year */}
      <HomeSection
        title={`Top Movies of ${new Date().getFullYear()}`}
        icon={<Star className="w-5 h-5 text-yellow-400" />}
        items={topOfYear}
        loading={loadingTop}
        linkTo="/top-of-year"
        accentColor="text-yellow-400"
        onCardClick={setSelectedItem}
        sectionId="top-year"
      />

      {/* Movers */}
      <HomeSection
        title="Latest Movers"
        icon={<Activity className="w-5 h-5 text-green-400" />}
        items={movers}
        loading={loadingMovers}
        linkTo="/movers"
        accentColor="text-green-400"
        onCardClick={setSelectedItem}
        sectionId="movers"
      />

      {/* On This Day */}
      <HomeSection
        title="On This Day"
        icon={<Calendar className="w-5 h-5 text-blue-300" />}
        items={onThisDay}
        loading={loadingOTD}
        linkTo="/on-this-day"
        accentColor="text-blue-300"
        onCardClick={setSelectedItem}
        sectionId="on-this-day"
      />
      
      {/* Modern Glassmorphism Detail Modal */}
      {selectedItem && (
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-300" 
          onClick={() => setSelectedItem(null)}
        >
          <div 
            className="bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl rounded-3xl border border-slate-200 dark:border-slate-700/50 shadow-2xl shadow-black/50 w-full max-w-4xl flex flex-col md:flex-row overflow-hidden relative animate-in zoom-in-95 duration-300" 
            onClick={e => e.stopPropagation()}
          >
            {/* Ambient glow effects */}
            <div className="absolute -top-20 -right-20 w-40 h-40 bg-blue-500/20 rounded-full blur-3xl pointer-events-none" />
            <div className="absolute -bottom-20 -left-20 w-40 h-40 bg-purple-500/20 rounded-full blur-3xl pointer-events-none" />
            
            {/* Close button with enhanced styling */}
            <button 
              onClick={() => setSelectedItem(null)}
              className="absolute top-4 right-4 p-2.5 bg-slate-200/80 dark:bg-slate-800/80 hover:bg-slate-300/80 dark:hover:bg-slate-700/80 backdrop-blur-sm rounded-full text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white z-20 transition-all duration-300 hover:rotate-90 border border-slate-200 dark:border-slate-700/50 hover:border-slate-400/50 dark:hover:border-slate-500/50 shadow-lg"
              title="Close"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Poster section */}
            <div className="w-full md:w-2/5 bg-slate-100 dark:bg-slate-800/50 relative overflow-hidden">
              {selectedItem.poster_url ? (
                <img 
                  src={selectedItem.poster_url} 
                  alt={selectedItem.title || selectedItem.title_display || 'Poster'}
                  className="w-full h-full object-cover min-h-75 md:min-h-0"
                />
              ) : (
                <div className="w-full h-64 md:h-full flex items-center justify-center bg-slate-200 dark:bg-slate-800">
                  <div className="flex flex-col items-center gap-3 text-slate-500 dark:text-slate-600">
                    <div className="w-24 h-24 rounded-3xl bg-slate-300/50 dark:bg-slate-700/50 flex items-center justify-center">
                      <ImageIcon className="w-12 h-12 text-slate-400 dark:text-slate-500" />
                    </div>
                    <span className="text-sm font-medium text-slate-700 dark:text-slate-400">No Poster Available</span>
                  </div>
                </div>
              )}
              {/* Gradient overlay on poster */}
              <div className="absolute inset-0 bg-linear-to-t from-white via-transparent to-transparent md:bg-linear-to-r md:from-transparent md:to-white/20 dark:from-slate-900 dark:to-transparent dark:md:from-transparent dark:md:to-slate-900/20" />
            </div>

            {/* Content section */}
            <div className="w-full md:w-3/5 p-8 flex flex-col relative">
              {/* Media type badge */}
              <div className="flex items-center gap-3 mb-3">
                <span className={`text-xs font-bold uppercase tracking-wider px-3 py-1.5 rounded-full ${selectedItem.media_type === 'tv' ? 'bg-purple-100 dark:bg-purple-500/20 text-purple-700 dark:text-purple-400 border border-purple-300 dark:border-purple-500/30' : 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400 border border-blue-300 dark:border-blue-500/30'}`}>
                  {selectedItem.media_type === "tv" ? "TV Series" : "Movie"}
                </span>
                {selectedItem.vote_average && (
                  <span className="flex items-center gap-1.5 text-sm font-bold text-amber-700 dark:text-amber-400 bg-amber-100 dark:bg-amber-500/10 px-3 py-1.5 rounded-full border border-amber-300 dark:border-amber-500/20">
                    <Star className="w-4 h-4 fill-current" /> 
                    {Number(selectedItem.vote_average).toFixed?.(1) || selectedItem.vote_average}
                  </span>
                )}
              </div>
              
              {/* Title */}
              <h2 className="text-3xl md:text-4xl font-black text-slate-900 dark:text-white mb-3 leading-tight">
                {selectedItem.title || selectedItem.title_display}
              </h2>
              
              {/* Meta info */}
              <div className="flex flex-wrap items-center gap-4 text-sm text-slate-600 dark:text-slate-400 mb-6">
                {selectedItem.release_date && (
                  <span className="flex items-center gap-2 bg-slate-100 dark:bg-slate-800/50 px-3 py-1.5 rounded-lg">
                    <Calendar className="w-4 h-4 text-slate-500" /> 
                    {selectedItem.release_date}
                  </span>
                )}
              </div>
              
              {/* Box Office stats with modern cards */}
              {(selectedItem.worldwide_gross_usd || selectedItem.india_net_cr) && (
                <div className="grid grid-cols-2 gap-4 mb-6">
                  {selectedItem.worldwide_gross_usd && (
                    <div className="bg-linear-to-br from-emerald-500/10 to-emerald-600/5 p-5 rounded-2xl border border-emerald-500/20 relative overflow-hidden group">
                      <div className="absolute top-0 right-0 w-20 h-20 bg-emerald-500/10 rounded-full blur-2xl group-hover:bg-emerald-500/20 transition-colors" />
                      <span className="text-xs font-semibold text-emerald-400/80 uppercase tracking-wider">Worldwide Gross</span>
                      <p className="text-2xl font-black text-emerald-400 mt-1">${(selectedItem.worldwide_gross_usd / 1000000).toFixed(1)}M</p>
                    </div>
                  )}
                  {selectedItem.india_net_cr && (
                    <div className="bg-linear-to-br from-orange-500/10 to-orange-600/5 p-5 rounded-2xl border border-orange-500/20 relative overflow-hidden group">
                      <div className="absolute top-0 right-0 w-20 h-20 bg-orange-500/10 rounded-full blur-2xl group-hover:bg-orange-500/20 transition-colors" />
                      <span className="text-xs font-semibold text-orange-400/80 uppercase tracking-wider">India Net</span>
                      <p className="text-2xl font-black text-orange-400 mt-1">₹{selectedItem.india_net_cr} Cr</p>
                    </div>
                  )}
                </div>
              )}
              
              {/* Action buttons */}
              <div className="mt-auto pt-4 flex gap-3">
                {fullDetails ? (
                  <button
                    onClick={() => { setFullDetails(null); setSelectedItem(null); }}
                    className="flex-1 bg-linear-to-r from-slate-600 to-slate-700 hover:from-slate-500 hover:to-slate-600 text-white px-6 py-3 rounded-xl font-bold text-sm transition-all duration-300 hover:shadow-lg text-center flex items-center justify-center gap-2"
                  >
                    Close
                    <X className="w-4 h-4" />
                  </button>
                ) : (
                  <button
                    onClick={() => fetchFullDetails(selectedItem)}
                    disabled={loadingFullDetails}
                    className="flex-1 bg-linear-to-r from-blue-500 to-indigo-600 hover:from-blue-400 hover:to-indigo-500 text-white px-6 py-3 rounded-xl font-bold text-sm transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/25 text-center flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    {loadingFullDetails ? <Loader2 className="w-4 h-4 animate-spin" /> : "View Full Details"}
                    {!loadingFullDetails && <ChevronRight className="w-4 h-4" />}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

