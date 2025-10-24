import { Calendar, ArrowRight } from "lucide-react";

interface HeroProps {
  onOpenAgent: () => void;
}

export function Hero({ onOpenAgent }: HeroProps) {
  return (
    <section id="inicio" className="container py-24 md:py-32">
      <div className="grid gap-8 lg:grid-cols-2 lg:gap-12 items-center">
        <div className="flex flex-col gap-6">
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
            Agenda tu Hora Médica{" "}
            <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              de Forma Fácil y Rápida
            </span>
          </h1>
          <p className="text-lg text-muted-foreground">
            Nuestro asistente virtual está disponible para ayudarte a agendar tu
            hora médica en el CESFAM. Servicio rápido, amable y disponible cuando
            lo necesites.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <button
              onClick={onOpenAgent}
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-6 py-3 text-base font-semibold text-white hover:bg-primary/90 transition-colors"
            >
              <Calendar className="h-5 w-5" />
              Consulta por tu Hora
            </button>
            <a
              href="#como-funciona"
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-primary px-6 py-3 text-base font-semibold text-primary hover:bg-primary/10 transition-colors"
            >
              Cómo Funciona
              <ArrowRight className="h-5 w-5" />
            </a>
          </div>
        </div>

        <div className="relative">
          <div className="rounded-2xl bg-gradient-to-br from-primary/10 to-secondary/10 p-8 text-center">
            <div className="mx-auto mb-4 flex h-24 w-24 items-center justify-center rounded-full bg-gradient-to-br from-primary to-secondary">
              <Calendar className="h-12 w-12 text-white" />
            </div>
            <h3 className="mb-2 text-2xl font-bold">Atención Personalizada</h3>
            <p className="text-muted-foreground">
              Asistente virtual entrenado para entregarte la mejor experiencia
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
