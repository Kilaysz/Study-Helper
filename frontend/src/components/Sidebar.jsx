import React from 'react';
import { 
  Bot, FileText, UploadCloud, CheckCircle2, Trash2, Plus, MessageSquare, X 
} from 'lucide-react';

export default function Sidebar({ 
  fileStatus, 
  fileName, 
  handleFileUpload, 
  handleRemoveFile, // <--- This function comes from App.jsx
  
  sessions,
  currentId,
  onNewChat,
  onSelectSession,
  onDeleteSession
}) {
  return (
    <aside className="w-80 bg-white border-r border-gray-200 flex flex-col shadow-sm z-10 shrink-0 h-full">
      
      {/* Header */}
      <div className="p-5 border-b border-gray-100 flex flex-col gap-4">
        <div className="flex items-center gap-3 text-blue-600">
          <div className="p-2 bg-blue-50 rounded-lg"><Bot size={24} /></div>
          <h1 className="text-xl font-bold tracking-tight">StudyPartner</h1>
        </div>
        <button onClick={onNewChat} className="flex items-center justify-center gap-2 w-full py-3 px-4 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-all shadow-sm font-medium">
          <Plus size={18} /> New Chat
        </button>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
         {sessions && sessions.map(session => (
          <div 
            key={session.id}
            onClick={() => onSelectSession(session.id)}
            className={`group flex items-center justify-between p-3 rounded-lg cursor-pointer transition-all ${
              session.id === currentId 
                ? 'bg-blue-50 text-blue-700 border-blue-100 border' 
                : 'hover:bg-gray-50 text-gray-700 border border-transparent'
            }`}
          >
            <div className="flex items-center gap-3 overflow-hidden">
              <MessageSquare size={16} className={session.id === currentId ? "text-blue-500" : "text-gray-400"} />
              <span className="text-sm font-medium truncate">{session.title || "New Chat"}</span>
            </div>
            <button 
              onClick={(e) => onDeleteSession(e, session.id)} 
              className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-100 hover:text-red-500 rounded transition-all"
            >
              <Trash2 size={14} />
            </button>
          </div>
        ))}
      </div>

      {/* File Upload Section */}
      <div className="p-5 border-t border-gray-100 bg-gray-50">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-500 mb-3">
          <FileText size={16} /> <span>Context File</span>
        </div>
        
        {fileStatus === 'success' ? (
          // Active File Card
          <div className="flex items-center justify-between p-3 bg-white border border-green-200 rounded-xl shadow-sm">
            <div className="flex items-center gap-3 overflow-hidden">
              <div className="p-2 bg-green-50 text-green-600 rounded-lg">
                <CheckCircle2 size={20} />
              </div>
              <div className="flex flex-col min-w-0">
                <span className="text-sm font-medium text-gray-800 truncate block w-32">
                  {fileName}
                </span>
                <span className="text-xs text-green-600">Active Context</span>
              </div>
            </div>
            
            {/* THIS BUTTON TRIGGERS THE DELETE SIGNAL */}
            <button 
              onClick={handleRemoveFile} 
              className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
              title="Remove File"
            >
              <X size={18} />
            </button>
          </div>
        ) : (
          // Upload Input
          <label className={`
            flex flex-col items-center justify-center w-full h-24 
            border-2 border-dashed rounded-xl cursor-pointer transition-all bg-white
            ${fileStatus === 'uploading' ? 'border-blue-300 bg-blue-50' : 'border-gray-300 hover:border-blue-400'}
          `}>
            <div className="flex flex-col items-center justify-center text-center px-4">
              {fileStatus === 'uploading' ? (
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
              ) : (
                <>
                  <UploadCloud className="w-6 h-6 text-gray-400 mb-1" />
                  <p className="text-xs text-gray-500">Click to Upload PDF</p>
                </>
              )}
            </div>
            <input type="file" className="hidden" accept=".pdf,.pptx" onChange={handleFileUpload} />
          </label>
        )}
      </div>
    </aside>
  );
}