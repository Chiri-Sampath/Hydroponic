/**
 * AgriSmart AI — API Configuration
 * ==================================
 * Single source of truth for API base URL.
 * Change this to production URL when deploying.
 */

const isLocalHost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

const AgriConfig = {
  // Uses local server when testing locally, and points to live production backend on Render/Vercel
  API_BASE: isLocalHost 
    ? 'http://localhost:5000/api' 
    : (window.ENV_API_BASE || localStorage.getItem('AGRISMART_API_URL') || 'https://agrismart-backend-kx8k.onrender.com/api'),
  APP_NAME: 'AgriSmart AI',
  APP_VERSION: '1.0.0',

  // Token storage keys
  TOKEN_KEY: 'agrismart_access_token',
  REFRESH_TOKEN_KEY: 'agrismart_refresh_token',
  USER_KEY: 'agrismart_user',

  // Demo mode notice
  DEMO_MODE: true,

  // Attribution
  WEATHER_SOURCE: 'Open-Meteo (open-meteo.com)',
  GEOCODING_SOURCE: 'OpenStreetMap Nominatim (nominatim.openstreetmap.org)',
};

// Automatically mount interactive bio-field background engine across all pages
(function autoLoadInteractiveBg() {
  if (window.__AgriSmartBgInitialized) return;
  const currentScript = document.currentScript;
  let basePath = 'js/';
  if (currentScript && currentScript.src) {
    basePath = currentScript.src.substring(0, currentScript.src.lastIndexOf('/') + 1);
  } else {
    basePath = window.location.pathname.includes('/pages/') ? '../../js/' : 'js/';
  }
  const bgScript = document.createElement('script');
  bgScript.src = basePath + 'interactive-bg.js';
  bgScript.defer = true;
  document.head.appendChild(bgScript);
})();

