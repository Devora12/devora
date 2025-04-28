// src/components/AnalysisResult.jsx
export default function AnalysisResult({ analysis }) {
    if (!analysis) return null
  
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h2 className="text-xl font-semibold mb-6">AI Analysis</h2>
        
        <div className="space-y-6">
          {/* Summary Section */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-medium mb-3">Summary of Changes</h3>
            <ul className="list-disc pl-5 space-y-2">
              {Array.isArray(analysis.summary_of_change) ? 
                analysis.summary_of_change.map((item, index) => (
                  <li key={index} className="text-sm">{item}</li>
                )) : 
                <li className="text-sm">{analysis.summary_of_change || 'No summary available'}</li>
              }
            </ul>
          </div>
  
          {/* Metrics Grid */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Code Complexity</p>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold">{analysis.code_complexity?.rating || 'N/A'}</span>
                <span className="text-sm text-blue-700">{analysis.code_complexity?.level || 'Not available'}</span>
              </div>
            </div>
  
            <div className="bg-green-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Code Quality</p>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold">{analysis.code_quality?.rating || 'N/A'}</span>
                <span className="text-sm text-green-700">{analysis.code_quality?.level || 'Not available'}</span>
              </div>
            </div>
  
            <div className="bg-purple-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Readability</p>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold">{analysis.code_readability?.rating || 'N/A'}</span>
                <span className="text-sm text-purple-700">{analysis.code_readability?.level || 'Not available'}</span>
              </div>
            </div>
  
            <div className="bg-orange-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600 mb-1">Developer Performance</p>
              <div className="flex items-baseline gap-2">
                <span className="text-2xl font-bold">{analysis.developer_performance?.rating || 'N/A'}</span>
                <span className="text-sm text-orange-700">{analysis.developer_performance?.level || 'Not available'}</span>
              </div>
            </div>
          </div>
  
          {/* Code Review Section */}
          <div>
            <h3 className="font-medium mb-3">Code Review</h3>
            <div className="prose max-w-none bg-gray-50 p-4 rounded-lg">
              {analysis.code_review || 'No code review available'}
            </div>
          </div>
  
          {/* Technical Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-yellow-50 p-4 rounded-lg">
              <h3 className="font-medium mb-3">Languages Used</h3>
              <div className="flex flex-wrap gap-2">
                {analysis.languages_used ? 
                  analysis.languages_used.split(', ').map((lang, index) => (
                    <span 
                      key={index}
                      className="px-2 py-1 bg-yellow-100 text-yellow-800 text-sm rounded-full"
                    >
                      {lang}
                    </span>
                  )) : 
                  <span className="text-sm">No languages specified</span>
                }
              </div>
            </div>
  
            <div className="bg-teal-50 p-4 rounded-lg">
              <h3 className="font-medium mb-3">Estimated Time</h3>
              <div className="text-3xl font-bold text-teal-700">
                {analysis.estimated_time?.hours || 'N/A'} hours
              </div>
            </div>
          </div>
  
          {/* Skills & Recommendations */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-indigo-50 p-4 rounded-lg">
              <h3 className="font-medium mb-3">Skills Gained</h3>
              <ul className="list-disc pl-5 space-y-2">
                {Array.isArray(analysis.skills_gained) ? 
                  analysis.skills_gained.map((skill, index) => (
                    <li key={index} className="text-sm">{skill}</li>
                  )) : 
                  <li className="text-sm">No skills listed</li>
                }
              </ul>
            </div>
  
            <div className="bg-pink-50 p-4 rounded-lg">
              <h3 className="font-medium mb-3">Recommendations</h3>
              <ul className="list-disc pl-5 space-y-2">
                {Array.isArray(analysis.recommendations) ? 
                  analysis.recommendations.map((rec, index) => (
                    <li key={index} className="text-sm">{rec}</li>
                  )) : 
                  <li className="text-sm">No recommendations available</li>
                }
              </ul>
            </div>
          </div>
        </div>
        
      </div>
    )
  }