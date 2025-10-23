# Frontend Setup Guide

## Prerequisites

- Node.js 18+ (check: `node --version`)
- npm 9+ (check: `npm --version`)
- Backend API running on :8001

## Installation

```bash
# From the frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will open at: **http://localhost:3000**

## Available Scripts

```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Configuration

### Vite Proxy

The `vite.config.js` proxies API requests:

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8001',
      changeOrigin: true,
    }
  }
}
```

This means:
- Frontend calls: `fetch('/api/health')`
- Proxied to: `http://localhost:8001/api/health`

### Environment Variables

Create `.env.local` for environment-specific config:

```bash
VITE_API_URL=http://localhost:8001  # Optional, defaults to proxy
```

## Backend Requirement

The FastAPI backend MUST be running:

```bash
# From project root
PYTHONPATH=$PWD ./venv/bin/uvicorn src.api.main:app --reload --port 8001
```

Verify backend is running:
```bash
curl http://localhost:8001/health
# Should return: {"status":"healthy",...}
```

## Development Workflow

1. **Start backend** (terminal 1):
   ```bash
   cd /Users/autonomos_dev/Projects/smartSalud_V2
   PYTHONPATH=$PWD ./venv/bin/uvicorn src.api.main:app --reload --port 8001
   ```

2. **Start frontend** (terminal 2):
   ```bash
   cd /Users/autonomos_dev/Projects/smartSalud_V2/frontend
   npm run dev
   ```

3. **Open browser**: http://localhost:3000

## Project Structure

See [STRUCTURE.md](./STRUCTURE.md) for detailed architecture.

## Troubleshooting

### Port 3000 already in use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
npm run dev -- --port 3001
```

### API requests failing
1. Check backend is running: `curl http://localhost:8001/health`
2. Check proxy config in `vite.config.js`
3. Open browser DevTools → Network tab

### Module not found errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Build errors
```bash
# Check Node.js version (needs 18+)
node --version

# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

## Design Principles

1. **Minimalist**: Clean, uncluttered interface
2. **Fast**: Optimized builds, code splitting
3. **Accessible**: Radix UI primitives, keyboard navigation
4. **Responsive**: Mobile-first design
5. **Modern**: Latest React patterns, hooks

## Tech Stack Summary

| Layer | Technology |
|-------|------------|
| Framework | React 18 |
| Build Tool | Vite 5 |
| Router | React Router 6 |
| State | TanStack Query |
| HTTP | Axios |
| Styling | Tailwind CSS |
| Components | Radix UI |
| Icons | Lucide React |
| Date Utils | date-fns |

## Next Steps

1. ✅ Basic structure complete
2. ✅ Routing working
3. ✅ API client configured
4. ⏳ Implement data fetching hooks
5. ⏳ Create data tables
6. ⏳ Add forms for CRUD operations
7. ⏳ Implement authentication
8. ⏳ Add real-time updates

See [STRUCTURE.md](./STRUCTURE.md) for implementation details.
