# Environment Variables Setup

This document explains the environment variables needed for deployment.

## Required Environment Variables

Create a `.env.local` file in the `frontend/` directory with these variables:

```bash
# API Configuration
# Base URL for the backend API (must include /api/v1)
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

# WebSocket URL (for real-time evaluation progress)
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Production Configuration

For production deployment, update the values to your production URLs:

```bash
# Production API
NEXT_PUBLIC_API_URL=https://api.yourdomain.com/api/v1

# Production WebSocket (use wss:// for secure websockets)
NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com
```

## Important Notes

1. **`NEXT_PUBLIC_API_URL` must include `/api/v1`** - This is the full base path for all API calls
2. **`NEXT_PUBLIC_WS_URL` should NOT include `/api/v1`** - WebSocket paths are added separately
3. **Use `wss://` for production WebSockets** - Secure WebSocket protocol for HTTPS sites
4. **Environment variables prefixed with `NEXT_PUBLIC_` are exposed to the browser** - Don't put sensitive secrets here

## Verifying Configuration

After setting up your environment variables, you can verify they're working by:

1. Checking the API health endpoint: Visit `/api/health` in your browser
2. Opening the browser console and checking for API call URLs
3. Testing a full evaluation run to verify WebSocket connectivity

## Troubleshooting

### API Calls Failing

- Verify `NEXT_PUBLIC_API_URL` is correct and includes `/api/v1`
- Check CORS settings on your backend for the frontend domain
- Verify the backend is accessible from the frontend's network

### WebSocket Connection Failing

- Verify `NEXT_PUBLIC_WS_URL` uses `wss://` for HTTPS sites
- Check that WebSocket upgrades are allowed through any proxies/load balancers
- Ensure firewall rules allow WebSocket connections

## Development vs Production

| Environment | API URL | WS URL |
|-------------|---------|--------|
| **Local Dev** | `http://localhost:8000/api/v1` | `ws://localhost:8000` |
| **Production** | `https://api.yourdomain.com/api/v1` | `wss://api.yourdomain.com` |
| **Staging** | `https://api-staging.yourdomain.com/api/v1` | `wss://api-staging.yourdomain.com` |

