// src/components/CommitDetails.jsx
export default function CommitDetails({ analysis }) {
    // Function to extract author name from raw author string
    const getAuthorName = (authorString) => {
      const match = authorString.match(/^(.*?) <.*?>$/);
      return match ? match[1] : authorString;
    };
  
    // Date formatting utility
    const formatDate = (dateString) => {
      const options = {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
        
      };
      return new Date(dateString).toLocaleDateString('en-US', options);
    };
  
    // Duration calculation utility
    const formatDuration = (start, end) => {
      const startDate = new Date(start);
      const endDate = new Date(end);
      const diffMs = endDate - startDate;
      
      const days = Math.floor(diffMs / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diffMs % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
  
      return `${days}d ${hours}h ${minutes}m`;
    };
  
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm">
        <h2 className="text-xl font-semibold mb-4">Commit Details</h2>
        
        <div className="space-y-4">
          <div>
            <h3 className="font-medium mb-2">Time Metrics</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 p-3 rounded">
                <p className="text-sm text-gray-600 mb-1">Start Time</p>
                <p className="font-medium">
                  {analysis?.time_metrics?.start_time 
                    ? formatDate(analysis.time_metrics.start_time) 
                    : 'N/A'}
                </p>
              </div>
  
              <div className="bg-gray-50 p-3 rounded">
                <p className="text-sm text-gray-600 mb-1">End Time</p>
                <p className="font-medium">
                  {analysis?.time_metrics?.end_time 
                    ? formatDate(analysis.time_metrics.end_time) 
                    : 'N/A'}
                </p>
              </div>
  
              <div className="bg-gray-50 p-3 rounded">
                <p className="text-sm text-gray-600 mb-1">Total Duration</p>
                <p className="font-medium">
                  {analysis?.time_metrics?.start_time && analysis?.time_metrics?.end_time
                    ? formatDuration(
                        analysis.time_metrics.start_time,
                        analysis.time_metrics.end_time
                      )
                    : 'N/A'}
                </p>
              </div>
            </div>
          </div>
  
          <div>
            <h3 className="font-medium mb-2">Commits ({analysis?.commits?.length || 0})</h3>
            <div className="space-y-3">
              {analysis?.commits?.map((commit) => (
                <div key={commit.hash} className="border rounded p-3">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="font-mono text-sm text-gray-600">{commit.hash}</p>
                      <p className="text-xs text-gray-500 mt-1">{formatDate(commit.date)}</p>
                    </div>
                    <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
                      {getAuthorName(commit.author)}
                    </span>
                  </div>
                  <p className="text-sm">{commit.message}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }
  