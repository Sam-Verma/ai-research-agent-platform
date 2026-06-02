import React, { useState } from 'react';
import { marked } from 'marked';
import { FileCode, Settings, Save } from 'lucide-react';

export default function ResearchCanvas({ research, projectId, onReportSaved }) {
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    if (!research || !research.answer || !projectId || saving) return;
    setSaving(true);
    try {
      await fetch(`http://127.0.0.1:8000/projects/${projectId}/reports`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          title: "Research Report " + new Date().toLocaleDateString(), 
          content: research.answer 
        })
      });
      alert('Report saved to project!');
      if(onReportSaved) onReportSaved();
    } catch (e) {
      alert('Failed to save report');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <div style={{ padding: '20px', borderBottom: '1px solid var(--border-glass)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ fontSize: '14px', letterSpacing: '1px', color: 'var(--text-muted)' }}>RESEARCH CANVAS</h2>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button onClick={handleSave} disabled={saving || !research} style={{ background: 'rgba(0, 240, 255, 0.1)', border: '1px solid var(--accent-cyan)', color: 'var(--accent-cyan)', borderRadius: '6px', padding: '6px 12px', cursor: research ? 'pointer' : 'not-allowed', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', opacity: research ? 1 : 0.5 }}>
            <Save size={14} /> {saving ? 'Saving...' : 'Save Report'}
          </button>
          <button style={{ background: 'rgba(176, 38, 255, 0.2)', border: 'none', borderRadius: '6px', padding: '6px', cursor: 'pointer', display: 'flex' }}><FileCode size={16} color="var(--accent-purple)"/></button>
        </div>
      </div>
      
      <div style={{ flex: 1, padding: '24px', overflowY: 'auto' }}>
        {research ? (
          <div 
            className="markdown-body" 
            dangerouslySetInnerHTML={{ __html: marked.parse(research.answer || '') }}
          />
        ) : (
          <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '14px', textAlign: 'center', padding: '40px' }}>
            Submit a query to generate a structured research report on this canvas.
          </div>
        )}
      </div>
    </div>
  );
}
