import { useState } from "react";
import { 
  Film, 
  Code, 
  FileText, 
  ExternalLink, 
  Server, 
  Database, 
  Globe, 
  Zap, 
  Shield, 
  TrendingUp,
  Trophy,
  Heart,
  BarChart3,
  Search,
  Calendar,
  Activity,
  Tv,
  Baby,
  Clapperboard,
  ChevronDown,
  ChevronUp,
  GitBranch,
  BookOpen,
  Terminal,
  Layers,
  Cpu
} from "lucide-react";

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  color: string;
}

function FeatureCard({ icon, title, description, color }: FeatureCardProps) {
  return (
    <div className="bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700/50 p-5 hover:border-emerald-400/50 dark:hover:border-slate-600/50 transition-all duration-300 group shadow-[0_2px_8px_rgba(0,0,0,0.04)]">
      <div className={`p-3 rounded-xl ${color} w-fit mb-4 group-hover:scale-110 transition-transform duration-300`}>
        {icon}
      </div>
      <h3 className="font-bold text-slate-900 dark:text-slate-100 mb-2">{title}</h3>
      <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">{description}</p>
    </div>
  );
}

interface SectionProps {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
  defaultOpen?: boolean;
}

function CollapsibleSection({ title, icon, children, defaultOpen = false }: SectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  
  return (
    <div className="bg-white dark:bg-slate-800/30 rounded-2xl border border-slate-200 dark:border-slate-700/50 overflow-hidden shadow-[0_2px_8px_rgba(0,0,0,0.04)]">
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-5 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400">
            {icon}
          </div>
          <h2 className="text-lg font-bold text-slate-900 dark:text-slate-100">{title}</h2>
        </div>
        {isOpen ? <ChevronUp className="w-5 h-5 text-slate-500 dark:text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-500 dark:text-slate-400" />}
      </button>
      {isOpen && (
        <div className="px-5 pb-5 border-t border-slate-200 dark:border-slate-700/50 pt-4">
          {children}
        </div>
      )}
    </div>
  );
}

