import React, { useState, useEffect } from 'react';
import ChatArea from './components/ChatArea';
import Sidebar from './components/Sidebar';
import useWebSocket from './hooks/useWebSocket';
import { Conversation, Message, WebSocketMessage } from './types';

const App: React.FC = () => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [showContext, setShowContext] = useState<boolean>(true);

  const { sendMessage, lastMessage, connectionStatus } = useWebSocket();

  useEffect(() => {
    // Load conversations from localStorage on component mount
    const savedConversations = localStorage.getItem('conversations');
    if (savedConversations) {
      const parsed = JSON.parse(savedConversations);
      setConversations(parsed);
      if (parsed.length > 0) {
        setCurrentConversation(parsed[0]);
      }
    }
  }, []);

  useEffect(() => {
    // Save conversations to localStorage whenever they change
    localStorage.setItem('conversations', JSON.stringify(conversations));
  }, [conversations]);

  useEffect(() => {
    if (lastMessage && currentConversation) {
      const wsMessage = JSON.parse(lastMessage) as WebSocketMessage;
      
      if (wsMessage.type === 'stream') {
        // Update the last message in the current conversation with the streamed content
        setConversations(prevConversations => {
          return prevConversations.map(conv => {
            if (conv.id === currentConversation.id) {
              const updatedMessages = [...conv.messages];
              const lastMessageIndex = updatedMessages.length - 1;
              if (lastMessageIndex >= 0) {
                updatedMessages[lastMessageIndex] = {
                  ...updatedMessages[lastMessageIndex],
                  content: updatedMessages[lastMessageIndex].content + wsMessage.content
                };
              }
              return { ...conv, messages: updatedMessages };
            }
            return conv;
          });
        });
      }
    }
  }, [lastMessage, currentConversation]);

  const createNewConversation = () => {
    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: 'New Conversation',
      messages: [],
      created_at: new Date().toISOString(),
    };
    setConversations([newConversation, ...conversations]);
    setCurrentConversation(newConversation);
  };

  const handleSendMessage = async (content: string) => {
    if (!currentConversation) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    };

    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: '',
      created_at: new Date().toISOString(),
    };

    setConversations(prevConversations => {
      return prevConversations.map(conv => {
        if (conv.id === currentConversation.id) {
          return {
            ...conv,
            messages: [...conv.messages, userMessage, assistantMessage],
          };
        }
        return conv;
      });
    });

    // Send message through WebSocket
    sendMessage(JSON.stringify({
      type: 'message',
      content,
      conversation_id: currentConversation.id,
      show_context: showContext,
    }));
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar
        conversations={conversations}
        currentConversation={currentConversation}
        onSelectConversation={setCurrentConversation}
        onNewConversation={createNewConversation}
      />
      <ChatArea
        conversation={currentConversation}
        onSendMessage={handleSendMessage}
        showContext={showContext}
        onToggleContext={() => setShowContext(!showContext)}
        connectionStatus={connectionStatus}
      />
    </div>
  );
};

export default App;
