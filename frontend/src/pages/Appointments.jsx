import { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Calendar as CalendarIcon, Plus, LayoutGrid, CalendarDays } from 'lucide-react'
import { FullscreenCalendar } from '@/components/ui/fullscreen-calendar'
import { AppointmentScheduler } from '@/components/ui/appointment-scheduler'
import { Button } from '@/components/ui/button'
import axios from 'axios'

export default function Appointments() {
  const [view, setView] = useState('calendar') // 'calendar' or 'scheduler'
  const [appointments, setAppointments] = useState([])
  const [loading, setLoading] = useState(true)
  const [showNewAppointment, setShowNewAppointment] = useState(false)

  // Sample data for scheduler (will be replaced with API calls)
  const schedulerData = {
    patientName: "Juan Pérez",
    doctorName: "Dr. César Durán",
    appointmentType: "Cons. Morbilidad",
    duration: "20 min",
    timezone: "America/Santiago",
    availableDates: [
      { date: 23, month: "Octubre", year: 2025, isAvailable: true },
      { date: 24, month: "Octubre", year: 2025, isAvailable: true },
      { date: 25, month: "Octubre", year: 2025, isAvailable: false },
      { date: 28, month: "Octubre", year: 2025, isAvailable: true },
      { date: 29, month: "Octubre", year: 2025, isAvailable: true },
      { date: 30, month: "Octubre", year: 2025, isAvailable: true },
    ],
    timeSlots: [
      { time: "09:00 AM", isAvailable: true },
      { time: "09:20 AM", isAvailable: true },
      { time: "09:40 AM", isAvailable: false },
      { time: "10:00 AM", isAvailable: true },
      { time: "10:20 AM", isAvailable: true },
      { time: "10:40 AM", isAvailable: true },
    ],
  }

  useEffect(() => {
    fetchAppointments()
  }, [])

  const fetchAppointments = async () => {
    try {
      setLoading(true)
      const response = await axios.get('/api/appointments')
      setAppointments(response.data)
    } catch (error) {
      console.error('Error fetching appointments:', error)
    } finally {
      setLoading(false)
    }
  }

  // Transform appointments for calendar view
  const calendarData = appointments.map(apt => ({
    day: new Date(apt.appointment_date),
    events: [{
      id: apt.id,
      name: apt.patient_name || 'Paciente',
      time: new Date(apt.appointment_date).toLocaleTimeString('es-CL', {
        hour: '2-digit',
        minute: '2-digit'
      }),
      datetime: apt.appointment_date,
    }]
  }))

  return (
    <div className="space-y-6">
      {/* Header Actions */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium">Gestión de Citas</h3>
          <p className="text-sm text-muted-foreground">
            Administra las citas médicas del sistema
          </p>
        </div>
        <div className="flex items-center gap-2">
          {/* View Toggle */}
          <div className="flex items-center gap-1 rounded-lg border bg-white p-1">
            <Button
              variant={view === 'calendar' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setView('calendar')}
              className="h-8"
            >
              <LayoutGrid className="mr-2 h-4 w-4" />
              Calendario
            </Button>
            <Button
              variant={view === 'scheduler' ? 'default' : 'ghost'}
              size="sm"
              onClick={() => setView('scheduler')}
              className="h-8"
            >
              <CalendarDays className="mr-2 h-4 w-4" />
              Agendar
            </Button>
          </div>

          <Button
            onClick={() => setShowNewAppointment(true)}
            className="inline-flex items-center"
          >
            <Plus className="mr-2 h-4 w-4" />
            Nueva Cita
          </Button>
        </div>
      </div>

      {/* Calendar View */}
      {view === 'calendar' && (
        <div className="rounded-lg border bg-white shadow-sm" style={{ height: '700px' }}>
          <FullscreenCalendar data={calendarData} />
        </div>
      )}

      {/* Scheduler View */}
      {view === 'scheduler' && (
        <div style={{ height: '700px' }}>
          <AppointmentScheduler
            patientName={schedulerData.patientName}
            doctorName={schedulerData.doctorName}
            appointmentType={schedulerData.appointmentType}
            duration={schedulerData.duration}
            timezone={schedulerData.timezone}
            availableDates={schedulerData.availableDates}
            timeSlots={schedulerData.timeSlots}
            onDateSelect={(date) => console.log('Selected date:', date)}
            onTimeSelect={(time) => console.log('Selected time:', time)}
            brandName="CESFAM"
          />
        </div>
      )}
    </div>
  )
}
