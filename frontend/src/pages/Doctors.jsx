import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card'
import { Stethoscope, Plus } from 'lucide-react'

export default function Doctors() {
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
            Lista de Doctores
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <Stethoscope className="mb-4 h-12 w-12 text-muted-foreground/50" />
            <p className="text-sm text-muted-foreground">
              No hay doctores registrados
            </p>
            <p className="mt-1 text-xs text-muted-foreground">
              Los doctores aparecerán aquí cuando se registren
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
