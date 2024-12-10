import React, { useState, useRef, useEffect } from 'react';
import { Conversation, Message } from '../types';
import { marked } from 'marked'; // Import the marked library

interface ChatAreaProps {
  conversation: Conversation | null;
  isStreaming: boolean;
  showContext: boolean;
  connectionStatus: 'connected' | 'disconnected';
  onToggleContext: () => void;
  onSendMessage: (message: string) => Promise<void>;
}

const ChatArea: React.FC<ChatAreaProps> = ({
  conversation,
  isStreaming,
  showContext,
  connectionStatus,
  onToggleContext,
  onSendMessage,
}) => {
  const [message, setMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation?.messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || isStreaming) return;

    const trimmedMessage = message.trim();
    setMessage('');
    await onSendMessage(trimmedMessage);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const isMarkdown = (text: string) => {
    // Simple check for markdown syntax
    return text.startsWith('#') || text.startsWith('*') || text.includes('**') || text.includes('__');
  };

  return (
    <div className="w-full flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50 shadow">
        <div className="flex items-center">
          <div
            className={`w-2 h-2 rounded-full mr-2 ${
              connectionStatus === 'connected' ? 'bg-green-500' : 'bg-red-500'
            }`}
          />
          <span className="text-sm text-gray-700 font-semibold">
            {connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        <button
          onClick={onToggleContext}
          className="text-sm text-blue-600 hover:text-blue-800 font-semibold"
        >
          {showContext ? 'Hide Context' : 'Show Context'}
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {conversation?.messages.map((msg: Message) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                msg.role === 'user'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-100 text-gray-900'
              } shadow-md`}
            >
              {isMarkdown(msg.content) ? (
                <div dangerouslySetInnerHTML={{ __html: marked(msg.content) }} />
              ) : (
                <span>{msg.content}</span>
              )}
            </div>
          </div>
        ))}
        {isStreaming && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-lg p-3">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <form onSubmit={handleSubmit} className="flex space-x-4">
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your message..."
            className="flex-1 min-h-[44px] max-h-32 p-2 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isStreaming}
          />
          <button
            type="submit"
            disabled={isStreaming || !message.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatArea;
