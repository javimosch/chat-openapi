export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: number;
  created_at: string; // Added created_at property
}

export interface Conversation {
  id: string;
  title: string;
  timestamp: number;
  messages: Message[];
  lastUpdated: number;
  created_at: string; // Added created_at property
}

export interface WebSocketMessage {
  type: 'token' | 'error' | 'end' | 'stream' | 'final'; // Added 'final' type
  content?: string;
  error?: string;
  conversation_id?: string;
}
