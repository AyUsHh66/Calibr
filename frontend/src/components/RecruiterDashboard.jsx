import React, { useState, useEffect } from 'react';
import { getRecruiterCandidates, compareCandidates } from '../api';

const ComparisonView = ({ sessionIds, onBack }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await compareCandidates(sessionIds);
        setData(result);
      } catch (err) {
        setError('Failed to load comparison data');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [sessionIds]);

  if (loading) return (
    <div className="loading-state">
      <div className="loader"></div>
      <p>Generating comparison...</p>
    </div>
  );

  if (error) return <div className="error-state">{error}</div>;

  return (
    <div className="comparison-container animate-fade-in">
      <div className="comparison-header">
        <button className="back-btn" onClick={onBack}>
          <span className="icon">←</span> Back to Dashboard
        </button>
        <h2>Candidate Comparison</h2>
      </div>

      <div className="comparison-grid">
        <div className="comparison-row header">
          <div className="skill-col">SKILL</div>
          {data.candidates.map(c => (
            <div key={c.session_id} className="candidate-col name">
              {c.name}
            </div>
          ))}
        </div>

        {data.all_skills.map(skill => (
          <div key={skill} className="comparison-row">
            <div className="skill-col">{skill}</div>
            {data.candidates.map(c => {
              const skillData = c.skills[skill] || { score: 0, level: 'N/A' };
              const barWidth = `${skillData.score}%`;
              return (
                <div key={c.session_id} className="candidate-col">
                  <div className="score-viz">
                    <div className="score-bar-bg">
                      <div className="score-bar-fill" style={{ width: barWidth }}></div>
                    </div>
                    <span className="score-text">{skillData.score}</span>
                  </div>
                </div>
              );
            })}
          </div>
        ))}

        <div className="comparison-row divider"></div>

        <div className="comparison-row metric">
          <div className="skill-col">JD Match</div>
          {data.candidates.map(c => (
            <div key={c.session_id} className="candidate-col metric-val">
              {c.jd_match}%
            </div>
          ))}
        </div>

        <div className="comparison-row metric">
          <div className="skill-col">Confidence</div>
          {data.candidates.map(c => (
            <div key={c.session_id} className="candidate-col metric-val">
              {c.confidence === 'genuine' ? '✓ Confident' : c.confidence === 'hedging' ? '⚠ Hedging' : '✘ Bluffing'}
            </div>
          ))}
        </div>

        <div className="comparison-row metric">
          <div className="skill-col">AI Suspicion</div>
          {data.candidates.map(c => (
            <div key={c.session_id} className="candidate-col metric-val">
              {c.ai_suspicion === 'high' ? '🔴 High' : c.ai_suspicion === 'medium' ? '🟡 Medium' : '🟢 Low'}
            </div>
          ))}
        </div>
      </div>

      <div className="comparison-verdict animate-fade-up">
        <h3>AI Verdict</h3>
        <p>"{data.verdict}"</p>
      </div>
    </div>
  );
};

const AnimatedCounter = ({ value, duration = 1000 }) => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let start = 0;
    const end = parseInt(value);
    if (isNaN(end)) {
      setCount(value);
      return;
    }
    if (start === end) return;

    let totalMiliseconds = duration;
    let incrementTime = 20;
    let totalSteps = totalMiliseconds / incrementTime;
    let increment = (end - start) / totalSteps;

    let timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        setCount(end);
        clearInterval(timer);
      } else {
        setCount(Math.floor(start));
      }
    }, incrementTime);

    return () => clearInterval(timer);
  }, [value, duration]);

  return <span>{count}</span>;
};

