import React from 'react';

const ProgressBar = ({ value, maxValue = 5, color = 'blue', label, showValue = true }) => {
  const percentage = (value / maxValue) * 100;
  
  const colorClasses = {
    blue: 'bg-blue-600',
    green: 'bg-green-600',
    purple: 'bg-purple-600',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
  };

  return (
    <div className="flex items-center">
      <div className="w-full bg-gray-200 rounded-full h-2.5">
        <div
          className={`${colorClasses[color]} h-2.5 rounded-full transition-all duration-300`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showValue && (
        <span className="ml-2 font-bold text-sm">
          {value.toFixed(1)}/{maxValue}
        </span>
      )}
    </div>
  );
};

export default ProgressBar;