import { useQuery } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Users, Plus, Mail, Phone, CreditCard } from 'lucide-react'
import apiClient from '@/api/client'

export default function Patients() {
  // Fetch patients from backend
  const { data: patients, isLoading } = useQuery({
    queryKey: ['patients'],
    queryFn: async () => {
      const response = await apiClient.get('/patients')
      return response.data
    },
  })

  return (
    <div className="space-y-6">
      {/* Header Actions */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium">Gestión de Pacientes</h3>
          <p className="text-sm text-muted-foreground">
            Administra la base de datos de pacientes
          </p>
        </div>
        <button className="inline-flex items-center rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/90">
          <Plus className="mr-2 h-4 w-4" />
          Nuevo Paciente
        </button>
      </div>

      {/* Patients List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Users className="mr-2 h-5 w-5" />
            Lista de Pacientes ({patients?.length || 0})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <p className="text-sm text-muted-foreground">Cargando pacientes...</p>
            </div>
          ) : patients && patients.length > 0 ? (
            <div className="space-y-3">
              {patients.map((patient) => (
                <div
                  key={patient.id}
                  className="flex items-center justify-between rounded-lg border p-4 transition-colors hover:bg-gray-50"
                >
                  <div className="flex-1">
                    <p className="font-medium text-lg">
                      {patient.first_name} {patient.last_name}
                    </p>
                    <div className="mt-2 flex flex-wrap gap-4 text-sm text-muted-foreground">
                      <div className="flex items-center">
                        <CreditCard className="mr-1.5 h-4 w-4" />
                        <span>{patient.rut}</span>
                      </div>
                      {patient.phone && (
                        <div className="flex items-center">
                          <Phone className="mr-1.5 h-4 w-4" />
                          <span>{patient.phone}</span>
                        </div>
                      )}
                      {patient.email && (
                        <div className="flex items-center">
                          <Mail className="mr-1.5 h-4 w-4" />
                          <span>{patient.email}</span>
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="text-right text-xs text-muted-foreground">
                    Registrado: {new Date(patient.created_at).toLocaleDateString('es-CL')}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Users className="mb-4 h-12 w-12 text-muted-foreground/50" />
              <p className="text-sm text-muted-foreground">
                No hay pacientes registrados
              </p>
              <p className="mt-1 text-xs text-muted-foreground">
                Los pacientes aparecerán aquí cuando se registren
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
