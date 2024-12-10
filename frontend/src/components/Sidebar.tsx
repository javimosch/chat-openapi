import React from 'react';
import { Conversation } from '../types';

interface SidebarProps {
  conversations: Conversation[];
  activeConversation: string | null;
  onNewConversation: () => void;
  onDeleteConversation: (id: string) => void;
  onSelectConversation: (id: string) => void;
  currentConversation: Conversation | null;
}

const Sidebar: React.FC<SidebarProps> = ({
  conversations,
  activeConversation,
  onNewConversation,
  onDeleteConversation,
  onSelectConversation,
  currentConversation,
}) => {
  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col shadow-lg">
      <div className="p-4 border-b border-gray-200">
        <button
          onClick={onNewConversation}
          className="w-full py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
        >
          New Chat
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto">
        {conversations
          .sort((a, b) => b.lastUpdated - a.lastUpdated)
          .map((conversation) => (
            <div
              key={conversation.id}
              className={`p-4 border-b border-gray-200 cursor-pointer hover:bg-gray-50 ${
                activeConversation === conversation.id ? 'bg-gray-100' : ''
              }`}
              onClick={() => onSelectConversation(conversation.id)}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {conversation.title}
                  </p>
                  <p className="text-xs text-gray-500">
                    {new Date(conversation.timestamp).toLocaleDateString()}
                  </p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteConversation(conversation.id);
                  }}
                  className="ml-2 text-gray-400 hover:text-red-500"
                >
                  <svg
                    className="w-4 h-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </button>
              </div>
            </div>
          ))}
      </div>
    </aside>
  );
};

export default Sidebar;
