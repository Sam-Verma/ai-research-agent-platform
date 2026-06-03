import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Loader2, Sparkles, Zap, MessageSquare, Plus, Trash2, ChevronDown } from 'lucide-react';

export default function ChatInterface({ projectId, onResearchComplete }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [chatMode, setChatMode] = useState('standard'); // 'standard', 'stream', 'research'
  const [sessionId, setSessionId] = useState('default-session');
  const [sessions, setSessions] = useState([]);
  const [projectName, setProjectName] = useState('');
  
  const messagesEndRef = useRef(null);
  const dropdownRef = useRef(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const menuRef = useRef(null);
  const [focusedIndex, setFocusedIndex] = useState(-1);

  useEffect(() => {
    if (projectId) {
      fetchSessions(projectId);
    }
  }, [projectId]);

  // fetch project metadata for header display
  useEffect(() => {
    if (!projectId) {
      setProjectName('');
      return;
    }

    let cancelled = false;
    fetch(`http://127.0.0.1:8000/projects/${projectId}`)
      .then(r => r.json())
      .then(d => { if (!cancelled) setProjectName(d.name || ''); })
      .catch(() => { if (!cancelled) setProjectName(''); });

    return () => { cancelled = true; };
  }, [projectId]);

  // close dropdown on outside click
  useEffect(() => {
    function onDocClick(e) {
      if (!dropdownRef.current) return;
      if (!dropdownRef.current.contains(e.target)) setDropdownOpen(false);
    }
    document.addEventListener('mousedown', onDocClick);
    return () => document.removeEventListener('mousedown', onDocClick);
  }, []);

  // manage focus when opening menu and when focusedIndex changes
  useEffect(() => {
    if (!dropdownOpen) return;
    // default focused index -> currently selected session or first
    const idx = Math.max(0, sessions.indexOf(sessionId));
    setFocusedIndex(idx >= 0 ? idx : 0);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dropdownOpen]);

  useEffect(() => {
    if (!dropdownOpen) return;
    const id = `session-item-${focusedIndex}`;
    const el = menuRef.current?.querySelector(`#${id}`);
    if (el) el.focus();
  }, [focusedIndex, dropdownOpen]);

  const fetchHistory = async (projId, sessId) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/chat/history?project_id=${projId}&session_id=${sessId}`);
      const data = await res.json();
      setMessages(data.messages || []);
      onResearchComplete(null);
    } catch (err) {
      console.error(err);
      setMessages([]);
    }
  };

  const fetchSessions = async (projId) => {
    try {
      const res = await fetch(`http://127.0.0.1:8000/chat/sessions?project_id=${projId}`);
      const data = await res.json();
      const ids = data.sessions?.map(s => s.session_id) || [];
      // Always ensure 'default-session' is available
      const allSessions = ['default-session', ...ids.filter(id => id !== 'default-session')];
      setSessions(allSessions);
      
      // Load history for current session or default
      if (sessionId && (sessionId === 'default-session' || ids.includes(sessionId))) {
        fetchHistory(projId, sessionId);
      } else {
        setSessionId('default-session');
        fetchHistory(projId, 'default-session');
      }
    } catch (err) {
      console.error('Failed to fetch sessions', err);
    }
  };


  const handleNewSession = () => {
    const newSessId = `sess-${Date.now()}`;
    setSessionId(newSessId);
    // Add new session to list if not already there
    setSessions(prev => {
      if (prev.includes(newSessId)) return prev;
      return [newSessId, ...prev];
    });
    setMessages([]);
    onResearchComplete(null);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading || !projectId) return;

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      if (chatMode === 'research') {
        const response = await fetch('http://127.0.0.1:8000/chat/research', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: projectId, session_id: sessionId, question: input })
        });
        const data = await response.json();
        setMessages(prev => [...prev, { role: 'assistant', content: "Research complete. Sources and plan are available on the canvas." }]);
        onResearchComplete({ plan: data.plan, research: data.research, answer: data.answer, citations: data.citations || [] });
      
      } else if (chatMode === 'standard') {
        const response = await fetch('http://127.0.0.1:8000/chat/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: projectId, session_id: sessionId, question: input })
        });
        const data = await response.json();
        setMessages(prev => [...prev, { role: 'assistant', content: data.answer }]);
      
      } else if (chatMode === 'stream') {
        const response = await fetch('http://127.0.0.1:8000/chat/stream', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ project_id: projectId, session_id: sessionId, question: input })
        });
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let assistantMessage = '';
        
        setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          const chunk = decoder.decode(value, { stream: true });
          const parts = chunk.split('data: ');
          
          let updateNeeded = false;
          for (let part of parts) {
            if (!part || part.includes('[DONE]')) continue;
            
            let text = part;
            if (text.endsWith('\n\n')) {
              text = text.slice(0, -2);
            } else if (text.endsWith('\n')) {
              text = text.slice(0, -1);
            }
            
            assistantMessage += text;
            updateNeeded = true;
          }
          
          if (updateNeeded) {
            setMessages(prev => {
              const newMsgs = [...prev];
              newMsgs[newMsgs.length - 1].content = assistantMessage;
              return newMsgs;
            });
          }
        }
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Error connecting to agent.' }]);
    } finally {
      setLoading(false);
    }
  };

  const modes = [
    { id: 'standard', icon: MessageSquare, label: 'Standard Chat' },
    { id: 'stream', icon: Zap, label: 'Stream Chat' },
    { id: 'research', icon: Sparkles, label: 'Research Workflow' },
  ];

  return (
    <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <div className="chat-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
          <div>
          <h2 style={{ fontSize: '14px', letterSpacing: '1px', color: 'var(--text-muted)', margin: 0 }}>
            {projectName || 'AGENT NEURO-LINK'}
          </h2>
          <div style={{ marginTop: '8px', display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
            <span style={{ color: 'var(--accent-cyan)', fontSize: '12px' }}>Session:</span>

            <div className="session-dropdown" ref={dropdownRef}>
              <div
                role="button"
                aria-haspopup="listbox"
                aria-expanded={dropdownOpen}
                aria-controls="session-menu"
                tabIndex={0}
                className="session-dropdown-toggle"
                onClick={() => setDropdownOpen(o => !o)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    setDropdownOpen(o => !o);
                    return;
                  }
                  if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    setDropdownOpen(true);
                    setFocusedIndex(0);
                    return;
                  }
                  if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    setDropdownOpen(true);
                    setFocusedIndex(Math.max(0, sessions.length - 1));
                    return;
                  }
                }}
              >
                <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '220px' }}>{sessionId}</div>
                <ChevronDown size={14} />
              </div>

              {dropdownOpen && (
                <div className="session-dropdown-menu" id="session-menu" role="listbox" ref={menuRef} aria-activedescendant={`session-item-${focusedIndex}`}>
                  {[...sessions].map((id, idx) => (
                    <div key={id}
                      id={`session-item-${idx}`}
                      role="option"
                      tabIndex={focusedIndex === idx ? 0 : -1}
                      aria-selected={id === sessionId}
                      className={"session-dropdown-item" + (id === sessionId ? ' active' : '')}
                      onClick={() => { setSessionId(id); fetchHistory(projectId, id); setDropdownOpen(false); }}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          e.preventDefault();
                          setSessionId(id);
                          fetchHistory(projectId, id);
                          setDropdownOpen(false);
                          return;
                        }
                        if (e.key === 'ArrowDown') {
                          e.preventDefault();
                          setFocusedIndex(i => Math.min(sessions.length - 1, i + 1));
                          return;
                        }
                        if (e.key === 'ArrowUp') {
                          e.preventDefault();
                          setFocusedIndex(i => Math.max(0, i - 1));
                          return;
                        }
                        if (e.key === 'Escape') {
                          e.preventDefault();
                          setDropdownOpen(false);
                          return;
                        }
                      }}
                    >{id}</div>
                  ))}
                </div>
              )}
            </div>

          </div>
        </div>

        <div style={{ display: 'flex', gap: '8px' }}>
          {sessionId !== 'default-session' && (
            <button 
              className="btn-session-delete"
              onClick={() => {
                if (window.confirm(`Delete session "${sessionId}"? Chat history will be lost.`)) {
                  fetch(`http://127.0.0.1:8000/chat/sessions?project_id=${projectId}&session_id=${sessionId}`, { method: 'DELETE' })
                    .then(() => {
                      setSessionId('default-session');
                      setSessions(prev => prev.filter(id => id !== sessionId));
                      fetchHistory(projectId, 'default-session');
                    })
                    .catch(err => alert('Delete failed'));
                }
              }}
            >
              <Trash2 size={14} /> Delete
            </button>
          )}
          <button 
            onClick={handleNewSession}
            style={{ background: 'transparent', border: '1px solid var(--border-glass)', borderRadius: '6px', padding: '6px 12px', cursor: 'pointer', color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}
          >
            <Plus size={14} /> New Session
          </button>
        </div>
      </div>

      {/* Mode Selector */}
      <div className="mode-selector">
        {modes.map(mode => (
          <button
            key={mode.id}
            onClick={() => setChatMode(mode.id)}
            style={{
              background: chatMode === mode.id ? 'rgba(176, 38, 255, 0.2)' : 'transparent',
              border: chatMode === mode.id ? '1px solid var(--accent-purple)' : '1px solid transparent',
              color: chatMode === mode.id ? '#fff' : 'var(--text-muted)',
              padding: '6px 12px',
              borderRadius: '20px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '12px'
            }}
          >
            <mode.icon size={14} color={chatMode === mode.id ? 'var(--accent-purple)' : 'var(--text-muted)'} />
            {mode.label}
          </button>
        ))}
      </div>

      <div style={{ flex: 1, padding: '20px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {messages.map((m, i) => (
          <div key={i} style={{ display: 'flex', gap: '16px', alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '80%' }}>
            {m.role === 'assistant' && (
              <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'rgba(176, 38, 255, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, border: '1px solid rgba(176, 38, 255, 0.3)' }}>
                <Bot size={18} color="var(--accent-purple)" />
              </div>
            )}
            
            <div style={{ 
              background: m.role === 'user' ? 'rgba(255,255,255,0.05)' : 'rgba(0, 240, 255, 0.05)',
              padding: '16px 20px',
              borderRadius: m.role === 'user' ? '20px 20px 0 20px' : '20px 20px 20px 0',
              border: m.role === 'user' ? '1px solid rgba(255,255,255,0.1)' : '1px solid rgba(0, 240, 255, 0.2)',
              fontSize: '14px',
              lineHeight: '1.5',
              whiteSpace: 'pre-wrap'
            }}>
              {m.content}
            </div>

            {m.role === 'user' && (
              <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'rgba(255,255,255,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <User size={18} color="#fff" />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
            <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'rgba(176, 38, 255, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', border: '1px solid rgba(176, 38, 255, 0.3)' }}>
              <Loader2 size={18} color="var(--accent-purple)" style={{ animation: 'spin 1s linear infinite' }} />
            </div>
            <div style={{ color: 'var(--text-muted)', fontSize: '13px', fontStyle: 'italic' }}>
              {chatMode === 'research' ? 'Agent is planning and researching...' : 'Agent is typing...'}
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div style={{ padding: '20px' }}>
        <form onSubmit={handleSend} style={{ position: 'relative', display: 'flex' }}>
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={projectId ? "Ask the research agent..." : "Select a project to start..."}
            disabled={!projectId}
            style={{ 
              width: '100%', 
              background: 'rgba(0,0,0,0.4)', 
              border: '1px solid var(--border-glass)', 
              padding: '16px 50px 16px 20px', 
              borderRadius: '24px',
              color: '#fff',
              outline: 'none',
              fontSize: '14px',
              opacity: projectId ? 1 : 0.5
            }}
          />
          <button type="submit" disabled={loading || !projectId} style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', background: 'var(--accent-purple)', border: 'none', width: '34px', height: '34px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: projectId ? 'pointer' : 'not-allowed', opacity: projectId ? 1 : 0.5 }}>
            <Send size={16} color="#fff" style={{ transform: 'translateX(-1px)' }} />
          </button>
        </form>
      </div>
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes spin { 100% { transform: rotate(360deg); } }
      `}} />
    </div>
  );
}
