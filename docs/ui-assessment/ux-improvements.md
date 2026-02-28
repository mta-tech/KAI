# KAI UI - UX Research Audit

**Generated**: February 8, 2026  
**Auditor**: UX Research Specialist  
**Target Persona**: Analytic Engineers - technical users who value efficiency, keyboard workflows, and high information density

---

## Executive Summary

This UX audit identifies **12 critical user experience issues** across the KAI Admin UI, categorized by severity. The findings focus on user journey friction, information architecture gaps, and onboarding deficiencies for analytic engineers.

**Key Findings:**
- **3 Critical** issues blocking primary workflows
- **5 High** priority issues causing significant friction
- **4 Medium** priority improvements for efficiency

---

## 1. Critical Issues

### 1.1 Chat Page: Dead-End Empty State

**Location**: `/chat` page  
**Severity**: Critical  
**User Impact**: Complete workflow blockage

**Issue**:
When users navigate to the Chat page without an active session, they encounter:
```tsx
<div className="flex flex-1 items-center justify-center text-muted-foreground">
  Select or create a session to start chatting
</div>
```

**Problems**:
- No clear call-to-action (CTA) button
- No explanation of what a "session" is or why it's needed
- No visual guidance on how to proceed
- Users must discover the connection selector in the sidebar independently

**Current User Journey** (Broken):
1. User clicks "Chat" in sidebar → Lands on empty state
2. User reads unhelpful message
3. User must look around to find connection selector
4. User must figure out they need to click "New Session"

**Recommended Fix**:
Create an actionable empty state with:
- Clear "Create Session" primary CTA button
- Brief explanation of sessions and their purpose
- Visual indicator pointing to the connection selector
- Sample questions to inspire first-time users

**Suggested Code Structure**:
```tsx
<div className="flex flex-1 items-center justify-center p-8">
  <Card className="max-w-md text-center">
    <CardContent className="space-y-4 pt-6">
      <MessageSquare className="h-12 w-12 mx-auto text-muted-foreground" />
      <div>
        <h3 className="text-lg font-semibold">Start Your Analysis</h3>
        <p className="text-sm text-muted-foreground mt-2">
          Select a database connection to begin asking questions about your data
        </p>
      </div>
      <Button onClick={handleCreateSession} size="lg">
        <Plus className="mr-2 h-4 w-4" />
        Create New Session
      </Button>
      <div className="text-xs text-muted-foreground">
        Select a connection from the sidebar first
      </div>
    </CardContent>
  </Card>
</div>
```

---

### 1.2 Knowledge Base: Connection-Dependent Empty State Without Guidance

**Location**: `/knowledge` page  
**Severity**: Critical  
**User Impact**: Confusion, unclear dependencies

**Issue**:
The Knowledge page shows an empty state when no connections exist, but doesn't explain:
- Why connections are required for knowledge base
- How to create the first connection
- What the knowledge base does for analytic workflows

**Current Empty State**:
```tsx
<Card>
  <CardContent className="p-8 text-center">
    <p className="text-muted-foreground">No database connections available.</p>
    <p className="text-sm text-muted-foreground">
      Create a database connection first to manage knowledge base.
    </p>
  </CardContent>
</Card>
```

**Problems**:
- No CTA to create a connection
- No link to Connections page
- No explanation of what knowledge base provides

**Recommended Fix**:
Add actionable guidance with navigation:
```tsx
<Card>
  <CardContent className="p-8 text-center">
    <BookOpen className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
    <h3 className="text-lg font-semibold mb-2">Knowledge Base Setup Required</h3>
    <p className="text-sm text-muted-foreground mb-6">
      Define business terms and AI instructions to improve query accuracy
    </p>
    <Button asChild>
      <Link href="/connections">
        <Database className="mr-2 h-4 w-4" />
        Create Your First Connection
      </Link>
    </Button>
  </CardContent>
</Card>
```

---

### 1.3 Scan Dialog: No Progress Indication or Time Estimate

**Location**: `/connections` → Scan Dialog  
**Severity**: Critical  
**User Impact**: Uncertainty, perception of broken system

**Issue**:
When scanning a database with AI:
- No progress percentage shown
- No time estimate provided
- No indication of which tables are being processed
- Button changes to "Scanning..." but gives no feedback

**Current State**:
```tsx
<Button onClick={handleScan} disabled={isLoading}>
  {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
  {isLoading ? 'Scanning...' : 'Start Scan'}
</Button>
```

**Problems**:
- For large databases, scans can take minutes
- Users can't tell if the system is working
- No way to know how many tables remain
- No cancel option after scan starts