export default function About() {
  const version = "2.0.0";
  const backendUrl = "http://localhost:8000";

  const apiEndpoints = [
    { method: "GET", path: "/api/movies", description: "Movie database operations" },
    { method: "GET", path: "/api/tv", description: "TV series database operations" },
    { method: "GET", path: "/api/anime", description: "Anime database operations" },
    { method: "GET", path: "/api/search", description: "Global search across all content" },
    { method: "GET", path: "/api/discover/{endpoint}", description: "Discovery hub (trending, in-theatres, etc.)" },
    { method: "GET", path: "/api/records", description: "Box office records and hall of fame" },
    { method: "GET", path: "/api/franchises", description: "Franchise management and hierarchy" },
    { method: "GET", path: "/api/watchlist", description: "User watchlist operations" },
    { method: "GET", path: "/api/compare", description: "Cross-category comparisons" },
    { method: "GET", path: "/api/scrape", description: "Scraping queue management" },
    { method: "GET", path: "/api/settings", description: "Application settings" },
    { method: "GET", path: "/api/logs", description: "System logs and events" },
  ];

  const dataSources = [
    { name: "TMDB", description: "The Movie Database - Primary metadata source", icon: Film },
    { name: "Box Office Mojo", description: "Box office data and records", icon: Trophy },
    { name: "Sacnilk", description: "Indian box office collections", icon: Globe },
    { name: "Jikan", description: "MyAnimeList API for anime data", icon: Tv },
    { name: "AniList", description: "Alternative anime metadata source", icon: Heart },
  ];

  return (
    <div className="max-w-7xl mx-auto pb-12 space-y-6">
      {/* Hero Section */}
      <header className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-700 p-8 md:p-12">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PHBhdGggZD0iTTM2IDM0aDR2NGgtNHpNMjAgMjBoNHY0aC00eiIvPjwvZz48L2c+PC9zdmc+')] opacity-30" />
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-4 mb-4">
              <div className="p-4 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20">
                <Film className="w-10 h-10 text-white" />
              </div>
              <div>
                <h1 className="text-4xl md:text-5xl font-black text-white tracking-tight">CineStats</h1>
                <p className="text-blue-100 font-medium">v{version}</p>
              </div>
            </div>
            <p className="text-lg text-blue-50 max-w-2xl leading-relaxed">
              A comprehensive media analytics platform for movies, TV series, anime, and box office data. 
              Track collections, analyze trends, and discover your next favorite content.
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-3">
            <a 
              href={`${backendUrl}/docs`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-5 py-3 bg-white text-blue-600 rounded-xl font-bold hover:bg-blue-50 transition-colors shadow-lg shadow-blue-900/20"
            >
              <Code className="w-5 h-5" />
              Swagger UI
              <ExternalLink className="w-4 h-4" />
            </a>
            <a 
              href={`${backendUrl}/openapi.json`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-5 py-3 bg-blue-500/20 backdrop-blur-sm text-white border border-white/30 rounded-xl font-bold hover:bg-blue-500/30 transition-colors"
            >
              <FileText className="w-5 h-5" />
              OpenAPI Spec
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>
        </div>
      </header>

      {/* Quick Links */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <a 
          href="https://github.com/shrey/cinestats"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-4 p-5 bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700/50 hover:border-blue-400/50 dark:hover:border-blue-500/50 transition-all group shadow-[0_2px_8px_rgba(0,0,0,0.04)]"
        >
          <div className="p-3 rounded-xl bg-blue-100 dark:bg-slate-700/50 group-hover:bg-blue-200 dark:group-hover:bg-blue-500/10 transition-colors">
            <GitBranch className="w-6 h-6 text-blue-600 dark:text-slate-300 group-hover:text-blue-700 dark:group-hover:text-blue-400" />
          </div>
          <div>
            <h3 className="font-bold text-slate-900 dark:text-slate-100">Source Code</h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">View on GitHub</p>
          </div>
        </a>
        
        <a 
          href={`${backendUrl}/docs`}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-4 p-5 bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700/50 hover:border-emerald-400/50 dark:hover:border-green-500/50 transition-all group shadow-[0_2px_8px_rgba(0,0,0,0.04)]"
        >
          <div className="p-3 rounded-xl bg-emerald-100 dark:bg-slate-700/50 group-hover:bg-emerald-200 dark:group-hover:bg-green-500/10 transition-colors">
            <BookOpen className="w-6 h-6 text-emerald-600 dark:text-slate-300 group-hover:text-emerald-700 dark:group-hover:text-green-400" />
          </div>
          <div>
            <h3 className="font-bold text-slate-900 dark:text-slate-100">API Documentation</h3>
            <p className="text-sm text-slate-600 dark:text-slate-400">Interactive Swagger UI</p>
          </div>
        </a>
        
        <div 
          className="flex items-center gap-4 p-5 bg-white dark:bg-slate-800/50 rounded-2xl border border-slate-200 dark:border-slate-700/50 hover:border-purple-400/50 dark:hover:border-purple-500/50 transition-all group shadow-[0_2px_8px_rgba(0,0,0,0.04)]"
        >
          <div className="p-3 rounded-xl bg-purple-100 dark:bg-slate-700/50 group-hover:bg-purple-200 dark:group-hover:bg-purple-500/10 transition-colors">
            <Terminal className="w-6 h-6 text-purple-600 dark:text-slate-300 group-hover:text-purple-700 dark:group-hover:text-purple-400" />
          </div>
          <div>
            <h3 className="font-bold text-slate-900 dark:text-slate-100">System Status</h3>
            <p className="text-sm text-slate-600 dark:text-slate-400 flex items-center gap-2">
              <span className="inline-flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
              All systems operational
            </p>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <CollapsibleSection title="Features & Capabilities" icon={<Zap className="w-5 h-5" />} defaultOpen={true}>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <FeatureCard 
            icon={<Database className="w-6 h-6 text-blue-400" />}
            title="Multi-Database Support"
            description="Track Movies, TV Series, Anime, Western Animation, and Cartoons with unified search and filtering."
            color="bg-blue-500/10"
          />
          <FeatureCard 
            icon={<Globe className="w-6 h-6 text-emerald-400" />}
            title="Global Box Office"
            description="Access worldwide and Indian box office data from Box Office Mojo and Sacnilk."
            color="bg-emerald-500/10"
          />
          <FeatureCard 
            icon={<Trophy className="w-6 h-6 text-amber-400" />}
            title="Hall of Fame"
            description="Browse box office records, milestones, and all-time highest grossing lists."
            color="bg-amber-500/10"
          />
          <FeatureCard 
            icon={<Heart className="w-6 h-6 text-rose-400" />}
            title="Watchlist"
            description="Personal watchlist with milestones tracking and progress management."
            color="bg-rose-500/10"
          />
          <FeatureCard 
            icon={<BarChart3 className="w-6 h-6 text-purple-400" />}
            title="Comparisons"
            description="Compare movies, franchises, and cross-category analytics with detailed metrics."
            color="bg-purple-500/10"
          />
          <FeatureCard 
            icon={<TrendingUp className="w-6 h-6 text-orange-400" />}
            title="Trending & Discovery"
            description="Discover trending content, movers, and what's hot at the box office."
            color="bg-orange-500/10"
          />
          <FeatureCard 
            icon={<Search className="w-6 h-6 text-cyan-400" />}
            title="Global Search"
            description="Unified search across all content types with intelligent matching."
            color="bg-cyan-500/10"
          />
          <FeatureCard 
            icon={<Calendar className="w-6 h-6 text-sky-400" />}
            title="On This Day"
            description="Discover what movies were released on today's date throughout history."
            color="bg-sky-500/10"
          />
          <FeatureCard 
            icon={<Activity className="w-6 h-6 text-green-400" />}
            title="Real-time Updates"
            description="Live scraping from multiple sources with automatic data synchronization."
            color="bg-green-500/10"
          />
        </div>
      </CollapsibleSection>

      {/* Architecture */}
      <CollapsibleSection title="System Architecture" icon={<Layers className="w-5 h-5" />}>
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                <Server className="w-5 h-5 text-blue-500 dark:text-blue-400" />
                Backend (FastAPI)
              </h3>
              <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 dark:text-blue-400 mt-1">•</span>
                  <span>FastAPI framework with async/await support</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 dark:text-blue-400 mt-1">•</span>
                  <span>SQLite database with automatic migrations</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 dark:text-blue-400 mt-1">•</span>
                  <span>Background queue worker for scraping tasks</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 dark:text-blue-400 mt-1">•</span>
                  <span>Rotating file logging with 10MB max size</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 dark:text-blue-400 mt-1">•</span>
                  <span>CORS enabled for frontend communication</span>
                </li>
              </ul>
            </div>
            
            <div className="space-y-4">
              <h3 className="font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
                <Cpu className="w-5 h-5 text-purple-500 dark:text-purple-400" />
                Frontend (React + Vite)
              </h3>
              <ul className="space-y-2 text-sm text-slate-600 dark:text-slate-400">
                <li className="flex items-start gap-2">
                  <span className="text-purple-500 dark:text-purple-400 mt-1">•</span>
                  <span>React 18 with TypeScript</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-purple-500 dark:text-purple-400 mt-1">•</span>
                  <span>Vite for fast development and building</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-purple-500 dark:text-purple-400 mt-1">•</span>
                  <span>Tailwind CSS with custom design system</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-purple-500 dark:text-purple-400 mt-1">•</span>
                  <span>React Router for SPA navigation</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-purple-500 dark:text-purple-400 mt-1">•</span>
                  <span>Client-side logging to backend</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </CollapsibleSection>

      {/* Data Sources */}
      <CollapsibleSection title="Data Sources" icon={<Database className="w-5 h-5" />}>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {dataSources.map((source) => (
            <div key={source.name} className="flex items-start gap-4 p-4 bg-slate-100 dark:bg-slate-700/30 rounded-xl border border-slate-200 dark:border-slate-700/50">
              <div className="p-2 bg-white dark:bg-slate-600/50 rounded-lg border border-slate-200 dark:border-slate-600">
                <source.icon className="w-5 h-5 text-slate-600 dark:text-slate-300" />
              </div>
              <div>
                <h4 className="font-bold text-slate-900 dark:text-slate-200">{source.name}</h4>
                <p className="text-sm text-slate-600 dark:text-slate-400">{source.description}</p>
              </div>
            </div>
          ))}
        </div>
      </CollapsibleSection>

      {/* API Endpoints */}
      <CollapsibleSection title="API Endpoints" icon={<Code className="w-5 h-5" />}>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-slate-100 dark:bg-slate-700/50 text-slate-700 dark:text-slate-300">
              <tr>
                <th className="p-3 rounded-l-lg font-semibold text-sm">Method</th>
                <th className="p-3 font-semibold text-sm">Endpoint</th>
                <th className="p-3 rounded-r-lg font-semibold text-sm">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-700/50">
              {apiEndpoints.map((endpoint, idx) => (
                <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-700/30 transition-colors">
                  <td className="p-3">
                    <span className={`inline-flex px-2 py-1 rounded text-xs font-bold ${
                      endpoint.method === 'GET' ? 'bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400' :
                      endpoint.method === 'POST' ? 'bg-emerald-100 text-emerald-700 dark:bg-green-500/20 dark:text-green-400' :
                      endpoint.method === 'PUT' ? 'bg-amber-100 text-amber-700 dark:bg-amber-500/20 dark:text-amber-400' :
                      'bg-rose-100 text-rose-700 dark:bg-red-500/20 dark:text-red-400'
                    }`}>
                      {endpoint.method}
                    </span>
                  </td>
                  <td className="p-3 font-mono text-sm text-slate-700 dark:text-slate-300">{endpoint.path}</td>
                  <td className="p-3 text-sm text-slate-600 dark:text-slate-400">{endpoint.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-500/10 rounded-xl border border-blue-200 dark:border-blue-500/20">
          <p className="text-sm text-blue-700 dark:text-blue-300">
            <strong>Note:</strong> Full API documentation with interactive testing is available via the 
            <a href={`${backendUrl}/docs`} target="_blank" rel="noopener noreferrer" className="text-blue-600 dark:text-blue-400 hover:underline mx-1">Swagger UI</a> 
            endpoint.
          </p>
        </div>
      </CollapsibleSection>

      {/* Tech Stack */}
      <CollapsibleSection title="Technology Stack" icon={<Terminal className="w-5 h-5" />}>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { category: "Backend", items: ["Python 3.14", "FastAPI", "Uvicorn", "SQLite", "curl_cffi", "BeautifulSoup"] },
            { category: "Frontend", items: ["React 18", "TypeScript", "Vite", "Tailwind CSS", "React Router", "Lucide Icons"] },
            { category: "Data", items: ["SQLite", "Pandas", "NumPy", "JSON", "CSV Export", "PDF ReportLab"] },
            { category: "DevOps", items: ["Git", "GitHub", "VS Code", "ESLint", "Black", "Pytest"] },
          ].map((stack) => (
            <div key={stack.category} className="bg-slate-100 dark:bg-slate-700/30 rounded-xl p-4 border border-slate-200 dark:border-slate-700/50">
              <h4 className="font-bold text-slate-900 dark:text-slate-200 mb-3">{stack.category}</h4>
              <ul className="space-y-1.5">
                {stack.items.map((item) => (
                  <li key={item} className="text-sm text-slate-600 dark:text-slate-400 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-500 dark:bg-blue-400" />
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </CollapsibleSection>

      {/* Footer Info */}
      <div className="text-center pt-8 border-t border-slate-200 dark:border-slate-700/50">
        <p className="text-slate-600 dark:text-slate-400 text-sm">
          CineStats v{version} • Built with React + FastAPI • © {new Date().getFullYear()}
        </p>
        <p className="text-slate-500 dark:text-slate-500 text-xs mt-2">
          Data provided by TMDB, Box Office Mojo, Sacnilk, and other sources. 
          This product uses the TMDB API but is not endorsed or certified by TMDB.
        </p>
      </div>
    </div>
  );
}
