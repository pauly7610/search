import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import { Message, Conversation, ChatState } from '../types/chat';

interface ChatStore extends ChatState {
  // Actions
  addMessage: (message: Message) => void;
  updateMessage: (messageId: string, updates: Partial<Message>) => void;
  setCurrentConversation: (conversation: Conversation | null) => void;
  setIsTyping: (isTyping: boolean) => void;
  setAgentStatus: (status: 'available' | 'busy' | 'away') => void;
  setConnectionStatus: (status: 'connected' | 'disconnected' | 'connecting') => void;
  clearMessages: () => void;
  addConversation: (conversation: Conversation) => void;
  updateConversation: (conversationId: string, updates: Partial<Conversation>) => void;
}

export const useChatStore = create<ChatStore>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        conversations: [],
        currentConversation: null,
        isTyping: false,
        agentStatus: 'available',
        connectionStatus: 'disconnected',

        // Actions
        addMessage: (message) =>
          set((state) => {
            const currentConversation = state.currentConversation;
            if (!currentConversation) return state;

            const updatedConversation = {
              ...currentConversation,
              messages: [...currentConversation.messages, message],
              updatedAt: new Date().toISOString(),
            };

            return {
              currentConversation: updatedConversation,
              conversations: state.conversations.map(conv =>
                conv.id === updatedConversation.id ? updatedConversation : conv
              ),
            };
          }),

        updateMessage: (messageId, updates) =>
          set((state) => {
            const currentConversation = state.currentConversation;
            if (!currentConversation) return state;

            const updatedMessages = currentConversation.messages.map(msg =>
              msg.id === messageId ? { ...msg, ...updates } : msg
            );

            const updatedConversation = {
              ...currentConversation,
              messages: updatedMessages,
              updatedAt: new Date().toISOString(),
            };

            return {
              currentConversation: updatedConversation,
              conversations: state.conversations.map(conv =>
                conv.id === updatedConversation.id ? updatedConversation : conv
              ),
            };
          }),

        setCurrentConversation: (conversation) =>
          set({ currentConversation: conversation }),

        setIsTyping: (isTyping) => set({ isTyping }),

        setAgentStatus: (agentStatus) => set({ agentStatus }),

        setConnectionStatus: (connectionStatus) => set({ connectionStatus }),

        clearMessages: () =>
          set((state) => ({
            currentConversation: state.currentConversation
              ? { ...state.currentConversation, messages: [] }
              : null,
          })),

        addConversation: (conversation) =>
          set((state) => ({
            conversations: [...state.conversations, conversation],
          })),

        updateConversation: (conversationId, updates) =>
          set((state) => ({
            conversations: state.conversations.map(conv =>
              conv.id === conversationId ? { ...conv, ...updates } : conv
            ),
          })),
      }),
      {
        name: 'chat-store',
        partialize: (state) => ({
          conversations: state.conversations,
          currentConversation: state.currentConversation,
        }),
      }
    ),
    { name: 'ChatStore' }
  )
);
