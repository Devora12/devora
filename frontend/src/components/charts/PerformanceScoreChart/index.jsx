import React, { useState, useEffect } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Legend, 
  ResponsiveContainer,
  Cell,
  LabelList
} from 'recharts';

const PerformanceScoreChart = ({ projectId }) => {
  const [performanceData, setPerformanceData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const getBarGradient = (score) => {
    if (score >= 10) return 'url(#excellentGradient)';
    if (score >= 5) return 'url(#goodGradient)';
    if (score >= 2) return 'url(#averageGradient)';
    if (score >= 1) return 'url(#belowAvgGradient)';
    return 'url(#poorGradient)';
  };

  useEffect(() => {
    if (projectId) {
      setLoading(true);
      fetch(`http://localhost:5000/api/project/${projectId}/performance-scores`)
        .then(response => {
          if (!response.ok) throw new Error('Failed to fetch performance scores');
          return response.json();
        })
        .then(data => {
          setPerformanceData(data);
          setError(null);
        })
        .catch(error => {
          console.error("Error fetching performance scores:", error);
          setError("Failed to load performance scores");
        })
        .finally(() => setLoading(false));
    }
  }, [projectId]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center text-red-500 p-4">
        <p>{error}</p>
      </div>
    );
  }

  if (performanceData.length === 0) {
    return (
      <div className="text-center text-gray-500 p-4">
        <p>No performance data available</p>
      </div>
    );
  }

  return (
    <div className="w-full">
      <div className="flex gap-4 mb-6">
        <div className="flex-1 h-96">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={performanceData}
              margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
            >
              <defs>
                <linearGradient id="excellentGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#34D399" stopOpacity={1} />
                  <stop offset="100%" stopColor="#10B981" stopOpacity={1} />
                </linearGradient>
                <linearGradient id="goodGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#60A5FA" stopOpacity={1} />
                  <stop offset="100%" stopColor="#3B82F6" stopOpacity={1} />
                </linearGradient>
                <linearGradient id="averageGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#FBBF24" stopOpacity={1} />
                  <stop offset="100%" stopColor="#F59E0B" stopOpacity={1} />
                </linearGradient>
                <linearGradient id="belowAvgGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#F87171" stopOpacity={1} />
                  <stop offset="100%" stopColor="#EF4444" stopOpacity={1} />
                </linearGradient>
                <linearGradient id="poorGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#9CA3AF" stopOpacity={1} />
                  <stop offset="100%" stopColor="#6B7280" stopOpacity={1} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="author" 
                angle={0} 
                textAnchor="middle" 
                height={80}
                interval={0}
              />
              <YAxis 
                label={{ value: 'Performance Score', angle: -90, position: 'insideLeft', dy: 70 }}
              />
              <Bar dataKey="performance_score" name="Performance Score" radius={[4, 4, 0, 0]}>
                {performanceData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getBarGradient(entry.performance_score)} />
                ))}
                <LabelList 
                  dataKey="performance_score" 
                  position="top" 
                  style={{ fontSize: '12px', fontWeight: 'bold' }}
                />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-gray-50 rounded-lg p-3 w-48 flex-shrink-0">
          <h4 className="font-medium text-sm mb-3">Performance Score</h4>
          <div className="space-y-2 text-xs">
            <div className="flex items-center">
              <div className="w-3 h-3 rounded mr-2" style={{ background: 'linear-gradient(to bottom, #34D399, #10B981)' }}></div>
              <span>Excellent </span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 rounded mr-2" style={{ background: 'linear-gradient(to bottom, #60A5FA, #3B82F6)' }}></div>
              <span>Good </span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 rounded mr-2" style={{ background: 'linear-gradient(to bottom, #FBBF24, #F59E0B)' }}></div>
              <span>Average </span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 rounded mr-2" style={{ background: 'linear-gradient(to bottom, #F87171, #EF4444)' }}></div>
              <span>Below Avg </span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 rounded mr-2" style={{ background: 'linear-gradient(to bottom, #9CA3AF, #6B7280)' }}></div>
              <span>Poor </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceScoreChart;
