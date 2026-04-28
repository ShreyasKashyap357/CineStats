import { X, Check } from "lucide-react";

interface GenreDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  availableGenres: string[];
  selectedGenres: string[];
  onGenreToggle: (genre: string) => void;
  onClearAll: () => void;
  onSelectAll: () => void;
}

export default function GenreDrawer({
  isOpen,
  onClose,
  availableGenres,
  selectedGenres,
  onGenreToggle,
  onClearAll,
  onSelectAll
}: GenreDrawerProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm animate-in fade-in duration-300"
        onClick={onClose}
      />

      {/* Drawer */}
      <div className="absolute right-0 top-0 h-full w-full max-w-md bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-700/50 shadow-2xl animate-in slide-in-from-right duration-300">
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-slate-200 dark:border-slate-700/50">
            <h2 className="text-xl font-bold text-slate-900 dark:text-slate-100">Filter by Genre</h2>
            <button
              onClick={onClose}
              className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800/50 hover:bg-slate-200 dark:hover:bg-slate-700/50 text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors"
              title="Close"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Actions */}
          <div className="flex gap-3 p-4 border-b border-slate-200 dark:border-slate-700/50">
            <button
              onClick={onSelectAll}
              className="flex-1 py-2 px-4 rounded-xl bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400 border border-blue-300 dark:border-blue-500/30 hover:bg-blue-200 dark:hover:bg-blue-500/30 font-bold text-sm transition-all"
            >
              Select All
            </button>
            <button
              onClick={onClearAll}
              className="flex-1 py-2 px-4 rounded-xl bg-slate-100 dark:bg-slate-800/50 text-slate-600 dark:text-slate-400 border border-slate-300 dark:border-slate-700/50 hover:bg-slate-200 dark:hover:bg-slate-700/50 font-bold text-sm transition-all"
            >
              Clear All
            </button>
          </div>

          {/* Genre List */}
          <div className="flex-1 overflow-y-auto p-4">
            <div className="grid grid-cols-2 gap-3">
              {availableGenres.map((genre) => {
                const isSelected = selectedGenres.includes(genre);
                return (
                  <button
                    key={genre}
                    onClick={() => onGenreToggle(genre)}
                    className={`p-4 rounded-xl border transition-all font-bold text-sm flex items-center justify-between ${
                      isSelected
                        ? 'bg-blue-100 dark:bg-blue-500/20 text-blue-700 dark:text-blue-400 border-blue-300 dark:border-blue-500/30'
                        : 'bg-slate-100 dark:bg-slate-800/50 text-slate-600 dark:text-slate-400 border-slate-300 dark:border-slate-700/50 hover:border-slate-400 dark:hover:border-slate-600'
                    }`}
                  >
                    <span>{genre}</span>
                    {isSelected && <Check className="w-4 h-4" />}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-slate-200 dark:border-slate-700/50">
            <div className="flex items-center justify-between text-sm text-slate-500 dark:text-slate-400 mb-4">
              <span>{selectedGenres.length} selected</span>
              <span>of {availableGenres.length} genres</span>
            </div>
            <button
              onClick={onClose}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-400 hover:to-indigo-500 text-white font-bold transition-all shadow-lg shadow-blue-500/20"
            >
              Apply Filters
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
