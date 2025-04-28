import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import axios from 'axios'
import Loader from '../components/Loader'
import AnalysisResult from '../components/AnalysisResult'
import CommitDetails from '../components/CommitDetails'
import TestCaseHeader from '../components/TestCaseHeader' // <-- Import TestCaseHeader

export default function AnalysisPage() {
  const { testcaseId } = useParams()
  const [analysis, setAnalysis] = useState(null)
  const [llmAnalysis, setLlmAnalysis] = useState(null)
  const [testCase, setTestCase] = useState(null) // <-- Add testCase state
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        const [analysisRes, llmRes, testCaseRes] = await Promise.all([
          axios.get(`/api/testcases/${testcaseId}/analyze`),
          axios.get(`/api/testcases/${testcaseId}/llm-analysis`),
          axios.get(`/api/testcases/${testcaseId}`) // <-- Fetch TestCase details
        ])

        setAnalysis(analysisRes.data.data)
        setLlmAnalysis(llmRes.data.data)
        setTestCase(testCaseRes.data.data)
      } catch (err) {
        setError(err.response?.data?.message || 'Error fetching analysis')
      } finally {
        setLoading(false)
      }
    }

    fetchAnalysis()
  }, [testcaseId])

  if (loading) return <Loader />
  if (error) return <div className="text-red-500 p-4">{error}</div>

  return (
    <div>
      {testCase && <TestCaseHeader testCase={testCase} />} {/* <-- Add TestCaseHeader */}
      
      <h1 className="text-2xl font-bold mb-6">Analysis for Test Case: {testcaseId}</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-6">
          <CommitDetails analysis={analysis} />
        </div>

        <div className="space-y-6">
          <AnalysisResult analysis={llmAnalysis} />
        </div>
      </div>
      
    </div>
  )
}
