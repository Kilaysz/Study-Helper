import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Send, User, Sparkles } from 'lucide-react';

export default function ChatArea({ 
  messages, 
  loading, 
  input, 
  setInput, 
  handleSend, 
  messagesEndRef,
  disableInput 
}) {
  return (
    <main className="flex-1 flex flex-col h-full bg-white relative">
      
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-8 space-y-6 scrollbar-default">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            
            {/* Bot Avatar */}
            {msg.role === 'assistant' && (
              <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-600 to-blue-500 flex items-center justify-center shadow-md flex-shrink-0 mt-1">
                <Sparkles size={20} className="text-white" />
              </div>
            )}

            {/* Message Bubble */}
            <div className={`
              max-w-[85%] lg:max-w-[75%] px-5 py-4 rounded-2xl shadow-sm text-sm leading-relaxed overflow-hidden
              ${msg.role === 'user' 
                ? 'bg-blue-600 text-white rounded-tr-sm' 
                : 'bg-gray-50 border border-gray-100 text-gray-800 rounded-tl-sm'}
            `}>
              {msg.role === 'assistant' ? (
                <div className="prose prose-sm max-w-none text-gray-800 
                  prose-p:leading-relaxed 
                  prose-pre:bg-gray-200 prose-pre:text-gray-700
                  prose-table:border-collapse prose-table:border prose-table:border-gray-300
                  prose-th:bg-gray-100 prose-th:p-2 prose-th:border prose-th:border-gray-300
                  prose-td:p-2 prose-td:border prose-td:border-gray-300">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.content}
                  </ReactMarkdown>
                </div>
              ) : (
                <div className="whitespace-pre-wrap">{msg.content}</div>
              )}
            </div>

            {/* User Avatar */}
            {msg.role === 'user' && (
              <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0 mt-1">
                <User size={20} className="text-gray-500" />
              </div>
            )}
          </div>
        ))}

        {/* Typing Indicator */}
        {loading && (
          <div className="flex gap-4 justify-start animate-pulse">
            <div className="w-10 h-10 rounded-full bg-gray-100"></div>
            <div className="h-10 bg-gray-100 rounded-2xl w-32 flex items-center px-4">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0ms'}}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-6 bg-white border-t border-gray-100">
        <div className="max-w-4xl mx-auto relative group">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder={loading ? "Waiting for response..." : `Type your message here...`}
            disabled={disableInput}
            className="w-full pl-5 pr-14 py-4 bg-gray-50 border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-100 focus:border-blue-500 transition-all shadow-sm placeholder-gray-400 text-gray-700"
          />
          <button 
            onClick={handleSend}
            disabled={disableInput}
            className="absolute right-2 top-2 p-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md active:scale-95"
          >
            <Send size={20} />
          </button>
        </div>
        <p className="text-center text-xs text-gray-400 mt-3 font-medium">
          AI can make mistakes. Please verify important information.
        </p>
      </div>
    </main>
  );
}