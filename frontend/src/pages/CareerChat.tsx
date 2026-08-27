import React, { useState, useEffect, useRef } from 'react';
import { Bot, Send, User, Sparkles, Wrench, Loader2, ArrowRight } from 'lucide-react';
import { api } from '../services/api';
import { ChatMessage } from '../types';

export const CareerChat: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 0,
      role: 'assistant',
      content: "Hello! I am your **CareerBridge AI Assistant**.\n\nI can analyze your student profile, search our curated 1,000+ internship knowledge base via Hybrid RAG, explain compatibility scores, highlight skill gaps, and track approaching deadlines.\n\nHow can I help you today?",
      tool_calls: [],
      created_at: new Date().toISOString()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const quickPrompts = [
    "Which internship should I apply to?",
    "Why am I a good match for AI/ML roles?",
    "What skills am I missing for the top match?",
    "What applications and deadlines are pending?",
    "How can I improve my resume ATS score?"
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
          content: `⚠️ Sorry, an issue occurred: ${err.message || 'Please try again.'}`,
          tool_calls: [],
          created_at: new Date().toISOString()
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-140px)] flex flex-col rounded-3xl bg-card border border-border/80 shadow-sm overflow-hidden animate-fadeIn pb-2">
      {/* Header */}
      <div className="p-4 border-b border-border bg-muted/30 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-primary to-accent flex items-center justify-center text-primary-foreground shadow-md">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <h2 className="font-bold text-sm flex items-center gap-2 text-foreground">
              CareerBridge AI Career Assistant
              <span className="px-2 py-0.5 text-[10px] font-bold bg-emerald-500/10 text-emerald-600 border border-emerald-500/20 rounded-full">
                Active
              </span>
            </h2>
            <p className="text-xs text-muted-foreground">Connected to Hybrid RAG index, student profile & application tracker</p>
          </div>
        </div>
      </div>

      {/* Messages Stream */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}
          >
            <div className="flex items-start gap-3 max-w-[85%]">
              {m.role === 'assistant' && (
                <div className="w-8 h-8 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center text-primary shrink-0 mt-0.5">
                  <Bot className="w-4 h-4" />
                </div>
              )}
              <div>
                {/* Tool call indicator badges */}
                {m.tool_calls && m.tool_calls.length > 0 && (
                  <div className="mb-2 flex flex-wrap gap-1.5">
                    {m.tool_calls.map((tc, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg text-xs font-mono bg-primary/10 text-primary border border-primary/20"
                      >
                        <Wrench className="w-3.5 h-3.5" />
                        tool: {tc.tool}()
                      </span>
                    ))}
                  </div>
                )}

                <div
                  className={`p-4 rounded-3xl text-sm leading-relaxed whitespace-pre-line ${
                    m.role === 'user'
                      ? 'bg-primary text-primary-foreground rounded-tr-none'
                      : 'bg-muted/50 dark:bg-muted/30 border border-border/80 text-foreground rounded-tl-none'
                  }`}
                >
                  {m.content}
                </div>
              </div>
              {m.role === 'user' && (
                <div className="w-8 h-8 rounded-xl bg-secondary flex items-center justify-center text-foreground shrink-0 mt-0.5">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground pl-11">
            <Loader2 className="w-4 h-4 animate-spin text-primary" />
            <span>AI Orchestrator is executing tools and retrieving context...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Quick Prompts Bar */}
      <div className="p-3 border-t border-border/60 bg-background/50 overflow-x-auto">
        <div className="flex gap-2 pb-1 no-scrollbar">
          {quickPrompts.map((prompt, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(prompt)}
              disabled={isLoading}
              className="text-xs px-3 py-1.5 rounded-full whitespace-nowrap bg-secondary hover:bg-accent text-secondary-foreground border border-border/60 transition flex items-center gap-1.5"
            >
              <Sparkles className="w-3 h-3 text-primary" />
              {prompt}
            </button>
          ))}
        </div>
      </div>

      {/* Input Box */}
      <div className="p-4 border-t border-border bg-card">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-3"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about internships, match scores, skill gaps, or preparation..."
            disabled={isLoading}
            className="flex-1 bg-background border border-input rounded-2xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="p-3 rounded-2xl bg-primary text-primary-foreground hover:bg-primary/90 transition disabled:opacity-50 shadow-md shadow-primary/20"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};

export default CareerChat;
