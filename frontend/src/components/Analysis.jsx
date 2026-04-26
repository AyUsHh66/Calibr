import React, { useState, useEffect } from 'react';
import { getAnalysis } from '../api';

const getSuspicionFlag = (suspicion, reason) => {
  switch (suspicion) {
    case 'high':
      return { 
        icon: '🔴', 
        label: 'Likely AI', 
        className: 'high', 
        reason: reason || 'Pattern matches AI generation' 
      };
    case 'medium':
      return { 
        icon: '🟡', 
        label: 'Uncertain', 
        className: 'medium', 
        reason: reason || 'Some textbook patterns detected' 
      };
    default:
      return null;
  }
};

const AnimatedCounter = ({ value, duration = 1000 }) => {
  const [count, setCount] = useState(0);

  useEffect(() => {
    let start = 0;
    const end = parseInt(value);
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

const Analysis = ({ sessionId, onViewPlan }) => {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [mounted, setMounted] = useState(false);

  const getConfidenceBadge = (signal) => {
    switch (signal) {
      case 'genuine':
        return { 
          label: '⚡ Confident', 
          className: 'badge-confident', 
          tooltip: 'Candidate gave specific examples and technical details' 
        };
      case 'hedging':
        return { 
          label: '⚠️ Hedging', 
          className: 'badge-hedging', 
          tooltip: 'Candidate used uncertain language — may know more than they showed' 
        };
      case 'bluffing':
        return { 
          label: '🚨 Bluffing', 
          className: 'badge-bluffing', 
          tooltip: 'Confident tone but lacked concrete specifics' 
        };
      default:
        return { label: signal, className: '', tooltip: '' };
    }
  };

  const getScoreColorClass = (score) => {
    if (score >= 70) return 'green';
    if (score >= 50) return 'amber';
    return 'red';
  };

  useEffect(() => {
    setLoading(true);
    getAnalysis(sessionId)
      .then(data => {
        if (data.error) {
          setError(data.error);
        } else {
          setAnalysisData(data);
          setTimeout(() => setMounted(true), 100);
        }
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, [sessionId]);

  if (loading) return (
    <div className="analysis-container stagger-children">
      <div className="skeleton hero-skeleton" style={{ height: '300px', marginBottom: '24px' }}></div>
      <div className="score-grid">
        <div className="skeleton card-skeleton" style={{ height: '250px' }}></div>
        <div className="skeleton card-skeleton" style={{ height: '250px' }}></div>
        <div className="skeleton card-skeleton" style={{ height: '250px' }}></div>
      </div>
    </div>
  );

  if (error) return (
    <div className="analysis-container error animate-fade-up">
      <div className="error-card shake">
        <h2>Oops!</h2>
        <p>{error}</p>
        <button className="primary-btn" onClick={() => window.location.reload()}>Retry</button>
      </div>
    </div>
  );

  const matchScore = analysisData.jd_match_score;
  const scoreClass = getScoreColorClass(matchScore);

  return (
    <div className="analysis-container stagger-children">
      <div className="hero-score-section animate-scale-in">
        <div className={`large-score ${scoreClass}`}>
          <AnimatedCounter value={matchScore} />
          <span className="percent">%</span>
        </div>
        <div className="score-label">JD Match Score</div>
        <div className={`candidate-badge badge-${analysisData.candidate_level.toLowerCase()} animate-pop-in`}>
          {analysisData.candidate_level}
        </div>
        
        <div className="ai-verdict-card">
          <div className="verdict-accent"></div>
          <p className="verdict-text">{analysisData.ai_verdict}</p>
        </div>
      </div>
      
      <div className="score-grid">
        {Object.entries(analysisData.scores).map(([skill, data], idx) => {
          const confidence = getConfidenceBadge(data.confidence_signal);
          const suspicion = getSuspicionFlag(data.ai_suspicion, data.suspicion_reason);
          const skillScoreClass = getScoreColorClass(data.score);
          
          return (
            <div 
              key={skill} 
              className={`skill-card ${skillScoreClass} ${mounted ? 'animate-card-entrance' : ''}`}
              style={{ animationDelay: `${idx * 100}ms` }}
            >
              <div className="skill-card-header">
                <h3>{skill}</h3>
                <div className="skill-score">
                  <AnimatedCounter value={data.score} />
                </div>
              </div>
              
              <div className="progress-container">
                <div 
                  className={`progress-bar-fill ${mounted ? 'animate-fill' : ''}`}
                  style={{ '--target-width': `${data.score}%` }}
                ></div>
              </div>

              <div className="skill-meta">
                <div className="meta-left">
                  <div className={`confidence-badge ${confidence.className} animate-pop-in`}>
                    {confidence.label}
                  </div>
                  {suspicion && (
                    <div className={`suspicion-flag ${suspicion.className} mini animate-pop-in`} title={suspicion.reason}>
                      <span className="flag-icon">{suspicion.icon}</span>
                      <span className="flag-label">{suspicion.label}</span>
                    </div>
                  )}
                </div>
                <div className="skill-level">{data.level}</div>
              </div>

              <div className="skill-details">
                <div className="detail-item">
                  <span className="detail-label">Strengths</span>
                  <p>{data.strength}</p>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Gaps</span>
                  <p>{data.gap}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>
      
      <div className="analysis-footer animate-fade-up" style={{ animationDelay: '600ms' }}>
        <button className="primary-btn" onClick={onViewPlan}>
          Generate My Learning Plan
          <div className="shimmer-sweep"></div>
        </button>
      </div>
    </div>
  );
};

export default Analysis;
