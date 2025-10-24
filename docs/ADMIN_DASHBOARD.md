# SmartSalud Admin Dashboard

Complete admin interface for managing the medical appointment system.

## Overview

- **Location**: `/frontend`
- **Tech Stack**: React 18 + Vite + Tailwind CSS + Radix UI
- **Backend API**: FastAPI on :8001
- **Frontend Dev Server**: :3000
- **Status**: ✅ Base structure complete, ready for feature implementation

---

## Quick Start

```bash
# Terminal 1: Start backend
cd /Users/autonomos_dev/Projects/smartSalud_V2
PYTHONPATH=$PWD ./venv/bin/uvicorn src.api.main:app --reload --port 8001

# Terminal 2: Start frontend
cd frontend
npm install  # First time only
npm run dev

# Open browser: http://localhost:3000
```

---

## Architecture

### Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Framework | React 18 | UI library with hooks |
| Build Tool | Vite 5 | Fast dev server + bundler |
| Router | React Router 6 | Client-side routing |
| Data Fetching | TanStack Query | Server state management |
| HTTP Client | Axios | API requests with interceptors |
| Styling | Tailwind CSS | Utility-first CSS |
| Components | Radix UI | Accessible primitives |
| Icons | Lucide React | Modern icon set |
| Date Utils | date-fns | Date formatting |

### Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── client.js           # Axios instance (proxy to :8001)
│   │
│   ├── components/
│   │   ├── ui/                 # Reusable UI components
│   │   │   └── Card.jsx        # Card with variants
│   │   │
│   │   └── layout/             # Layout components
│   │       ├── Layout.jsx      # Main wrapper (sidebar + content)
│   │       ├── Sidebar.jsx     # Navigation menu
│   │       └── Header.jsx      # Page header with title
│   │
│   ├── pages/                  # Route components
│   │   ├── Dashboard.jsx       # Stats overview
│   │   ├── Appointments.jsx    # Appointment management
│   │   ├── Patients.jsx        # Patient management
│   │   └── Doctors.jsx         # Doctor management
│   │
│   ├── hooks/                  # Custom React hooks (future)
│   ├── lib/
│   │   └── utils.js            # Utility functions (cn)
│   │
│   ├── styles/
│   │   └── globals.css         # Tailwind + CSS variables
│   │
│   ├── App.jsx                 # Root component with routes
│   └── main.jsx                # Entry point with providers
│
├── index.html
├── vite.config.js              # Vite config + API proxy
├── tailwind.config.js          # Tailwind theme
└── package.json
```

### Routing

```
/ (Layout with sidebar)
├── /dashboard           # Stats and overview
├── /appointments        # Manage appointments
├── /patients            # Manage patients
└── /doctors             # Manage doctors
```

---

## Design System

### Color Palette (Minimalist)

- **Background**: Pure white + subtle gradients
- **Foreground**: Near-black text (#0F172A)
- **Primary**: Black (actions)
- **Secondary**: Soft gray (#F1F5F9)
- **Muted**: Light gray (#64748B)
- **Accent**: Soft pastels (blue, purple, amber, green)
- **Borders**: Very light gray (#E2E8F0)

### Components

All components use:
- **Radix UI primitives** for accessibility (ARIA, keyboard nav)
- **Tailwind CSS** for styling (utility classes)
- **Lucide React** for icons (consistent 24x24 grid)
- **Glass morphism** effects (backdrop-blur + transparency)

### Layout

```
┌─────────────────────────────────────────┐
│  Sidebar (64px)  │  Header (64px)       │
│                  ├─────────────────────  │
│  Navigation      │                       │
│  - Dashboard     │  Main Content Area    │
│  - Citas         │  (scrollable)         │
│  - Pacientes     │                       │
│  - Doctores      │                       │
│                  │                       │
└─────────────────────────────────────────┘
```

---

## Implementation Status

### ✅ Completed

1. **Project Setup**
   - [x] Vite + React + Tailwind configured
   - [x] Package dependencies installed (465 packages)
   - [x] ESLint configured
   - [x] API proxy to :8001 working

2. **Layout Components**
   - [x] `Layout.jsx` - Main wrapper
   - [x] `Sidebar.jsx` - Navigation (4 routes)
   - [x] `Header.jsx` - Dynamic page titles

3. **UI Components**
   - [x] `Card.jsx` - Reusable card with variants
   - [x] Utility functions (`cn()` for class merging)

4. **Pages (Placeholder)**
   - [x] Dashboard - Stats grid + activity feed
   - [x] Appointments - Empty state with CTA
   - [x] Patients - Empty state with CTA
   - [x] Doctors - Empty state with CTA

5. **API Integration**
   - [x] Axios client with interceptors
   - [x] TanStack Query setup
   - [x] Health check query (Dashboard)

6. **Routing**
   - [x] React Router configured
   - [x] All 4 pages accessible
   - [x] Active state styling in sidebar

### ⏳ Next Steps (Priority Order)

#### Phase 1: Data Fetching (IMMEDIATE)
1. **Create API hooks** (`src/hooks/`)
   ```javascript
   // useAppointments.js
   export function useAppointments(filters) {
     return useQuery({
       queryKey: ['appointments', filters],
       queryFn: () => apiClient.get('/appointments', { params: filters })
     })
   }

   // Similar for: usePatients, useDoctors, useStats
   ```

2. **Implement Dashboard stats**
   - Fetch real data from `/api/stats` endpoint
   - Display today's appointments count
   - Show pending/confirmed counts
   - Recent activity feed

#### Phase 2: Data Tables (Week 1)
1. **Appointments Table**
   - List view with columns: Patient, Doctor, Date, Status
   - Sortable columns (date, status)
   - Filter by status (PENDING, CONFIRMED, CANCELLED)
   - Pagination (20 per page)
   - Click row to view details

2. **Patients Table**
   - Columns: Name, RUT, Phone, Email
   - Search by name/RUT
   - Click to view appointment history

3. **Doctors Table**
   - Columns: Name, Specialty, Sector, Calendar Email
   - View weekly schedule
   - Appointment count this week

#### Phase 3: CRUD Forms (Week 2)
1. **Create Appointment Form**
   - Patient selector (autocomplete)
   - Doctor selector (filtered by specialty)
   - Date/time picker (only available slots)
   - Appointment type dropdown
   - Notes textarea

2. **Create Patient Form**
   - RUT input (with validation)
   - Name, phone, email fields
   - Form validation with error messages

3. **Edit Forms**
   - Pre-populate with existing data
   - Same validation as create
   - Cancel/save actions

#### Phase 4: Real-time Features (Week 3)
1. **Auto-refresh queries**
   - Poll every 30s for new appointments
   - Optimistic updates on mutations

2. **Notifications**
   - Toast messages for success/error
   - Badge count for pending appointments

#### Phase 5: Polish (Week 4)
1. **Loading states**
   - Skeleton loaders for tables
   - Spinner for form submissions

2. **Error handling**
   - Empty states with illustrations
   - Retry buttons for failed queries

3. **Mobile responsive**
   - Collapsible sidebar
   - Touch-friendly buttons
   - Responsive tables

---

## API Endpoints (Backend)

### Current (Implemented in FastAPI)

```
GET  /health                    # Health check
GET  /api/stats                 # Dashboard stats (TODO)
GET  /api/appointments          # List appointments
POST /api/appointments          # Create appointment
GET  /api/appointments/:id      # Get appointment
PUT  /api/appointments/:id      # Update appointment
GET  /api/patients              # List patients
POST /api/patients              # Create patient
GET  /api/doctors               # List doctors
```

### Required (To Be Implemented)

```
GET  /api/appointments/available  # Get available time slots
GET  /api/doctors/:id/schedule    # Get doctor weekly schedule
GET  /api/stats/daily              # Daily statistics
```

---

## Development Workflow

### Running Both Services

```bash
# Terminal 1: Backend
cd /Users/autonomos_dev/Projects/smartSalud_V2
PYTHONPATH=$PWD ./venv/bin/uvicorn src.api.main:app --reload --port 8001