**Recommended Fix**:
Implement progress tracking with table count:
```tsx
// Add to scan dialog
{isLoading && (
  <div className="space-y-2">
    <div className="flex items-center justify-between text-sm">
      <span>Scanning tables...</span>
      <span className="text-muted-foreground">
        {scannedTables} / {totalTables}
      </span>
    </div>
    <Progress value={(scannedTables / totalTables) * 100} />
    <p className="text-xs text-muted-foreground">
      Estimated time remaining: {estimatedTime} minutes
    </p>
  </div>
)}
```

---

## 2. High Priority Issues

### 2.1 Session Sidebar: Unclear Session Management

**Location**: `/chat` → Session Sidebar  
**Severity**: High  
**User Impact**: Difficulty managing multiple sessions

**Issue**:
Sessions are displayed with minimal information:
- No indication of session content or topic
- No last activity timestamp
- No connection badge (which DB was used)
- Delete button only appears on hover

**Problems**:
- Can't identify sessions without clicking them
- No way to search or filter sessions
- Can't see which database connection was used
- Hard to find old sessions

**Recommended Fix**:
Enhanced session cards with metadata:
```tsx
<div className="group flex items-start justify-between rounded-md p-2 text-sm hover:bg-muted">
  <button className="flex flex-1 flex-col items-start gap-1 text-left">
    <div className="flex items-center gap-2">
      <MessageSquare className="h-4 w-4" />
      <span className="font-medium">
        {session.title || `Session ${session.id.slice(0, 8)}`}
      </span>
      <Badge variant="outline" className="text-xs">
        {session.connection_alias}
      </Badge>
    </div>
    <div className="flex items-center gap-2 text-xs text-muted-foreground">
      <Clock className="h-3 w-3" />
      {formatDistanceToNow(new Date(session.updated_at))}
    </div>
  </button>
  <Button variant="ghost" size="sm" className="opacity-0 group-hover:opacity-100">
    <Trash2 className="h-3 w-3" />
  </Button>
</div>
```

---

### 2.2 Schema Page: No Context on Empty Table Selection

**Location**: `/schema` page  
**Severity**: High  
**User Impact**: Confusion about expected content

**Issue**:
When no table is selected:
```tsx
<div className="flex h-full items-center justify-center text-muted-foreground">
  Select a table to view details
</div>
```

**Problems**:
- Doesn't explain what information will be shown
- No sample or example of table details
- Doesn't indicate which connection is currently selected

**Recommended Fix**:
```tsx
<div className="flex h-full items-center justify-center p-8">
  <Card className="max-w-sm text-center">
    <CardContent className="pt-6 space-y-4">
      <Table2 className="h-12 w-12 mx-auto text-muted-foreground" />
      <div>
        <h3 className="font-semibold">Table Details</h3>
        <p className="text-sm text-muted-foreground mt-2">
          Select a table from the sidebar to view columns, relationships, and AI-generated descriptions
        </p>
      </div>
    </CardContent>
  </Card>
</div>
```

---

### 2.3 Connection Deletion: Unsafe Confirmation Pattern

**Location**: `/connections` → Connection Table  
**Severity**: High  
**User Impact**: Risk of accidental data loss

**Issue**:
Current deletion uses browser's `confirm()` dialog:
```tsx
const handleDelete = async (id: string) => {
  if (confirm('Are you sure you want to delete this connection?')) {
    await deleteMutation.mutateAsync(id);
  }
};
```

**Problems**:
- Uses native browser confirm (poor UX)
- Doesn't show what will be affected
- No indication of cascading effects (MDL, knowledge, sessions)
- Can't undo

**Recommended Fix**:
Implement proper confirmation dialog:
```tsx
<Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Delete Connection?</DialogTitle>
      <DialogDescription>
        This will permanently delete "{connection.alias}" and cannot be undone.
      </DialogDescription>
    </DialogHeader>
    
    <Alert variant="destructive">
      <AlertTriangle className="h-4 w-4" />
      <AlertTitle>Warning</AlertTitle>
      <AlertDescription>
        This will also affect:
        <ul className="list-disc list-inside mt-2">
          <li>{manifestCount} MDL manifests</li>
          <li>{glossaryCount} glossary terms</li>
          <li>{sessionCount} chat sessions</li>
        </ul>
      </AlertDescription>
    </Alert>
    
    <DialogFooter>
      <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
        Cancel
      </Button>
      <Button variant="destructive" onClick={confirmDelete}>
        Delete Connection
      </Button>
    </DialogFooter>
  </DialogContent>
</Dialog>
```

---

### 2.4 Dashboard: Missing Quick Start for New Users

**Location**: `/` (Dashboard)  
**Severity**: High  
**User Impact**: Poor first-time experience

**Issue**:
When no connections exist, the dashboard shows:
- "Connections": 0
- No guidance on what to do first
- Quick Actions are visible but not contextual to new users

**Problems**:
- New users don't know where to start
- No explanation of the KAI workflow
- Missing onboarding for first-time setup

