# Getting Started with KAI

**KAI (Knowledge Agent for Intelligence Query)** is an AI-powered database intelligence and analysis tool designed for analytic engineers. Query your database using natural language, discover insights, and export results with ease.

---

## What is KAI?

KAI transforms how you interact with databases:

- **Natural Language Queries** - Ask questions in plain English, KAI writes the SQL
- **Intelligent Analysis** - Get insights, patterns, and trends automatically
- **Knowledge Base** - Build a reusable library of queries and domain knowledge
- **Multi-Database Support** - PostgreSQL, MySQL, Snowflake, and more
- **Export & Visualize** - Send results to your favorite tools

**Target Users:** Analytic engineers, data analysts, and developers who prefer keyboard-driven workflows and information-dense interfaces.

---

## Prerequisites

Before you begin, ensure you have:

1. **Database Connection**
   - Connection string or credentials for your database
   - Supported: PostgreSQL, MySQL, Snowflake, SQL Server, Oracle
   - Network access from KAI to your database

2. **LLM API Key** (Choose One)
   - **OpenAI**: `OPENAI_API_KEY` - Best for complex queries
   - **Google Gemini**: `GOOGLE_API_KEY` - Cost-effective alternative
   - **Ollama**: For local, private LLM inference (no API key needed)
   - **OpenRouter**: Access to multiple LLM providers

3. **Modern Web Browser**
   - Chrome/Edge 90+, Firefox 88+, Safari 14+
   - JavaScript enabled

---

## Quick Start (5 Minutes)

### Step 1: Access KAI

Open your web browser and navigate to your KAI instance:
- **Local Development**: `http://localhost:8015`
- **Production**: Contact your administrator for the URL

### Step 2: Connect Your Database

1. Click **Settings** in the sidebar
2. Navigate to **Connections**
3. Click **Add Connection**
4. Enter your database credentials:
   ```
   Name: My Database
   Connection String: postgresql://user:password@host:5432/database
   ```
5. Click **Test Connection**
6. Click **Save**

### Step 3: Configure LLM

1. In Settings, navigate to **LLM Configuration**
2. Select your provider (OpenAI, Google, or Ollama)
3. Enter your API key
4. Choose a model:
   - **OpenAI**: `gpt-4o-mini` (fast, cost-effective)
   - **Google**: `gemini-2.0-flash` (fast, cost-effective)
   - **Ollama**: `llama3.2` (local, private)
5. Click **Save**

### Step 4: Start Your First Chat

1. Click **Chat** in the sidebar
2. Click **New Chat**
3. Type a natural language query:
   ```
   What are the top 10 products by revenue?
   ```
4. Press **Enter** or click **Send**
5. KAI generates SQL, executes it, and displays results

### Step 5: Explore Results

- **View SQL**: Click the SQL tab to see the generated query
- **Export**: Click **Export** to download as CSV, JSON, or Excel
- **Visualize**: Click **Visualize** to create charts
- **Save Query**: Click **Save** to add to your knowledge base

---

## Next Steps

Congratulations! You've completed your first query. Here's what to do next:

### [ ] Set Up Keyboard Shortcuts

Press `?` anytime to see all available shortcuts. Power users navigate KAI entirely by keyboard.

**Essential Shortcuts:**
- `Cmd/Ctrl + K` - Open command palette
- `?` - Show keyboard shortcuts
- `Cmd/Ctrl + N` - New chat

### [ ] Create a Knowledge Base Entry

Save useful queries and domain knowledge:

1. Run a query you want to reuse
2. Click **Save to Knowledge Base**
3. Add a description and tags
4. Access anytime from the **Knowledge Base** section

### [ ] Browse Your Database

Explore your schema:

1. Click **Data** in the sidebar
2. Select **Tables**
3. Browse table names, columns, and relationships
4. Use AI descriptions to understand unfamiliar tables

### [ ] Configure Your Preferences

Customize KAI to your workflow:

1. Click **Settings**
2. **Theme**: Choose light, dark, or system theme
3. **Language**: Select English or Indonesian
4. **Editor**: Adjust SQL editor preferences

---

## Key Concepts

### Chat Sessions

Chat sessions are conversational query experiences. KAI maintains context across messages, allowing follow-up questions and refinements.

**Example:**
```
You: Show me sales by region
KAI: [Displays results]
You: Just for North America
KAI: [Filters and updates results]
You: Group by state
KAI: [Groups results by state]
```

### Knowledge Base

The Knowledge Base stores:
- **Queries**: Reusable SQL queries with descriptions
- **Glossaries**: Domain-specific terminology (e.g., "MRR" = "Monthly Recurring Revenue")
- **Skills**: Pre-built analysis patterns (e.g., "Cohort Analysis")

**Benefits:**
- Share knowledge with your team
- Standardize query patterns
- Onboard new team members faster

### Data Explorer

Browse your database schema without writing SQL:
- View all tables and columns
- See AI-generated descriptions
- Understand relationships
- Preview sample data

---

## Common Tasks

### Run a Saved Query

1. Click **Knowledge Base**
2. Browse or search for your query
3. Click to open
4. Review parameters
5. Click **Run Query**

### Export Results

After running a query:
1. Click the **Export** button
2. Choose format:
   - **CSV** - For Excel, Google Sheets
   - **JSON** - For applications, APIs
   - **Excel** - With formatting
3. File downloads automatically

### Share a Query

1. Save query to Knowledge Base
2. Click **Share**
3. Copy link or invite team members
4. Recipients can view and run the query

---

## Troubleshooting

### "Connection Failed" Error

**Check:**
- Database is accessible from your network
- Credentials are correct
- Database allows connections from KAI's IP address
- Firewall rules permit traffic

**Solution:** Contact your database administrator to whitelist KAI's IP.

### "API Key Invalid" Error

**Check:**
- API key is correct
- API key has sufficient credits/quota
- API key is enabled for the selected model

**Solution:** Regenerate API key from your LLM provider's dashboard.

### "Query Timed Out" Error

**Check:**
- Query isn't scanning too much data
- Database has sufficient resources
- Network connection is stable

**Solution:** Add filters to reduce data size, or contact your DBA about database performance.

---

## Getting Help

### Keyboard Shortcuts

Press `?` anywhere in KAI to see all available shortcuts.

### Documentation

- **Component Library**: [Storybook Documentation](http://localhost:6006)
- **API Reference**: `/docs/apis/`
- **Deployment Guide**: `/docs/deployment/`

### Support

- **GitHub Issues**: Report bugs and request features
- **Discord/Slack**: Join the community (link from administrator)
- **Email**: Contact your KAI administrator

---

## Keyboard Shortcuts Reference

### Global
| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + K` | Open command palette |
| `?` | Show keyboard shortcuts |
| `Cmd/Ctrl + /` | Focus search |

### Chat
| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + N` | New chat |
| `Enter` | Send message |
| `Shift + Enter` | New line in message |

### Navigation
| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + 1` | Go to Chat |
| `Cmd/Ctrl + 2` | Go to Knowledge Base |
| `Cmd/Ctrl + 3` | Go to Data |

---

## What's Next?

- [ ] Complete the [Chat Tutorial](chat/natural-language-queries.md)
- [ ] Learn about [Knowledge Base Management](knowledge-base/creating-entries.md)
- [ ] Explore [Advanced Data Analysis](data/browsing-tables.md)
- [ ] Customize your [Settings](settings/theme-preferences.md)

---

**Welcome to KAI! Happy querying!** 🚀
