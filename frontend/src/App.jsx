import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import ResearchCanvas from './components/ResearchCanvas';

function App() {
  const [projects, setProjects] = useState([]);
  const [activeProjectId, setActiveProjectId] = useState(null);
  const [currentResearch, setCurrentResearch] = useState(null);

  const fetchProjects = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/projects/');
      const data = await res.json();
      setProjects(data);
      if (data.length > 0 && !activeProjectId) {
        setActiveProjectId(data[0].id);
      }
    } catch (err) {
      console.error("Failed to fetch projects", err);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const [refreshTrigger, setRefreshTrigger] = useState(0);

  return (
    <div className="app-container">
      <Sidebar 
        projects={projects}
        activeProjectId={activeProjectId} 
        setActiveProjectId={setActiveProjectId} 
        refreshProjects={fetchProjects}
        onLoadReport={setCurrentResearch}
        refreshTrigger={refreshTrigger}
      />
      
      <ChatInterface 
        projectId={activeProjectId} 
        onResearchComplete={setCurrentResearch} 
      />
      
      <ResearchCanvas 
        research={currentResearch}
        projectId={activeProjectId}
        onReportSaved={() => setRefreshTrigger(t => t + 1)}
      />
    </div>
  );
}

export default App;
