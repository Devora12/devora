import React, { useState, useRef, useEffect } from 'react';

const Dropdown = ({ 
  options = [], 
  value, 
  onChange, 
  placeholder = "Select an option",
  searchable = false,
  onSearch = null,
  searchPlaceholder = "Search...",
  renderOption = null,
  loading = false 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearchChange = (e) => {
    const term = e.target.value;
    setSearchTerm(term);
    if (onSearch) onSearch(term);
  };

  const handleOptionSelect = (option) => {
    onChange(option);
    setIsOpen(false);
    setSearchTerm('');
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <div
        className="w-full px-4 py-2 border rounded-md bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer flex justify-between items-center"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className={value ? 'text-black' : 'text-gray-500'}>
          {value ? (renderOption ? renderOption(value) : value) : placeholder}
        </span>
        <svg 
          className={`w-5 h-5 transform transition-transform ${isOpen ? 'rotate-180' : ''}`} 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>

      {isOpen && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
          {searchable && (
            <div className="p-3 border-b border-gray-200 bg-gray-50">
              <input
                type="text"
                placeholder={searchPlaceholder}
                className="w-full px-3 py-2 border border-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-gray-100 text-black placeholder-gray-500"
                value={searchTerm}
                onChange={handleSearchChange}
                onClick={(e) => e.stopPropagation()}
              />
            </div>
          )}

          {loading ? (
            <div className="px-4 py-3 text-gray-500 text-center">Loading...</div>
          ) : options.length > 0 ? (
            options.map((option, index) => (
              <div
                key={index}
                className="px-4 py-3 hover:bg-blue-50 cursor-pointer border-b border-gray-100 last:border-b-0"
                onClick={() => handleOptionSelect(option)}
              >
                {renderOption ? renderOption(option) : option}
              </div>
            ))
          ) : (
            <div className="px-4 py-3 text-gray-500 text-center">
              No options available
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Dropdown;