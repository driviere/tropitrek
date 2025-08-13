import { MapPin, Palmtree, Camera, Calendar } from "lucide-react";
import { useState } from "react";

interface SuggestedPrompt {
  id: string;
  text: string;
  category: string;
  icon: React.ReactNode;
}

const SuggestedPrompt = ({
  prompt,
  onSelect,
}: {
  prompt: SuggestedPrompt;
  onSelect: (text: string) => void;
}) => {
  return (
    <button
      onClick={() => onSelect(prompt.text)}
      className="group p-4 bg-white rounded-xl border border-gray-200 hover:border-green-300 hover:shadow-md transition-all duration-200 text-left hover:bg-gradient-to-br hover:from-blue-50 hover:to-green-50"
    >
      <div className="flex items-start space-x-3">
        <div className="w-8 h-8 bg-gradient-to-br from-blue-100 to-green-100 rounded-lg flex items-center justify-center group-hover:from-blue-200 group-hover:to-green-200 transition-colors">
          {prompt.icon}
        </div>
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-900 group-hover:text-green-700 transition-colors">
            {prompt.text}
          </p>
          <p className="text-xs text-gray-500 mt-1">{prompt.category}</p>
        </div>
      </div>
    </button>
  );
};

const EmptyState = ({
  onPromptSelect,
}: {
  onPromptSelect: (text: string) => void;
}) => {
  const suggestedPrompts: SuggestedPrompt[] = [];

  const [videoError, setVideoError] = useState(false);

  return (
    <div className="flex-1 flex flex-col items-center justify-start pt-8 pb-4 px-8 animate-fadeIn bg-gradient-to-br from-blue-50 via-white to-green-50">
      <div className="text-center mb-6">
        <div className="w-[8rem] h-[8rem] mx-auto flex items-center justify-center mb-4">
          {!videoError ? (
            <video
              src="/bot-vid.mp4"
              className="w-full h-full object-contain"
              autoPlay
              loop
              muted
              playsInline
              onError={() => setVideoError(true)}
            />
          ) : (
            <img
              src="/logo.png"
              alt="TropicTrek Logo"
              className="w-full h-full object-contain"
            />
          )}
        </div>
        <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent mb-2">
          Welcome to TropicTrek! 🌴
        </h2>
        <p className="text-gray-600 max-w-xl mx-auto text-sm">
          Your AI-powered Caribbean travel assistant for the Eastern Caribbean
          Currency Union (ECCU) countries. Let me help you plan the perfect
          island adventure!
        </p>
        <div className="mt-3 text-xs text-gray-500">
          <span className="inline-flex items-center space-x-1 flex-wrap justify-center">
            <span>🏝️ Antigua & Barbuda</span>
            <span>•</span>
            <span>🌿 Dominica</span>
            <span>•</span>
            <span>🌺 Grenada</span>
            <span>•</span>
            <span>⛰️ St. Kitts & Nevis</span>
            <span>•</span>
            <span>🏔️ St. Lucia</span>
            <span>•</span>
            <span>⛵ St. Vincent & the Grenadines</span>
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-w-6xl w-full">
        {suggestedPrompts.map((prompt) => (
          <SuggestedPrompt
            key={prompt.id}
            prompt={prompt}
            onSelect={onPromptSelect}
          />
        ))}
      </div>


    </div>
  );
};
export default EmptyState;
