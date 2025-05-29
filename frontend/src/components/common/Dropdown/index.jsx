import React, { useState, useRef, useEffect } from 'react';

const Dropdown = ({ 
  options = [], 
  value, 
  onChange, 
  placeholder = "Select an option",
  searchable = false,
  searchPlaceholder = "Search...",
  displayKey = null,
  descriptionKey = "description",
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

  const handleOptionSelect = (option) => {
    onChange(option);
    setIsOpen(false);
    setSearchTerm('');
  };

  // Get the text to display
  const getDisplayText = (item) => {
    if (!item) return '';
    if (displayKey && item[displayKey]) return item[displayKey];
    if (typeof item === 'string') return item;
    // If it's an object without displayKey, try common fields
    if (typeof item === 'object') {
      return item.name || item.title || item.label || JSON.stringify(item);
    }
    return String(item);
  };

  // Get the full display text with description inline
  const getFullDisplayText = (item) => {
    const name = getDisplayText(item);
    const description = descriptionKey && item[descriptionKey] ? item[descriptionKey] : '';
    return description ? `${name} - ${description}` : name;
  };

  const filteredOptions = searchable && searchTerm 
    ? options.filter(option => 
        getFullDisplayText(option).toLowerCase().includes(searchTerm.toLowerCase())
      )
    : options;

  return (
    <div className="relative w-full" ref={dropdownRef}>
      <div
        className="w-full px-4 py-2 border rounded-md bg-white cursor-pointer flex justify-between items-center hover:bg-gray-50"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className={value ? 'text-black' : 'text-gray-500'}>
          {value ? getFullDisplayText(value) : placeholder}
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
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
          {searchable && (
            <div className="p-3 border-b">
              <input
                type="text"
                placeholder={searchPlaceholder}
                className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onClick={(e) => e.stopPropagation()}
              />
            </div>
          )}

          {loading ? (
            <div className="px-4 py-3 text-center text-gray-500">Loading...</div>
          ) : filteredOptions.length > 0 ? (
            filteredOptions.map((option, index) => (
              <div
                key={index}
                className="px-4 py-3 hover:bg-blue-50 cursor-pointer border-b last:border-b-0"
                onClick={() => handleOptionSelect(option)}
              >
                <div className="flex items-center">
                  <span className="font-medium text-black">{getDisplayText(option)}</span>
                  {descriptionKey && option[descriptionKey] && (
                    <>
                      <span className="mx-2 text-gray-400">-</span>
                      <span className="text-gray-600">{option[descriptionKey]}</span>
                    </>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div className="px-4 py-3 text-center text-gray-500">No options found</div>
          )}
        </div>
      )}
    </div>
  );
};

export default Dropdown;