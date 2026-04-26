import React, { useState, useEffect } from 'react';
import { API_BASE_URL } from '../api';

const LearningPlan = ({ sessionId, onBack }) => {
  const [items, setItems] = useState([]);
  const [isGenerating, setIsGenerating] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState('');
  const [planContext, setPlanContext] = useState('');
  const [summary, setSummary] = useState('');

  useEffect(() => {
    const eventSource = new EventSource(`${API_BASE_URL}/api/sessions/${sessionId}/plan`);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'status') {
          setSummary(data.message);
        } else if (data.type === 'metadata') {
          setPlanContext(data.context);
          setSummary(data.summary);
        } else if (data.type === 'item') {
          setItems(prev => [...prev, data.data]);
        } else if (data.type === 'error') {
          setError(data.message);
          setIsGenerating(false);
          eventSource.close();
        } else if (data.type === 'done') {
          setIsGenerating(false);
          eventSource.close();
        }
      } catch (err) {
        console.error("Failed to parse SSE data:", err);
      }
    };

    eventSource.onerror = (err) => {
      console.error("SSE error:", err);
      setError("Failed to connect to the learning plan generator. Please try again.");
      setIsGenerating(false);
      eventSource.close();
    };

    return () => eventSource.close();
  }, [sessionId]);

  const totalWeeks = items.reduce((acc, item) => acc + (item.time_weeks || 0), 0);

  const handleDownloadPDF = async () => {
    try {
      setDownloading(true);
      const response = await fetch(
        `${API_BASE_URL}/api/sessions/${sessionId}/plan/pdf`,
        {
          method: 'GET',
          headers: {
            'Accept': 'application/pdf'
          }
        }
      );
      
      if (!response.ok) throw new Error('PDF generation failed');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `calibr-report-${sessionId.slice(0, 8)}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("PDF download error:", err);
      setError("Failed to download PDF. Please try again.");
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="plan-container stagger-children">
      <header className="plan-header animate-fade-up">
        <h2 className="gradient-text">
          {planContext === 'senior_growth' ? 'Mastery Roadmap' : 'Bridge Your Skill Gaps'}
        </h2>
        {summary && (
          <div className="summary-banner-card">
            <div className="banner-content">
              <span className="icon">📚</span>
              <p>{items.length > 0 ? `${totalWeeks}-week personalised roadmap · ${items.length} skills to master` : summary}</p>
            </div>
          </div>
        )}
      </header>

      {error && (
        <div className="error-card shake">
          <p>{error}</p>
          <button className="primary-btn" onClick={() => window.location.reload()}>Retry</button>
        </div>
      )}

      {isGenerating && items.length === 0 && (
        <div className="skeleton-plan-grid">
          <div className="skeleton card-skeleton" style={{ height: '300px' }}></div>
          <div className="skeleton card-skeleton" style={{ height: '300px' }}></div>
        </div>
      )}
      
      <div className="plan-items">
        {(items || []).map((item, idx) => {
          const weekByWeek = item.week_by_week || item.weekly_breakdown || item.weeks || [];
          const resources = item.resources || item.resource_list || [];
          const timeWeeks = item.time_weeks || item.time_estimate || item.duration || "2-4 weeks";
          const whyAdjacent = item.why_adjacent || item.rationale || item.reason || "";
          
          return (
            <div 
              key={idx} 
              className="plan-card animate-card-entrance"
              style={{ animationDelay: `${idx * 150}ms` }}
            >
              <div className={`priority-accent p${item.priority}`}></div>
              <div className="plan-card-header">
                <div className="title-group">
                  <h3>{item.skill}</h3>
                  <span className={`priority-badge p${item.priority} animate-pop-in`}>P{item.priority}</span>
                </div>
                <div className="duration-chip">{timeWeeks} Weeks</div>
              </div>
              
              <div className="plan-card-body">
                <div className="rationale-box">
                  <p>{whyAdjacent}</p>
                </div>
                
                <div className="timeline-container">
                  <div className="timeline-line"></div>
                  <div className="weeks-list">
                    {(weekByWeek || []).map((week, i) => (
                      <div key={i} className="week-node">
                        <div className="node-circle"></div>
                        <div className="week-content">
                          <span className="week-label">Week {i + 1}</span>
                          <p>{week}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="resources-container">
                  <h4>Top Resources</h4>
                  <div className="resource-chips">
                    {(resources || []).map((res, i) => (
                      <a 
                        key={i} 
                        href={res.url} 
                        target="_blank" 
                        rel="noreferrer" 
                        className={`resource-chip ${(res.type || 'DOC').toLowerCase()}`}
                      >
                        <span className="res-icon">
                          {res.type === 'COURSE' && '🎓'}
                          {res.type === 'BOOK' && '📖'}
                          {res.type === 'PROJECT' && '🛠️'}
                          {res.type === 'DOC' && '📄'}
                        </span>
                        {res.title}
                      </a>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      {!isGenerating && items.length > 0 && (
        <div className="total-timeline-bar animate-fade-up">
          <div className="timeline-progress" style={{ width: '100%' }}></div>
          <div className="timeline-markers">
            <span>Start</span>
            <span>Week {Math.floor(totalWeeks/2)}</span>
            <span className="ready-endpoint">✓ Job Ready</span>
          </div>
        </div>
      )}

      <div className="plan-actions animate-fade-up">
        <button className="ghost-btn" onClick={onBack}>
          ← Back to Analysis
        </button>
        {!isGenerating && items.length > 0 && (
          <button 
            className="primary-btn pdf-btn" 
            onClick={handleDownloadPDF}
            disabled={downloading}
          >
            <span className="icon">↓</span> 
            {downloading ? 'Generating PDF...' : 'Download PDF Report'}
          </button>
        )}
      </div>
    </div>
  );
};

export default LearningPlan;
