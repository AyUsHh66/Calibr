const getApiBaseUrl = () => {
  let url = import.meta.env.VITE_API_URL || '';
  
  // If we are in production and VITE_API_URL is missing, use the hardcoded Render URL
  if (!url && import.meta.env.PROD) {
    url = 'https://calibr-api.onrender.com';
  }
  
  // Fallback for local development if nothing is set
  if (!url) {
    url = ''; // Will use relative paths, which Vite proxy handles in dev
  }

  // Remove trailing slash if it exists
  if (url.endsWith('/')) {
    url = url.slice(0, -1);
  }
  return url;
};

export const API_BASE_URL = getApiBaseUrl();

// Debug helper to log requests
const fetchWithLogging = async (path, options = {}) => {
  const url = `${API_BASE_URL}${path}`;
  console.log(`[API Request] ${options.method || 'GET'} ${url}`);
  try {
    const response = await fetch(url, options);
    console.log(`[API Response] ${response.status} ${url}`);
    return response;
  } catch (err) {
    console.error(`[API Error] ${url}`, err);
    throw err;
  }
};

export const createSession = async (jd, resume) => {
  try {
    const response = await fetchWithLogging('/api/sessions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ jd, resume }),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error('Session creation failed:', {
        status: response.status,
        statusText: response.statusText,
        errorData
      });
      throw new Error(errorData.detail || `Failed to create session (Server Error ${response.status})`);
    }
    return response.json();
  } catch (err) {
    if (err.name === 'TypeError' && err.message === 'Failed to fetch') {
      throw new Error('Network error: Cannot reach the backend. Check VITE_API_URL or CORS settings.');
    }
    throw err;
  }
};

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetchWithLogging('/api/upload', {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) throw new Error('Failed to upload file');
  return response.json();
};

export const getQuestion = async (sessionId, skillIndex, questionNumber) => {
  const response = await fetchWithLogging(`/api/sessions/${sessionId}/question?skill_index=${skillIndex}&question_number=${questionNumber}`);
  if (!response.ok) throw new Error('Failed to fetch question');
  return response.json();
};

export const submitAnswer = async (sessionId, skillIndex, questionNumber, answer, conversationHistory, responseTime) => {
  const response = await fetchWithLogging(`/api/sessions/${sessionId}/answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      skill_index: skillIndex,
      question_number: questionNumber,
      answer,
      conversation_history: conversationHistory,
      response_time: responseTime
    }),
  });
  if (!response.ok) throw new Error('Failed to submit answer');
  return response.json();
};

export const getAnalysis = async (sessionId) => {
  const response = await fetchWithLogging(`/api/sessions/${sessionId}/analysis`);
  if (!response.ok) throw new Error('Failed to fetch analysis');
  return response.json();
};

export const getSession = async (sessionId) => {
  const response = await fetchWithLogging(`/api/sessions/${sessionId}`);
  if (!response.ok) throw new Error('Failed to fetch session');
  return response.json();
};

export const deleteSession = async (sessionId) => {
  const response = await fetchWithLogging(`/api/sessions/${sessionId}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete session');
  return response.json();
};

export const getRecruiterCandidates = async () => {
  const response = await fetchWithLogging('/api/recruiter/candidates');
  if (!response.ok) throw new Error('Failed to fetch recruiter candidates');
  return response.json();
};

export const compareCandidates = async (sessionIds) => {
  const response = await fetchWithLogging(`/api/recruiter/compare?session_ids=${sessionIds.join(',')}`);
  if (!response.ok) throw new Error('Failed to compare candidates');
  return response.json();
};
