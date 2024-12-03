export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: number;
}

export interface Conversation {
  id: string;
  title: string;
  timestamp: number;
  messages: Message[];
  lastUpdated: number;
}

export interface WebSocketMessage {
  type: 'token' | 'error' | 'end';
  content?: string;
  error?: string;
}
