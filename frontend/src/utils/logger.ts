/**
 * CineStats Frontend Logger
 * Client-side logging utility that sends logs to backend for centralized storage
 */

type LogLevel = 'INFO' | 'WARNING' | 'ERROR' | 'DEBUG';

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  source: string;
  message: string;
  context?: Record<string, any>;
}

class Logger {
  private source: string;
  private logQueue: LogEntry[] = [];
  private maxQueueSize = 50;
  private flushInterval = 5000; // 5 seconds

  constructor(source: string) {
    this.source = source;
    this.startFlushInterval();
  }

  private getTimestamp(): string {
    const now = new Date();
    const day = String(now.getDate()).padStart(2, '0');
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const year = now.getFullYear();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    const ms = String(now.getMilliseconds()).padStart(3, '0');
    return `${day}${month}${year} ${hours}${minutes}${seconds}.${ms}`;
  }

  private addToQueue(entry: LogEntry) {
    this.logQueue.push(entry);
    if (this.logQueue.length >= this.maxQueueSize) {
      this.flush();
    }
  }

  private async flush() {
    if (this.logQueue.length === 0) return;

    const logsToSend = [...this.logQueue];
    this.logQueue = [];

    try {
      await fetch('http://localhost:8000/api/logs/client', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ logs: logsToSend }),
      });
    } catch (e) {
      // If backend is unavailable, keep logs in queue for retry
      this.logQueue = [...logsToSend, ...this.logQueue];
      console.error('[Logger] Failed to send logs to backend:', e);
    }
  }

  private startFlushInterval() {
    setInterval(() => this.flush(), this.flushInterval);
  }

  private log(level: LogLevel, message: string, context?: Record<string, any>) {
    const entry: LogEntry = {
      timestamp: this.getTimestamp(),
      level,
      source: this.source,
      message,
      context,
    };

    // Console output for development
    const consoleMethod = level === 'ERROR' ? console.error : 
                         level === 'WARNING' ? console.warn :
                         level === 'DEBUG' ? console.debug : console.log;
    consoleMethod(`[${entry.timestamp}] [${level}] [${this.source}] ${message}`, context || '');

    // Add to queue for backend storage
    this.addToQueue(entry);
  }

  info(message: string, context?: Record<string, any>) {
    this.log('INFO', message, context);
  }

  warning(message: string, context?: Record<string, any>) {
    this.log('WARNING', message, context);
  }

  error(message: string, context?: Record<string, any>) {
    this.log('ERROR', message, context);
  }

  debug(message: string, context?: Record<string, any>) {
    this.log('DEBUG', message, context);
  }

  // Flush remaining logs before page unload
  flushOnUnload() {
    window.addEventListener('beforeunload', () => {
      this.flush();
    });
  }
}

// Create logger instances for different parts of the app
export const appLogger = new Logger('frontend-app');
export const apiLogger = new Logger('frontend-api');
export const uiLogger = new Logger('frontend-ui');

// Log startup
appLogger.info('Frontend application initialized');
