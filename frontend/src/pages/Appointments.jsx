import { useState, useEffect } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Calendar as CalendarIcon, Plus, LayoutGrid, CalendarDays } from 'lucide-react'
import { FullscreenCalendar } from '@/components/ui/fullscreen-calendar'
import { AppointmentScheduler } from '@/components/ui/appointment-scheduler'
import { Button } from '@/components/ui/button'
import axios from 'axios'

const API_URL = 'http://localhost:8001'

export default function Appointments() {
  const [view, setView] = useState('calendar') // 'calendar' or 'scheduler'
  const [appointments, setAppointments] = useState([])
  const [doctors, setDoctors] = useState([])
  const [patients, setPatients] = useState([])
  const [appointmentTypes, setAppointmentTypes] = useState([])
  const [loading, setLoading] = useState(true)

  // Scheduler state
  const [selectedDoctor, setSelectedDoctor] = useState(null)
  const [selectedPatient, setSelectedPatient] = useState(null)
  const [selectedAppointmentType, setSelectedAppointmentType] = useState(null)
  const [selectedDate, setSelectedDate] = useState(null)
  const [availableSlots, setAvailableSlots] = useState([])
  const [loadingSlots, setLoadingSlots] = useState(false)

  useEffect(() => {
    fetchInitialData()
  }, [])

  const fetchInitialData = async () => {
    try {
      setLoading(true)
      const [appointmentsRes, doctorsRes, patientsRes, typesRes] = await Promise.all([
        axios.get(`${API_URL}/api/appointments`),
        axios.get(`${API_URL}/api/doctors`),
        axios.get(`${API_URL}/api/patients?limit=20`),
        axios.get(`${API_URL}/api/appointment-types`)
      ])

      setAppointments(appointmentsRes.data)
      setDoctors(doctorsRes.data)
      setPatients(patientsRes.data)
      setAppointmentTypes(typesRes.data)

      // Select first doctor and appointment type by default
      if (doctorsRes.data.length > 0) {
        setSelectedDoctor(doctorsRes.data[0])
      }
      if (typesRes.data.length > 0) {
        setSelectedAppointmentType(typesRes.data[0])
      }
      if (patientsRes.data.length > 0) {
        setSelectedPatient(patientsRes.data[0])
      }
    } catch (error) {
      console.error('Error fetching initial data:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchAppointments = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/appointments`)
      setAppointments(response.data)
    } catch (error) {
      console.error('Error fetching appointments:', error)
    }
  }

  const fetchAvailableSlots = async (date) => {
    if (!selectedDoctor || !selectedAppointmentType) return

    try {
      setLoadingSlots(true)
      const dateStr = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
      const response = await axios.get(`${API_URL}/api/doctors/${selectedDoctor.id}/availability`, {
        params: {
          target_date: dateStr,
          appointment_type_id: selectedAppointmentType.id
        }
      })

      // Convert to scheduler format
      const slots = response.data.map(slot => ({
        time: new Date(slot.start_time).toLocaleTimeString('es-CL', {
          hour: '2-digit',
          minute: '2-digit',
          hour12: true
        }),
        isAvailable: slot.is_available
      }))

      setAvailableSlots(slots)
    } catch (error) {
      console.error('Error fetching availability:', error)
      setAvailableSlots([])
    } finally {
      setLoadingSlots(false)
    }
  }

  const handleDateSelect = (date) => {
    // date is now a full Date object from AppointmentScheduler
    setSelectedDate(date.getDate())
    fetchAvailableSlots(date)
  }

  const handleTimeSelect = async (time) => {
    if (!selectedPatient || !selectedDoctor || !selectedAppointmentType || !selectedDate) {
      alert('Por favor seleccione todos los campos requeridos')
      return
    }

    try {
      // Parse the selected time and combine with selected date
      const [timeStr, period] = time.split(' ')
      const [hours, minutes] = timeStr.split(':').map(Number)
      let hour24 = hours
      if (period === 'PM' && hours !== 12) hour24 += 12
      if (period === 'AM' && hours === 12) hour24 = 0

      const appointmentDate = new Date()
      appointmentDate.setDate(selectedDate)
      appointmentDate.setHours(hour24, minutes, 0, 0)

      const response = await axios.post(`${API_URL}/api/appointments`, {
        patient_id: selectedPatient.id,
        doctor_id: selectedDoctor.id,
        appointment_type_id: selectedAppointmentType.id,
        appointment_date: appointmentDate.toISOString(),
        notes: null
      })

      alert(`Cita creada exitosamente! ID: ${response.data.id}\nCalendar Event ID: ${response.data.calendar_event_id}`)

      // Refresh appointments and switch to calendar view
      await fetchAppointments()
      setView('calendar')
    } catch (error) {
      console.error('Error creating appointment:', error)
      alert(`Error al crear cita: ${error.response?.data?.detail || error.message}`)
    }
  }

  // Transform appointments for calendar view - group by day
  const calendarData = appointments.reduce((acc, apt) => {
    const date = new Date(apt.appointment_date)
    const dateKey = date.toDateString()

    if (!acc[dateKey]) {
      acc[dateKey] = {
        day: date,
        events: []
      }
    }

    acc[dateKey].events.push({
      id: apt.id,
      name: `${apt.patient_name || 'Paciente'} - ${apt.appointment_type_name}`,
      time: date.toLocaleTimeString('es-CL', {
        hour: '2-digit',
        minute: '2-digit'
      }),
      datetime: apt.appointment_date,
    })

    return acc
  }, {})

  const calendarDataArray = Object.values(calendarData)

  // Generate available dates for next 30 days
  const getAvailableDates = () => {
    const dates = []
    const today = new Date()

    for (let i = 0; i < 30; i++) {
      const date = new Date(today)
      date.setDate(today.getDate() + i)

      // Skip Sundays (day 0)
      if (date.getDay() === 0) continue

      dates.push({
        date: date.getDate(),
        month: date.toLocaleDateString('es-CL', { month: 'long' }),
        year: date.getFullYear(),
        isAvailable: true
      })
    }

    return dates
  }

  const handleEventClick = (event) => {
    // Find the full appointment data
    const appointment = appointments.find(apt => apt.id === event.id)
    if (appointment) {
      const details = `
Cita ID: ${appointment.id}
Paciente: ${appointment.patient_name || 'N/A'}
Doctor: ${appointment.doctor_name || 'N/A'}
Tipo: ${appointment.appointment_type_name}
Fecha: ${new Date(appointment.appointment_date).toLocaleString('es-CL')}
Estado: ${appointment.status}
${appointment.notes ? `Notas: ${appointment.notes}` : ''}
      `.trim()
      alert(details)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-muted-foreground">Cargando...</p>
      </div>
    )
  }

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
            onClick={() => setView('scheduler')}
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
          <FullscreenCalendar data={calendarDataArray} onEventClick={handleEventClick} />
        </div>
      )}

      {/* Scheduler View */}
      {view === 'scheduler' && selectedDoctor && selectedPatient && selectedAppointmentType && (
        <div style={{ height: '700px' }}>
          <AppointmentScheduler
            patientName={`${selectedPatient.first_name} ${selectedPatient.last_name}`}
            doctorName={selectedDoctor.name}
            appointmentType={selectedAppointmentType.name}
            duration={`${selectedAppointmentType.duration_minutes} min`}
            timezone="America/Santiago"
            availableDates={getAvailableDates()}
            timeSlots={availableSlots}
            onDateSelect={handleDateSelect}
            onTimeSelect={handleTimeSelect}
            brandName="CESFAM"
          />
        </div>
      )}

      {/* Loading State for Scheduler */}
      {view === 'scheduler' && (!selectedDoctor || !selectedPatient || !selectedAppointmentType) && (
        <div className="flex items-center justify-center h-96">
          <p className="text-muted-foreground">Cargando datos iniciales...</p>
        </div>
      )}
    </div>
  )
}
