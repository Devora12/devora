import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  BarChart, 
  CartesianGrid, 
  XAxis, 
  YAxis, 
  Tooltip, 
  Legend, 
  Bar, 
  ResponsiveContainer,
  LabelList 
} from 'recharts';

function TeamTimeMetricsChart({ projectId }) {
  const [teamMetrics, setTeamMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const API_URL = 'http://20.205.22.95:5000/api';
  
  useEffect(() => {
    if (!projectId) return;
    
    setLoading(true);
    
    axios.get(`${API_URL}/project/${projectId}/members-time-metrics`)
      .then(response => {
        setTeamMetrics(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error("Error fetching team time metrics:", error);
        setError("Failed to load team time metrics");
        setLoading(false);
      });
  }, [projectId]);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }
  if (error) return <p className="text-red-500">{error}</p>;
  if (!teamMetrics || teamMetrics.length === 0) return <p className="text-gray-500">No team time metrics available</p>;

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={teamMetrics}
          margin={{ top: 20, right: 30, left: 20, bottom: 30 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="author" angle={0} textAnchor="middle" height={50} />
          <YAxis label={{ value: 'Hours', angle: -90, position: 'insideLeft' }} />
          <Tooltip 
            formatter={(value, name) => {
              return [`${value.toFixed(1)} hours`, name];
            }}
            labelFormatter={(label) => `Team Member: ${label}`}
          />
          <Legend />
          <Bar dataKey="total_working_hours" name="Working Hours" fill="#FF8C00" />
          <Bar dataKey="estimated_time" name="Estimated Time" fill="#1E90FF" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default TeamTimeMetricsChart;