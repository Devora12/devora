// App.js
import React, { useState } from 'react';
import ProjectSelection from './components/sections/ProjectSelection';
import ProjectOverview from './components/sections/ProjectOverview';
import TeamMembersSection from './components/sections/TeamMembersSection';
import { useProjectData } from './hooks/useProjects';
import "./index.css";

function App() {
  const [selectedProject, setSelectedProject] = useState(null);
  const [selectedAuthor, setSelectedAuthor] = useState(null);

  const { authors } = useProjectData(selectedProject?.id);

  const handleProjectSelect = (project) => {
    setSelectedProject(project);
    setSelectedAuthor(null); // Reset author when project changes
  };

  const handleAuthorChange = (e) => {
    const author = e.target.value;
    setSelectedAuthor(author || null);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800">
            Developer Analytics Dashboard Testing
          </h1>
        </header>

        {/* Project Selection */}
        <ProjectSelection
          selectedProject={selectedProject}
          onProjectSelect={handleProjectSelect}
        />

        {/* Project Overview */}
        {selectedProject && (
          <ProjectOverview project={selectedProject} />
        )}

        {/* Team Members Section */}
        {selectedProject && (
          <TeamMembersSection
            authors={authors}
            selectedAuthor={selectedAuthor}
            onAuthorChange={handleAuthorChange}
          />
        )}
      </div>
    </div>
  );
}

export default App;
