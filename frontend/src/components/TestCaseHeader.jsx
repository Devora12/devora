export default function TestCaseHeader({ testCase }) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-sm mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-2xl font-bold">{testCase.testCase}</h1>
            <p className="text-gray-600 mt-2">{testCase.objective}</p>
          </div>
          <div className="text-right">
            <span className={`px-3 py-1 text-sm rounded-full ${
              testCase.status === 'Passed' ? 'bg-green-100 text-green-800' :
              testCase.status === 'Failed' ? 'bg-red-100 text-red-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              Status: {testCase.status}
            </span>
            <p className="mt-2 text-sm text-gray-600">
              Priority: {testCase.priority || 'N/A'}
            </p>
          </div>
        </div>
      </div>
    )
  }