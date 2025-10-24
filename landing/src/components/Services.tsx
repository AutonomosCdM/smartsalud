import { Stethoscope, HeartPulse, Baby, Apple, Activity, Brain, Smile, Users } from "lucide-react";

const services = [
  {
    icon: Stethoscope,
    title: "Medicina General",
    description: "Consultas médicas, controles de enfermedades crónicas y atención preventiva",
  },
  {
    icon: HeartPulse,
    title: "Enfermería",
    description: "Curaciones, inyectables, control de signos vitales y educación en salud",
  },
  {
    icon: Baby,
    title: "Matrona",
    description: "Control prenatal, posparto, planificación familiar y salud de la mujer",
  },
  {
    icon: Smile,
    title: "Odontología",
    description: "Atención dental preventiva, tratamientos básicos y urgencias dentales",
  },
  {
    icon: Apple,
    title: "Nutrición",
    description: "Control nutricional, educación alimentaria y programas de salud",
  },
  {
    icon: Activity,
    title: "Kinesiología",
    description: "Rehabilitación física, ejercicios terapéuticos y programa adulto mayor",
  },
  {
    icon: Brain,
    title: "Salud Mental",
    description: "Atención psicológica y psiquiátrica, apoyo emocional y terapia",
  },
  {
    icon: Users,
    title: "Trabajo Social",
    description: "Orientación sobre beneficios, apoyo en trámites y derivaciones",
  },
];

export function Services() {
  return (
    <section id="servicios" className="py-24">
      <div className="container">
        <div className="mx-auto max-w-3xl text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
            Nuestros Servicios
          </h2>
          <p className="text-lg text-muted-foreground">
            Atención integral para toda la familia
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {services.map((service) => (
            <div
              key={service.title}
              className="rounded-2xl bg-card p-6 shadow-sm transition-all hover:shadow-md hover:-translate-y-1"
            >
              <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-primary/10">
                <service.icon className="h-7 w-7 text-primary" />
              </div>
              <h3 className="mb-2 text-lg font-semibold">{service.title}</h3>
              <p className="text-sm text-muted-foreground">{service.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