**Recommended Fix**:
Add first-time user welcome card:
```tsx
{connections.length === 0 && (
  <Card className="border-primary/50 bg-primary/5">
    <CardHeader>
      <CardTitle className="flex items-center gap-2">
        <Sparkles className="h-5 w-5" />
        Welcome to KAI
      </CardTitle>
    </CardHeader>
    <CardContent className="space-y-4">
      <p className="text-sm">
        Get started by connecting your database. KAI will help you analyze 
        your data using natural language queries.
      </p>
      <div className="flex gap-2">
        <Button asChild>
          <Link href="/connections">
            <Database className="mr-2 h-4 w-4" />
            Add Your First Connection
          </Link>
        </Button>
        <Button variant="outline" asChild>
          <Link href="/docs">Read Documentation</Link>
        </Button>
      </div>
    </CardContent>
  </Card>
)}
```

---

### 2.5 Scan Progress: No Visibility into Active Scans

**Location**: `/connections` page  
**Severity**: High  
**User Impact**: Uncertainty during long operations

**Issue**:
While scanning, users see:
- Badge showing "Scanning with AI..."
- No details on progress
- Scan progress banner is minimal

**Problems**:
- Can't tell if scan is stuck or progressing
- No estimated completion time
- Can't see which tables are being processed
- No option to cancel scan

**Recommended Fix**:
Enhanced progress banner with details:
```tsx
<Alert>
  <Loader2 className="h-4 w-4 animate-spin" />
  <AlertTitle>Scanning in Progress</AlertTitle>
  <AlertDescription>
    <div className="space-y-2">
      <p>
        Processing {activeScan.connectionName} ({scannedTables}/{totalTables} tables)
      </p>
      <Progress value={progressPercent} />
      <p className="text-xs text-muted-foreground">
        Current: {currentTable} • Est. {estimatedTime} remaining
      </p>
      <Button variant="outline" size="sm" onClick={cancelScan}>
        Cancel Scan
      </Button>
    </div>
  </AlertDescription>
</Alert>
```

---

## 3. Medium Priority Issues

### 3.1 Chat Input: Limited Keyboard Shortcuts Documentation

**Location**: `/chat` → Chat Input  
**Severity**: Medium  
**User Impact**: Reduced efficiency for power users

**Issue**:
Placeholder shows `(Cmd+Enter to send)` but:
- No documentation of other shortcuts
- No visible shortcuts menu
- Can't discover available shortcuts

**Recommended Fix**:
Add keyboard shortcuts help:
- Show keyboard shortcut hint in a tooltip
- Add `?` keyboard shortcut to show all shortcuts
- Display shortcuts in a modal or sidebar

---

### 3.2 MDL Page: Empty State Lacks Context

**Location**: `/mdl` page  
**Severity**: Medium  
**User Impact**: Unclear value proposition

**Issue**:
```tsx
<p className="text-muted-foreground">No MDL manifests yet.</p>
<p className="text-sm text-muted-foreground">
  Create one by building from a database connection.
</p>
```

**Problems**:
- Doesn't explain what MDL is
- No link to build MDL from a connection
- No example of MDL benefits

**Recommended Fix**:
```tsx
<Card className="text-center p-8">
  <Layers className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
  <h3 className="text-lg font-semibold mb-2">Semantic Layer Not Defined</h3>
  <p className="text-sm text-muted-foreground mb-6">
    MDL (Model Definition Language) creates a semantic layer that improves 
    AI query accuracy by defining business metrics and relationships
  </p>
  <Button asChild>
    <Link href="/connections">
      <Database className="mr-2 h-4 w-4" />
      Build MDL from Connection
    </Link>
  </Button>
</Card>
```

---

### 3.3 Connection Selection: No Visual Hierarchy in Select Dropdowns

**Location**: Multiple pages (Chat, Knowledge, Schema)  
**Severity**: Medium  
**User Impact**: Difficult to distinguish connections

**Issue**:
Connection select dropdowns show only alias/ID:
- No database type indicator
- No connection status
- No visual distinction between connections

**Recommended Fix**:
```tsx
<SelectItem value={conn.id}>
  <div className="flex items-center gap-2">
    <Database className="h-4 w-4" />
    <span>{conn.alias || conn.id.slice(0, 8)}</span>
    <Badge variant="outline" className="ml-auto">
      {conn.dialect}
    </Badge>
  </div>
</SelectItem>
```

---

### 3.4 Error Messages: Generic Error Handling

**Location**: Global error handling  
**Severity**: Medium  
**User Impact**: Can't diagnose or fix errors

**Issue**:
Error boundary and error page show generic messages:
- "This section failed to load"
- "An error occurred while loading this page"

**Problems**:
- No actionable error information
- No suggested fixes
- No way to report the error

