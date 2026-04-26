import React, { useState, useEffect } from 'react';
import Setup from './components/Setup';
import Chat from './components/Chat';
import Analysis from './components/Analysis';
import LearningPlan from './components/LearningPlan';
import RecruiterDashboard from './components/RecruiterDashboard';
import { getSession, deleteSession } from './api';

function App() {
  const [session, setSession] = useState(null);
  const [view, setView] = useState('setup'); // setup, chat, analysis, plan, recruiter
  const [role, setRole] = useState('candidate'); // candidate, recruiter

  useEffect(() => {
    const savedId = localStorage.getItem('calibr_session_id');
    if (savedId && role === 'candidate') {
      getSession(savedId)
        .then(data => {
          if (data && data.id) {
            setSession(data);
            if (data.status === 'complete') {
              setView('analysis');
            } else {
              setView('chat');
            }
          } else {
            localStorage.removeItem('calibr_session_id');
          }
        })
        .catch((err) => {
          console.error("Failed to load session:", err);
          localStorage.removeItem('calibr_session_id');
        });
    }
  }, [role]);

  const handleSessionCreated = (data) => {
    localStorage.setItem('calibr_session_id', data.id);
    setSession(data);
    setView('chat');
  };

  const handleAssessmentComplete = () => {
    setView('analysis');
  };

  const handleViewReport = (sessionId) => {
    setSession({ id: sessionId });
    setView('analysis');
    setRole('candidate');
  };

  const toggleRole = (newRole) => {
    setRole(newRole);
    if (newRole === 'recruiter') {
      setView('recruiter');
    } else {
      // Return to candidate flow
      const savedId = localStorage.getItem('calibr_session_id');
      if (savedId) {
        setView('analysis'); // Or chat, logic in useEffect handles it
      } else {
        setView('setup');
      }
    }
  };

  return (
    <div className="app-container">
      <nav className="navbar">
        <div className="nav-left">
          <div className="logo">
            <span className="symbol">◈</span>
            <span className="calibr">calibr</span>
          </div>
          <div className="role-toggle" data-role={role}>
            <div className="toggle-indicator"></div>
            <button 
              className={`toggle-btn ${role === 'candidate' ? 'active' : ''}`}
              onClick={() => toggleRole('candidate')}
            >
              Candidate
            </button>
            <button 
              className={`toggle-btn ${role === 'recruiter' ? 'active' : ''}`}
              onClick={() => toggleRole('recruiter')}
            >
              Recruiter
            </button>
          </div>
        </div>
        {session && role === 'candidate' && (
          <button className="reset-btn" onClick={async () => {
            const id = session.id || session.session_id;
            try {
              await deleteSession(id);
            } catch (err) {
              console.error("Failed to delete session on backend", err);
            }
            localStorage.removeItem('calibr_session_id');
            window.location.reload();
          }}>New Assessment</button>
        )}
      </nav>

      <main className="content">
        {role === 'recruiter' ? (
          <RecruiterDashboard onViewReport={handleViewReport} />
        ) : (
          <>
            {view === 'setup' && <Setup onSessionCreated={handleSessionCreated} />}
            {view === 'chat' && (
              <Chat 
                sessionId={session.id || session.session_id} 
                skills={session.skills} 
                initialSkillIndex={session.current_skill_index}
                initialQuestionNumber={session.current_question_number}
                initialHistory={session.chat_history}
                onComplete={handleAssessmentComplete} 
              />
            )}
            {view === 'analysis' && (
              <Analysis 
                sessionId={session.id || session.session_id} 
                onViewPlan={() => setView('plan')} 
              />
            )}
            {view === 'plan' && (
              <LearningPlan 
                sessionId={session.id || session.session_id} 
                onBack={() => setView('analysis')}
              />
            )}
          </>
        )}
      </main>
    </div>
  );
}

export default App;
