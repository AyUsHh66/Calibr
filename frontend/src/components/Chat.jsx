import React, { useState, useEffect, useRef } from 'react';
import { getQuestion, submitAnswer, deleteSession } from '../api';

const Chat = ({ sessionId, skills, onComplete, initialSkillIndex = 0, initialQuestionNumber = 1, initialHistory = [] }) => {
  const [currentSkillIndex, setCurrentSkillIndex] = useState(initialSkillIndex);
  const [currentQuestionNumber, setCurrentQuestionNumber] = useState(initialQuestionNumber);
  const [messages, setMessages] = useState(initialHistory.map(m => ({
    role: m.role === 'assistant' ? 'agent' : m.role,
    content: m.content,
    skill: m.skill
  })));
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [startTime, setStartTime] = useState(Date.now());
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages, isTyping]);

  // Initial question or follow-up if history ends with user message
  useEffect(() => {
    const lastMessage = messages[messages.length - 1];
    
    // Fetch if history is empty OR if last message is from user (refresh happened before next question)
    if (messages.length === 0 || (lastMessage && lastMessage.role === 'user')) {
      const fetchQuestion = async () => {
        setIsTyping(true);
        try {
          const data = await getQuestion(sessionId, currentSkillIndex, currentQuestionNumber);
          
          if (!skills || !skills[currentSkillIndex]) {
            throw new Error("Skill data missing");
          }
          
          const skillName = skills[currentSkillIndex].skill;
          
          const newMsg = { 
            role: 'agent', 
            content: messages.length === 0 
              ? `Starting with ${skillName}. ${data.question}`
              : data.question,
            skill: skillName
          };
          
          setMessages(prev => [...prev, newMsg]);
          setStartTime(Date.now());
        } catch (err) {
          console.error(err);
        } finally {
          setIsTyping(false);
        }
      };
      fetchQuestion();
    }
  }, [sessionId, skills]); // Run once on mount

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input;
    const responseTime = (Date.now() - startTime) / 1000; // time in seconds
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      // Send full conversation history with skill attribution
      const history = messages.map(m => ({ 
        role: m.role === 'agent' ? 'assistant' : m.role, 
        content: m.content,
        skill: m.skill
      }));

      const result = await submitAnswer(
        sessionId, 
        currentSkillIndex, 
        currentQuestionNumber, 
        userMessage,
        history,
        responseTime
      );

      if (result.next_action === 'next_question') {
        const nextQNum = currentQuestionNumber + 1;
        setCurrentQuestionNumber(nextQNum);
        setIsTyping(true);
        const qData = await getQuestion(sessionId, currentSkillIndex, nextQNum);
        setMessages(prev => [...prev, { 
          role: 'agent', 
          content: qData.question,
          skill: skills[currentSkillIndex].skill
        }]);
        setStartTime(Date.now());
        setIsTyping(false);
      } else if (result.next_action === 'next_skill') {
        const nextIdx = currentSkillIndex + 1;
        setCurrentSkillIndex(nextIdx);
        setCurrentQuestionNumber(1);
        setIsTyping(true);
        const qData = await getQuestion(sessionId, nextIdx, 1);
        setMessages(prev => [...prev, { 
          role: 'agent', 
          content: `Great. Now let's discuss ${skills[nextIdx].skill}. ${qData.question}`,
          skill: skills[nextIdx].skill
        }]);
        setStartTime(Date.now());
        setIsTyping(false);
      } else if (result.next_action === 'complete') {
        onComplete();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
      setIsTyping(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header animate-fade-up">
        <div className="skill-pills-container">
          {skills.map((s, idx) => (
            <div 
              key={idx} 
              className={`skill-pill ${idx === currentSkillIndex ? 'active pulse-glow' : idx < currentSkillIndex ? 'completed' : 'upcoming'}`}
            >
              {idx < currentSkillIndex && <span className="check">✓</span>}
              {s.skill}
            </div>
          ))}
        </div>
        
        <div className="question-counter">
          <span className="counter-text">Question {currentQuestionNumber} / 3</span>
          <div className="dot-indicators">
            {[1, 2, 3].map(n => (
              <div 
                key={n} 
                className={`dot ${n < currentQuestionNumber ? 'filled' : n === currentQuestionNumber ? 'pulsing' : 'empty'}`}
              ></div>
            ))}
          </div>
        </div>
      </div>

      <div className="messages-list stagger-children">
        {messages.map((m, i) => (
          <div key={i} className={`message-wrapper ${m.role}`}>
            {m.role === 'agent' && (
              <div className="agent-avatar">AI</div>
            )}
            <div className="message-bubble-container">
              {m.role === 'agent' && m.skill && (
                <div className="skill-tag">{m.skill}</div>
              )}
              <div className={`message-bubble ${m.role} animate-fade-in`}>
                {m.content}
              </div>
            </div>
          </div>
        ))}
        {isTyping && (
          <div className="message-wrapper agent">
            <div className="agent-avatar">AI</div>
            <div className="message-bubble agent typing">
              <span className="dot"></span>
              <span className="dot"></span>
              <span className="dot"></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-wrapper">
        <form onSubmit={handleSend} className="chat-input-area">
          <textarea 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your answer here..."
            disabled={loading}
            rows="1"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend(e);
              }
            }}
          />
          <button type="submit" className="send-btn" disabled={loading || !input.trim()}>
            Send
          </button>
        </form>
        <div className="input-tip">
          💡 Mention specific versions and real projects for higher scores
        </div>
      </div>
    </div>
  );
};

export default Chat;
