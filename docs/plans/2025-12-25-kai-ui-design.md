# KAI UI Design

**Date:** 2025-12-25
**Status:** Approved
**Author:** Claude + User

## Overview

A developer-focused admin UI for KAI that exposes all CLI functionality through a clean web interface. Built with Next.js 14, shadcn/ui, and Tailwind CSS.

### Goals

- Provide UI access to all KAI CLI commands
- Enable interactive chat with full agent transparency
- Manage database connections, schema, and MDL semantic layer
- Support developer debugging and monitoring workflows

### Target Users

Developers and Data Engineers setting up connections, scanning databases, configuring MDL, and debugging agent behavior.

---

## Codebase Structure

```
services/KAI/
├── app/                    # Existing backend (unchanged location)
│   ├── api/
│   ├── modules/
│   ├── utils/
│   └── ...
├── ui/                     # New Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js App Router
│   │   ├── components/    # Reusable UI components
│   │   ├── lib/           # API client, utilities
│   │   └── hooks/         # React hooks
│   ├── package.json
│   ├── next.config.js
│   └── tailwind.config.js
├── pyproject.toml          # Existing Python config
├── langgraph.json
└── CLAUDE.md
```

---

## Navigation Structure

```
KAI Admin
├── Dashboard              # Overview, quick stats, health checks
├── Connections            # Database connection management
├── Schema                 # Table descriptions, scanning
├── MDL                    # Semantic layer management
├── Chat                   # Interactive analysis (full agent view)
├── Knowledge              # Business glossary, instructions
└── Logs                   # Execution logs, debugging
```

---

## Page Designs

### Dashboard Page (`/`)

- Connection count with health status
- Recent executions (last 5)
- Quick actions: add connection, start chat, scan tables
- System info: KAI version, LLM config, Typesense status

---

### Connections Page (`/connections`)

**List View:**
- Table showing all connections: alias, dialect (PostgreSQL/MySQL/etc), schemas, status indicator
- Quick actions: test connection, scan, edit, delete
- "Add Connection" button opens modal

**Add/Edit Connection Modal:**
- Form fields: alias, connection URI (with show/hide toggle), schemas (multi-select or comma-separated)
- "Test Connection" button with inline success/error feedback
- URI format helper based on selected dialect

**Connection Detail View (`/connections/[id]`):**
- Connection info card with metadata
- List of schemas with table counts
- Quick links to scan, view tables, create MDL

---

### Schema Page (`/schema`)

**Table Browser:**
- Sidebar: tree view of connections → schemas → tables
- Main panel: selected table details

**Table Detail View:**
- Table name, description (editable inline)
- Columns list: name, type, nullable, AI-generated description
- "Scan with AI" button to generate/regenerate descriptions
- Scan status indicator (pending, scanning, completed)

**Bulk Operations:**
- Select multiple tables for batch scanning
- Progress indicator during AI description generation
- Filter by: connection, schema, scan status

---

### MDL Page (`/mdl`)

**Manifest List:**
- Cards or table showing all MDL manifests: name, connection, model count, version
- Quick actions: edit, export JSON, delete
- "Create Manifest" and "Build from Database" buttons

**Manifest Detail (`/mdl/[id]`):**

Three-tab layout:

**Tab 1: Models**
- List of models (tables) with column counts
- Click to expand: columns, primary key, calculated columns
- Add/remove models from manifest
- Inline editing for descriptions

**Tab 2: Relationships**
- Visual list showing: `orders` → `customers` (MANY_TO_ONE)
- Join condition displayed
- Add relationship modal: select models, join type dropdown, condition builder
- Delete relationship with confirmation

**Tab 3: Metrics**
- Business metrics list: name, base object, dimensions, measures
- Expandable to show full metric definition
- Add/edit metric form with expression builder

**Sidebar Actions:**
- Export to WrenAI JSON (download)
- Validate manifest (shows errors inline)
- Sync with database (detect schema changes)

**Visual Schema Diagram (optional enhancement):**
- ERD-style view showing models as nodes, relationships as edges
- Uses ReactFlow or similar library

---

### Chat Page (`/chat`)

**Layout:**
- Left sidebar: connection selector, session history
- Main panel: chat interface with full agent transparency

**Connection Context:**
- Dropdown to select active database connection
- Optional: select MDL manifest for semantic context
- Shows selected connection info as a pill/badge

**Chat Interface:**

**Message Input:**
- Multi-line text area at bottom
- Send button, keyboard shortcut (Cmd+Enter)
- Mode selector: full_autonomy, analysis, query, script

**Agent Response Display (mirrors CLI output):**

```
┌─ Todo List ──────────────────────────┐
│ ○ Understand the question            │
│ ➜ Query the database (in progress)   │
│ ✔ Analyze results (completed)        │
└──────────────────────────────────────┘

┌─ Reasoning ──────────────────────────┐
│ I need to find revenue by region... │
└──────────────────────────────────────┘

➜ Calling tool: execute_sql
   query: SELECT region, SUM(amount)...
   ✔ Result: [collapsible table]

┌─ Analysis / Result ──────────────────┐
│ Revenue breakdown shows...           │
│ [chart if applicable]                │
└──────────────────────────────────────┘
```

