import { Activity } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t bg-muted/50">
      <div className="container py-12">
        <div className="grid gap-8 md:grid-cols-3">
          <div>
            <div className="flex items-center gap-2 mb-4">
              <Activity className="h-6 w-6 text-primary" />
              <span className="text-lg font-bold">CESFAM</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Centro de Salud Familiar<br />
              Atención integral para toda la comunidad
            </p>
          </div>

          <div>
            <h4 className="font-semibold mb-4">Enlaces Útiles</h4>
            <div className="flex flex-col gap-2">
              <a
                href="https://www.fonasa.cl"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-muted-foreground hover:text-primary transition-colors"
              >
                FONASA
              </a>
              <a
                href="https://www.minsal.cl"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-muted-foreground hover:text-primary transition-colors"
              >
                MINSAL
              </a>
              <a
                href="#servicios"
                className="text-sm text-muted-foreground hover:text-primary transition-colors"
              >
                Servicios
              </a>
              <a
                href="#contacto"
                className="text-sm text-muted-foreground hover:text-primary transition-colors"
              >
                Contacto
              </a>
            </div>
          </div>

          <div>
            <h4 className="font-semibold mb-4">Síguenos</h4>
            <div className="flex gap-4">
              <a
                href="#"
                className="text-2xl hover:scale-110 transition-transform"
                aria-label="Facebook"
              >
                📘
              </a>
              <a
                href="#"
                className="text-2xl hover:scale-110 transition-transform"
                aria-label="Instagram"
              >
                📷
              </a>
              <a
                href="#"
                className="text-2xl hover:scale-110 transition-transform"
                aria-label="Twitter"
              >
                🐦
              </a>
            </div>
          </div>
        </div>

        <div className="mt-8 border-t pt-8 text-center text-sm text-muted-foreground">
          <p>&copy; 2025 CESFAM. Todos los derechos reservados.</p>
          <p className="mt-1">
            Powered by{" "}
            <a
              href="https://elevenlabs.io"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              ElevenLabs AI
            </a>
          </p>
        </div>
      </div>
    </footer>
  );
}
