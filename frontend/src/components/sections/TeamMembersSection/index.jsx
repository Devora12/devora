import React, { useState } from 'react';
import MetricCard from '../../common/MetricCard';
import WorkMetricsChart from '../../charts/WorkMetricsChart';
import LoadingSpinner from '../../common/LoadingSpinner';
import { useAuthorData, useAuthorMetrics } from '../../../hooks/useAuthors';
import { formatDate, calculateDaysDifference } from '../../../utils/formatters';
import { METRIC_COLORS } from '../../../utils/constants';

const TeamMembersSection = ({ authors, selectedAuthor, onAuthorChange }) => {
  const [selectedTestcase, setSelectedTestcase] = useState('all');
  
  const { authorTestcases, loading: testcasesLoading } = useAuthorData(selectedAuthor);
  const { 
    authorMetrics, 
    workMetrics, 
    loading: metricsLoading 
  } = useAuthorMetrics(selectedAuthor, selectedTestcase);

  const handleTestcaseChange = (e) => {
    setSelectedTestcase(e.target.value);
  };

  const renderMetricsGrid = () => {
    if (!authorMetrics) return null;

    const metrics = [
      { key: 'code_complexity', label: 'Code Complexity', color: 'blue' },
      { key: 'code_quality', label: 'Code Quality', color: 'green' },
      { key: 'code_readability', label: 'Code Readability', color: 'purple' },
      { key: 'developer_performance', label: 'Developer Performance', color: 'yellow' },
      { key: 'function_complexity', label: 'Function Complexity', color: 'red' },
    ];

    const daysSinceLastCommit = calculateDaysDifference(
      authorMetrics.current_date, 
      authorMetrics.last_commit_date
    );

    return (
      <div className="grid grid-cols-2 gap-4">
        {metrics.map(({ key, label, color }) => (
          <MetricCard
            key={key}
            title={label}
            value={authorMetrics[key]}
            color={color}
            type="progress"
          />
        ))}
        
        <div className="bg-white p-4 rounded-md shadow">
          <p className="text-sm text-gray-500 mb-2">Last TestCases Pass Date</p>
          <p className="font-medium">{formatDate(authorMetrics.last_commit_date)}</p>
          <p className="text-xs text-gray-500">
            Today: {formatDate(authorMetrics.current_date)}
          </p>
          <p className="text-sm font-bold text-indigo-600 mt-1">
            {daysSinceLastCommit} days since Passed TestCases
          </p>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-8">
      <h2 className="text-2xl font-bold text-gray-800 mb-4">Team Members</h2>

      {/* Author Selection */}
      <div className="mb-6">
        <label className="block text-gray-700 font-medium mb-2">Select Team Member</label>
        <select
          className="w-full px-4 py-2 border rounded-md bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
          onChange={onAuthorChange}
          value={selectedAuthor || ''}
        >
          <option value="">Select a team member</option>
          {authors.map(author => (
            <option key={author} value={author}>{author}</option>
          ))}
        </select>
      </div>

      {selectedAuthor && (
        <>
          {/* Testcase Selection */}
          <div className="mb-6">
            <label className="block text-gray-700 font-medium mb-2">
              Select Testcase for Metrics
            </label>
            {testcasesLoading ? (
              <LoadingSpinner size="sm" text="Loading testcases..." />
            ) : (
              <select
                className="w-full px-4 py-2 border bg-gray-100 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                onChange={handleTestcaseChange}
                value={selectedTestcase}
              >
                <option value="all">All Testcases (Average)</option>
                {authorTestcases.map(testcase => (
                  <option key={testcase} value={testcase}>{testcase}</option>
                ))}
              </select>
            )}
          </div>

          {/* Metrics Display */}
          {metricsLoading ? (
            <LoadingSpinner text="Loading metrics..." />
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Developer Metrics */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold mb-4">Developer Metrics</h3>
                {renderMetricsGrid()}
              </div>

              {/* Work Metrics */}
              {workMetrics && (
                <div className="bg-gray-50 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">Work Time Metrics</h3>
                  <WorkMetricsChart workMetrics={workMetrics} />
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default TeamMembersSection;