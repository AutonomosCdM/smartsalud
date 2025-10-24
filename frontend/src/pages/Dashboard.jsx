import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Calendar, Users, Clock, CheckCircle, Stethoscope, User } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import apiClient from '@/api/client'
import { ConversationBar } from '@/components/ui/conversation-bar'

export default function Dashboard() {
  const [conversationLog, setConversationLog] = useState([])

  // Traducción de estados
  const translateStatus = (status) => {
    const translations = {
      'CONFIRMED': 'Confirmado',
      'PENDING': 'Pendiente',
      'CANCELLED': 'Cancelado',
      'RESCHEDULED': 'Reagendado',
      'COMPLETED': 'Completado',
      'NO_SHOW': 'No asistió'
    }
    return translations[status] || status
  }

  // Fetch dashboard stats
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const response = await apiClient.get('/stats')
      return response.data
    },
  })

  // Fetch doctors
  const { data: doctors, isLoading: doctorsLoading } = useQuery({
    queryKey: ['doctors'],
    queryFn: async () => {
      const response = await apiClient.get('/doctors')
      return response.data
    },
  })

  // Fetch patients
  const { data: patients, isLoading: patientsLoading } = useQuery({
    queryKey: ['patients-dashboard'],
    queryFn: async () => {
      const response = await apiClient.get('/patients?limit=5')
      return response.data
    },
  })

  // Fetch appointments (with refetch for real-time updates)
  const { data: appointments, isLoading: appointmentsLoading, refetch: refetchAppointments } = useQuery({
    queryKey: ['appointments-dashboard'],
    queryFn: async () => {
      const response = await apiClient.get('/appointments')
      return response.data
    },
    refetchInterval: 3000,  // Auto-refresh every 3s to see calendar updates
  })

  const statsConfig = [
    {
      name: 'Citas Hoy',
      value: stats?.appointments_today || 0,
      icon: Calendar,
      color: 'from-blue-400 to-blue-500',
    },
    {
      name: 'Confirmadas',
      value: stats?.confirmed_appointments || 0,
      icon: CheckCircle,
      color: 'from-green-400 to-green-500',
    },
    {
      name: 'Pendientes',
      value: stats?.pending_appointments || 0,
      icon: Clock,
      color: 'from-amber-400 to-amber-500',
    },
    {
      name: 'Reagendadas',
      value: stats?.rescheduled_appointments || 0,
      icon: Calendar,
      color: 'from-indigo-400 to-indigo-500',
    },
    {
      name: 'Canceladas',
      value: stats?.cancelled_appointments || 0,
      icon: Calendar,
      color: 'from-red-400 to-red-500',
    },
  ]

  // Get upcoming appointments (next 5)
  const upcomingAppointments = appointments
    ? appointments
        .filter(apt => new Date(apt.appointment_date) > new Date())
        .slice(0, 5)
    : []

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-5">
        {statsConfig.map((stat) => (
          <Card key={stat.name}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    {stat.name}
                  </p>
                  <p className="mt-2 text-3xl font-bold">
                    {statsLoading ? '...' : stat.value}
                  </p>
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

      {/* Doctors and Patients Row */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Doctors Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Stethoscope className="mr-2 h-5 w-5" />
              Doctores ({stats?.active_doctors || 0})
            </CardTitle>
          </CardHeader>
          <CardContent>
            {doctorsLoading ? (
              <p className="text-sm text-muted-foreground">Cargando...</p>
            ) : doctors && doctors.length > 0 ? (
              <div className="space-y-3">
                {doctors.map((doctor) => (
                  <div key={doctor.id} className="flex items-center justify-between rounded-lg border p-3">
                    <div>
                      <p className="font-medium">{doctor.name}</p>
                      <p className="text-sm text-muted-foreground">{doctor.specialty}</p>
                    </div>
                    <div className="text-right text-sm text-muted-foreground">
                      {doctor.sector}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No hay doctores registrados</p>
            )}
          </CardContent>
        </Card>

        {/* Patients Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <User className="mr-2 h-5 w-5" />
              Pacientes Recientes
            </CardTitle>
          </CardHeader>
          <CardContent>
            {patientsLoading ? (
              <p className="text-sm text-muted-foreground">Cargando...</p>
            ) : patients && patients.length > 0 ? (
              <div className="space-y-3">
                {patients.map((patient) => (
                  <div key={patient.id} className="flex items-center justify-between rounded-lg border p-3">
                    <div>
                      <p className="font-medium">{patient.first_name} {patient.last_name}</p>
                      <p className="text-sm text-muted-foreground">{patient.email}</p>
                    </div>
                    <div className="text-right text-sm text-muted-foreground">
                      {patient.rut}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No hay pacientes registrados</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Upcoming Appointments */}
      <Card>
        <CardHeader>
          <CardTitle>Próximas Citas</CardTitle>
        </CardHeader>
        <CardContent>
          {appointmentsLoading ? (
            <p className="text-sm text-muted-foreground">Cargando...</p>
          ) : upcomingAppointments.length > 0 ? (
            <div className="space-y-3">
              {upcomingAppointments.map((apt) => (
                <div key={apt.id} className="flex items-center justify-between rounded-lg border p-4">
                  <div className="flex-1">
                    <p className="font-medium">{apt.patient_name}</p>
                    <p className="text-sm text-muted-foreground">
                      Dr. {apt.doctor_name} • {apt.appointment_type_name}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">
                      {new Date(apt.appointment_date).toLocaleDateString('es-CL')}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(apt.appointment_date).toLocaleTimeString('es-CL', { hour: '2-digit', minute: '2-digit' })}
                    </p>
                    <span className={`inline-block mt-1 rounded-full px-2 py-1 text-xs ${
                      apt.status === 'CONFIRMED' ? 'bg-green-100 text-green-800' :
                      apt.status === 'PENDING' ? 'bg-yellow-100 text-yellow-800' :
                      apt.status === 'RESCHEDULED' ? 'bg-indigo-100 text-indigo-800' :
                      apt.status === 'CANCELLED' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {translateStatus(apt.status)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center py-12 text-muted-foreground">
              <p>No hay citas programadas</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Voice Agent - Fixed Bottom Right */}
      <div className="fixed bottom-0 right-0 z-50 w-full max-w-md">
        <ConversationBar
          agentId="agent_0501k86dtzadfh6sf3sj171e89ww"
          onConnect={() => {
            console.log('Voice agent connected')
            setConversationLog(prev => [...prev, { type: 'system', text: '✅ Conectado al agente médico' }])
          }}
          onDisconnect={() => {
            console.log('Voice agent disconnected')
            setConversationLog(prev => [...prev, { type: 'system', text: '⚠️ Desconectado' }])
          }}
          onMessage={(message) => {
            console.log('Message:', message)
            setConversationLog(prev => [...prev, message])
            // Refetch appointments when agent makes changes
            refetchAppointments()
          }}
          onError={(error) => {
            console.error('Voice error:', error)
            setConversationLog(prev => [...prev, { type: 'error', text: `❌ ${error.message}` }])
          }}
        />
      </div>
    </div>
  )
}
