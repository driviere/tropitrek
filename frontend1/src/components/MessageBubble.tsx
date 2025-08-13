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
          <div className="text-sm leading-relaxed flex gap-3">
            <img
              src="/bot-icon.png"
              alt="TropicTrek AI"
              className="w-8 h-8 object-contain flex-shrink-0 mt-1"
            />
            <div className="flex-1">
              {/* Process message content to handle both text and images */}
              {(() => {
                // Debug logging outside of render
                if (process.env.NODE_ENV === 'development') {
                  console.log('Full message content:', message.content);
                  // Test if our regex works with a sample
                  const testLine = "![beach view](https://images.unsplash.com/photo-1635450737602-4522ad50351e)";
                  const testMatch = testLine.match(/!\[([^\]]*)\]\(([^)]+)\)/);
                  console.log('Test regex match:', testMatch);
                  
                  // Check if message contains any image markdown
                  const hasImageMarkdown = message.content.includes('![');
                  console.log('Message contains image markdown:', hasImageMarkdown);
                  
                  // For testing: if this is an AI message about images, let's see what we got
                  if (message.content.toLowerCase().includes('image') || message.content.toLowerCase().includes('beach')) {
                    console.log('🔍 This message mentions images/beach. Full content:', message.content);
                    
                    // Test if we can manually inject an image for testing
                    if (message.content.includes('Here are some beautiful images')) {
                      console.log('🧪 This looks like an image response, but no markdown detected');
                      console.log('🧪 Expected format: ![alt text](image_url)');
                    }
                  }
                }
                
                // Extract all image URLs from the message content using regex
                const imageUrls = [];
                const imageRegex = /https:\/\/images\.unsplash\.com\/[^\s)]+/g;
                let match;
                while ((match = imageRegex.exec(message.content)) !== null) {
                  imageUrls.push(match[0]);
                }
                
                if (process.env.NODE_ENV === 'development') {
                  console.log('Found image URLs:', imageUrls);
                }
                
                const elements = [];
                
                // Add images if found
                if (imageUrls.length > 0) {
                  elements.push(
                    <div key="images" className="mb-4">
                      <div className="grid grid-cols-1 gap-3">
                        {imageUrls.map((imageUrl, imgIndex) => (
                          <div key={`img-${imgIndex}`} className="my-2">
                            <img
                              src={imageUrl}
                              alt={`Caribbean destination image ${imgIndex + 1}`}
                              className="max-w-full h-auto rounded-lg shadow-lg border border-gray-200"
                              loading="lazy"
                              onError={(e) => {
                                console.error('Image failed to load:', imageUrl);
                                const target = e.currentTarget;
                                target.style.display = 'none';
                                
                                // Show fallback
                                const fallback = target.nextElementSibling as HTMLElement;
                                if (fallback && fallback.classList.contains('image-fallback')) {
                                  fallback.style.display = 'block';
                                }
                              }}
                              onLoad={() => {
                                console.log('✅ Image loaded successfully:', imageUrl);
                              }}
                            />
                            <div 
                              className="image-fallback bg-gray-100 border-2 border-dashed border-gray-300 rounded-lg p-4 text-center text-gray-500"
                              style={{ display: 'none' }}
                            >
                              <div className="flex flex-col items-center">
                                <svg className="w-8 h-8 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                                </svg>
                                <p className="text-sm font-medium">Image unavailable</p>
                                <p className="text-xs text-gray-400 mt-1">Caribbean destination image</p>
                                <p className="text-xs text-gray-400 mt-1 break-all">{imageUrl}</p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                }
                
                // Add text content
                message.content.split('\n').forEach((line, index) => {
                  // Skip lines that contain image URLs or markdown
                  if (line.includes('https://images.unsplash.com/') || line.match(/!\[([^\]]*)\]\(([^)]+)\)/)) {
                    return;
                  }
                  
                  // Regular text processing with blue emphasis
                  const processLine = (text: string) => {
                    // Look for words that should be emphasized (destinations, important terms)
                    const emphasizedWords = [
                      'Dominica', 'Grenada', 'St. Lucia', 'St. Kitts', 'Nevis', 'Antigua', 'Barbuda', 
                      'St. Vincent', 'Grenadines', 'Anguilla', 'Caribbean', 'ECCU',
                      'Adventure Seeker', 'Cultural Explorer', 'Relaxation', 'budget', 'moderate', 'luxury',
                      'itinerary', 'PDF', 'weather', 'festival', 'beach', 'waterfall', 'rainforest'
                    ];
                    
                    let processedText = text;
                    emphasizedWords.forEach(word => {
                      const regex = new RegExp(`\\b${word}\\b`, 'gi');
                      processedText = processedText.replace(regex, `<span class="text-blue-600 font-medium">${word}</span>`);
                    });
                    
                    return processedText;
                  };

                  elements.push(
                    <div 
                      key={`text-${index}`} 
                      className="mb-1"
                      dangerouslySetInnerHTML={{ 
                        __html: line ? processLine(line) : '\u00A0' 
                      }}
                    />
                  );
                });
                
                return elements;
              })()}
            </div>
          </div>
        )}

        {/* PDF Download Section for AI messages with generated PDFs */}
        {!isUser && message.pdfGenerated && message.pdfId && onPdfDownload && (
          <div className="mt-4 p-3 bg-gradient-to-r from-blue-50 to-green-50 border border-blue-200 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-green-500 rounded-full flex items-center justify-center">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-semibold text-gray-800">Your Itinerary PDF is Ready!</p>
                  <p className="text-xs text-gray-600">Click to download your complete travel plan</p>
                </div>
              </div>
              <button
                onClick={() => onPdfDownload(message.pdfId!)}
                className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-500 to-green-500 text-white text-sm font-medium rounded-lg hover:from-blue-600 hover:to-green-600 transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                <svg
                  className="w-4 h-4 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                Download PDF
              </button>
            </div>
            
            {/* Alternative direct link option */}
            <div className="mt-2 pt-2 border-t border-blue-200">
              <p className="text-xs text-gray-600">
                💡 <strong>Tip:</strong> Right-click the download button and select "Save link as..." to save directly to your preferred location.
              </p>
              <a
                href={`http://localhost:8000/download/${message.pdfId}`}
                download
                className="inline-flex items-center text-xs text-blue-600 hover:text-blue-800 underline mt-1"
              >
                <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
                Direct download link
              </a>
            </div>
          </div>
        )}

        <span
          className={`text-xs mt-2 block ${
            isUser ? "opacity-70" : "opacity-50"
          }`}
        >
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
