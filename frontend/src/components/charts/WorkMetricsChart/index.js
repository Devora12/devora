import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LabelList } from 'recharts';
import { formatNumber, getEfficiencyColor } from '../../../utils/formatters';

const WorkMetricsChart = ({ workMetrics }) => {
  if (!workMetrics) return null;

  const totalData = [
    {
      name: "Hours",
      "Working Hours": parseFloat(workMetrics.totals.total_working_hours).toFixed(2),
      "Estimated Time": parseFloat(workMetrics.totals.estimated_time).toFixed(2)
    }
  ];

  const efficiencyRatio = workMetrics.totals.estimated_time / workMetrics.totals.total_working_hours;
  const timeDifference = workMetrics.totals.total_working_hours - workMetrics.totals.estimated_time;

  return (
    <div>
      {/* Testcase Working Hours vs Estimated Time */}
      <div className="mb-6">
        <h4 className="text-md font-medium mb-2">Working Hours vs Estimated Time (by Testcase)</h4>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={workMetrics.testcases}
              margin={{ top: 20, right: 30, left: 20, bottom: 30 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="testcase" angle={-45} textAnchor="end" height={70} />
              <YAxis label={{ value: 'Hours', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Bar dataKey="total_working_hours" name="Working Hours" fill="#8884d8" />
              <Bar dataKey="estimated_time" name="Estimated Time" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Total Working Hours vs Estimated Time */}
      <div>
        <h4 className="text-md font-medium mb-2">Total Time Metrics</h4>
        <div className="h-24">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              layout="vertical"
              data={totalData}
              margin={{ top: 5, right: 30, left: 20, bottom: 2 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis type="category" dataKey="name" />
              <Tooltip />
              <Legend />
              <Bar dataKey="Working Hours" fill="#8884d8">
                <LabelList dataKey="Working Hours" position="right" />
              </Bar>
              <Bar dataKey="Estimated Time" fill="#82ca9d">
                <LabelList dataKey="Estimated Time" position="right" />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Summary Cards */}
        <div className="mt-4 grid grid-cols-2 gap-4">
          <div className="bg-white p-4 rounded-md shadow">
            <p className="text-sm text-gray-500">Efficiency Ratio</p>
            <p className={`font-bold text-2xl ${getEfficiencyColor(efficiencyRatio)}`}>
              {formatNumber(efficiencyRatio, 2)}
            </p>
          </div>
          <div className="bg-white p-4 rounded-md shadow">
            <p className="text-sm text-gray-500">Time Difference</p>
            <p className="font-bold text-2xl text-blue-800">
              {formatNumber(timeDifference)} hours
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WorkMetricsChart;