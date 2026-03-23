# AI Services API Documentation

---

## 1. Chat with AI Assistant

**Endpoint:** `POST /api/ai/chat`

**Description:** Send message to AI assistant for help with course content

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "message": "Can you explain what recursion is in simple terms?",
  "context": {
    "course_id": "770e8400-e29b-41d4-a716-446655440000",
    "topic_id": "990e8400-e29b-41d4-a716-446655440005",
    "conversation_history": [
      {
        "role": "user",
        "content": "I'm learning about functions",
        "timestamp": "2024-03-15T14:00:00Z"
      },
      {
        "role": "assistant",
        "content": "Functions are reusable blocks of code...",
        "timestamp": "2024-03-15T14:00:05Z"
      }
    ]
  }
}
```

**Field Descriptions:**
- `message` (string, required): User's question or message
- `context` (object, required): Conversation context
  - `course_id` (UUID, optional): Current course
  - `topic_id` (UUID, optional): Current topic
  - `conversation_history` (array, optional): Previous messages (last 5)

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "response": "Recursion is when a function calls itself to solve a problem. Think of it like looking in a mirror that reflects another mirror - you see infinite reflections. In programming, a recursive function breaks down a big problem into smaller, similar problems until it reaches a simple case it can solve directly.",
    "suggestions": [
      "Can you show me an example of recursion?",
      "What's the difference between recursion and iteration?",
      "When should I use recursion?"
    ],
    "related_topics": [
      {
        "id": "990e8400-e29b-41d4-a716-446655440006",
        "title": "Recursive Functions in Python",
        "course_id": "770e8400-e29b-41d4-a716-446655440000"
      },
      {
        "id": "990e8400-e29b-41d4-a716-446655440007",
        "title": "Base Cases and Recursive Cases",
        "course_id": "770e8400-e29b-41d4-a716-446655440000"
      }
    ]
  }
}
```

---

## 2. Simplify Content

**Endpoint:** `POST /api/ai/simplify`

**Description:** Simplify complex content for better understanding

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "content": "The time complexity of the quicksort algorithm is O(n log n) on average, but can degrade to O(n²) in the worst case when the pivot selection is poor.",
  "level": "basic",
  "language": "English"
}
```

**Field Descriptions:**
- `content` (string, required): Content to simplify
- `level` (string, required): Simplification level
  - `"basic"`: Very simple explanation
  - `"intermediate"`: Moderate complexity
  - `"advanced"`: Technical but clearer
- `language` (string, required): Output language
  - `"English"`, `"Igbo"`, `"Hausa"`, `"Yoruba"`

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "simplified_content": "Quicksort is usually very fast - it takes about n log n time. But sometimes, if we're unlucky with how we split the data, it can be slower and take n² time.",
    "key_points": [
      "Quicksort is usually fast",
      "Average time: n log n",
      "Worst case: n²",
      "Speed depends on how data is split"
    ],
    "examples": [
      "Think of sorting a deck of cards by picking a middle card and putting smaller cards on left, bigger on right",
      "If you always pick the smallest card as your middle card, it takes much longer"
    ]
  }
}
```

---

## 3. Start Voice Chat Session

**Endpoint:** `POST /api/voice/session`

**Description:** Initialize a voice chat session

**Request Headers:**
```
Authorization: Bearer {access_token}
```

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "session_id": "abc123-def456-ghi789",
    "supported_languages": [
      "English",
      "Igbo",
      "Hausa",
      "Yoruba"
    ],
    "max_duration": 300
  }
}
```

**Field Descriptions:**
- `session_id`: Unique session identifier
- `supported_languages`: Available languages for voice input
- `max_duration`: Maximum session duration in seconds

---

## 4. Transcribe Voice Input

**Endpoint:** `POST /api/voice/transcribe`

**Description:** Transcribe voice input and get AI response

**Request Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "session_id": "abc123-def456-ghi789",
  "audio_data": "base64_encoded_audio_data_here...",
  "language": "English"
}
```

**Field Descriptions:**
- `session_id` (string, required): Session ID from voice/session
- `audio_data` (string, required): Base64 encoded audio data
- `language` (string, required): Audio language

**Success Response (200):**
```json
{
  "success": true,
  "data": {
    "transcription": "What is the difference between a list and a tuple in Python?",
    "confidence": 0.95,
    "ai_response": "Great question! Lists and tuples are both used to store multiple items, but they have key differences. Lists are mutable (you can change them) and use square brackets [], while tuples are immutable (cannot be changed) and use parentheses (). Lists are better when you need to modify data, tuples are better for fixed data."
  }
}
```

---

## Frontend Implementation Examples

### React AI Chat Component

```typescript
// components/AIChat.tsx
import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export const AIChat: React.FC<{ token: string; courseId: string; topicId: string }> = ({
  token,
  courseId,
  topicId
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(
        'http://localhost:8000/api/ai/chat',
        {
          message: input,
          context: {
            course_id: courseId,
            topic_id: topicId,
            conversation_history: messages.slice(-5)
          }
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.data.data.response,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ai-chat">
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="content">{msg.content}</div>
            <div className="timestamp">{new Date(msg.timestamp).toLocaleTimeString()}</div>
          </div>
        ))}
        {loading && <div className="message assistant loading">Thinking...</div>}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask me anything..."
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
};
```

### Vue.js Content Simplifier

```vue
<template>
  <div class="content-simplifier">
    <div class="controls">
      <select v-model="level">
        <option value="basic">Basic</option>
        <option value="intermediate">Intermediate</option>
        <option value="advanced">Advanced</option>
      </select>
      
      <select v-model="language">
        <option value="English">English</option>
        <option value="Igbo">Igbo</option>
        <option value="Hausa">Hausa</option>
        <option value="Yoruba">Yoruba</option>
      </select>
      
      <button @click="simplify" :disabled="loading">
        {{ loading ? 'Simplifying...' : 'Simplify' }}
      </button>
    </div>

    <div class="content">
      <div class="original">
        <h3>Original Content</h3>
        <p>{{ originalContent }}</p>
      </div>

      <div v-if="simplified" class="simplified">
        <h3>Simplified Content</h3>
        <p>{{ simplified.simplified_content }}</p>
        
        <div class="key-points">
          <h4>Key Points:</h4>
          <ul>
            <li v-for="(point, idx) in simplified.key_points" :key="idx">
              {{ point }}
            </li>
          </ul>
        </div>

        <div class="examples">
          <h4>Examples:</h4>
          <ul>
            <li v-for="(example, idx) in simplified.examples" :key="idx">
              {{ example }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

const props = defineProps(['content', 'token']);

const level = ref('basic');
const language = ref('English');
const simplified = ref(null);
const loading = ref(false);
const originalContent = ref(props.content);

const simplify = async () => {
  loading.value = true;
  
  try {
    const response = await axios.post(
      '/api/ai/simplify',
      {
        content: originalContent.value,
        level: level.value,
        language: language.value
      },
      {
        headers: {
          'Authorization': `Bearer ${props.token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    simplified.value = response.data.data;
  } catch (error) {
    console.error('Failed to simplify content:', error);
  } finally {
    loading.value = false;
  }
};
</script>
```