const RecruiterDashboard = ({ onViewReport }) => {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedIds, setSelectedIds] = useState([]);
  const [isComparing, setIsComparing] = useState(false);

  const toggleSelection = (id) => {
    setSelectedIds(prev => 
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  useEffect(() => {
    setLoading(true);
    getRecruiterCandidates()
      .then(data => {
        setCandidates(data);
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const getMatchColorClass = (score) => {
    if (score < 50) return 'red';
    if (score < 70) return 'amber';
    return 'green';
  };

  const calculateStats = () => {
    if (candidates.length === 0) return { avg: 0, total: 0, topGap: 'N/A' };
    const total = candidates.length;
    const avg = Math.round(candidates.reduce((acc, c) => acc + c.jd_match_score, 0) / total);
    
    const gapCounts = {};
    candidates.forEach(c => {
      gapCounts[c.top_gap] = (gapCounts[c.top_gap] || 0) + 1;
    });
    const topGap = Object.entries(gapCounts).sort((a, b) => b[1] - a[1])[0][0];

    return { avg, total, topGap };
  };

  if (loading) return (
    <div className="dashboard-container stagger-children">
      <div className="skeleton stats-skeleton" style={{ height: '120px', marginBottom: '32px' }}></div>
      <div className="skeleton table-skeleton" style={{ height: '400px' }}></div>
    </div>
  );

  if (error) return (
    <div className="dashboard-container error animate-fade-up">
      <div className="error-card shake">
        <h2>Error loading dashboard</h2>
        <p>{error}</p>
        <button className="primary-btn" onClick={() => window.location.reload()}>Retry</button>
      </div>
    </div>
  );

  const stats = calculateStats();

  if (isComparing) {
    return (
      <ComparisonView 
        sessionIds={selectedIds} 
        onBack={() => setIsComparing(false)} 
      />
    );
  }

  return (
    <div className="dashboard-container stagger-children">
      <header className="dashboard-header animate-fade-up">
        <h1 className="gradient-text">Candidate Intelligence</h1>
        <p className="subtitle">Real-time assessment insights across your talent pool</p>
      </header>

      <div className="stats-row">
        <div className="stat-card animate-scale-in" style={{ animationDelay: '100ms' }}>
          <div className="stat-value"><AnimatedCounter value={stats.total} /></div>
          <div className="stat-label">Total Assessed</div>
        </div>
        <div className="stat-card animate-scale-in" style={{ animationDelay: '200ms' }}>
          <div className="stat-value"><AnimatedCounter value={stats.avg} />%</div>
          <div className="stat-label">Avg. JD Match</div>
        </div>
        <div className="stat-card animate-scale-in" style={{ animationDelay: '300ms' }}>
          <div className="stat-value truncate" title={stats.topGap}>{stats.topGap}</div>
          <div className="stat-label">Top Skill Gap</div>
        </div>
      </div>

      <div className="dashboard-actions animate-fade-up">
        {selectedIds.length >= 2 && (
          <button 
            className="primary-btn compare-btn pulse-glow"
            onClick={() => setIsComparing(true)}
          >
            Compare Selected ({selectedIds.length})
            <div className="shimmer-sweep"></div>
          </button>
        )}
      </div>

      {candidates.length === 0 ? (
        <div className="empty-state-card animate-fade-up">
          <p>No assessments completed yet</p>
        </div>
      ) : (
        <div className="candidates-list">
          <div className="list-header">
            <span className="checkbox-cell"></span>
            <span>Candidate</span>
            <span>JD Match</span>
            <span>Top Gap</span>
            <span>Confidence</span>
            <span>AI Risk</span>
            <span>Actions</span>
          </div>
          {candidates.map((candidate, idx) => {
            const scoreClass = getMatchColorClass(candidate.jd_match_score);
            const isSelected = selectedIds.includes(candidate.session_id);
            return (
              <div 
                key={candidate.session_id} 
                className={`candidate-row animate-card-entrance ${isSelected ? 'selected' : ''}`}
                style={{ animationDelay: `${idx * 100}ms` }}
              >
                <div className="checkbox-cell">
                  <input 
                    type="checkbox" 
                    checked={isSelected}
                    onChange={() => toggleSelection(candidate.session_id)}
                    className="candidate-checkbox"
                  />
                </div>
                <div className="name-cell">
                  <div className="avatar-mini">{candidate.candidate_name.charAt(0)}</div>
                  <div className="info">
                    <span className="name">{candidate.candidate_name}</span>
                    <span className="date">{new Date(candidate.assessed_at).toLocaleDateString()}</span>
                  </div>
                </div>
                
                <div className="match-cell">
                  <div className={`match-pill-container ${scoreClass}`}>
                    <div className="match-pill-fill" style={{ width: `${candidate.jd_match_score}%` }}></div>
                    <span className="match-value">{candidate.jd_match_score}%</span>
                  </div>
                </div>
                
                <div className="gap-cell">
                  <span className="gap-text">{candidate.top_gap}</span>
                </div>
                
        <div className="confidence-cell">
          <div className="mini-bars">
            {[1, 2, 3, 4, 5].map(i => {
              const isActive = i <= (candidate.confidence_avg === 'genuine' ? 5 : candidate.confidence_avg === 'hedging' ? 3 : 1);
              return <div key={i} className={`mini-bar ${isActive ? scoreClass : ''}`}></div>;
            })}
          </div>
        </div>
        
        <div className="suspicion-cell">
          <div className={`suspicion-flag ${candidate.ai_suspicion}`} title={candidate.ai_suspicion === 'high' ? 'Likely AI-assisted' : candidate.ai_suspicion === 'medium' ? 'Uncertain' : 'Authentic'}>
            <span className="flag-icon">{candidate.ai_suspicion === 'high' ? '🔴' : candidate.ai_suspicion === 'medium' ? '🟡' : '🟢'}</span>
            <span className="flag-label">{candidate.ai_suspicion === 'high' ? 'AI' : candidate.ai_suspicion === 'medium' ? 'Suspect' : 'Human'}</span>
          </div>
        </div>
                
                <div className="action-cell">
                  <button 
                    className="view-report-link"
                    onClick={() => onViewReport(candidate.session_id)}
                  >
                    View Report <span className="arrow">→</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default RecruiterDashboard;
