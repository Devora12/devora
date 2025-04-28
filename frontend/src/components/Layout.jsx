import { Link, Outlet } from 'react-router-dom'
import { HomeIcon } from '@heroicons/react/24/outline'

export default function Layout() {
  return (
    <div className="min-h-screen">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-3">
          <div className="flex items-center gap-4">
            <Link to="/" className="flex items-center gap-2 text-primary hover:text-secondary">
              <HomeIcon className="w-6 h-6" />
              <span className="text-xl font-bold">QA Analytics</span>
            </Link>
          </div>
        </div>
      </nav>
      
      <main className="max-w-7xl mx-auto px-4 py-6">
        <Outlet />
      </main>
      
    </div>
  )
}