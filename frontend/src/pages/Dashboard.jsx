import { useQuery } from '@tanstack/react-query'
import { Calendar, Users, Clock, CheckCircle } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import apiClient from '@/api/client'

const stats = [
  {
    name: 'Citas Hoy',
    value: '0',
    icon: Calendar,
    color: 'from-blue-400 to-blue-500',
  },
  {
    name: 'Pacientes Activos',
    value: '0',
    icon: Users,
    color: 'from-purple-400 to-purple-500',
  },
  {
    name: 'Citas Pendientes',
    value: '0',
    icon: Clock,
    color: 'from-amber-400 to-amber-500',
  },
  {
    name: 'Confirmadas',
    value: '0',
    icon: CheckCircle,
    color: 'from-green-400 to-green-500',
  },
]

export default function Dashboard() {
  // Placeholder query - will be implemented with real API
  const { data: healthCheck } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const response = await apiClient.get('/health')
      return response.data
    },
  })

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.name}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    {stat.name}
                  </p>
                  <p className="mt-2 text-3xl font-bold">{stat.value}</p>
                </div>
                <div
                  className={`flex h-12 w-12 items-center justify-center rounded-lg bg-gradient-to-br ${stat.color}`}
                >
                  <stat.icon className="h-6 w-6 text-white" />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle>Actividad Reciente</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-12 text-muted-foreground">
            <p>No hay actividad reciente</p>
          </div>
        </CardContent>
      </Card>

      {/* System Status */}
      {healthCheck && (
        <Card>
          <CardHeader>
            <CardTitle>Estado del Sistema</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <div className="h-3 w-3 rounded-full bg-green-500" />
              <span className="text-sm text-muted-foreground">
                Sistema operativo
              </span>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
