const getApiBaseUrl = () => {
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  // In dev (Vite) and prod (Nginx), we use the /api proxy
  return '';
};

export const API_BASE_URL = getApiBaseUrl();

export const createSession = async (jd, resume) => {
  const response = await fetch(`${API_BASE_URL}/api/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ jd, resume }),
  });
  if (!response.ok) throw new Error('Failed to create session');
  return response.json();
};

export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) throw new Error('Failed to upload file');
  return response.json();
};

export const getQuestion = async (sessionId, skillIndex, questionNumber) => {
  const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/question?skill_index=${skillIndex}&question_number=${questionNumber}`);
  if (!response.ok) throw new Error('Failed to fetch question');
  return response.json();
};

export const submitAnswer = async (sessionId, skillIndex, questionNumber, answer, conversationHistory, responseTime) => {
  const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/answer`, {
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
  const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/analysis`);
  if (!response.ok) throw new Error('Failed to fetch analysis');
  return response.json();
};

export const getSession = async (sessionId) => {
  const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}`);
  if (!response.ok) throw new Error('Failed to fetch session');
  return response.json();
};

export const deleteSession = async (sessionId) => {
  const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete session');
  return response.json();
};

export const getRecruiterCandidates = async () => {
  const response = await fetch(`${API_BASE_URL}/api/recruiter/candidates`);
  if (!response.ok) throw new Error('Failed to fetch recruiter candidates');
  return response.json();
};

export const compareCandidates = async (sessionIds) => {
  const response = await fetch(`${API_BASE_URL}/api/recruiter/compare?session_ids=${sessionIds.join(',')}`);
  if (!response.ok) throw new Error('Failed to compare candidates');
  return response.json();
};
