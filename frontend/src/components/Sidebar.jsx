import React, { useState, useEffect, useRef } from 'react';
import { LayoutDashboard, FileText, Database, BookOpen, Plus, UploadCloud, Download } from 'lucide-react';

export default function Sidebar({ projects, activeProjectId, setActiveProjectId, refreshProjects, onLoadReport, refreshTrigger }) {
  const [newProjectTitle, setNewProjectTitle] = useState('');
  const [documents, setDocuments] = useState([]);
  const [reports, setReports] = useState([]);
  const fileInputRef = useRef(null);

  const fetchProjectData = async () => {
    if (!activeProjectId) return;
    try {
      const docRes = await fetch(`http://127.0.0.1:8000/projects/${activeProjectId}/documents`);
      const repRes = await fetch(`http://127.0.0.1:8000/projects/${activeProjectId}/reports`);
      setDocuments(await docRes.json());
      setReports(await repRes.json());
    } catch (e) { console.error("Error fetching project data", e); }
  };

  useEffect(() => {
    fetchProjectData();
  }, [activeProjectId, refreshTrigger]);

  const handleCreateProject = async (e) => {
    e.preventDefault();
    if (!newProjectTitle.trim()) return;
    
    await fetch('http://127.0.0.1:8000/projects/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: newProjectTitle, query: '' })
    });
    setNewProjectTitle('');
    refreshProjects();
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file || !activeProjectId) return;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("project_id", activeProjectId);

    try {
      await fetch('http://127.0.0.1:8000/upload/pdf', {
        method: 'POST',
        body: formData
      });
      alert('PDF Uploaded successfully!');
      fetchProjectData();
    } catch (err) {
      alert('Upload failed');
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '30px', overflowY: 'auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <div style={{ background: 'var(--accent-purple)', borderRadius: '8px', padding: '6px' }}>
          <LayoutDashboard size={20} color="#fff" />
        </div>
        <h2 style={{ fontSize: '18px', margin: 0 }}>AI Research</h2>
      </div>

      <div>
        <h3 style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '16px', letterSpacing: '1px' }}>PROJECTS</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {projects.map(p => (
            <div 
              key={p.id}
              onClick={() => setActiveProjectId(p.id)}
              style={{
                padding: '12px 16px',
                background: activeProjectId === p.id ? 'rgba(176, 38, 255, 0.15)' : 'transparent',
                border: activeProjectId === p.id ? '1px solid var(--accent-purple)' : '1px solid transparent',
                borderRadius: '12px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                color: activeProjectId === p.id ? '#fff' : 'var(--text-muted)'
              }}
            >
              <Database size={18} color={activeProjectId === p.id ? 'var(--accent-purple)' : 'var(--text-muted)'} />
              <span style={{ fontSize: '14px', fontWeight: 500, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{p.title}</span>
            </div>
          ))}
        </div>
        
        <form onSubmit={handleCreateProject} style={{ marginTop: '16px', display: 'flex', gap: '8px' }}>
          <input 
            type="text" 
            placeholder="New Project..."
            value={newProjectTitle}
            onChange={(e) => setNewProjectTitle(e.target.value)}
            style={{ flex: 1, padding: '8px 12px', borderRadius: '8px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border-glass)', color: '#fff' }}
          />
          <button type="submit" style={{ background: 'var(--accent-purple)', border: 'none', borderRadius: '8px', padding: '8px', cursor: 'pointer' }}>
            <Plus size={16} color="#fff" />
          </button>
        </form>
      </div>

      <div>
        <h3 style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '16px', letterSpacing: '1px' }}>DOCUMENTS</h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <input 
            type="file" 
            accept=".pdf" 
            ref={fileInputRef} 
            onChange={handleFileUpload} 
            style={{ display: 'none' }} 
          />
          <div 
            onClick={() => {
              if(!activeProjectId) return alert("Select a project first");
              fileInputRef.current.click();
            }}
            style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '8px 16px', cursor: 'pointer', color: 'var(--accent-cyan)' }}
          >
            <UploadCloud size={18} />
            <span style={{ fontSize: '14px' }}>Upload PDF</span>
          </div>
          
          {documents.map(d => (
            <div key={`doc-${d.id}`} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '4px 16px', color: 'var(--text-muted)' }}>
              <BookOpen size={16} />
              <span style={{ fontSize: '13px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{d.filename}</span>
            </div>
          ))}

          <h3 style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '16px', marginBottom: '16px', letterSpacing: '1px' }}>SAVED REPORTS</h3>
          
          {reports.map(r => (
            <div key={`rep-${r.id}`} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', padding: '4px 16px', cursor: 'pointer', color: 'var(--text-muted)' }}>
              <div onClick={() => onLoadReport({ answer: r.content })} style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1 }}>
                <FileText size={16} color="var(--accent-purple)" />
                <span style={{ fontSize: '13px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{r.title} ({new Date(r.created_at).toLocaleDateString()})</span>
              </div>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  const url = `http://127.0.0.1:8000/projects/${activeProjectId}/reports/${r.id}/download`;
                  const link = document.createElement('a');
                  link.href = url;
                  link.target = '_blank';
                  document.body.appendChild(link);
                  link.click();
                  document.body.removeChild(link);
                }}
                style={{ background: 'rgba(0, 240, 255, 0.08)', border: '1px solid var(--accent-cyan)', borderRadius: '999px', cursor: 'pointer', padding: '6px 10px', color: 'var(--accent-cyan)', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}
              >
                <Download size={14} /> Download
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