**Recommended Fix**:
Add detailed error context:
```tsx
<Card className="m-4">
  <CardHeader>
    <CardTitle className="flex items-center gap-2 text-destructive">
      <AlertTriangle className="h-5 w-5" />
      Component Error
    </CardTitle>
  </CardHeader>
  <CardContent className="space-y-4">
    <p className="text-sm text-muted-foreground">
      This section failed to load.
    </p>
    
    {errorDetails && (
      <Collapsible>
        <CollapsibleTrigger className="text-sm">
          View Error Details
        </CollapsibleTrigger>
        <CollapsibleContent>
          <pre className="rounded bg-muted p-2 text-xs overflow-x-auto mt-2">
            {errorDetails}
          </pre>
        </CollapsibleContent>
      </Collapsible>
    )}
    
    <div className="flex gap-2">
      <Button size="sm" onClick={retry}>
        Try Again
      </Button>
      <Button size="sm" variant="outline" onClick={copyError}>
        Copy Error Report
      </Button>
    </div>
  </CardContent>
</Card>
```

---

## 4. User Journey Analysis

### 4.1 New User Onboarding Journey

**Current State** (Fragmented):
1. Land on Dashboard → No connections, no clear next step
2. Click Connections → See table with "No database connections yet"
3. Click "Add Connection" → Form with no examples
4. After creating connection → Back to table, no indication to proceed
5. Navigate to Chat → Empty state with no guidance
6. Must discover connection selector in sidebar

**Friction Points**:
- No "welcome tour" or first-time user flow
- Each page assumes user knows what to do
- No progressive disclosure of features
- Missing "quick start" wizard

**Recommended Journey**:
1. Dashboard shows welcome card with "Get Started" CTA
2. Guided connection creation with example URIs
3. Prompt to scan with AI after connection created
4. Redirect to Chat with first session auto-created
5. Show sample queries specific to their database

### 4.2 Daily Workflow Journey

**Current State**:
- Navigate to page → Select connection → Perform action
- Each page requires connection re-selection
- No persistent context across pages

**Recommended**:
- Remember last-used connection globally
- Show current connection in header
- Quick switcher in header for power users

---

## 5. Information Architecture Issues

### 5.1 Navigation Hierarchy

**Issue**: Sidebar treats all pages equally, but they have different usage patterns:
- High-frequency: Dashboard, Chat, Schema
- Medium-frequency: Connections, Knowledge
- Low-frequency: MDL, Logs (not implemented)

**Recommendation**:
- Group navigation by frequency/use case
- Add keyboard shortcuts (Cmd+1, Cmd+2, etc.)
- Collapse low-frequency sections

### 5.2 Connection Scope

**Issue**: Connection selection is per-page, not global:
- Must re-select on Chat, Knowledge, Schema pages
- No indication of current active connection
- Can't tell which connection is "primary"

**Recommendation**:
- Add global connection selector to header
- Persist connection choice across sessions
- Show connection context in all relevant pages

---

## 6. Accessibility Considerations

### 6.1 Empty State Accessibility

**Current Issues**:
- Empty states not announced to screen readers
- No ARIA labels for context
- Missing skip links for empty states

**Recommended**:
```tsx
<div role="region" aria-label="No sessions available" aria-live="polite">
  <EmptyState />
</div>
```

### 6.2 Error Accessibility

**Current Issues**:
- Error messages not consistently associated with form fields
- No `aria-describedby` linking errors to inputs
- Screen reader users may miss error context

---

## 7. Recommendations Summary

### Immediate Actions (Critical)

1. **Fix Chat page empty state** - Add actionable CTA and guidance
2. **Fix Knowledge page empty state** - Add connection creation flow
3. **Add scan progress indication** - Show table-by-table progress

### Short-term Improvements (High Priority)

4. **Enhance session cards** - Show metadata and connection info
5. **Improve schema empty state** - Add context about table details
6. **Replace confirm dialogs** - Use proper confirmation UI
7. **Add welcome card** - Guide new users on dashboard
8. **Enhance scan progress banner** - Show detailed progress

### Long-term Enhancements (Medium Priority)

9. **Document keyboard shortcuts** - Add shortcuts help modal
10. **Improve MDL empty state** - Explain value proposition
11. **Enhance connection selectors** - Show database type and status
12. **Improve error handling** - Add actionable error messages

---

## 8. Success Metrics

Track these metrics to validate UX improvements:

- **First Connection Time**: Time from sign-up to first successful connection
- **First Query Time**: Time from first connection to first chat query
- **Session Return Rate**: Percentage of users who return within 7 days
- **Empty State CTR**: Click-through rate on empty state CTAs
- **Task Completion Rate**: Percentage of users who complete key workflows

---

**Next Steps**: Coordinate with visual design and frontend architecture teams to implement recommended fixes prioritized by severity.
