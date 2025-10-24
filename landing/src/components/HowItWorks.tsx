import { MessageCircle, ClipboardList, Calendar, CheckCircle } from "lucide-react";

const steps = [
  {
    number: 1,
    icon: MessageCircle,
    title: "Inicia la Conversación",
    description: "Haz clic en el botón de chat y saluda a nuestro asistente virtual",
  },
  {
    number: 2,
    icon: ClipboardList,
    title: "Proporciona tus Datos",
    description: "El asistente te pedirá nombre, RUT y teléfono de contacto",
  },
  {
    number: 3,
    icon: Calendar,
    title: "Elige tu Horario",
    description: "Selecciona la especialidad y el horario que más te acomode",
  },
  {
    number: 4,
    icon: CheckCircle,
    title: "Confirma tu Hora",
    description: "Recibirás confirmación por SMS y podrás acudir a tu cita",
  },
];

export function HowItWorks() {
  return (
    <section id="como-funciona" className="bg-muted/50 py-24">
      <div className="container">
        <div className="mx-auto max-w-3xl text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
            ¿Cómo Funciona?
          </h2>
          <p className="text-lg text-muted-foreground">
            Simple, rápido y disponible 24/7
          </p>
        </div>

        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          {steps.map((step) => (
            <div
              key={step.number}
              className="relative rounded-2xl bg-background p-6 shadow-sm transition-all hover:shadow-md hover:-translate-y-1"
            >
              <div className="absolute -top-4 -right-4 flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-primary to-secondary text-white font-bold">
                {step.number}
              </div>
              <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10">
                <step.icon className="h-8 w-8 text-primary" />
              </div>
              <h3 className="mb-2 text-xl font-semibold">{step.title}</h3>
              <p className="text-sm text-muted-foreground">{step.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
