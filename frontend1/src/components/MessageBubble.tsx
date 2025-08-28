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
      className={`flex ${isUser ? "justify-end" : "justify-start"
        } mb-4 animate-slideUp`}
    >
      <div
        className={`max-w-[80%] px-4 py-3 rounded-2xl ${isUser
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
              alt="Trekki"
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

                // Extract PDF download URLs from the message content
                const pdfUrls = [];
                const pdfRegex = /http:\/\/localhost:8000\/download-pdf\/[^\s]+\.pdf/g;
                let pdfMatch;
                while ((pdfMatch = pdfRegex.exec(message.content)) !== null) {
                  pdfUrls.push(pdfMatch[0]);
                }

                // Extract YouTube embed URLs from the message content
                const videoEmbedUrls = [];
                const videoEmbedRegex = /https:\/\/www\.youtube\.com\/embed\/[^\s]+/g;
                let videoMatch;
                while ((videoMatch = videoEmbedRegex.exec(message.content)) !== null) {
                  videoEmbedUrls.push(videoMatch[0]);
                }

                if (process.env.NODE_ENV === 'development') {
                  console.log('Found image URLs:', imageUrls);
                  console.log('Found PDF URLs:', pdfUrls);
                  console.log('Found video embed URLs:', videoEmbedUrls);
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

                // Add PDF download links if found
                if (pdfUrls.length > 0) {
                  elements.push(
                    <div key="pdf-links" className="mb-4">
                      {pdfUrls.map((pdfUrl, pdfIndex) => {
                        const filename = pdfUrl.split('/').pop() || 'itinerary.pdf';
                        return (
                          <div key={`pdf-${pdfIndex}`} className="my-3 p-3 bg-gradient-to-r from-blue-50 to-green-50 border border-blue-200 rounded-lg">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-3">
                                <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-green-500 rounded-full flex items-center justify-center">
                                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                  </svg>
                                </div>
                                <div>
                                  <p className="text-sm font-semibold text-gray-800">📄 Your Itinerary PDF</p>
                                  <p className="text-xs text-gray-600">{filename}</p>
                                </div>
                              </div>
                              <a
                                href={pdfUrl}
                                download
                                className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white text-sm font-medium rounded-lg hover:from-green-600 hover:to-emerald-600 transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                              >
                                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                                Download PDF
                              </a>
                            </div>
                            <div className="mt-2 pt-2 border-t border-blue-200">
                              <p className="text-xs text-gray-600">
                                🌴 <strong>Ready for your Caribbean adventure!</strong> Click to download your complete travel itinerary.
                              </p>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  );
                }

                // Add YouTube videos if found
                if (videoEmbedUrls.length > 0) {
                  elements.push(
                    <div key="videos" className="mb-4">
                      <div className="space-y-3">
                        {videoEmbedUrls.map((embedUrl, videoIndex) => (
                          <div key={`video-${videoIndex}`} className="relative aspect-video bg-black rounded-lg overflow-hidden shadow-lg">
                            <iframe
                              src={embedUrl}
                              title={`Caribbean destination video ${videoIndex + 1}`}
                              className="w-full h-full"
                              frameBorder="0"
                              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                              allowFullScreen
                            />
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                }

                // Add text content
                message.content.split('\n').forEach((line, index) => {
                  // Skip lines that contain image URLs, PDF URLs, video URLs, or video information
                  if (line.includes('https://images.unsplash.com/') ||
                    line.includes('http://localhost:8000/download-pdf/') ||
                    line.includes('https://www.youtube.com/watch') ||
                    line.includes('https://www.youtube.com/embed') ||
                    line.includes('https://i.ytimg.com/') ||
                    line.match(/!\[([^\]]*)\]\(([^)]+)\)/) ||
                    line.match(/\*\*\d+\.\s*[^*]+\*\*/) ||
                    line.includes('Channel:') ||
                    line.includes('Description:') ||
                    line.includes('Watch:') ||
                    line.includes('Embed:') ||
                    line.includes('Thumbnail:') ||
                    line.trim().startsWith('**') && line.includes('**')) {
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
                  <p className="text-xs text-gray-600">Preview and edit before downloading</p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => message.onPdfPreview?.(message.pdfId!, message.content)}
                  className="inline-flex items-center px-3 py-2 bg-blue-500 text-white text-sm font-medium rounded-lg hover:bg-blue-600 transition-all duration-200 shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                >
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  Preview
                </button>
                <button
                  onClick={() => onPdfDownload(message.pdfId!)}
                  className="inline-flex items-center px-3 py-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white text-sm font-medium rounded-lg hover:from-green-600 hover:to-emerald-600 transition-all duration-200 shadow-md hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
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
                  Download
                </button>
              </div>
            </div>

            {/* Helpful tip */}
            <div className="mt-2 pt-2 border-t border-blue-200">
              <p className="text-xs text-gray-600">
                💡 <strong>Tip:</strong> Use Preview to review and edit your itinerary before downloading the final PDF.
              </p>
            </div>
          </div>
        )}

        <span
          className={`text-xs mt-2 block ${isUser ? "opacity-70" : "opacity-50"
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
