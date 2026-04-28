import { LayoutGrid, List } from "lucide-react";

interface TableToggleProps {
  viewMode: "grid" | "table";
  onViewModeChange: (mode: "grid" | "table") => void;
  className?: string;
}

export default function TableToggle({ viewMode, onViewModeChange, className = "" }: TableToggleProps) {
  return (
    <div className={`flex items-center bg-slate-100 dark:bg-slate-800/50 rounded-xl p-1 border border-slate-200 dark:border-slate-700/50 ${className}`}>
      <button
        onClick={() => onViewModeChange("grid")}
        className={`p-2 rounded-lg transition-all ${viewMode === "grid" ? "bg-slate-300 dark:bg-slate-700 text-slate-800 dark:text-slate-100" : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"}`}
        title="Grid view"
      >
        <LayoutGrid className="w-4 h-4" />
      </button>
      <button
        onClick={() => onViewModeChange("table")}
        className={`p-2 rounded-lg transition-all ${viewMode === "table" ? "bg-slate-300 dark:bg-slate-700 text-slate-800 dark:text-slate-100" : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"}`}
        title="Table view"
      >
        <List className="w-4 h-4" />
      </button>
    </div>
  );
}
