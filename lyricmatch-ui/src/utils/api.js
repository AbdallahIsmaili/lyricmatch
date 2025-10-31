import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// export const uploadAudio = async (file) => {
//   const formData = new FormData();
//   formData.append('audio', file);
  
//   const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
//     headers: {
//       'Content-Type': 'multipart/form-data',
//     },
//   });
  
//   return response.data;
// };

// export const getJobStatus = async (jobId) => {
//   const response = await api.get(`/status/${jobId}`);
//   return response.data;
// };

export const searchLyrics = async (query) => {
  const response = await api.post('/search', { query });
  return response.data;
};

export const getStats = async () => {
  const response = await api.get('/stats');
  return response.data;
};

export const getGPUStatus = async () => {
  const response = await api.get('/gpu/status');
  return response.data;
};

export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};


export const uploadAudio = async (file, config, tier) => {
  const formData = new FormData();
  formData.append('audio', file);
  formData.append('tier', tier);
  formData.append('whisper_model', config.whisper_model);
  formData.append('engine', config.engine);
  formData.append('use_gpu', config.use_gpu || 'false');
  
  // Send matching method info
  formData.append('matching_method', config.matching_method || 'tfidf');
  formData.append('hybrid_methods', JSON.stringify(config.hybrid_methods || []));
  
  // Legacy fingerprint flag (for backwards compatibility)
  const use_fingerprint = config.matching_method === 'fingerprint' || 
                         (config.matching_method === 'hybrid' && config.hybrid_methods?.includes('fingerprint'));
  formData.append('use_fingerprint', use_fingerprint.toString());
  
  if (config.sbert_model) {
    formData.append('sbert_model', config.sbert_model);
  }
  
  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: 'POST',
    body: formData,
  });
  
  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || 'Upload failed');
  }
  return response.json();
};


export const getJobStatus = async (jobId) => {
  const response = await fetch(`${API_BASE_URL}/status/${jobId}`);
  if (!response.ok) throw new Error('Status check failed');
  return response.json();
};

export const fetchSpotifyTrack = async (artist, title) => {
  try {
    const response = await fetch(`${API_BASE_URL}/spotify/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ artist, title })
    });
    
    if (response.ok) {
      const data = await response.json();
      return data;
    }
  } catch (error) {
    console.error('Spotify fetch error:', error);
  }
  return null;
};

export const fetchYouTubeVideo = async (artist, title) => {
  try {
    const response = await fetch(`${API_BASE_URL}/youtube/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ artist, title })
    });
    
    if (response.ok) {
      return await response.json();
    }
  } catch (error) {
    console.error('YouTube fetch error:', error);
  }
  return null;
};

export const fetchArtistSongs = async (artistName) => {
  const response = await fetch(`${API_BASE_URL}/lyrics/fetch-artist`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ artist_name: artistName })
  });
  
  const data = await response.json();
  
  if (!response.ok) {
    throw new Error(data.error || 'Failed to fetch artist songs');
  }
  
  return data;
};

