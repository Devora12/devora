import React from 'react';
import TestcasesPieChart from '../../charts/TestcasesPieChart';
import CommitTimelineChart from '../../charts/CommitTimelineChart';
import TeamTimeMetricsChart from '../../charts/TeamTimeMetricsChart';
import PerformanceScoreChart from '../../charts/PerformanceScoreChart';
import LoadingSpinner from '../../common/LoadingSpinner';
import { useProjectData } from '../../../hooks/useProjects';

const ProjectOverview = ({ project }) => {
  const { testcasesByAuthor, loading, error } = useProjectData(project?.id);

  if (loading) return <LoadingSpinner text="Loading project data..." />;
  if (error) return <div className="text-red-500">Error: {error}</div>;

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">
        Project Overview: {project.name}
      </h2>

      {/* Team Time Metrics Bar Chart */}
      <div className="mt-8 bg-gray-50 rounded-lg p-4">
        <h3 className="text-lg font-semibold mb-4">Team Time Metrics</h3>
        <TeamTimeMetricsChart 
          projectId={project.id} 
          LoadingComponent={<LoadingSpinner text="Loading team metrics..." />}
        />
      </div>

      {/* Performance Score Chart */}
      <div className="mt-8 bg-gray-50 rounded-lg p-4 mb-6">
        <h3 className="text-lg font-semibold mb-4">Team Performance Scores</h3>
        <PerformanceScoreChart 
          projectId={project.id}
          LoadingComponent={<LoadingSpinner text="Loading performance scores..." />}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Testcases by Author (Pie Chart) */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4">Testcases by Author</h3>
          <TestcasesPieChart 
            data={testcasesByAuthor}
            LoadingComponent={<LoadingSpinner text="Loading testcases data..." />}
          />
        </div>

        {/* Commits Timeline (Line Chart) */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold mb-4">Commit Timeline</h3>
          <CommitTimelineChart 
            projectId={project.id}
            LoadingComponent={<LoadingSpinner text="Loading commit timeline..." />}
          />
        </div>
      </div>
    </div>
  );
};

export default ProjectOverview;