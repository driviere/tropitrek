import React, { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import type { Message } from "./lib/types";
import EmptyState from "./components/EmptyState";
import ChatMessages from "./components/ChatMessages";
import UserInput from "./components/UserInput";
import { chatAPI } from "./lib/api";
import { toast, Toaster } from "sonner";

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [inputValue, setInputValue] = useState("");
  const [sessionId, setSessionId] = useState<string>("");
  const [availablePdfs, setAvailablePdfs] = useState<{[key: string]: string}>({});

  // Check backend health on component mount
  useEffect(() => {
    const checkBackendHealth = async () => {
      try {
        await chatAPI.healthCheck();
        toast.success("🌴 TropicTrek is ready to help you plan your Caribbean adventure!");
      } catch (error) {
        toast.error("⚠️ Unable to connect to TropicTrek backend. Please ensure the server is running on localhost:8000");
      }
    };

    checkBackendHealth();
  }, []);

  const handlePdfDownload = async (pdfId: string) => {
    try {
      toast.loading("📄 Preparing your itinerary PDF...");
      const blob = await chatAPI.downloadPdf(pdfId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `TropicTrek_Itinerary_${pdfId}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      toast.success("🎉 Your Caribbean itinerary has been downloaded!");
    } catch (error) {
      console.error('Error downloading PDF:', error);
      toast.error("❌ Failed to download PDF. Please try again.");
    }
  };

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      content,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    setIsLoading(true);

    try {
      const response = await chatAPI.sendMessage({
        message: content,
        session_id: sessionId || undefined
      });

      // Update session ID if this is the first message
      if (!sessionId) {
        setSessionId(response.session_id);
      }

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.response,
        sender: "ai",
        timestamp: new Date(),
        pdfId: response.pdf_id,
        pdfGenerated: response.pdf_generated
      };

      setMessages((prev) => [...prev, aiMessage]);

      // Store PDF info if generated
      if (response.pdf_generated && response.pdf_id) {
        setAvailablePdfs(prev => ({
          ...prev,
          [response.pdf_id!]: `TropicTrek Itinerary PDF`
        }));
        toast.success("🎉 Your personalized Caribbean itinerary is ready for download!");
      }

    } catch (error) {
      console.error("Error calling TropicTrek API:", error);
      
      // Add error message to chat
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: "🌴 Sorry, I'm having trouble connecting right now. Please make sure the TropicTrek backend is running and try again. I'm here to help you plan your perfect Caribbean adventure!",
        sender: "ai",
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, errorMessage]);
      toast.error("❌ Connection error. Please check if the backend server is running.");
    } finally {
      setIsLoading(false);
    }
  };

  const handlePromptSelect = (promptText: string) => {
    setInputValue(promptText);
  };

  const isEmpty = messages.length === 0;

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 transition-colors duration-200">
      <Toaster 
        position="top-right" 
        richColors 
        closeButton 
        duration={4000}
      />
      
      {/* Fixed Navbar */}
      <Navbar />

      {/* Main content area - takes remaining space */}
      <div className="flex-1 flex flex-col min-h-0">
        {isEmpty ? (
          <div className="flex-1 flex flex-col">
            <EmptyState onPromptSelect={handlePromptSelect} />
          </div>
        ) : (
          <ChatMessages 
            messages={messages} 
            isLoading={isLoading} 
            onPdfDownload={handlePdfDownload}
          />
        )}
        
        {/* Fixed Input at bottom */}
        <UserInput
          onSendMessage={handleSendMessage}
          disabled={isLoading}
          value={inputValue}
          onChange={setInputValue}
        />
      </div>

      <style jsx>{`
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        .animate-slideUp {
          animation: slideUp 0.3s ease-out;
        }

        .animate-fadeIn {
          animation: fadeIn 0.5s ease-out;
        }
      `}</style>
    </div>
  );
};

export default ChatInterface;
