# Frontend - Agente CESFAM

Aplicación web Next.js para el agente conversacional CESFAM.

## 🚀 Quick Start

```bash
# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run dev

# Build para producción
npm run build

# Ejecutar en producción
npm start
```

## 📦 Dependencias Principales

- **Next.js 14** - Framework React
- **Tailwind CSS** - Estilos utility-first
- **TypeScript** - Type safety
- **Lucide React** - Iconos
- **ElevenLabs React** - Componentes de voz

## 🎨 Componentes UI de ElevenLabs

Este proyecto está preparado para usar los componentes UI de ElevenLabs.

### Instalar Componentes

```bash
# Instalar todos los componentes
npm run components:add all

# Instalar componente específico
npm run components:add <component-name>
```

Componentes disponibles:
- Orb de voz
- Waveforms
- Audio players
- Voice agents

Ver más en: [https://ui.elevenlabs.io](https://ui.elevenlabs.io)

## 🔧 Configuración

### Variables de Entorno

Crea un archivo `.env.local` en la carpeta `frontend`:

```env
NEXT_PUBLIC_ELEVENLABS_API_KEY=sk_dcb9b49e02f97490dae332c287a31847519896a2a462bf27
NEXT_PUBLIC_AGENT_ID=your_agent_id_here  # Opcional
```

## 📁 Estructura

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx        # Layout principal
│   │   ├── page.tsx          # Página home
│   │   └── globals.css       # Estilos globales
│   └── components/
│       ├── VoiceAgent.tsx    # Componente del agente de voz
│       ├── Header.tsx        # Header del sitio
│       ├── Hero.tsx          # Sección hero
│       ├── HowItWorks.tsx    # Cómo funciona
│       ├── Services.tsx      # Servicios
│       ├── Schedule.tsx      # Horarios
│       ├── Contact.tsx       # Contacto
│       └── Footer.tsx        # Footer
├── public/                   # Archivos estáticos
├── tailwind.config.ts        # Config Tailwind
└── package.json
```

## 🎨 Personalización

### Colores

Edita los colores en `src/app/globals.css`:

```css
:root {
  --primary: 210 100% 50%;      /* Azul CESFAM */
  --secondary: 151 100% 33%;    /* Verde */
  /* ... más colores */
}
```

### Componentes

Todos los componentes están en `src/components/`. Edítalos para cambiar el contenido.

## 🚀 Deploy

### Vercel (Recomendado)

```bash
# Instalar Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Netlify

```bash
# Build
npm run build

# Deploy la carpeta .next
```

### Otros Hosting

1. Build: `npm run build`
2. Sube la carpeta `.next` y `public`
3. Configura las variables de entorno

## 📖 Documentación

- [Next.js Docs](https://nextjs.org/docs)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [ElevenLabs UI](https://ui.elevenlabs.io)
