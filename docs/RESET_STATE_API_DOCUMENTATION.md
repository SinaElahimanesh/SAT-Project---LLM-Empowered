# Reset State Machine API Documentation

## Overview
The Reset State Machine API allows you to reset a user's conversation state back to the initial state and start a new session. This creates a fresh conversation session while preserving the chat history from previous sessions.

## API Endpoints

### 1. Reset State Machine
**POST** `/api/reset-state/`

### 2. Get Chat History (Session-based)
**GET** `/api/chat-history/?session_id=<session_id>`

### 3. Get User Sessions
**GET** `/api/user-sessions/`

### Authentication
All endpoints require authentication. Include the JWT access token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

### Request/Response Details

#### Reset State Machine
**Request:**
- **Method**: POST
- **Content-Type**: application/json
- **Body**: Empty (no body required)

**Response (200 OK):**
```json
{
    "message": "State machine reset successfully",
    "new_state": "GREETING_FORMALITY_NAME",
    "message_count": 0,
    "emotion": null,
    "response": null,
    "stage": "Beginning",
    "current_day": 1,
    "session_id": 3
}
```

#### Get Chat History
**Request:**
- **Method**: GET
- **URL**: `/api/chat-history/?session_id=2` (optional parameter)
- If no session_id provided, returns current session messages

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "text": "سلام",
        "timestamp": "2024-01-15T10:30:00Z",
        "session_id": 2,
        "is_user": true
    },
    {
        "id": 2,
        "text": "سلام! چطور هستید؟",
        "timestamp": "2024-01-15T10:30:05Z",
        "session_id": 2,
        "is_user": false
    }
]
```

#### Get User Sessions
**Request:**
- **Method**: GET
- **URL**: `/api/user-sessions/`

**Response (200 OK):**
```json
{
    "sessions": [1, 2, 3],
    "total_sessions": 3
}
```

## What Gets Reset

When you call the reset API, the following happens:

1. **New Session Created**: A new session ID is generated
2. **State Reset**: Reset to `"GREETING_FORMALITY_NAME"` (initial state)
3. **Message Count**: Reset to `0` (counts only current session messages)
4. **Emotion**: Reset to `null`
5. **Response**: Reset to `null`
6. **Exercises Done**: Reset to empty set
7. **Repetition Prevention**: Cleared for the user
8. **Memory Preserved**: Previous session history is preserved but not used in new session

## Session-Based Architecture

### Key Features:
- **Session Isolation**: Each reset creates a new session with unique ID
- **History Preservation**: Previous sessions remain accessible
- **Message Counting**: Only counts messages in current session
- **Memory Context**: Uses only current session messages for context

### Session Flow:
1. User starts conversation → Session 1
2. User resets → Session 2 (new session ID)
3. Previous Session 1 history preserved
4. New conversation starts fresh in Session 2

## Frontend Implementation Examples

### JavaScript/React Example
```javascript
const resetStateMachine = async () => {
    try {
        const response = await fetch('/api/reset-state/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            },
        });

        if (response.ok) {
            const data = await response.json();
            console.log('State machine reset successfully:', data);
            
            // Update your frontend state
            setCurrentState(data.new_state);
            setMessageCount(data.message_count);
            setUserEmotion(data.emotion);
            setUserStage(data.stage);
            setCurrentDay(data.current_day);
            setCurrentSessionId(data.session_id);
            
            // Clear chat history in UI (but preserve in backend)
            setChatHistory([]);
            
            // Show success message
            alert('New conversation session started!');
        } else {
            const errorData = await response.json();
            console.error('Failed to reset state:', errorData);
            alert('Failed to start new session');
        }
    } catch (error) {
        console.error('Error resetting state:', error);
        alert('Error starting new session');
    }
};

// Get chat history for specific session
const getSessionHistory = async (sessionId) => {
    try {
        const response = await fetch(`/api/chat-history/?session_id=${sessionId}`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            },
        });

        if (response.ok) {
            const messages = await response.json();
            return messages;
        }
    } catch (error) {
        console.error('Error fetching session history:', error);
    }
};

// Get all user sessions
const getUserSessions = async () => {
    try {
        const response = await fetch('/api/user-sessions/', {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            },
        });

        if (response.ok) {
            const data = await response.json();
            return data.sessions;
        }
    } catch (error) {
        console.error('Error fetching user sessions:', error);
    }
};
```

### React Hook Example
```javascript
import { useState } from 'react';