**Features:**
- Streaming tokens with live markdown rendering
- Collapsible tool call sections (expand to see input/output)
- Subagent delegation shown with indentation
- SQL results as sortable tables
- Charts rendered inline (using existing chart tools)

**Session Management:**
- Sessions persist in sidebar
- Resume previous conversations
- Clear/new session button

---

### Knowledge Page (`/knowledge`)

**Two-tab layout:**

**Tab 1: Business Glossary**
- Searchable list of glossary terms
- Each term shows: name, definition, related tables/columns
- Add/edit term modal with fields: term, definition, synonyms, linked entities
- Bulk import from CSV/JSON

**Tab 2: Instructions**
- List of SQL instructions/rules for the agent
- Each instruction: name, content preview, associated connection
- Add/edit with rich text or markdown editor
- Examples: "Always use LEFT JOIN for customer data", "Revenue = SUM(amount) - SUM(refunds)"

---

### Logs Page (`/logs`)

**Execution History:**
- Table of past agent executions: timestamp, prompt preview, status, duration
- Filter by: connection, date range, status (success/error)
- Click to expand full execution details

**Execution Detail View:**
- Original prompt
- Full agent trace: thinking, tool calls, subagents
- Collapsible sections matching chat format
- Final result/error
- Copy raw JSON for debugging

**Live View (optional):**
- Real-time stream of current executions
- Useful when running via CLI or API while monitoring in UI

---

## Technical Implementation

### Tech Stack

```
Frontend:
├── Next.js 14 (App Router)
├── React 18
├── TypeScript
├── Tailwind CSS
├── shadcn/ui components
├── TanStack Query (data fetching)
├── Zustand (lightweight state)
└── ReactFlow (optional: MDL diagram)
```

### API Client Layer

```typescript
// ui/src/lib/api/client.ts
const API_BASE = process.env.NEXT_PUBLIC_KAI_API_URL || 'http://localhost:8015';

// Typed API functions
export const connections = {
  list: () => fetch(`${API_BASE}/api/v1/database-connections`),
  create: (data) => fetch(...),
  test: (id) => fetch(...),
};

export const agent = {
  stream: (prompt, connectionId) => {
    // SSE for streaming agent responses
    return new EventSource(`${API_BASE}/api/v1/agent/stream?...`);
  },
};
```

### Key Components

| Component | Purpose |
|-----------|---------|
| `<AgentMessage>` | Renders streaming response with panels |
| `<ToolCallBlock>` | Collapsible tool input/output |
| `<TodoList>` | Live todo status display |
| `<SQLResultTable>` | Sortable data table for query results |
| `<ConnectionSelector>` | Dropdown with connection picker |
| `<MDLRelationshipEditor>` | Form for join definitions |

### Backend Changes Needed

- Add SSE streaming endpoint for agent (if not exists)
- Ensure CORS configured for `localhost:3001`
- Expose execution history via new endpoint

### Authentication

None initially - local development tool. Auth can be added later via Keycloak integration.

---

## Implementation Phases

### Phase 1: Foundation
- Project setup: Next.js, shadcn/ui, Tailwind, API client
- Layout shell: sidebar navigation, header
- Dashboard page with basic stats
- Connections CRUD (list, add, edit, delete, test)

### Phase 2: Schema & MDL
- Schema browser with table tree
- Table detail view with column editing
- AI scanning trigger and status
- MDL manifest CRUD
- Models, relationships, metrics management

### Phase 3: Interactive Chat
- Chat UI with message history
- SSE streaming integration
- Agent transparency components (todos, tool calls, reasoning)
- SQL result tables
- Session persistence

### Phase 4: Knowledge & Polish
- Business glossary CRUD
- Instructions management
- Execution logs viewer
- Error handling, loading states
- Responsive design polish

---

## File Count Estimate

```
ui/
├── src/app/           # ~10 route files
├── src/components/    # ~25 components
├── src/lib/           # ~5 utility files
├── src/hooks/         # ~5 hooks
└── config files       # ~5 files
Total: ~50 files
```

---

## API Endpoints Used

### Existing Endpoints
- `POST /api/v1/database-connections` - Create connection
- `GET /api/v1/database-connections` - List connections
- `PUT /api/v1/database-connections/{id}` - Update connection
- `DELETE /api/v1/database-connections/{id}` - Delete connection
- `GET /api/v1/table-descriptions` - List table descriptions
- `POST /api/v1/table-descriptions/scan` - Trigger AI scan
- `GET /api/v1/mdl/manifests` - List MDL manifests
- `POST /api/v1/mdl/manifests` - Create manifest
- `POST /api/v1/mdl/manifests/build` - Build from database
- `GET /api/v1/business-glossary` - List glossary terms
- `GET /api/v1/instructions` - List instructions

### New Endpoints Needed
- `GET /api/v1/agent/stream` - SSE streaming for agent execution
- `GET /api/v1/agent/sessions` - List chat sessions
- `GET /api/v1/agent/sessions/{id}` - Get session history
- `GET /api/v1/agent/executions` - Execution history for logs
- `GET /api/v1/health` - System health check

---

## Next Steps

1. Create the `ui/` directory structure
2. Initialize Next.js project with TypeScript
3. Configure shadcn/ui and Tailwind
4. Implement Phase 1 (Foundation)
