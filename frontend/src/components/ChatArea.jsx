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
    <main className="flex-1 flex flex-col h-full bg-gradient-to-br from-slate-50 via-blue-50/30 to-purple-50/20 relative">
      
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-8 space-y-8 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-transparent">
        {messages.map((msg, idx) => (
          <div 
            key={idx} 
            className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in fade-in slide-in-from-bottom-3 duration-500`}
            style={{ animationDelay: `${idx * 50}ms` }}
          >
            
            {/* Bot Avatar */}
            {msg.role === 'assistant' && (
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-500 via-blue-600 to-indigo-600 flex items-center justify-center shadow-lg flex-shrink-0 mt-1 ring-2 ring-blue-100 hover:scale-110 transition-transform duration-300">
                <Sparkles size={22} className="text-white" />
              </div>
            )}

            {/* Message Bubble */}
            <div className={`
              max-w-[85%] lg:max-w-[70%] px-6 py-4 rounded-3xl shadow-md text-sm leading-relaxed overflow-hidden transition-all duration-300 hover:shadow-xl
              ${msg.role === 'user' 
                ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white rounded-tr-md shadow-blue-200/50' 
                : 'bg-white/95 backdrop-blur-sm border border-gray-200/50 text-gray-800 rounded-tl-md'}
            `}>
              {msg.role === 'assistant' ? (
                <div className="prose prose-sm max-w-none text-gray-800 
                  prose-p:leading-relaxed prose-p:my-2
                  prose-headings:text-gray-900 prose-headings:font-semibold prose-headings:mb-3 prose-headings:mt-4
                  prose-pre:bg-gray-100 prose-pre:text-gray-800 prose-pre:rounded-xl prose-pre:shadow-inner prose-pre:p-4
                  prose-code:text-blue-600 prose-code:bg-blue-50 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-xs
                  prose-table:border-collapse prose-table:w-full prose-table:my-4
                  prose-thead:bg-gradient-to-br prose-thead:from-gray-100 prose-thead:to-gray-200
                  prose-th:p-3 prose-th:border prose-th:border-gray-300 prose-th:font-bold prose-th:text-left prose-th:text-gray-900
                  prose-td:p-3 prose-td:border prose-td:border-gray-200 prose-td:align-top prose-td:whitespace-normal
                  prose-tbody:bg-white
                  prose-tr:border-b prose-tr:border-gray-200
                  prose-a:text-blue-600 prose-a:no-underline hover:prose-a:underline
                  prose-strong:text-gray-900 prose-strong:font-bold
                  prose-ul:my-2 prose-ul:list-disc prose-ul:pl-6
                  prose-ol:my-2 prose-ol:list-decimal prose-ol:pl-6
                  prose-li:my-1 prose-li:leading-relaxed
                  prose-blockquote:border-l-4 prose-blockquote:border-blue-500 prose-blockquote:pl-4 prose-blockquote:italic">
                  <ReactMarkdown 
                    remarkPlugins={[remarkGfm]}
                    components={{
                      table: ({node, ...props}) => (
                        <div className="overflow-x-auto my-4 rounded-lg border border-gray-300">
                          <table className="min-w-full border-collapse" {...props} />
                        </div>
                      ),
                      thead: ({node, ...props}) => (
                        <thead className="bg-gradient-to-br from-gray-100 to-gray-200" {...props} />
                      ),
                      tbody: ({node, ...props}) => (
                        <tbody className="bg-white divide-y divide-gray-200" {...props} />
                      ),
                      tr: ({node, ...props}) => (
                        <tr className="hover:bg-gray-50 transition-colors" {...props} />
                      ),
                      th: ({node, ...props}) => (
                        <th className="p-4 border-r border-gray-300 font-bold text-left text-gray-900 last:border-r-0 whitespace-nowrap" {...props} />
                      ),
                      td: ({node, children, ...props}) => (
                        <td className="p-4 border-r border-gray-200 align-top last:border-r-0" {...props}>
                          <div className="whitespace-pre-wrap break-words">{children}</div>
                        </td>
                      ),
                      ul: ({node, ...props}) => (
                        <ul className="list-disc pl-5 my-2 space-y-1" {...props} />
                      ),
                      li: ({node, ...props}) => (
                        <li className="text-sm leading-relaxed" {...props} />
                      ),
                      p: ({node, children, ...props}) => (
                        <div className="my-1" {...props}>{children}</div>
                      ),
                      br: () => <br />
                    }}
                  >
                    {(() => {
                      let content = msg.content;
                      
                      // Replace HTML br tags with markdown line breaks
                      content = content.replace(/<br\s*\/?>/gi, '  \n');
                      
                      // Fix orphaned bullet points that appear on their own row
                      // Pattern: | cell | cell | cell |\n| • content |
                      // Convert to: | cell | cell | cell • content |
                      content = content.replace(/\|([^|\n]+)\|([^|\n]+)\|([^|\n]+)\|\s*\n\s*\|\s*([•\-\*][^\|]*?)\s*\|/g, 
                        '| $1 | $2 | $3 $4 |');
                      
                      // Also handle cases where bullet points come right after cell content
                      content = content.replace(/\|\s*([^|\n]+?)\s*\n+\s*([•\-\*])/g, '| $1 $2');
                      
                      return content;
                    })()}
                  </ReactMarkdown>
                </div>
              ) : (
                <div className="whitespace-pre-wrap">{msg.content}</div>
              )}
            </div>

            {/* User Avatar */}
            {msg.role === 'user' && (
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-slate-200 to-slate-300 flex items-center justify-center flex-shrink-0 mt-1 shadow-md ring-2 ring-slate-100">
                <User size={22} className="text-slate-600" />
              </div>
            )}
          </div>
        ))}

        {/* Typing Indicator */}
        {loading && (
          <div className="flex gap-4 justify-start">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-blue-100 to-blue-200 animate-pulse"></div>
            <div className="h-12 bg-white/90 backdrop-blur-sm rounded-3xl w-24 flex items-center justify-center px-5 shadow-md border border-gray-200/50">
              <div className="flex gap-1.5">
                <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0ms'}}></div>
                <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
                <div className="w-2.5 h-2.5 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-6 bg-white/80 backdrop-blur-xl border-t border-gray-200/60 shadow-2xl">
        <div className="max-w-4xl mx-auto relative group">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && handleSend()}
            placeholder={loading ? "Waiting for response..." : "Ask me anything..."}
            disabled={disableInput}
            className="w-full pl-6 pr-16 py-5 bg-white border-2 border-gray-200 rounded-3xl 
              focus:outline-none focus:ring-4 focus:ring-blue-100 focus:border-blue-500 
              transition-all duration-300 shadow-lg placeholder-gray-400 text-gray-700 
              hover:border-blue-300 hover:shadow-xl disabled:bg-gray-50 disabled:cursor-not-allowed"
          />
          <button 
            onClick={handleSend}
            disabled={disableInput}
            className="absolute right-2 top-2 p-3.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-2xl 
              hover:from-blue-700 hover:to-blue-800 
              disabled:opacity-50 disabled:cursor-not-allowed 
              transition-all duration-300 shadow-lg active:scale-95 hover:shadow-xl
              hover:ring-4 hover:ring-blue-100"
          >
            <Send size={22} />
          </button>
        </div>
        <p className="text-center text-xs text-gray-400 mt-4 font-medium tracking-wide">
          AI can make mistakes. Please verify important information.
        </p>
      </div>
    </main>
  );
}