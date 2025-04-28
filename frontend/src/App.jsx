import { Route, Routes } from 'react-router-dom'
import ProjectsPage from './pages/ProjectsPage'
import ModulesPage from './pages/ModulesPage'
import TestCasesPage from './pages/TestCasesPage'
import AnalysisPage from './pages/AnalysisPage'
import Layout from './components/Layout'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<ProjectsPage />} />
        <Route path="projects/:projectId/modules" element={<ModulesPage />} />
        <Route path="modules/:moduleId/testcases" element={<TestCasesPage />} />
        <Route path="testcases/:testcaseId/analysis" element={<AnalysisPage />} />
      </Route>
    </Routes>
    
  )
}