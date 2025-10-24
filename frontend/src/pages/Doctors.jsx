import { useQuery } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Stethoscope, Plus, Mail, MapPin, Calendar } from 'lucide-react'
import apiClient from '@/api/client'

export default function Doctors() {
  // Fetch doctors from backend
  const { data: doctors, isLoading } = useQuery({
    queryKey: ['doctors'],
    queryFn: async () => {
      const response = await apiClient.get('/doctors')
      return response.data
    },
  })

  return (
    <div className="space-y-6">
      {/* Header Actions */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium">Gestión de Doctores</h3>
          <p className="text-sm text-muted-foreground">
            Administra el equipo médico y sus horarios
          </p>
        </div>
        <button className="inline-flex items-center rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90">
          <Plus className="mr-2 h-4 w-4" />
          Nuevo Doctor
        </button>
      </div>

      {/* Doctors List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Stethoscope className="mr-2 h-5 w-5" />
            Lista de Doctores ({doctors?.length || 0})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <p className="text-sm text-muted-foreground">Cargando doctores...</p>
            </div>
          ) : doctors && doctors.length > 0 ? (
            <div className="space-y-3">
              {doctors.map((doctor) => (
                <div
                  key={doctor.id}
                  className="flex items-center justify-between rounded-lg border p-4 transition-colors hover:bg-gray-50"
                >
                  <div className="flex-1">
                    <p className="font-medium text-lg">Dr. {doctor.name}</p>
                    <div className="mt-2 flex flex-wrap gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center">
                        <Stethoscope className="mr-1.5 h-4 w-4" />
                        <span>{doctor.specialty}</span>
                      </div>
                      {doctor.sector && (
                        <div className="flex items-center">
                          <MapPin className="mr-1.5 h-4 w-4" />
                          <span>Sector {doctor.sector}</span>
                        </div>
                      )}
                      {doctor.calendar_email && (
                        <div className="flex items-center">
                          <Calendar className="mr-1.5 h-4 w-4" />
                          <span>{doctor.calendar_email}</span>
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    <span
                      className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${
                        doctor.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {doctor.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Stethoscope className="mb-4 h-12 w-12 text-muted-foreground/50" />
              <p className="text-sm text-muted-foreground">
                No hay doctores registrados
              </p>
              <p className="mt-1 text-xs text-muted-foreground">
                Los doctores aparecerán aquí cuando se registren
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
