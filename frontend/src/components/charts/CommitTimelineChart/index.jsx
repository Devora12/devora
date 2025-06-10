import React, { useState, useEffect } from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { format, parseISO } from 'date-fns';

const CommitTimelineChart = ({ projectId }) => {
  const [commitData, setCommitData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const API_URL = 'http://20.205.22.95:2001/api'; // Update with your actual API URL
  const COLORS = ['#4285F4', '#EA4335', '#FBBC05', '#34A853'];
  
  useEffect(() => {
    // Fetch commit timeline data
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_URL}/project/${projectId}/commit-timeline`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        setCommitData(data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };
    
    if (projectId) {
      fetchData();
    }
  }, [projectId]);
  
  // Process data for the chart
  const processDataForChart = () => {
    // Group data by dates and collect each author's commit counts for that date
    const dateMap = new Map();
    
    commitData.forEach(item => {
      const date = format(parseISO(item.date), 'yyyy-MM-dd');
      const author = item.author;
      const commits = item.commits; // Changed from cumulative_commits to commits
      
      if (!dateMap.has(date)) {
        dateMap.set(date, { date });
      }
      
      // Store this author's commit count for this date
      dateMap.get(date)[author] = commits;
    });
    
    // Convert map to array and sort by date
    return Array.from(dateMap.values()).sort((a, b) => new Date(a.date) - new Date(b.date));
  };

  // Get unique authors from the data
  const getUniqueAuthors = () => {
    const authors = new Set();
    commitData.forEach(item => authors.add(item.author));
    return Array.from(authors);
  };
  
  const chartData = processDataForChart();
  const authors = getUniqueAuthors();
  
  const formatDate = (dateString) => {
    try {
      if (!dateString) return '';
      return format(parseISO(dateString), 'MM/dd/yy');
    } catch (e) {
      console.error("Date formatting error:", e);
      return dateString;
    }
  };

  if (loading) return <div className="text-center py-4">Loading commit data...</div>;
  if (error) return <div className="text-center text-red-500 py-4">Error: {error}</div>;
  if (commitData.length === 0) return <div className="text-center text-gray-500 py-4">No commit data available</div>;

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 35 }}
        >
          
          <XAxis 
            dataKey="date" 
            tickFormatter={formatDate}
            angle={-30}
            textAnchor="end"
            height={60}
            tick={{ fontSize: 12 }}
          />
          <YAxis 
            label={{ value: 'Commits', angle: -90, position: 'insideLeft',dy:40 }}
          />
          <Tooltip 
            labelFormatter={formatDate}
            formatter={(value, name) => [value, name]}
          />
          <Legend />
          {authors.map((author, index) => (
            <Line
              key={author}
              type="basis"
              dataKey={author}
              name={author}
              stroke={COLORS[index % COLORS.length]}
              activeDot={{ r: 5 }}
              connectNulls
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CommitTimelineChart;
