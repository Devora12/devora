import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { CHART_COLORS } from '../../../utils/constants';

const TestcasesPieChart = ({ data = [] }) => {
  if (data.length === 0) {
    return (
      <div className="h-80 flex items-center justify-center">
        <p className="text-gray-500">No testcase data available</p>
      </div>
    );
  }

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="count"
            nameKey="author"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={CHART_COLORS[index % CHART_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value, name, props) => {
              const entry = data.find(entry => entry.author === props.payload.author);
              return [
                <div key="tooltip">
                  <div>Count: {value}</div>
                  <div>Testcases: {entry?.testcases.join(', ')}</div>
                </div>
              ];
            }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default TestcasesPieChart;