const useSessionManagement = () => {
    const [isResetting, setIsResetting] = useState(false);
    const [error, setError] = useState(null);
    const [currentSessionId, setCurrentSessionId] = useState(null);

    const resetState = async (accessToken) => {
        setIsResetting(true);
        setError(null);

        try {
            const response = await fetch('/api/reset-state/', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/json',
                },
            });

            const data = await response.json();

            if (response.ok) {
                setCurrentSessionId(data.session_id);
                return {
                    success: true,
                    data: data
                };
            } else {
                setError(data.error || 'Failed to reset state');
                return {
                    success: false,
                    error: data.error
                };
            }
        } catch (err) {
            setError('Network error occurred');
            return {
                success: false,
                error: 'Network error occurred'
            };
        } finally {
            setIsResetting(false);
        }
    };

    const getSessionHistory = async (accessToken, sessionId) => {
        try {
            const response = await fetch(`/api/chat-history/?session_id=${sessionId}`, {
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                },
            });

            if (response.ok) {
                return await response.json();
            }
        } catch (error) {
            console.error('Error fetching session history:', error);
        }
    };

    return { 
        resetState, 
        getSessionHistory, 
        isResetting, 
        error, 
        currentSessionId 
    };
};
```

### Session History Component
```jsx
const SessionHistory = ({ accessToken }) => {
    const [sessions, setSessions] = useState([]);
    const [selectedSession, setSelectedSession] = useState(null);
    const [sessionMessages, setSessionMessages] = useState([]);

    useEffect(() => {
        // Load all sessions
        fetch('/api/user-sessions/', {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            },
        })
        .then(response => response.json())
        .then(data => setSessions(data.sessions));
    }, [accessToken]);

    const loadSessionHistory = async (sessionId) => {
        const messages = await fetch(`/api/chat-history/?session_id=${sessionId}`, {
            headers: {
                'Authorization': `Bearer ${accessToken}`,
            },
        }).then(response => response.json());
        
        setSessionMessages(messages);
        setSelectedSession(sessionId);
    };

    return (
        <div className="session-history">
            <h3>Previous Sessions</h3>
            <div className="session-list">
                {sessions.map(sessionId => (
                    <button
                        key={sessionId}
                        onClick={() => loadSessionHistory(sessionId)}
                        className={selectedSession === sessionId ? 'active' : ''}
                    >
                        Session {sessionId}
                    </button>
                ))}
            </div>
            
            {selectedSession && (
                <div className="session-messages">
                    <h4>Session {selectedSession} Messages</h4>
                    {sessionMessages.map(message => (
                        <div key={message.id} className={`message ${message.is_user ? 'user' : 'bot'}`}>
                            <span className="timestamp">{message.timestamp}</span>
                            <span className="text">{message.text}</span>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};
```

## UI Integration Suggestions

### Reset Button with Session Info
```jsx
<button 
    onClick={resetStateMachine}
    disabled={isResetting}
    className="reset-button"
>
    {isResetting ? 'Starting New Session...' : `Start New Session (Current: ${currentSessionId})`}
</button>
```

### Session Selector
```jsx
<div className="session-selector">
    <label>Current Session: {currentSessionId}</label>
    <select onChange={(e) => loadSession(e.target.value)}>
        {sessions.map(sessionId => (
            <option key={sessionId} value={sessionId}>
                Session {sessionId}
            </option>
        ))}
    </select>
</div>
```

### Confirmation Dialog
```jsx
const handleReset = () => {
    const confirmed = window.confirm(
        'Start a new conversation session? Previous session will be preserved but you\'ll start fresh.'
    );
    
    if (confirmed) {
        resetStateMachine();
    }
};
```

## Important Notes

1. **Session Preservation**: Previous sessions are never deleted, only archived
2. **Message Counting**: Only counts messages in the current active session
3. **Memory Context**: Each session operates independently
4. **Session IDs**: Auto-incrementing integers starting from 1
5. **Authentication**: All endpoints require valid JWT token
6. **State Isolation**: Each session has its own state machine state

## Error Handling

Always handle potential errors:
- Network errors
- Authentication errors
- Invalid session IDs
- Server errors

## Testing

Example cURL commands:

```bash
# Reset state machine
curl -X POST \
  http://localhost:8000/api/reset-state/ \
  -H 'Authorization: Bearer your_access_token_here' \
  -H 'Content-Type: application/json'

# Get chat history for session 2
curl -X GET \
  'http://localhost:8000/api/chat-history/?session_id=2' \
  -H 'Authorization: Bearer your_access_token_here'

# Get all user sessions
curl -X GET \
  http://localhost:8000/api/user-sessions/ \
  -H 'Authorization: Bearer your_access_token_here'
```
