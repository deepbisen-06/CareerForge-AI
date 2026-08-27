import React, { useState, useEffect, useRef } from 'react';
import { Bot, Send, X, Sparkles, MessageSquare, Wrench, ChevronRight, User, Loader2 } from 'lucide-react';
import { api } from '../services/api';
import { ChatMessage } from '../types';

interface DrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const CareerAssistantDrawer: React.FC<DrawerProps> = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 0,
      role: 'assistant',
      content: "Hi! I'm your **CareerBridge AI Assistant**. Ask me anything about your matched internships, skill gaps, resume improvements, interview prep, or application deadlines.",
      tool_calls: [],
      created_at: new Date().toISOString()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const quickPrompts = [
    "Which internship should I apply to?",
    "What skills am I missing for top matches?",
    "What applications and deadlines are pending?",
    "How can I improve my resume ATS score?"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  const handleSend = async (textToSend?: string) => {
    const query = textToSend || input;
    if (!query.trim() || isLoading) return;

    const userMsg: ChatMessage = {
      id: Date.now(),
      role: 'user',
      content: query,
      tool_calls: [],
      created_at: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMsg]);
    if (!textToSend) setInput('');
    setIsLoading(true);

    try {
      const assistantMsg = await api.chat.sendMessage({ message: query });
      setMessages(prev => [...prev, assistantMsg]);
    } catch (err: any) {
      setMessages(prev => [
        ...prev,
        {
          id: Date.now(),
          role: 'assistant',
          content: `⚠️ Sorry, I encountered an issue: ${err.message || 'Please try again.'}`,
          tool_calls: [],
          created_at: new Date().toISOString()
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[480px] bg-card border-l border-border shadow-2xl flex flex-col transition-all duration-300 animate-in slide-in-from-right">
      {/* Header */}
      <div className="p-4 border-b border-border flex items-center justify-between bg-muted/40">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-primary to-accent flex items-center justify-center text-primary-foreground shadow-md">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h3 className="font-semibold text-sm flex items-center gap-1.5 text-foreground">
              CareerBridge AI
              <span className="px-2 py-0.5 text-[10px] font-medium bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-full border border-emerald-500/20">
                Online
              </span>
            </h3>
            <p className="text-xs text-muted-foreground">Context-aware Career Agent & Tool Caller</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg text-muted-foreground hover:text-foreground hover:bg-accent transition"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Message Stream */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}
          >
            <div className="flex items-start gap-2.5 max-w-[90%]">
              {m.role === 'assistant' && (
                <div className="w-7 h-7 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary shrink-0 mt-0.5">
                  <Bot className="w-4 h-4" />
                </div>
              )}
              <div>
                {/* Tool call indicator badge */}
                {m.tool_calls && m.tool_calls.length > 0 && (
                  <div className="mb-2 flex flex-wrap gap-1.5">
                    {m.tool_calls.map((tc, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[11px] font-mono bg-primary/10 text-primary border border-primary/20"
                      >
                        <Wrench className="w-3 h-3" />
                        tool: {tc.tool}()
                      </span>
                    ))}
                  </div>
                )}
                
                <div
                  className={`p-3.5 rounded-2xl text-sm leading-relaxed whitespace-pre-line ${
                    m.role === 'user'
                      ? 'bg-primary text-primary-foreground rounded-tr-none'
                      : 'bg-muted/70 dark:bg-muted/40 border border-border/70 text-foreground rounded-tl-none'
                  }`}
                >
                  {m.content}
                </div>
              </div>
              {m.role === 'user' && (
                <div className="w-7 h-7 rounded-lg bg-secondary flex items-center justify-center text-foreground shrink-0 mt-0.5">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground pl-9">
            <Loader2 className="w-4 h-4 animate-spin text-primary" />
            <span>AI Orchestrator is analyzing profile & executing tools...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompt Chips */}
      <div className="p-2.5 px-4 border-t border-border/50 bg-background/50 overflow-x-auto">
        <div className="flex gap-1.5 pb-1 no-scrollbar">
          {quickPrompts.map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(prompt)}
              disabled={isLoading}
              className="text-xs px-2.5 py-1 rounded-full whitespace-nowrap bg-secondary/80 hover:bg-secondary text-secondary-foreground border border-border/50 transition flex items-center gap-1"
            >
              <Sparkles className="w-3 h-3 text-primary" />
              {prompt}
            </button>
          ))}
        </div>
      </div>

      {/* Input Form */}
      <div className="p-3.5 border-t border-border bg-card">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask CareerBridge AI anything..."
            disabled={isLoading}
            className="flex-1 bg-background border border-input rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 transition"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="p-2.5 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 transition disabled:opacity-50 shadow-md shadow-primary/20"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};

export default CareerAssistantDrawer;
