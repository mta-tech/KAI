# KAI Web UI

A modern Next.js-based web interface for interacting with the KAI (Knowledge Agent for Intelligence Query) backend.

## Overview

The KAI Web UI provides an intuitive interface for:
- **Interactive Chat** - Natural language conversations with your data
- **Dashboard Management** - Create and view data dashboards
- **SQL Query Interface** - Execute and visualize database queries
- **Analytics** - View statistical analysis and forecasts
- **Configuration** - Manage database connections and settings

## Tech Stack

- **Framework**: [Next.js 15](https://nextjs.org/) (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **API Client**: Fetch API / Axios
- **State Management**: React Context / Zustand (if applicable)

## Getting Started

### Prerequisites

- **Node.js**: 18.x or higher ([Download](https://nodejs.org/))
- **npm**, **yarn**, **pnpm**, or **bun**
- **KAI Backend**: Running at http://localhost:8015

### Installation

1. **Navigate to the UI directory**

   ```bash
   cd ui
   ```

2. **Install dependencies**

   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

3. **Configure environment variables**

   Create a `.env.local` file:

   ```bash
   # API Configuration
   NEXT_PUBLIC_API_URL=http://localhost:8015
   NEXT_PUBLIC_API_BASE_PATH=/api/v1

   # Optional: Authentication
   NEXT_PUBLIC_AUTH_ENABLED=false
   ```

4. **Run the development server**

   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   ```

5. **Open your browser**

   Navigate to [http://localhost:3000](http://localhost:3000)

## Project Structure

```
ui/
├── app/                    # Next.js app router
│   ├── (dashboard)/       # Dashboard routes
│   ├── (auth)/            # Authentication routes
│   ├── api/               # API route handlers
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── components/            # React components
│   ├── ui/               # shadcn/ui components
│   ├── chat/             # Chat interface
│   ├── dashboard/        # Dashboard components
│   └── shared/           # Shared components
├── lib/                   # Utility functions
│   ├── api.ts            # API client
│   ├── utils.ts          # Helper functions
│   └── hooks/            # Custom React hooks
├── types/                 # TypeScript type definitions
├── public/                # Static assets
└── styles/                # Global styles
```

## Available Scripts

```bash
# Development
npm run dev          # Start dev server
npm run build        # Build for production
npm run start        # Start production server

# Code Quality
npm run lint         # Run ESLint
npm run type-check   # TypeScript type checking
npm run format       # Format with Prettier

# Testing (if configured)
npm run test         # Run tests
npm run test:watch   # Watch mode
```

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | KAI backend URL | `http://localhost:8015` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_BASE_PATH` | API base path | `/api/v1` |
| `NEXT_PUBLIC_AUTH_ENABLED` | Enable authentication | `false` |
| `NEXT_PUBLIC_ANALYTICS_ID` | Analytics tracking ID | - |

## Features

### Chat Interface

Interactive conversational interface for natural language queries:

```typescript
// Example API call
const response = await fetch(`${API_URL}/sessions`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    db_alias: 'my_database',
    user_id: 'user123'
  })
});
```

### Dashboard Builder

Create dashboards from natural language descriptions:

```typescript
const dashboard = await createDashboard({
  name: 'Sales Overview',
  description: 'Show total revenue, top products, and trends',
  db_alias: 'sales_db'
});
```

### SQL Query Interface

Execute and visualize SQL queries:

```typescript
const result = await executeSql({
  prompt: 'Show top 10 customers by revenue',
  db_alias: 'crm_db'
});
```

## Development Guidelines

### Code Style

- **TypeScript**: Use strict mode, avoid `any`
- **Components**: Functional components with hooks
- **File naming**: kebab-case for files, PascalCase for components
- **Imports**: Organize with absolute imports (`@/components/...`)

### Component Example

```typescript
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { useApi } from '@/lib/hooks/useApi';

interface ChatProps {
  sessionId: string;
  onMessageSent?: (message: string) => void;
}

export function ChatInterface({ sessionId, onMessageSent }: ChatProps) {
  const [message, setMessage] = useState('');
  const { post, loading } = useApi();

  const handleSend = async () => {
    if (!message.trim()) return;

    await post(`/sessions/${sessionId}/messages`, {
      content: message
    });

    onMessageSent?.(message);
    setMessage('');
  };

  return (
    <div className="flex flex-col gap-4">
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Ask a question..."
        className="w-full p-2 border rounded"
      />
      <Button onClick={handleSend} disabled={loading}>
        {loading ? 'Sending...' : 'Send'}
      </Button>
    </div>
  );
}
```

### API Integration

Use the centralized API client:

```typescript
// lib/api.ts
export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`);
    if (!response.ok) throw new Error('API Error');
    return response.json();
  }

  async post<T>(endpoint: string, data: unknown): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('API Error');
    return response.json();
  }
}

export const api = new ApiClient(
  process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8015'
);
```

## Deployment

### Vercel (Recommended)

1. **Connect your repository** to Vercel
2. **Set environment variables** in Vercel dashboard
3. **Deploy** - automatic on git push

### Docker

```bash
# Build
docker build -t kai-ui .

# Run
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://api:8015 \
  kai-ui
```

### Manual Build

```bash
npm run build
npm run start
```

## Troubleshooting

### Common Issues

**1. API Connection Failed**

```bash
# Check backend is running
curl http://localhost:8015/health

# Verify NEXT_PUBLIC_API_URL in .env.local
```

**2. Build Errors**

```bash
# Clear cache
rm -rf .next
npm run build
```

**3. Port Already in Use**

```bash
# Use different port
PORT=3001 npm run dev
```

### Development Tips

- **Hot Reload**: Changes auto-refresh in dev mode
- **Type Safety**: Run `npm run type-check` before committing
- **API Inspection**: Use browser DevTools Network tab
- **Component Testing**: Use React DevTools extension

## Contributing

See the main [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

### UI-Specific Guidelines

1. **Use shadcn/ui components** for consistency
2. **Follow responsive design** principles
3. **Test on multiple browsers** (Chrome, Firefox, Safari)
4. **Accessibility**: Use semantic HTML and ARIA labels
5. **Performance**: Lazy load heavy components

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com/)
- [KAI API Documentation](../docs/apis/README.md)

---

**Need Help?** Open an issue or check the [main README](../README.md)
