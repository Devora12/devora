import React, { useState, useMemo } from 'react';
import Dropdown from '../../common/Dropdown';
import LoadingSpinner from '../../common/LoadingSpinner';
import { useProjects } from '../../../hooks/useProjects';

const ProjectSelection = ({ selectedProject, onProjectSelect }) => {
  const { projects, loading, error } = useProjects();
  const [searchTerm, setSearchTerm] = useState('');

  const filteredProjects = useMemo(() => {
    if (!searchTerm.trim()) return projects;
    
    return projects.filter(project =>
      project.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      project.description.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [projects, searchTerm]);

  const renderProjectOption = (project) => (
    <div>
      <div className="font-medium text-gray-900">{project.name}</div>
      <div className="text-sm text-gray-500">{project.description}</div>
    </div>
  );

  const getSelectedValue = () => {
    if (!selectedProject) return null;
    return `${selectedProject.name} - ${selectedProject.description}`;
  };

  if (loading) return <LoadingSpinner text="Loading projects..." />;
  if (error) return <div className="text-red-500">Error: {error}</div>;

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-8">
      <label className="block text-gray-700 font-medium mb-2">Select Project</label>
      
      <Dropdown
        options={filteredProjects}
        value={getSelectedValue()}
        onChange={onProjectSelect}
        placeholder="Select a project"
        searchable={true}
        onSearch={setSearchTerm}
        searchPlaceholder="Search projects..."
        renderOption={renderProjectOption}
      />
      
      {searchTerm && (
        <p className="text-sm text-gray-600 mt-2">
          {filteredProjects.length} project{filteredProjects.length !== 1 ? 's' : ''} found
        </p>
      )}
    </div>
  );
};

export default ProjectSelection;