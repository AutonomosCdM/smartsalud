import { Activity } from "lucide-react";

interface HeaderProps {
  onOpenAgent: () => void;
}

export function Header({ onOpenAgent }: HeaderProps) {
  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="h-8 w-8 text-primary" />
          <span className="text-xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
            CESFAM
          </span>
        </div>

        <nav className="hidden md:flex gap-6">
          <a href="#inicio" className="text-sm font-medium hover:text-primary transition-colors">
            Inicio
          </a>
          <a href="#servicios" className="text-sm font-medium hover:text-primary transition-colors">
            Servicios
          </a>
          <a href="#horarios" className="text-sm font-medium hover:text-primary transition-colors">
            Horarios
          </a>
          <a href="#contacto" className="text-sm font-medium hover:text-primary transition-colors">
            Contacto
          </a>
        </nav>

        <button
          onClick={onOpenAgent}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white hover:bg-primary/90 transition-colors"
        >
          Consulta por tu Hora
        </button>
      </div>
    </header>
  );
}
