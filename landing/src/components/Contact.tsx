import { MapPin, Phone, Mail, AlertTriangle } from "lucide-react";

const contacts = [
  {
    icon: MapPin,
    title: "Ubicación",
    content: "Av. Bernardo O'Higgins 555\nFutrono, Región de Los Ríos",
  },
  {
    icon: Phone,
    title: "Teléfono",
    content: "+56 63 248 1234",
  },
  {
    icon: Mail,
    title: "Email",
    content: "contacto@cesfamfutrono.cl",
  },
  {
    icon: AlertTriangle,
    title: "Urgencias",
    content: "SAMU: 131\nAmbulancia: 132",
  },
];

export function Contact() {
  return (
    <section id="contacto" className="py-24">
      <div className="container">
        <div className="mx-auto max-w-3xl text-center mb-16">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl mb-4">
            Contacto
          </h2>
        </div>

        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {contacts.map((contact) => (
            <div
              key={contact.title}
              className="rounded-2xl bg-card p-6 text-center shadow-sm transition-all hover:shadow-md hover:-translate-y-1"
            >
              <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-primary/10">
                <contact.icon className="h-7 w-7 text-primary" />
              </div>
              <h3 className="mb-2 text-lg font-semibold">{contact.title}</h3>
              <p className="text-sm text-muted-foreground whitespace-pre-line">
                {contact.content}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
