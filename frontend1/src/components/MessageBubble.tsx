import { type Message } from "../lib/types";
import ReactMarkdown from "react-markdown";

interface MessageBubbleProps {
  message: Message;
  onPdfDownload?: (pdfId: string) => void;
}

const MessageBubble = ({ message, onPdfDownload }: MessageBubbleProps) => {
  const isUser = message.sender === "user";

  return (
    <div
      className={`flex ${
        isUser ? "justify-end" : "justify-start"
      } mb-4 animate-slideUp`}
    >
      <div
        className={`max-w-[80%] px-4 py-3 rounded-2xl ${
          isUser
            ? "bg-blue-500 text-white rounded-br-sm"
            : "bg-white text-gray-800 border border-gray-200 rounded-bl-md"
        } shadow-sm`}
      >
        {isUser ? (
          <p className="text-sm leading-relaxed">{message.content}</p>
        ) : (
          <div className="text-sm leading-relaxed prose prose-sm max-w-none">
            <ReactMarkdown
              components={{
                img: ({ src, alt }) => (
                  <img 
                    src={src} 
                    alt={alt} 
                    className="max-w-full h-auto rounded-lg my-2"
                    loading="lazy"
                  />
                ),
                p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                ul: ({ children }) => <ul className="list-disc list-inside mb-2">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal list-inside mb-2">{children}</ol>,
                li: ({ children }) => <li className="mb-1">{children}</li>,
                strong: ({ children }) => <strong className="font-semibold text-blue-600">{children}</strong>,
                em: ({ children }) => <em className="italic text-gray-600">{children}</em>,
                h1: ({ children }) => <h1 className="text-lg font-bold mb-2 text-green-600">{children}</h1>,
                h2: ({ children }) => <h2 className="text-base font-semibold mb-2 text-green-600">{children}</h2>,
                h3: ({ children }) => <h3 className="text-sm font-semibold mb-1 text-green-600">{children}</h3>,
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        )}
        
        {/* PDF Download Button for AI messages with generated PDFs */}
        {!isUser && message.pdfGenerated && message.pdfId && onPdfDownload && (
          <div className="mt-3 pt-2 border-t border-gray-200">
            <button
              onClick={() => onPdfDownload(message.pdfId!)}
              className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-500 to-green-500 text-white text-sm font-medium rounded-lg hover:from-blue-600 hover:to-green-600 transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-105"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              📄 Download Your Caribbean Itinerary
            </button>
          </div>
        )}
        
        <span className={`text-xs mt-2 block ${isUser ? 'opacity-70' : 'opacity-50'}`}>
          {message.timestamp.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </span>
      </div>
    </div>
  );
};
export default MessageBubble;
