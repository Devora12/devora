import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import axios from 'axios'
import Loader from '../components/Loader'

export default function TestCasesPage() {
  const { moduleId } = useParams()
  const [testCases, setTestCases] = useState([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('ALL')

  useEffect(() => {
    const fetchTestCases = async () => {
      try {
        const response = await axios.get(`/api/modules/${moduleId}/testcases`)
        setTestCases(response.data.data)
      } catch (error) {
        console.error('Error fetching test cases:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchTestCases()
  }, [moduleId])

  const filteredTestCases = statusFilter === 'ALL' 
    ? testCases 
    : testCases.filter(testCase => testCase.status === statusFilter)

  if (loading) return <Loader />

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Test Cases</h1>
        <div className="flex items-center">
          <label htmlFor="statusFilter" className="mr-2 text-sm font-medium text-gray-700">
            Filter by Status:
          </label>
          <select
            id="statusFilter"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-white border border-gray-300 rounded-md py-2 px-3 shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
          >
            <option value="ALL">ALL</option>
            <option value="PASS" className="text-green-600">PASS</option>
            <option value="FAIL" className="text-red-600">FAIL</option>
            <option value="PENDING" className="text-yellow-600">PENDING</option>
          </select>
        </div>
      </div>
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Test Case ID</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Name</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Objective</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Status</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {filteredTestCases.map(testCase => (
              <tr key={testCase.testCaseId} className="hover:bg-gray-50">
                <td className="px-6 py-4">{testCase.testCaseId}</td>
                <td className="px-6 py-4">{testCase.testCase}</td>
                <td className="px-6 py-4">{testCase.objective}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    testCase.status === 'PASS' ? 'bg-green-100 text-green-800' :
                    testCase.status === 'FAIL' ? 'bg-red-100 text-red-800' :
                    testCase.status === 'PENDING' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {testCase.status}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <Link
                    to={`/testcases/${testCase.testCaseId}/analysis`}
                    className="text-primary hover:text-secondary"
                  >
                    Analyze
                  </Link>
                  
                </td>
              </tr>
            ))}
            {filteredTestCases.length === 0 && (
              <tr>
                <td colSpan="5" className="px-6 py-4 text-center text-gray-500">
                  No test cases found with the selected status.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}