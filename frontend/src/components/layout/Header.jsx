import { useLocation } from 'react-router-dom'
import { Bell } from 'lucide-react'

const pageTitles = {
  '/dashboard': 'Dashboard',
  '/appointments': 'Gestión de Citas',
  '/patients': 'Gestión de Pacientes',
  '/doctors': 'Gestión de Doctores',
}

export default function Header() {
  const location = useLocation()
  const pageTitle = pageTitles[location.pathname] || 'SmartSalud'

  return (
    <header className="flex h-16 items-center justify-between border-b border-border bg-white/80 px-6 backdrop-blur-sm">
      <h2 className="text-2xl font-semibold text-foreground">{pageTitle}</h2>

      <div className="flex items-center space-x-4">
        {/* Notifications */}
        <button className="rounded-lg p-2 text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground">
          <Bell className="h-5 w-5" />
        </button>

        {/* User info */}
        <div className="flex items-center space-x-3">
          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-400 to-purple-500" />
          <span className="text-sm font-medium text-foreground">Admin</span>
        </div>
      </div>
    </header>
  )
}
