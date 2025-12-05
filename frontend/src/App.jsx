import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { 
  Send, 
  UploadCloud, 
  FileText, 
  Bot, 
  User, 
  Sparkles, 
  Settings, 
  Trash2, 
  CheckCircle2, 
  AlertCircle 
} from 'lucide-react';

// --- CONFIGURATION ---
let API_URL = "http://localhost:8000";

export default function App() {
  // --- STATE ---
  const [messages, setMessages] = useState([
    { 
      role: 'assistant', 
      content: "Hello! I'm your **AI Study Partner**.\n\nI can help you:\n1. **Query** the web for real-time info.\n2. **Summarize** complex PDFs.\n3. **Validate** claims against academic papers.\n\nUpload a file or ask me a question to get started!" 
    }
  ]);
  const [input, setInput] = useState('');
  const [mode, setMode] = useState('Query (Web Search)');
  const [fileStatus, setFileStatus] = useState(null); 
  const [fileName, setFileName] = useState('');
  const [fileContent, setFileContent] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const messagesEndRef = useRef(null);

  // --- EFFECTS ---
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // --- HANDLERS ---

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setFileStatus('uploading');
    setFileName(file.name);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) throw new Error("Upload failed");
      
      const data = await response.json();
      setFileContent(data.content);
      setFileStatus('success');
    } catch (error) {
      console.error(error);
      setFileStatus('error');
      setFileName("Upload Failed");
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userText = input;
    setInput('');
    setLoading(true);

    // 1. Add User Message
    setMessages(prev => [...prev, { role: 'user', content: userText }]);

    try {
      // 2. Send to Backend
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userText,
          mode: mode,
          file_content: fileContent,
          history: messages.map(m => ({ role: m.role, content: m.content }))
        }),
      });

      if (!response.ok) throw new Error("API Error");

      const data = await response.json();
      
      // 3. Add AI Response
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);

    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `⚠️ **Connection Error:** I couldn't reach the backend at \`${API_URL}\`. Please check if \`server.py\` is running.` 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([{ role: 'assistant', content: "Chat cleared. Ready for a new topic!" }]);
    setFileStatus(null);
    setFileName('');
    setFileContent(null);
  };

  return (
    <div className="flex h-screen bg-gray-50 text-gray-800 font-sans overflow-hidden">
      
      {/* --- SIDEBAR --- */}
      <aside className="w-80 bg-white border-r border-gray-200 flex flex-col shadow-sm z-10 shrink-0">
        <div className="p-6 border-b border-gray-100">
          {/* Changed text-brand-600 to text-blue-600 */}
          <div className="flex items-center gap-3 text-blue-600 mb-1">
            <div className="p-2 bg-blue-50 rounded-lg">
              <Bot size={24} />
            </div>
            <h1 className="text-xl font-bold tracking-tight">StudyPartner</h1>
          </div>
          <p className="text-xs text-gray-400 font-medium ml-1">POWERED BY LANGGRAPH</p>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-8">
          
          {/* Mode Selector */}
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-gray-500 tracking-wide">
              <Settings size={16} />
              <span>AGENT MODE</span>
            </div>
            <div className="relative">
              {/* Changed focus:ring-brand-500 to focus:ring-blue-500 */}
              <select 
                value={mode} 
                onChange={(e) => setMode(e.target.value)}
                className="w-full appearance-none bg-gray-50 border border-gray-200 text-gray-700 py-3 px-4 pr-8 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent cursor-pointer font-medium transition-all hover:bg-gray-100"
              >
                <option>Query (Web Search)</option>
                <option>Summarize (Document)</option>
                <option>Validate (Fact Check)</option>
              </select>
              <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-gray-500">
                <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>
              </div>
            </div>
            <p className="text-xs text-gray-400 px-1 leading-relaxed">
              {mode.includes('Query') && "Searches the web for up-to-date answers."}
              {mode.includes('Summarize') && "Reads your PDF and extracts key insights."}
              {mode.includes('Validate') && "Checks specific claims against academic papers."}
            </p>
          </div>

          {/* File Upload Context */}
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-gray-500 tracking-wide">
              <FileText size={16} />
              <span>CONTEXT FILE</span>
            </div>
            
            {/* Changed border-brand-500/600 to blue-500/600 */}
            <label className={`
              flex flex-col items-center justify-center w-full h-32 
              border-2 border-dashed rounded-xl cursor-pointer transition-all duration-200
              ${fileStatus === 'uploading' ? 'bg-gray-50 border-gray-300' : ''}
              ${fileStatus === 'success' ? 'bg-green-50 border-green-300' : 'hover:bg-gray-50 border-gray-300 hover:border-blue-500'}
            `}>
              <div className="flex flex-col items-center justify-center pt-5 pb-6 text-center px-4">
                {fileStatus === 'uploading' ? (
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mb-2"></div>
                ) : fileStatus === 'success' ? (
                  <CheckCircle2 className="w-8 h-8 text-green-500 mb-2" />
                ) : fileStatus === 'error' ? (
                  <AlertCircle className="w-8 h-8 text-red-400 mb-2" />
                ) : (
                  <UploadCloud className="w-8 h-8 text-gray-400 mb-2" />
                )}
                
                <p className={`text-sm font-medium truncate w-full px-2 ${fileStatus === 'success' ? 'text-green-700' : 'text-gray-500'}`}>
                  {fileName || "Click to upload PDF"}
                </p>
                {!fileName && <p className="text-xs text-gray-400 mt-1">PDF or PPTX (Max 10MB)</p>}
              </div>
              <input type="file" className="hidden" accept=".pdf,.pptx" onChange={handleFileUpload} />
            </label>
          </div>
        </div>

        {/* Sidebar Footer */}
        <div className="p-6 border-t border-gray-100 mt-auto">
          <button 
            onClick={clearChat}
            className="flex items-center justify-center gap-2 w-full py-2.5 px-4 rounded-lg text-gray-500 hover:text-red-500 hover:bg-red-50 transition-colors text-sm font-medium"
          >
            <Trash2 size={16} />
            Clear Conversation
          </button>
        </div>
      </aside>

      {/* --- MAIN CHAT AREA --- */}
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
              {/* Changed bg-brand-600 to bg-blue-600 */}
              <div className={`
                max-w-[80%] lg:max-w-[70%] px-5 py-4 rounded-2xl shadow-sm text-sm leading-relaxed
                ${msg.role === 'user' 
                  ? 'bg-blue-600 text-white rounded-tr-sm' 
                  : 'bg-gray-50 border border-gray-100 text-gray-800 rounded-tl-sm'}
              `}>
                {msg.role === 'assistant' ? (
                  <div className="prose prose-sm max-w-none text-gray-800 prose-p:leading-relaxed prose-pre:bg-gray-200 prose-pre:text-gray-700">
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  </div>
                ) : (
                  msg.content
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
            {/* Changed focus:ring-brand-100 to focus:ring-blue-100 */}
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder={loading ? "Waiting for response..." : `Type your message here...`}
              disabled={loading}
              className="w-full pl-5 pr-14 py-4 bg-gray-50 border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-100 focus:border-blue-500 transition-all shadow-sm placeholder-gray-400 text-gray-700"
            />
            {/* Changed bg-brand-600 to bg-blue-600 */}
            <button 
              onClick={handleSend}
              disabled={loading || !input.trim()}
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
    </div>
  );
}