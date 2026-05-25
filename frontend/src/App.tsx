import { Routes, Route } from 'react-router-dom'
import Layout from '@components/Layout'
import Dashboard from '@pages/Dashboard'
import AnalyticsPage from '@pages/AnalyticsPage'
import ContentPage from '@pages/ContentPage'
import SMIPage from '@pages/SMIPage'
import MarketResearchPage from '@pages/MarketResearchPage'
import DotAnalysisPage from '@pages/DotAnalysisPage'
import HelpColleaguePage from '@pages/HelpColleaguePage'
import HelpColleagueDetailPage from '@pages/HelpColleagueDetailPage'
import HelpColleagueProfilePage from '@pages/HelpColleagueProfilePage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="analytics" element={<AnalyticsPage />} />
        <Route path="content" element={<ContentPage />} />
        <Route path="smi" element={<SMIPage />} />
        <Route path="market-research" element={<MarketResearchPage />} />
        <Route path="dot-analysis" element={<DotAnalysisPage />} />
        <Route path="help-colleague" element={<HelpColleaguePage />} />
        <Route path="help-colleague/:id" element={<HelpColleagueDetailPage />} />
        <Route path="help-colleague/profile/:userId" element={<HelpColleagueProfilePage />} />
      </Route>
    </Routes>
  )
}

export default App
