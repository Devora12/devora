import React from 'react';
import ProgressBar from '../ProgressBar';

const MetricCard = ({ title, value, maxValue = 5, color = 'blue', type = 'progress' }) => {
  return (
    <div className="bg-white p-4 rounded-md shadow">
      <p className="text-sm text-gray-500 mb-2">{title}</p>
      {type === 'progress' ? (
        <ProgressBar value={value} maxValue={maxValue} color={color} />
      ) : (
        <p className="font-medium text-gray-900">{value}</p>
      )}
    </div>
  );
};

export default MetricCard;