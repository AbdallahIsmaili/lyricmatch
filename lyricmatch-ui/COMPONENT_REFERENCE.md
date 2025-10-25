# Component Reference Guide

## Quick Component Props Reference

### TierBadge
```jsx
<TierBadge 
  tier="free" | "premium"
  size="sm" | "lg"
/>
```

### WaveformVisualizer
```jsx
<WaveformVisualizer 
  isActive={boolean}
/>
```

### Header
```jsx
<Header 
  currentTier="free" | "premium"
  onChangeTier={() => void}
  setShowArtistFetch={(boolean) => void}
/>
```

### HistoryModal
```jsx
<HistoryModal 
  isOpen={boolean}
  onClose={() => void}
  onSelectItem={(item) => void}
/>
```

### ConfigModal
```jsx
<ConfigModal 
  isOpen={boolean}
  onClose={() => void}
  onStart={(config) => void}
  currentTier="free" | "premium"
  onChangeTier={() => void}
/>
```

### TierSelectionModal
```jsx
<TierSelectionModal 
  isOpen={boolean}
  onClose={() => void}
  onSelectTier={(tier) => void}
/>
```

### ArtistFetchModal
```jsx
<ArtistFetchModal 
  isOpen={boolean}
  onClose={() => void}
  onFetch={() => void}
/>
```

### UploadView
```jsx
<UploadView 
  onUpload={(file) => void}
  currentTier="free" | "premium"
  onOpenConfig={() => void}
/>
```

### AudioRecorder
```jsx
<AudioRecorder 
  onRecordingComplete={(file) => void}
  currentTier="free" | "premium"
/>
```

### ProcessingView
```jsx
<ProcessingView 
  progress={number}          // 0-100
  filename={string}
  status="queued" | "preprocessing" | "transcribing" | "matching" | "complete"
  tier="free" | "premium"
  config={{
    whisper_model: string,
    engine: string,
    sbert_model?: string
  }}
/>
```

### ResultsView
```jsx
<ResultsView 
  results={{
    topMatch: {
      title: string,
      artist: string,
      album?: string,
      year?: number,
      final_score: number,
      lyrics_cleaned?: string,
      match_percentage?: number
    },
    transcription?: string,
    audioInfo?: {
      sample_rate: number,
      duration: number,
      bitrate: number,
      channels: number,
      file_size_mb: number
    }
  }}
  onReset={() => void}
  tier="free" | "premium"
  config={{
    engine: string
  }}
/>
```

### StreamingButton
```jsx
<StreamingButton 
  platform="spotify" | "youtube"
  url={string}
  loading={boolean}
  artist={string}
  title={string}
  previewUrl={string | null}
/>
```

### MatchExplanation
```jsx
<MatchExplanation 
  match={{
    final_score: number,
    match_type: string,
    common_word_count?: number,
    neural_score?: number,
    fuzzy_score?: number,
    match_percentage?: number
  }}
  tier="free" | "premium"
  engine="tfidf" | "neural" | "hybrid"
/>
```

### LyricsMatchDisplay
```jsx
<LyricsMatchDisplay 
  queryText={string}
  songLyrics={string}
  matchPercentage={number}
/>
```

### SongPreview
```jsx
<SongPreview 
  artist={string}
  title={string}
  album={string}
/>
```

---

## Context Usage

### ThemeProvider
```jsx
import { ThemeProvider, useTheme } from './contexts/ThemeContext';

// Wrap app
<ThemeProvider>
  <App />
</ThemeProvider>

// Use in component
function MyComponent() {
  const { theme, toggleTheme } = useTheme();
  
  return (
    <button onClick={toggleTheme}>
      Current: {theme}
    </button>
  );
}
```

---

## Utility Functions

### Database (db.js)
```javascript
import { initDB, saveToHistory, getHistory, clearHistory } from './utils/db';

// Initialize
await initDB();

// Save to history
await saveToHistory({
  filename: 'song.mp3',
  topMatch: {...},
  tier: 'premium',
  config: {...}
});

// Get history
const items = await getHistory(20); // limit 20

// Clear all
await clearHistory();
```

