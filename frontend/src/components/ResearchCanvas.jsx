import React, { useState } from 'react';
import { marked } from 'marked';
import { FileCode, Save } from 'lucide-react';
import { API_BASE_URL } from '../config';

export default function ResearchCanvas({ research, projectId, onReportSaved }) {
  const [saving, setSaving] = useState(false);

  const getSavedContent = () => {
    if (!research) return '';

    let content = research.answer || '';

    if (research.citations?.length) {
      content += '\n\nSources:\n';
      content += research.citations.map((citation, idx) => {
        if (citation.type === 'document') {
          return `${idx + 1}. ${citation.source} - ${citation.snippet}`;
        }

        return `${idx + 1}. ${citation.title || citation.link} - ${citation.snippet}`;
      }).join('\n');
    }

    return content;
  };

  const handleSave = async () => {
    if (!research || !research.answer || !projectId || saving) return;
    setSaving(true);
    try {
      await fetch(`${API_BASE_URL}/projects/${projectId}/reports`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          title: "Research Report " + new Date().toLocaleDateString(), 
          content: getSavedContent(),
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

  const renderCitations = () => {
    if (!research?.citations?.length) return null;

    return (
      <div style={{ marginTop: '24px' }}>
        <h3 style={{ color: 'var(--text-muted)', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '1px' }}>Sources</h3>
        <div style={{ display: 'grid', gap: '12px', marginTop: '12px' }}>
          {research.citations.map((citation, idx) => (
            <div key={idx} style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '14px', padding: '14px' }}>
              <div style={{ fontSize: '13px', color: 'var(--text-main)', marginBottom: '6px' }}><strong>[{idx + 1}]</strong> {citation.type === 'document' ? citation.source : citation.title || citation.link}</div>
              {citation.link && citation.type !== 'document' ? (
                <a href={citation.link} target="_blank" rel="noreferrer" style={{ color: 'var(--accent-cyan)', fontSize: '12px', wordBreak: 'break-all' }}>{citation.link}</a>
              ) : null}
              <div style={{ marginTop: '8px', fontSize: '13px', color: 'var(--text-muted)', whiteSpace: 'pre-wrap' }}>{citation.snippet}</div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderPlan = () => {
    if (!research?.plan) return null;

    return (
      <div style={{ marginBottom: '24px' }}>
        <h3 style={{ color: 'var(--text-muted)', fontSize: '13px', textTransform: 'uppercase', letterSpacing: '1px' }}>Research Plan</h3>
        <div className="markdown-body" dangerouslySetInnerHTML={{ __html: marked.parse(research.plan) }} />
      </div>
    );
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
          <>
            {renderPlan()}
            <div className="markdown-body" dangerouslySetInnerHTML={{ __html: marked.parse(research.answer || '') }} />
            {renderCitations()}
          </>
        ) : (
          <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', fontSize: '14px', textAlign: 'center', padding: '40px' }}>
            Submit a query to generate a structured research report on this canvas.
          </div>
        )}
      </div>
    </div>
  );
}
