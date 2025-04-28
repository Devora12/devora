import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import axios from 'axios'
import Loader from '../components/Loader'

export default function ModulesPage() {
  const { projectId } = useParams()
  const [modules, setModules] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchModules = async () => {
      try {
        const response = await axios.get(`/api/projects/${projectId}/modules`)
        setModules(response.data.data)
      } catch (error) {
        console.error('Error fetching modules:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchModules()
  }, [projectId])

  if (loading) return <Loader />

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Test Modules</h1>
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <table className="min-w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Module ID</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Name</th>
              <th className="px-6 py-3 text-left text-sm font-medium text-gray-500">Description</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {modules.map(module => (
              <tr key={module.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <Link
                    to={`/modules/${module.id}/testcases`}
                    className="text-primary hover:text-secondary"
                  >
                    {module.id}
                  </Link>
                </td>
                <td className="px-6 py-4">{module.name}</td>
                <td className="px-6 py-4">{module.description}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
    </div>
  )
}