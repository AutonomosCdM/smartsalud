# Frontend Structure

## Directory Layout

```
frontend/
├── public/                      # Static assets
├── src/
│   ├── api/                     # API integration layer
│   │   └── client.js            # Axios instance with interceptors
│   │
│   ├── components/
│   │   ├── ui/                  # Reusable UI components
│   │   │   └── Card.jsx         # Card component with variants
│   │   │
│   │   └── layout/              # Layout components
│   │       ├── Layout.jsx       # Main layout wrapper
│   │       ├── Sidebar.jsx      # Navigation sidebar
│   │       └── Header.jsx       # Page header with title
│   │
│   ├── pages/                   # Page components (routes)
│   │   ├── Dashboard.jsx        # Main dashboard with stats
│   │   ├── Appointments.jsx     # Appointments management
│   │   ├── Patients.jsx         # Patients management
│   │   └── Doctors.jsx          # Doctors management
│   │
│   ├── hooks/                   # Custom React hooks
│   │   └── (future)             # useAppointments, usePatients, etc.
│   │
│   ├── lib/                     # Utilities
│   │   └── utils.js             # cn() for class merging
│   │
│   ├── styles/
│   │   └── globals.css          # Tailwind + custom CSS variables
│   │
│   ├── App.jsx                  # Root component with routes
│   └── main.jsx                 # Entry point with providers
│
├── index.html                   # HTML template
├── package.json                 # Dependencies
├── vite.config.js               # Vite configuration + proxy
├── tailwind.config.js           # Tailwind theme
├── postcss.config.js            # PostCSS plugins
└── .eslintrc.cjs                # ESLint rules
```

## Routing Structure

```
/ (Layout)
├── /dashboard           → Dashboard.jsx
├── /appointments        → Appointments.jsx
├── /patients            → Patients.jsx
└── /doctors             → Doctors.jsx
```

## Component Hierarchy

```
App
└── BrowserRouter
    └── QueryClientProvider
        └── Routes
            └── Layout
                ├── Sidebar (navigation)
                ├── Header (page title)
                └── Outlet (page content)
                    ├── Dashboard
                    ├── Appointments
                    ├── Patients
                    └── Doctors
```

## Data Flow

```
Component
    ↓
useQuery (TanStack Query)
    ↓
apiClient (Axios)
    ↓
Vite Proxy (/api → :8001)
    ↓
FastAPI Backend
```

## Design System

### Colors (CSS Variables)
- `--background`: Page background
- `--foreground`: Text color
- `--primary`: Main action color
- `--secondary`: Secondary elements
- `--muted`: Subtle backgrounds
- `--accent`: Highlights
- `--border`: Borders
- `--destructive`: Error/delete actions

### Components
- Built with Radix UI primitives (accessible)
- Styled with Tailwind CSS
- Icons from Lucide React

### Layout
- Sidebar: 256px fixed width
- Header: 64px fixed height
- Content: Scrollable main area
- Responsive grid for cards/stats

## Next Steps

1. **Implement API hooks** in `src/hooks/`:
   - `useAppointments()`
   - `usePatients()`
   - `useDoctors()`
   - `useStats()`

2. **Create data tables** in pages:
   - Sortable columns
   - Filters
   - Pagination

3. **Add forms** for CRUD:
   - Create appointment
   - Edit patient
   - Manage doctor schedules

4. **Implement real-time updates**:
   - WebSocket for notifications
   - Auto-refresh queries

5. **Add authentication**:
   - Login page
   - Protected routes
   - User context
