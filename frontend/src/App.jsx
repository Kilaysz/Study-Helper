import React, { useState, useRef, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';

// --- CONFIGURATION ---
let API_URL = "http://localhost:8000";

try {
  // Safe check for environment variables
  if (import.meta && import.meta.env && import.meta.env.VITE_API_URL) {
    API_URL = import.meta.env.VITE_API_URL;
  }
} catch (error) {
  console.warn("Using default API URL:", API_URL);
}

export default function App() {
  // --- STATE ---
  const [sessions, setSessions] = useState([]);
  const [currentId, setCurrentId] = useState(null);
  
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  
  const [fileStatus, setFileStatus] = useState(null); 
  const [fileName, setFileName] = useState('');
  const [fileContent, setFileContent] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const messagesEndRef = useRef(null);

  // --- INIT & PERSISTENCE ---

  // 1. Load Sessions on Mount
  useEffect(() => {
    const storedSessions = JSON.parse(localStorage.getItem('chat_sessions') || '[]');
    setSessions(storedSessions);
    
    if (storedSessions.length > 0) {
      // Load the most recent session
      loadSession(storedSessions[0].id);
    } else {
      // Start a fresh session
      createNewSession();
    }
  }, []);

  // 2. Save Current Session whenever content changes
  useEffect(() => {
    if (!currentId) return;

    // Don't save if it's just the default greeting and no file
    const isDefault = messages.length === 1 && messages[0].role === 'assistant';
    if (isDefault && !fileContent) return;

    const allHistory = JSON.parse(localStorage.getItem('chat_history') || '{}');
    
    // Update the history storage
    allHistory[currentId] = {
      messages,
      fileName,
      fileContent,
      fileStatus
    };
    localStorage.setItem('chat_history', JSON.stringify(allHistory));

    // Update the session list (Title & Timestamp)
    setSessions(prev => {
      const existingIndex = prev.findIndex(s => s.id === currentId);
      
      // Generate a title from the first user message, or file name, or default
      const firstUserMsg = messages.find(m => m.role === 'user');
      let title = "New Chat";
      if (firstUserMsg) {
        title = firstUserMsg.content.slice(0, 30) + (firstUserMsg.content.length > 30 ? "..." : "");
      } else if (fileName) {
        title = `File: ${fileName}`;
      }

      const newSessionInfo = { id: currentId, title, date: new Date().toISOString() };
      
      let newSessions;
      if (existingIndex >= 0) {
        newSessions = [...prev];
        // Only update title/date, keep id
        newSessions[existingIndex] = { ...newSessions[existingIndex], title, date: new Date().toISOString() };
        
        // Move to top if it's the current one being edited
        if (existingIndex !== 0) {
            newSessions.splice(existingIndex, 1);
            newSessions.unshift(newSessionInfo);
        }
      } else {
        newSessions = [newSessionInfo, ...prev]; // Add to top
      }
      
      localStorage.setItem('chat_sessions', JSON.stringify(newSessions));
      return newSessions;
    });

  }, [messages, fileContent, fileName, currentId]);

  // --- SESSION MANAGERS ---

  const createNewSession = () => {
    const newId = Date.now().toString();
    setCurrentId(newId);
    setMessages([{ 
      role: 'assistant', 
      content: "Hello! I'm your **AI Study Partner**. \n\nUpload a file or ask me anything—I'll automatically figure out if you need a summary, a fact-check, a quiz, or just a web search!" 
    }]);
    setFileStatus(null);
    setFileName('');
    setFileContent(null);
  };

  const loadSession = (id) => {
    const allHistory = JSON.parse(localStorage.getItem('chat_history') || '{}');
    const data = allHistory[id];
    
    if (data) {
      setCurrentId(id);
      setMessages(data.messages || []);
      setFileName(data.fileName || '');
      setFileContent(data.fileContent || null);
      setFileStatus(data.fileStatus || null);
    } else {
      createNewSession();
    }
  };

  const deleteSession = (e, id) => {
    e.stopPropagation(); // Prevent triggering selection
    
    const newSessions = sessions.filter(s => s.id !== id);
    setSessions(newSessions);
    localStorage.setItem('chat_sessions', JSON.stringify(newSessions));
    
    // Cleanup actual data
    const allHistory = JSON.parse(localStorage.getItem('chat_history') || '{}');
    delete allHistory[id];
    localStorage.setItem('chat_history', JSON.stringify(allHistory));

    // If we deleted the current session, switch to another or create new
    if (id === currentId) {
      if (newSessions.length > 0) loadSession(newSessions[0].id);
      else createNewSession();
    }
  };

  // --- SCROLLING ---
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
    if (!input.trim() && !fileContent) return; 
    
    const userText = input.trim() || "Analyze this document.";

    setInput('');
    setLoading(true);

    setMessages(prev => [...prev, { role: 'user', content: userText }]);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userText,
          file_content: fileContent,
          history: messages.map(m => ({ role: m.role, content: m.content }))
        }),
      });

      if (!response.ok) throw new Error("API Error");

      const data = await response.json();
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }]);

    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `⚠️ **Error:** Backend connection failed at \`${API_URL}\`. Is the server running?` 
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50 text-gray-800 font-sans overflow-hidden">
      <Sidebar 
        fileStatus={fileStatus} 
        fileName={fileName} 
        handleFileUpload={handleFileUpload}
        
        // Passing new Session props to Sidebar
        sessions={sessions}
        currentId={currentId}
        onNewChat={createNewSession}
        onSelectSession={loadSession}
        onDeleteSession={deleteSession}
      />
      
      <ChatArea 
        messages={messages} 
        loading={loading} 
        input={input} 
        setInput={setInput} 
        handleSend={handleSend} 
        messagesEndRef={messagesEndRef}
        disableInput={loading}
      />
    </div>
  );
}