### API (api.js)
```javascript
import { 
  uploadAudio, 
  getJobStatus, 
  fetchSpotifyTrack, 
  fetchYouTubeVideo,
  fetchArtistSongs 
} from './utils/api';

// Upload audio
const { job_id } = await uploadAudio(file, config, tier);

// Check status
const status = await getJobStatus(jobId);

// Get Spotify data
const spotify = await fetchSpotifyTrack(artist, title);
// Returns: { url, image, preview_url }

// Get YouTube data
const youtube = await fetchYouTubeVideo(artist, title);
// Returns: { url }

// Fetch artist songs
const result = await fetchArtistSongs(artistName);
// Returns: { artist, songs_added }
```

### Theme (theme.js)
```javascript
import { 
  initTheme, 
  setTheme, 
  getTheme, 
  toggleTheme,
  watchSystemTheme,
  getThemeColors,
  isDarkMode 
} from './utils/theme';

// Initialize on app load
initTheme();

// Set theme
setTheme('dark');

// Get current
const current = getTheme(); // 'dark' or 'light'

// Toggle
const newTheme = toggleTheme();

// Check mode
if (isDarkMode()) {
  console.log('Dark mode active');
}

// Get colors
const colors = getThemeColors();
console.log(colors.bgPrimary);

// Watch system changes
const cleanup = watchSystemTheme((theme) => {
  console.log('System theme:', theme);
});
// Call cleanup() when done
```

---

## Common Patterns

### Modal Pattern
```jsx
const [showModal, setShowModal] = useState(false);

<button onClick={() => setShowModal(true)}>Open</button>

<ConfigModal 
  isOpen={showModal}
  onClose={() => setShowModal(false)}
  onStart={(config) => {
    console.log(config);
    setShowModal(false);
  }}
/>
```

### File Upload Pattern
```jsx
const handleFileUpload = (file) => {
  // Validate
  if (file.size > maxSize) {
    setError('File too large');
    return;
  }
  
  // Process
  setUploadedFile(file);
  startProcessing(file);
};

<UploadView onUpload={handleFileUpload} />
```

### State Flow Pattern
```jsx
// App.tsx typical flow
const [view, setView] = useState('upload');
const [results, setResults] = useState(null);

// Upload → Processing → Results
setView('processing');
// ... processing ...
setView('results');
```

---

## Styling Reference

### CSS Variables
```css
/* Available in all components */
var(--bg-primary)
var(--bg-secondary)
var(--bg-tertiary)
var(--bg-header)
var(--text-primary)
var(--text-secondary)
var(--text-tertiary)
var(--border)
var(--accent)
var(--accent-secondary)
var(--premium)
var(--premium-glow)
```

### Common Tailwind Classes Used
- `bg-[var(--bg-primary)]`
- `text-[var(--text-primary)]`
- `border-[var(--border)]`
- `hover:bg-[var(--bg-secondary)]`
- `transition-all duration-300`

---

## Error Handling

### API Errors
```javascript
try {
  const response = await uploadAudio(file, config, tier);
} catch (error) {
  setError(error.message);
}
```

### Database Errors
```javascript
try {
  await saveToHistory(data);
} catch (error) {
  console.error('Failed to save:', error);
  // Non-critical, continue
}
```

---

## Testing Tips

### Component Testing
```javascript
import { render, screen } from '@testing-library/react';
import { TierBadge } from './TierBadge';

test('renders premium badge', () => {
  render(<TierBadge tier="premium" />);
  expect(screen.getByText('Premium')).toBeInTheDocument();
});
```

### Context Testing
```javascript
import { ThemeProvider } from './contexts/ThemeContext';

test('theme toggle works', () => {
  render(
    <ThemeProvider>
      <MyComponent />
    </ThemeProvider>
  );
  // ... test theme functionality
});
```

---

## Performance Tips

1. **Lazy load modals**: Only render when `isOpen={true}`
2. **Memoize callbacks**: Use `useCallback` for handlers
3. **Debounce API calls**: Add delays for polling
4. **Canvas optimization**: RequestAnimationFrame in WaveformVisualizer
5. **Image lazy loading**: Use loading="lazy" on images

---

## Accessibility

All components include:
- Semantic HTML
- ARIA labels where needed
- Keyboard navigation support
- Focus management
- Color contrast compliance

---

## Browser Support

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support (iOS 13+)
- Opera: ✅ Full support

Requires:
- IndexedDB
- MediaRecorder API
- Canvas API
- CSS Custom Properties