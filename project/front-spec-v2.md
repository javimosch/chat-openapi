# Frontend Specification V2 - POC Phase

## Layout Structure
```
+----------------+------------------+
|                |                 |
|    Sidebar     |   Chat Area     |
|    (History)   |                 |
|                |                 |
|                |                 |
|                |                 |
+----------------+------------------+
```

## Core Components

### 1. Chat Area (Main Content)
- Centered chat container with fixed width (max-width: 800px)
- Message display area with vertical scrolling
- Simple message input at bottom
- Loading indicator during message streaming
- Context toggle button (top-right)
- Basic markdown rendering for responses
- Auto-scroll to bottom on new messages
- Visual distinction between user and assistant messages

### 2. History Sidebar (Left)
- Collapsible sidebar (toggle button for mobile)
- List of conversation threads
- Each thread shows:
  - First message preview (truncated)
  - Timestamp
  - Delete button
- New conversation button at top
- Scroll with fixed height
- Active conversation highlighted

## Functionality

### Chat Operations
1. Message Input
   - Send on Enter
   - Shift+Enter for new line
   - Basic input validation
   - Disable during response streaming

2. Message Display
   - Stream tokens into message container
   - Show typing indicator during streaming
   - Format code blocks and links
   - Support basic markdown
   - Show error messages when connection fails

3. Context Display
   - Toggle button shows/hides context panel
   - Context displayed in collapsible section
   - Basic formatting for readability

### Conversation Management
1. History Storage
   ```typescript
   interface Conversation {
     id: string;
     title: string;         // First message preview
     timestamp: number;
     messages: Message[];
     lastUpdated: number;
   }
   ```

2. LocalStorage Implementation
   - Auto-save conversations
   - Load on page refresh
   - Clear old conversations when storage limit reached
   - Export/import functionality (basic JSON)

3. Thread Operations
   - Create new thread
   - Delete thread (with confirmation)
   - Switch between threads
   - Auto-create thread on first message

## Responsive Behavior
- Mobile-first approach
- Sidebar collapses on mobile
- Touch-friendly buttons and controls
- Readable text size on all devices
- Simple transitions for UI changes

## Error Handling
- Connection loss notification
- Retry button for failed messages
- Clear error messages
- Graceful fallback for unsupported features

## Performance Considerations
- Lazy load conversation history
- Limit stored conversations
- Simple animations only
- Efficient DOM updates during streaming

## User Experience
- Clear loading states
- Simple, intuitive controls
- Consistent spacing and typography
- Minimal color palette
- Focus on readability

## Technical Implementation Notes
1. State Management
   ```javascript
   // Simple state structure
   const appState = {
     conversations: Map<string, Conversation>,
     activeConversation: string | null,
     isStreaming: boolean,
     showContext: boolean,
     connectionStatus: 'connected' | 'disconnected'
   }
   ```

2. LocalStorage Schema
   ```javascript
   // Storage key structure
   const STORAGE_KEYS = {
     CONVERSATIONS: 'openapi-chat-conversations',
     SETTINGS: 'openapi-chat-settings'
   }
   ```

3. WebSocket Events
   ```javascript
   // Event types
   const WS_EVENTS = {
     MESSAGE: 'message',
     ERROR: 'error',
     RECONNECT: 'reconnect',
     CLOSE: 'close'
   }
   ```

## Success Metrics
1. Core Functionality
   - Message sending/receiving works reliably
   - History persists across refreshes
   - Context toggle functions correctly
   - Responsive design works on mobile

2. Performance
   - Smooth message streaming
   - Quick thread switching
   - Responsive UI interactions

3. Reliability
   - No data loss on refresh
   - Graceful error handling
   - Stable WebSocket connection
