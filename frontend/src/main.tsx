import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { appLogger } from './utils/logger'

// Log frontend startup
appLogger.info('=' * 60);
appLogger.info('CINESTATS FRONTEND STARTUP');
appLogger.info('=' * 60);
appLogger.info(`Platform: ${navigator.platform}`);
appLogger.info(`User Agent: ${navigator.userAgent}`);
appLogger.info(`Screen Resolution: ${window.screen.width}x${window.screen.height}`);
appLogger.info(`Viewport: ${window.innerWidth}x${window.innerHeight}`);
appLogger.info(`Language: ${navigator.language}`);
appLogger.info('Frontend application initializing...');

// Enable flush on page unload
appLogger.flushOnUnload();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

appLogger.info('React application mounted successfully');
appLogger.info('=' * 60);
appLogger.info('CINESTATS FRONTEND READY');
appLogger.info('=' * 60);
