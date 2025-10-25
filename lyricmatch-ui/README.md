# WaveSeek - Refactored Component Structure

## 📁 Project Structure

```
src/
├── App.tsx                          # Main application component
├── styles/
│   └── theme.css                    # Theme variables and global styles
├── contexts/
│   └── ThemeContext.jsx             # Theme provider and hook
├── utils/
│   ├── db.js                        # IndexedDB utilities for history
│   ├── api.js                       # API functions for backend calls
│   └── theme.js                     # Theme utility functions
└── components/
    ├── Header.jsx                   # Main header with navigation
    ├── TierBadge.jsx                # Premium/Free tier badge
    ├── ConfigModal.jsx              # Configuration modal for settings
    ├── TierSelectionModal.jsx       # Tier selection modal
    ├── WaveformVisualizer.jsx       # Audio waveform visualization
    ├── HistoryModal.jsx             # Search history modal
    ├── ArtistFetchModal.jsx         # Add artist to database modal
    ├── UploadView.jsx               # Upload and record tabs view
    ├── AudioRecorder.jsx            # Audio recording component
    ├── ProcessingView.jsx           # Processing status view
    ├── ResultsView.jsx              # Results display view
    ├── StreamingButton.jsx          # Spotify/YouTube buttons
    ├── MatchExplanation.jsx         # Match explanation display
    ├── LyricsMatchDisplay.jsx       # Lyrics matching visualization
    └── SongPreview.jsx              # Song preview component
```

## 🚀 Component Overview

### Core Components

#### **App.tsx**
- Main application component
- Manages global state (view, tier, results, etc.)
- Handles file upload and processing flow
- Coordinates between different views

#### **Header.jsx**
- Application header with branding
- Navigation controls (History, Theme Toggle, Tier Change, Add Artist)
- Integrates HistoryModal

### Context & Utilities

#### **ThemeContext.jsx**
- Provides theme state (dark/light mode)
- `useTheme()` hook for accessing theme

#### **db.js**
- `initDB()` - Initialize IndexedDB
- `saveToHistory()` - Save search to history
- `getHistory()` - Retrieve search history
- `clearHistory()` - Clear all history

#### **api.js**
- `uploadAudio()` - Upload audio file
- `getJobStatus()` - Poll job status
- `fetchSpotifyTrack()` - Get Spotify data
- `fetchYouTubeVideo()` - Get YouTube data
- `fetchArtistSongs()` - Add artist to database

#### **theme.js**
- `initTheme()` - Initialize theme system
- `setTheme()` - Set and persist theme
- `getTheme()` - Get current theme
- `toggleTheme()` - Toggle between dark/light
- `watchSystemTheme()` - Listen to system theme changes
- `getThemeColors()` - Get current theme colors
- `applyCustomTheme()` - Apply custom colors
- `resetTheme()` - Reset to default
- `isDarkMode()` / `isLightMode()` - Check current mode

### UI Components

#### **TierBadge.jsx**
Simple badge component showing Free/Premium status with icon.

#### **ConfigModal.jsx**
Configuration modal for selecting:
- Whisper model (tiny, base, small, medium, large)
- Matching engine (TF-IDF, Neural, Hybrid)
- SBERT model (for neural/hybrid)

#### **TierSelectionModal.jsx**
Modal for choosing between Free and Premium tiers with feature comparison.

#### **WaveformVisualizer.jsx**
Canvas-based animated waveform visualization.

#### **HistoryModal.jsx**
Displays search history from IndexedDB with:
- Search results
- Timestamps
- Configuration used
- Clear history option

#### **ArtistFetchModal.jsx**
Modal to add an artist's songs to the database via Genius API.

### View Components

#### **UploadView.jsx**
Main upload interface with:
- Drag & drop file upload
- Browse file button
- Audio recorder tab
- Feature highlights

#### **AudioRecorder.jsx**
Audio recording component with:
- Real-time waveform visualization
- Duration timer
- Pause/Resume controls
- Max duration based on tier

#### **ProcessingView.jsx**
Processing status display with:
- Circular progress indicator
- Stage-by-stage breakdown
- Animated waveform
- Configuration info

