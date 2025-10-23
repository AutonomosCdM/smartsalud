# SmartSalud Admin Dashboard

Minimalist admin interface for the SmartSalud V2 medical appointment system.

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool
- **React Router** - Routing
- **TanStack Query** - Data fetching
- **Tailwind CSS** - Styling
- **Radix UI** - Accessible components
- **Lucide React** - Icons

## Getting Started

```bash
# Install dependencies
npm install

# Start dev server (runs on :3000)
npm run dev

# Build for production
npm run build
```

## Project Structure

```
src/
├── api/          # API client (Axios)
├── components/   # React components
│   ├── ui/       # Reusable UI components
│   └── layout/   # Layout components (Sidebar, Header)
├── pages/        # Page components
├── hooks/        # Custom React hooks
├── lib/          # Utility functions
└── styles/       # Global CSS
```

## API Integration

The frontend proxies API requests to the FastAPI backend running on `:8001`.

- Proxy configured in `vite.config.js`
- API client in `src/api/client.js`
- All `/api/*` requests forwarded to `http://localhost:8001/api/*`

## Design System

- **Colors**: Soft pastels, white, black with transparency
- **Components**: Radix UI primitives
- **Styling**: Tailwind utility classes
- **Layout**: Sidebar navigation with header

## Development

The backend API must be running for full functionality:

```bash
# In the project root
PYTHONPATH=$PWD ./venv/bin/uvicorn src.api.main:app --reload --port 8001
```

Then start the frontend:

```bash
cd frontend
npm run dev
```

Access the dashboard at: http://localhost:3000
