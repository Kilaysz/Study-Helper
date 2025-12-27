import React, { useState, useRef, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';

// --- CONFIGURATION ---
let API_URL = "http://localhost:8000";
try {
  if (import.meta && import.meta.env && import.meta.env.VITE_API_URL) {
    API_URL = import.meta.env.VITE_API_URL;
  }
} catch (error) {
  console.warn("Using default API URL:", API_URL);
}

export default function App() {
  const [sessions, setSessions] = useState([]);
  const [currentId, setCurrentId] = useState(null);
  
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  
  const [fileStatus, setFileStatus] = useState(null); 
  const [fileName, setFileName] = useState('');
  const [fileContent, setFileContent] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const messagesEndRef = useRef(null);

  // --- HELPER: Signal Backend to Delete File ---
  const clearBackendFile = async () => {
    try {
      await fetch(`${API_URL}/delete-file`, { method: 'DELETE' });
      console.log("Backend file cleared.");
    } catch (err) {
      console.error("Failed to clear backend file:", err);
    }
  };

  // --- INIT & PERSISTENCE ---

  useEffect(() => {
    const storedSessions = JSON.parse(localStorage.getItem('chat_sessions') || '[]');
    setSessions(storedSessions);
    if (storedSessions.length > 0) {
      loadSession(storedSessions[0].id);
    } else {
      createNewSession();
    }
  }, []);

  useEffect(() => {
    if (!currentId) return;
    const isDefault = messages.length === 1 && messages[0].role === 'assistant';
    if (isDefault && !fileContent) return;

    const allHistory = JSON.parse(localStorage.getItem('chat_history') || '{}');
    // Save MESSAGES ONLY (File is ephemeral)
    allHistory[currentId] = { messages };
    localStorage.setItem('chat_history', JSON.stringify(allHistory));

    setSessions(prev => {
      const existingIndex = prev.findIndex(s => s.id === currentId);
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
        newSessions[existingIndex] = { ...newSessions[existingIndex], title, date: new Date().toISOString() };
        if (existingIndex !== 0) {
            newSessions.splice(existingIndex, 1);
            newSessions.unshift(newSessionInfo);
        }
      } else {
        newSessions = [newSessionInfo, ...prev];
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
    
    // Reset Frontend State
    setFileStatus(null);
    setFileName('');
    setFileContent(null);
    
    // Reset Backend State
    clearBackendFile();
  };

  const loadSession = (id) => {
    const allHistory = JSON.parse(localStorage.getItem('chat_history') || '{}');
    const data = allHistory[id];
    
    if (data) {
      setCurrentId(id);
      setMessages(data.messages || []);
      
      // 1. Clear Frontend File State
      setFileName('');
      setFileContent(null);
      setFileStatus(null);
      
      // 2. Clear Backend File State (Switching context)
      clearBackendFile();
    } else {
      createNewSession();
    }
  };

  const deleteSession = (e, id) => {
    e.stopPropagation();
    const newSessions = sessions.filter(s => s.id !== id);
    setSessions(newSessions);
    localStorage.setItem('chat_sessions', JSON.stringify(newSessions));
    
    const allHistory = JSON.parse(localStorage.getItem('chat_history') || '{}');
    delete allHistory[id];
    localStorage.setItem('chat_history', JSON.stringify(allHistory));

    if (id === currentId) {
      if (newSessions.length > 0) loadSession(newSessions[0].id);
      else createNewSession();
    }
  };

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
    } finally {
      try { e.target.value = ''; } catch (err) { /* ignore */ }
    }
  };

  // UPDATED: Handle Manual File Delete
  const handleFileDelete = () => {
    // 1. Clear Frontend
    setFileStatus(null);
    setFileName('');
    setFileContent(null);

    // 2. Clear Backend
    clearBackendFile();
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
        content: `⚠️ **Error:** Backend connection failed at \`${API_URL}\`.` 
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
        handleRemoveFile={handleFileDelete} // Pass updated handler
        
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