#### **ResultsView.jsx**
Comprehensive results display with:
- Album artwork
- Track information
- Streaming service links
- Match explanations
- Audio analysis stats

#### **StreamingButton.jsx**
Streaming service button with:
- Spotify/YouTube integration
- 30-second preview player (Spotify)
- Fallback search links

#### **MatchExplanation.jsx**
Explains why the match was found:
- Engine-specific explanations
- Confidence level
- Match statistics

#### **LyricsMatchDisplay.jsx**
Visualizes lyrics matching:
- Top matching phrases
- Highlighted lyrics
- Match percentage visualization

#### **SongPreview.jsx**
Simple song preview component with:
- Spotify search link
- YouTube search link
- External link indicators

## 🎨 Styling

### Theme System
The app uses CSS custom properties for theming:
- `--bg-primary`, `--bg-secondary`, `--bg-tertiary`
- `--text-primary`, `--text-secondary`, `--text-tertiary`
- `--border`, `--accent`, `--accent-secondary`
- `--premium`, `--premium-glow`

Themes automatically switch between dark and light modes using `data-theme` attribute.

## 📦 Dependencies

All components use:
- **React** (hooks: useState, useEffect, useRef)
- **lucide-react** for icons
- **Tailwind CSS** utility classes
- CSS custom properties for theming

## 🔧 Integration

### Import Example
```javascript
// In App.tsx
import { ThemeProvider } from './contexts/ThemeContext';
import { Header } from './components/Header';
import { UploadView } from './components/UploadView';
import { SongPreview } from './components/SongPreview';
import { uploadAudio, getJobStatus } from './utils/api';
import { saveToHistory } from './utils/db';
import { initTheme, toggleTheme } from './utils/theme';
import './styles/theme.css';

// Initialize theme on app load
useEffect(() => {
  initTheme();
}, []);
```

### Usage Example
```javascript
<ThemeProvider>
  <Header 
    currentTier={tier} 
    onChangeTier={handleChangeTier}
    setShowArtistFetch={setShowArtistFetch}
  />
  <UploadView 
    onUpload={handleFileUpload}
    currentTier={tier}
    onOpenConfig={() => setShowConfigModal(true)}
  />
  {/* In results view */}
  <SongPreview 
    artist={topMatch.artist}
    title={topMatch.title}
    album={topMatch.album}
  />
</ThemeProvider>
```

### Theme Utilities Usage
```javascript
import { toggleTheme, getThemeColors, watchSystemTheme } from './utils/theme';

// Toggle theme
const handleToggle = () => {
  const newTheme = toggleTheme();
  console.log('Switched to:', newTheme);
};

// Get current colors
const colors = getThemeColors();
console.log('Primary background:', colors.bgPrimary);

// Watch system theme changes
useEffect(() => {
  const cleanup = watchSystemTheme((systemTheme) => {
    console.log('System theme changed to:', systemTheme);
  });
  return cleanup;
}, []);
```

## ✨ Features

- **Modular Architecture**: Each component is self-contained
- **Reusable Utilities**: Shared functions in utils/
- **Theme Support**: Light/Dark mode with smooth transitions
- **Type Safety**: Clear prop interfaces
- **State Management**: Centralized in App.tsx
- **Persistent Storage**: IndexedDB for history
- **Session Storage**: Resume interrupted sessions

## 🚦 State Flow

1. **Upload** → File selected → Config modal → Processing
2. **Processing** → Poll status → Complete → Results
3. **Results** → Display match → Save to history → Option to reset

## 📝 Notes

- All components use React hooks (no class components)
- Theme context available via `useTheme()` hook
- Theme utilities available in `utils/theme.js`
- API calls centralized in `utils/api.js`
- History stored in browser's IndexedDB
- Session state persisted in sessionStorage
- All modals use portal-like fixed positioning
- `SongPreview` component for simple music service links

## 🔐 Security

- No localStorage/sessionStorage for artifacts
- All data stored in IndexedDB
- API calls to localhost backend only
- No sensitive data exposure

---

**Note**: Make sure to import `theme.css` in your main App.tsx file to enable theme support!