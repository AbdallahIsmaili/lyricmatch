// src/utils/theme.js

/**
 * Initialize theme system
 * Call this once when the app loads
 */
export const initTheme = () => {
  // Check if theme is already set in localStorage
  const savedTheme = localStorage.getItem('waveseek-theme');
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  
  // Use saved theme, otherwise use system preference
  const initialTheme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
  
  // Apply theme to document
  document.documentElement.setAttribute('data-theme', initialTheme);
  
  return initialTheme;
};

/**
 * Set theme and persist to localStorage
 * @param {string} theme - 'dark' or 'light'
 */
export const setTheme = (theme) => {
  if (theme !== 'dark' && theme !== 'light') {
    console.error('Invalid theme. Use "dark" or "light"');
    return;
  }
  
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('waveseek-theme', theme);
};

/**
 * Get current theme
 * @returns {string} Current theme ('dark' or 'light')
 */
export const getTheme = () => {
  return document.documentElement.getAttribute('data-theme') || 'dark';
};

/**
 * Toggle between dark and light theme
 * @returns {string} New theme
 */
export const toggleTheme = () => {
  const currentTheme = getTheme();
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
  setTheme(newTheme);
  return newTheme;
};

/**
 * Listen to system theme changes
 * @param {Function} callback - Called when system theme changes
 * @returns {Function} Cleanup function to remove listener
 */
export const watchSystemTheme = (callback) => {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  
  const handler = (e) => {
    const systemTheme = e.matches ? 'dark' : 'light';
    callback(systemTheme);
  };
  
  // Modern browsers
  if (mediaQuery.addEventListener) {
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  } 
  // Fallback for older browsers
  else {
    mediaQuery.addListener(handler);
    return () => mediaQuery.removeListener(handler);
  }
};

/**
 * Get theme colors for current theme
 * @returns {Object} Object with color values
 */
export const getThemeColors = () => {
  const root = document.documentElement;
  const computedStyle = getComputedStyle(root);
  
  return {
    bgPrimary: computedStyle.getPropertyValue('--bg-primary').trim(),
    bgSecondary: computedStyle.getPropertyValue('--bg-secondary').trim(),
    bgTertiary: computedStyle.getPropertyValue('--bg-tertiary').trim(),
    textPrimary: computedStyle.getPropertyValue('--text-primary').trim(),
    textSecondary: computedStyle.getPropertyValue('--text-secondary').trim(),
    textTertiary: computedStyle.getPropertyValue('--text-tertiary').trim(),
    border: computedStyle.getPropertyValue('--border').trim(),
    accent: computedStyle.getPropertyValue('--accent').trim(),
    accentSecondary: computedStyle.getPropertyValue('--accent-secondary').trim(),
    premium: computedStyle.getPropertyValue('--premium').trim(),
    premiumGlow: computedStyle.getPropertyValue('--premium-glow').trim(),
  };
};

/**
 * Apply custom theme colors
 * @param {Object} colors - Object with color overrides
 */
export const applyCustomTheme = (colors) => {
  const root = document.documentElement;
  
  Object.entries(colors).forEach(([key, value]) => {
    // Convert camelCase to kebab-case
    const cssVar = key.replace(/([A-Z])/g, '-$1').toLowerCase();
    root.style.setProperty(`--${cssVar}`, value);
  });
};

/**
 * Reset theme to default
 */
export const resetTheme = () => {
  const root = document.documentElement;
  const theme = getTheme();
  
  // Remove all inline styles
  root.removeAttribute('style');
  
  // Reapply data-theme attribute
  root.setAttribute('data-theme', theme);
};

/**
 * Check if dark mode is active
 * @returns {boolean}
 */
export const isDarkMode = () => {
  return getTheme() === 'dark';
};

/**
 * Check if light mode is active
 * @returns {boolean}
 */
export const isLightMode = () => {
  return getTheme() === 'light';
};

/**
 * Preload theme to avoid flash
 * Add this script tag to your HTML head before other scripts
 */
export const getThemePreloadScript = () => {
  return `
    <script>
      (function() {
        const savedTheme = localStorage.getItem('waveseek-theme');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const theme = savedTheme || (systemPrefersDark ? 'dark' : 'light');
        document.documentElement.setAttribute('data-theme', theme);
      })();
    </script>
  `;
};

// Export all functions as default
export default {
  initTheme,
  setTheme,
  getTheme,
  toggleTheme,
  watchSystemTheme,
  getThemeColors,
  applyCustomTheme,
  resetTheme,
  isDarkMode,
  isLightMode,
  getThemePreloadScript
};