import React, { useState, useEffect } from 'react';
import ChatArea from './components/ChatArea';
import Sidebar from './components/Sidebar';
import useWebSocket from './hooks/useWebSocket';
import { Conversation, Message, WebSocketMessage } from './types';
import { v4 as uuidv4 } from 'uuid';

const App: React.FC = () => {
  const [conversations, setConversations] = useState<Map<string, Conversation>>(new Map());
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [showContext, setShowContext] = useState<boolean>(true);
  const [isStreaming, setIsStreaming] = useState<boolean>(false);

  const { sendMessage, lastMessage, isConnected, subscribeToMessages } = useWebSocket();

  useEffect(() => {
    const savedConversations = localStorage.getItem('conversations');
    if (savedConversations) {
      const parsed: Conversation[] = JSON.parse(savedConversations);
      const conversationMap = new Map(parsed.map(conv => [conv.id, conv]));
      setConversations(conversationMap);
      if (parsed.length > 0) {
        setCurrentConversation(parsed[0]);
      }
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('conversations', JSON.stringify(Array.from(conversations.values())));
  }, [conversations]);

  useEffect(() => {
    if (isConnected) {
      subscribeToMessages((message: WebSocketMessage) => {
        console.log('Message received:', message);
        if (message.type === 'stream') {
          setIsStreaming(true);
        } else if (message.type === 'token' && currentConversation) {
          setConversations(prevConversations => {
            const updatedConversations = new Map(prevConversations);
            const conv = updatedConversations.get(currentConversation.id);
            if (conv) {
              const lastMessageIndex = conv.messages.length - 1;
              if (lastMessageIndex >= 0 && conv.messages[lastMessageIndex].role === 'assistant') {
                conv.messages[lastMessageIndex].content += message.content || '';
              } else {
                const assistantMessage: Message = {
                  id: uuidv4(),
                  role: 'assistant',
                  content: message.content || '',
                  created_at: new Date().toISOString(),
                  timestamp: Date.now(),
                };
                conv.messages.push(assistantMessage);
              }
              updatedConversations.set(currentConversation.id, { ...conv });
            }
            return updatedConversations;
          });
        } else if (message.type === 'final' && currentConversation) {
          setConversations(prevConversations => {
            const updatedConversations = new Map(prevConversations);
            const conv = updatedConversations.get(currentConversation.id);
            if (conv) {
              const lastMessageIndex = conv.messages.length - 1;
              if (lastMessageIndex >= 0 && conv.messages[lastMessageIndex].role === 'assistant') {
                conv.messages[lastMessageIndex].content += message.content || '';
              }
              updatedConversations.set(currentConversation.id, { ...conv });
            }
            return updatedConversations;
          });
          setIsStreaming(false);
        }
      });
    }
  }, [isConnected, subscribeToMessages, currentConversation]);

  const createNewConversation = () => {
    const newConversation: Conversation = {
      id: Date.now().toString(),
      title: 'New Conversation',
      messages: [],
      created_at: new Date().toISOString(),
      timestamp: Date.now(),
      lastUpdated: Date.now(),
    };
    setConversations(prevConversations => new Map(prevConversations).set(newConversation.id, newConversation));
    setCurrentConversation(newConversation);
  };

  const handleSendMessage = async (content: string) => {
    if (!currentConversation) return;

    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content,
      created_at: new Date().toISOString(),
      timestamp: Date.now(),
    };

    setConversations(prevConversations => {
      const updatedConversations = new Map(prevConversations);
      const conv = updatedConversations.get(currentConversation.id);
      if (conv) {
        updatedConversations.set(currentConversation.id, {
          ...conv,
          messages: [...conv.messages, userMessage],
        });
      }
      return updatedConversations;
    });

    sendMessage(JSON.stringify({
      type: 'message',
      content,
      conversation_id: currentConversation.id,
      show_context: showContext,
    }));
  };

  const handleDeleteConversation = (id: string) => {
    setConversations(prevConversations => {
      const updatedConversations = new Map(prevConversations);
      updatedConversations.delete(id);
      return updatedConversations;
    });
    if (currentConversation && currentConversation.id === id) {
      setCurrentConversation(null);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100 w-full">
      <Sidebar
        conversations={Array.from(conversations.values())}
        currentConversation={currentConversation}
        activeConversation={currentConversation ? currentConversation.id : null}
        onSelectConversation={(id: string) => {
          const selectedConversation = conversations.get(id) || null;
          setCurrentConversation(selectedConversation);
        }}
        onNewConversation={createNewConversation}
        onDeleteConversation={handleDeleteConversation}
      />
      <ChatArea
        conversation={currentConversation}
        onSendMessage={handleSendMessage}
        showContext={showContext}
        onToggleContext={() => setShowContext(!showContext)}
        connectionStatus={isConnected ? "connected" : "disconnected"}
        isStreaming={isStreaming}
      />
    </div>
  );
};

export default App;