# Terminal 2: Frontend
cd frontend
npm run dev

# Access: http://localhost:3000
```

### Making API Calls

Frontend code:
```javascript
import apiClient from '@/api/client'
import { useQuery } from '@tanstack/react-query'

function MyComponent() {
  const { data, isLoading } = useQuery({
    queryKey: ['appointments'],
    queryFn: async () => {
      const res = await apiClient.get('/appointments')
      return res.data
    }
  })

  // Render data...
}
```

The proxy automatically forwards `/api/*` to `http://localhost:8001/api/*`.

### Adding New Pages

1. Create component in `src/pages/MyPage.jsx`
2. Add route in `src/App.jsx`:
   ```javascript
   <Route path="my-page" element={<MyPage />} />
   ```
3. Add navigation in `src/components/layout/Sidebar.jsx`:
   ```javascript
   { name: 'My Page', href: '/my-page', icon: MyIcon }
   ```

---

## Troubleshooting

### Frontend won't start
```bash
# Clear and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### API calls fail (CORS)
- Backend must be running on :8001
- Check proxy config in `vite.config.js`
- Verify backend allows CORS (already configured in FastAPI)

### Build errors
```bash
# Check Node version (needs 18+)
node --version

# Clear Vite cache
rm -rf frontend/node_modules/.vite
npm run dev
```

---

## File References

### Key Files

- **[frontend/src/api/client.js](../frontend/src/api/client.js)** - Axios instance
- **[frontend/src/App.jsx](../frontend/src/App.jsx)** - Routes
- **[frontend/src/components/layout/Sidebar.jsx](../frontend/src/components/layout/Sidebar.jsx)** - Navigation
- **[frontend/vite.config.js](../frontend/vite.config.js)** - Proxy config
- **[frontend/tailwind.config.js](../frontend/tailwind.config.js)** - Theme

### Documentation

- **[frontend/README.md](../frontend/README.md)** - Quick reference
- **[frontend/SETUP.md](../frontend/SETUP.md)** - Setup guide
- **[frontend/STRUCTURE.md](../frontend/STRUCTURE.md)** - Architecture details

---

## Design Inspiration

Minimalist admin dashboards:
- [21st.dev](https://21st.dev) - Clean, modern, soft colors
- [Linear](https://linear.app) - Keyboard-first, fast
- [Vercel Dashboard](https://vercel.com) - Simple, elegant

Key principles:
- **Less is more** - No unnecessary elements
- **Fast by default** - Optimize bundle, lazy load
- **Accessible** - Keyboard nav, ARIA, semantic HTML
- **Professional** - Clean typography, consistent spacing

---

## Summary

### What We Built
✅ Complete frontend structure with:
- Modern React 18 setup with Vite
- Clean routing (4 pages)
- Minimalist design system
- API integration layer ready
- All dependencies installed (465 packages)

### What's Next
⏳ Implement features in this order:
1. API hooks for data fetching
2. Tables for appointments/patients/doctors
3. Forms for CRUD operations
4. Real-time updates
5. Mobile responsive polish

### Time to First Feature
- **API hooks**: ~2 hours
- **First table**: ~4 hours
- **First form**: ~6 hours
- **Complete CRUD**: ~2 days

Ready to build! 🚀
