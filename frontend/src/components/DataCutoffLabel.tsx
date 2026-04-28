import { useState, useEffect } from "react";
import { Clock } from "lucide-react";

interface DataCutoffLabelProps {
  className?: string;
}

export default function DataCutoffLabel({ className = "" }: DataCutoffLabelProps) {
  // Get the most recent data update date from localStorage or use a default
  const [cutoffDate, setCutoffDate] = useState<string>("");
  
  useEffect(() => {
    const stored = localStorage.getItem("data_cutoff_date");
    if (stored) {
      setCutoffDate(stored);
    } else {
      // Default to current date if not set
      const today = new Date().toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric"
      });
      setCutoffDate(today);
    }
  }, []);

  return (
    <div className={`flex items-center gap-2 text-xs text-slate-500 dark:text-slate-500 ${className}`}>
      <Clock className="w-3 h-3" />
      <span>Data current as of {cutoffDate}</span>
    </div>
  );
}
