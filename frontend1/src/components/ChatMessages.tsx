import { useEffect, useRef } from "react";
import { type Message } from "../lib/types";
import MessageBubble from "./MessageBubble";
import Loader from "./Loader";

interface ChatMessagesProps {
  messages: Message[];
  isLoading: boolean;
  onPdfDownload?: (pdfId: string) => void;
}

const ChatMessages = ({
  messages,
  isLoading,
  onPdfDownload,
}: ChatMessagesProps) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
      {messages.map((message) => (
        <MessageBubble 
          key={message.id} 
          message={message} 
          onPdfDownload={onPdfDownload}
        />
      ))}
      {isLoading && (
        <div className="flex justify-start mb-4">
          <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-md px-4 py-3 shadow-sm">
            <Loader />
            <p className="text-sm text-gray-600 mt-2">🌴 TropicTrek is planning your Caribbean adventure...</p>
          </div>
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
};
export default ChatMessages;
