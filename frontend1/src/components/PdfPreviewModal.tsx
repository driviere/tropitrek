import React, { useState } from 'react';
import { X, Download, Edit3, Save, Eye } from 'lucide-react';

interface PdfPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  pdfContent: string;
  pdfId: string;
  travelerName: string;
  destination: string;
  onDownload: (pdfId: string) => void;
  onSaveEdits: (pdfId: string, editedContent: string) => void;
}

const PdfPreviewModal: React.FC<PdfPreviewModalProps> = ({
  isOpen,
  onClose,
  pdfContent,
  pdfId,
  travelerName,
  destination,
  onDownload,
  onSaveEdits,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedContent, setEditedContent] = useState(pdfContent);
  const [hasChanges, setHasChanges] = useState(false);

  if (!isOpen) return null;

  const handleContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setEditedContent(e.target.value);
    setHasChanges(e.target.value !== pdfContent);
  };

  const handleSaveEdits = () => {
    onSaveEdits(pdfId, editedContent);
    setHasChanges(false);
    setIsEditing(false);
  };

  const handleCancelEdit = () => {
    setEditedContent(pdfContent);
    setHasChanges(false);
    setIsEditing(false);
  };

  const renderPreviewContent = (content: string) => {
    return content.split('\n').map((line, index) => {
      // Handle headers
      if (line.startsWith('# ')) {
        return (
          <h1 key={index} className="text-2xl font-bold text-blue-800 mb-4 mt-6">
            {line.replace('# ', '')}
          </h1>
        );
      }
      if (line.startsWith('## ')) {
        return (
          <h2 key={index} className="text-xl font-semibold text-blue-700 mb-3 mt-5">
            {line.replace('## ', '')}
          </h2>
        );
      }
      if (line.startsWith('### ')) {
        return (
          <h3 key={index} className="text-lg font-semibold text-blue-600 mb-2 mt-4">
            {line.replace('### ', '')}
          </h3>
        );
      }
      
      // Handle bold text
      if (line.startsWith('**') && line.endsWith('**')) {
        return (
          <p key={index} className="font-semibold text-gray-800 mb-2">
            {line.replace(/\*\*/g, '')}
          </p>
        );
      }
      
      // Handle bullet points
      if (line.startsWith('- ')) {
        return (
          <li key={index} className="ml-4 mb-1 text-gray-700">
            {line.replace('- ', '')}
          </li>
        );
      }
      
      // Handle empty lines
      if (line.trim() === '') {
        return <div key={index} className="mb-2"></div>;
      }
      
      // Regular text
      return (
        <p key={index} className="text-gray-700 mb-2 leading-relaxed">
          {line}
        </p>
      );
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-green-500 rounded-full flex items-center justify-center">
              <Eye className="w-4 h-4 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-gray-800">
                Itinerary Preview
              </h2>
              <p className="text-sm text-gray-600">
                {travelerName} • {destination}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {!isEditing ? (
              <>
                <button
                  onClick={() => setIsEditing(true)}
                  className="flex items-center space-x-2 px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                >
                  <Edit3 className="w-4 h-4" />
                  <span>Edit</span>
                </button>
                <button
                  onClick={() => onDownload(pdfId)}
                  className="flex items-center space-x-2 px-3 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                >
                  <Download className="w-4 h-4" />
                  <span>Download</span>
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={handleCancelEdit}
                  className="px-3 py-2 text-gray-600 hover:text-gray-800 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveEdits}
                  disabled={!hasChanges}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                    hasChanges
                      ? 'bg-green-500 text-white hover:bg-green-600'
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  <Save className="w-4 h-4" />
                  <span>Save Changes</span>
                </button>
              </>
            )}
            
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-hidden">
          {isEditing ? (
            <div className="h-full p-4">
              <textarea
                value={editedContent}
                onChange={handleContentChange}
                className="w-full h-full p-4 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                placeholder="Edit your itinerary content here..."
              />
              {hasChanges && (
                <p className="text-sm text-blue-600 mt-2">
                  ✨ You have unsaved changes
                </p>
              )}
            </div>
          ) : (
            <div className="h-full overflow-y-auto p-6 bg-gray-50">
              <div className="bg-white rounded-lg shadow-sm p-6 max-w-none prose prose-sm">
                {renderPreviewContent(editedContent)}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <div className="flex items-center space-x-4">
              <span>📄 PDF Preview</span>
              <span>•</span>
              <span>Generated by TropicTrek</span>
            </div>
            <div className="flex items-center space-x-2">
              {isEditing ? (
                <span className="text-blue-600">✏️ Editing Mode</span>
              ) : (
                <span>👁️ Preview Mode</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PdfPreviewModal;