import React, { useState, useRef } from 'react';
import { createSession, uploadFile } from '../api';

const Setup = ({ onSessionCreated }) => {
  const [jd, setJd] = useState('');
  const [resume, setResume] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dragField, setDragField] = useState(null); // 'jd' or 'resume'
  const [uploadState, setUploadState] = useState({ jd: 'idle', resume: 'idle' });
  const [uploadMessage, setUploadMessage] = useState({ jd: '', resume: '' });
  
  const jdInputRef = useRef(null);
  const resumeInputRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!jd || !resume) {
      setError('Please provide both a job description and a resume.');
      return;
    }

    setLoading(true);
    setError('');
    try {
      const data = await createSession(jd, resume);
      localStorage.setItem('calibr_session_id', data.session_id);
      onSessionCreated(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDragOver = (e, field) => {
    e.preventDefault();
    e.stopPropagation();
    setDragField(field);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragField(null);
  };

  const handleFileDrop = async (file, field) => {
    if (!file) return;

    // Validate file type
    const validTypes = ['application/pdf', 'text/plain', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!validTypes.includes(file.type) && !file.name.endsWith('.docx')) {
      setError('Please upload a PDF, TXT, or DOCX file.');
      return;
    }

    setUploadState(prev => ({ ...prev, [field]: 'uploading' }));
    setUploadMessage(prev => ({ ...prev, [field]: 'Extracting text...' }));
    setError(''); // Clear any previous errors
    
    try {
      const result = await uploadFile(file);
      
      if (result.success) {
        if (field === 'jd') setJd(result.text);
        if (field === 'resume') setResume(result.text);
        
        setUploadState(prev => ({ ...prev, [field]: 'success' }));
        setUploadMessage(prev => ({ 
          ...prev, 
          [field]: `✓ ${result.filename} extracted (${result.char_count.toLocaleString()} chars)` 
        }));
      } else {
        setUploadState(prev => ({ ...prev, [field]: 'error' }));
        setUploadMessage(prev => ({ ...prev, [field]: `✗ ${result.error}` }));
        setError(result.error);
      }
    } catch (err) {
      setUploadState(prev => ({ ...prev, [field]: 'error' }));
      setUploadMessage(prev => ({ ...prev, [field]: '✗ Upload failed. Please paste text manually.' }));
      setError('Connection failed. Please ensure the backend is running.');
    }
  };

  const onDrop = (e, field) => {
    e.preventDefault();
    e.stopPropagation();
    setDragField(null);
    const file = e.dataTransfer.files[0];
    handleFileDrop(file, field);
  };

  const onFileChange = (e, field) => {
    const file = e.target.files[0];
    handleFileDrop(file, field);
  };

  return (
    <div className="setup-container animate-fade-up">
      <header className="setup-header">
        <h1 className="gradient-text">Know exactly who you're hiring</h1>
        <p className="subtitle">AI-powered skill assessment that goes beyond the resume</p>
      </header>
      
      <form onSubmit={handleSubmit} className="setup-form stagger-children">
        {/* Job Description Card */}
        <div className="setup-card" style={{ animationDelay: '0ms' }}>
          <div className="input-group">
            <div className="label-row">
              <label>Job Description</label>
              {uploadMessage.jd && (
                <span className={`upload-status ${uploadState.jd}`}>
                  {uploadMessage.jd}
                </span>
              )}
            </div>
            <div 
              className={`drag-drop-zone ${dragField === 'jd' ? 'dragging' : ''} ${uploadState.jd}`}
              onDragOver={(e) => handleDragOver(e, 'jd')}
              onDragLeave={handleDragLeave}
              onDrop={(e) => onDrop(e, 'jd')}
              onClick={() => jdInputRef.current.click()}
            >
              <textarea 
                value={jd} 
                onChange={(e) => setJd(e.target.value)} 
                onDragOver={(e) => handleDragOver(e, 'jd')}
                onDrop={(e) => onDrop(e, 'jd')}
                placeholder="Drop JD (PDF/DOCX/TXT) here or paste text below..."
                required
                onClick={(e) => e.stopPropagation()}
                disabled={uploadState.jd === 'uploading'}
              />
              <input 
                type="file" 
                accept=".pdf,.txt,.docx" 
                hidden 
                ref={jdInputRef} 
                onChange={(e) => onFileChange(e, 'jd')}
              />
              {(dragField === 'jd' || uploadState.jd === 'uploading') && (
                <div className="drag-overlay">
                  {uploadState.jd === 'uploading' ? (
                    <div className="loader-container">
                      <div className="spinner"></div>
                      <span>Extracting text...</span>
                    </div>
                  ) : "Drop to upload"}
                </div>
              )}
            </div>
          </div>
        </div>
        
        {/* Resume Card */}
        <div className="setup-card" style={{ animationDelay: '150ms' }}>
          <div className="input-group">
            <div className="label-row">
              <label>Resume</label>
              {uploadMessage.resume && (
                <span className={`upload-status ${uploadState.resume}`}>
                  {uploadMessage.resume}
                </span>
              )}
            </div>
            <div 
              className={`drag-drop-zone ${dragField === 'resume' ? 'dragging' : ''} ${uploadState.resume}`}
              onDragOver={(e) => handleDragOver(e, 'resume')}
              onDragLeave={handleDragLeave}
              onDrop={(e) => onDrop(e, 'resume')}
              onClick={() => resumeInputRef.current.click()}
            >
              <textarea 
                value={resume} 
                onChange={(e) => setResume(e.target.value)} 
                onDragOver={(e) => handleDragOver(e, 'resume')}
                onDrop={(e) => onDrop(e, 'resume')}
                placeholder="Drop Resume (PDF/DOCX/TXT) here or paste text below..."
                required
                onClick={(e) => e.stopPropagation()}
                disabled={uploadState.resume === 'uploading'}
              />
              <input 
                type="file" 
                accept=".pdf,.txt,.docx" 
                hidden 
                ref={resumeInputRef} 
                onChange={(e) => onFileChange(e, 'resume')}
              />
              {(dragField === 'resume' || uploadState.resume === 'uploading') && (
                <div className="drag-overlay">
                  {uploadState.resume === 'uploading' ? (
                    <div className="loader-container">
                      <div className="spinner"></div>
                      <span>Extracting text...</span>
                    </div>
                  ) : "Drop to upload"}
                </div>
              )}
            </div>
          </div>
        </div>
        
        {error && <div className="error-message shake">{error}</div>}
        
        <div className="button-container">
          <button type="submit" className="primary-btn" disabled={loading}>
            {loading ? (
              <span className="loading-content">
                <span className="dots">...</span> Analysing...
              </span>
            ) : (
              'Start Assessment'
            )}
          </button>
          {loading && <div className="shimmer-progress"></div>}
        </div>
      </form>
    </div>
  );
};

export default Setup;
