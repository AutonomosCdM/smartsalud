import { Clock, AlertCircle } from "lucide-react";

const schedule = [
  { day: "Lunes a Viernes", time: "8:00 - 17:00" },
  { day: "Sábado", time: "9:00 - 13:00" },
  { day: "Domingo y Festivos", time: "Cerrado" },
];

interface ScheduleProps {
  onOpenAgent: () => void;
}

export function Schedule({ onOpenAgent }: ScheduleProps) {
  return (
    <section id="horarios" className="bg-muted/50 py-24">
      <div className="container">
        <div className="grid gap-8 lg:grid-cols-2 items-center">
          <div>
            <h2 className="text-3xl font-bold tracking-tight mb-6">
              Horarios de Atención
            </h2>

            <div className="rounded-2xl bg-background shadow-md overflow-hidden mb-6">
              {schedule.map((item, index) => (
                <div
                  key={index}
                  className={`flex items-center justify-between p-4 ${
                    index !== schedule.length - 1 ? "border-b" : ""
                  }`}
                >
                  <span className="font-semibold">{item.day}</span>
                  <span className="text-primary font-semibold">{item.time}</span>
                </div>
              ))}
            </div>

            <div className="rounded-lg border-l-4 border-primary bg-primary/10 p-4">
              <div className="flex gap-3">
                <AlertCircle className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold mb-1">Importante</p>
                  <p className="text-sm text-muted-foreground">
                    Llega 10 minutos antes de tu hora y trae tu carnet de identidad
                    y credencial de FONASA o ISAPRE.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="rounded-2xl bg-gradient-to-br from-primary to-secondary p-8 text-white text-center">
            <Clock className="h-16 w-16 mx-auto mb-4" />
            <h3 className="text-2xl font-bold mb-2">¿Necesitas agendar?</h3>
            <p className="mb-6 opacity-90">
              Nuestro asistente virtual está disponible 24/7 para ayudarte
            </p>
            <button
              onClick={onOpenAgent}
              className="rounded-lg bg-white px-6 py-3 font-semibold text-primary hover:bg-gray-100 transition-colors"
            >
              Agendar Ahora
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
