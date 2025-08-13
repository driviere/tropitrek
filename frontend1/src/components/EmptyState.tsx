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
    <div className="flex flex-col items-center justify-start pt-1 pb-1 px-4 animate-fadeIn bg-gradient-to-br from-blue-50 via-white to-green-50">
      <div className="text-center mb-1">
        <div className="w-[14rem] h-[14rem] mx-auto flex items-center justify-center">
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
        <h2 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent mb-1">
          Welcome to TropiTrek! 🌴
        </h2>
        <p className="text-gray-600 max-w-lg mx-auto text-xs">
          Let Trekki help you plan the perfect
          island adventure!
        </p>
        <div className="mt-2 text-xs text-gray-500">
          <span className="inline-flex items-center space-x-1 flex-wrap justify-center">
            <span>🏝️ Antigua & Barbuda</span>
            <span>•</span>
            <span>🏖️ Anguilla</span>
            <span>•</span>
            <span>🌿 Dominica</span>
            <span>•</span>
            <span>🌺 Grenada</span>
            <span>•</span>
            <span>🌋 Montserrat</span>
            <span>•</span>
            <span>⛰️ St. Kitts & Nevis</span>
            <span>•</span>
            <span>🏔️ St. Lucia</span>
            <span>•</span>
            <span>⛵ St. Vincent & the Grenadines</span>
          </span>
        </div>
      </div>

      {/* Heritage-themed suggested prompts */}
      <div className="max-w-7xl w-full">
        <h3 className="text-base font-semibold text-center mb-3 text-gray-700">
        ✨ Discover the rich heritage and cultural treasures of the Caribbean ✨
        </h3>
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-1">
          {/* Dominica - Waitukubuli Trail */}
          <button
            onClick={() => onPromptSelect("I would like to explore the Waitukubuli trail over 5 days.")}
            className="group px-2 py-1 bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded hover:border-green-400 hover:shadow-sm transition-all duration-200 text-center"
          >
            <div className="flex flex-col items-center space-y-0.5">
              <span className="text-sm">🥾</span>
              <p className="text-xs font-medium text-green-800 leading-tight">
                I would like to explore the Waitukubuli trail over 5 days.
              </p>
              <span className="text-xs text-green-600">Dominica</span>
            </div>
          </button>

          {/* Anguilla - Heritage Collection Museum */}
          <button
            onClick={() => onPromptSelect("Give me an itinerary based around visiting the The Heritage Collection Museum.")}
            className="group px-2 py-1 bg-gradient-to-br from-blue-50 to-cyan-50 border border-blue-200 rounded hover:border-blue-400 hover:shadow-sm transition-all duration-200 text-center"
          >
            <div className="flex flex-col items-center space-y-0.5">
              <span className="text-sm">🏛️</span>
              <p className="text-xs font-medium text-blue-800 leading-tight">
                Give me an itinerary based around visiting the The Heritage Collection Museum.
              </p>
              <span className="text-xs text-blue-600">Anguilla</span>
            </div>
          </button>

          {/* St. Vincent & the Grenadines - Fort Charlotte */}
          <button
            onClick={() => onPromptSelect("I want to go on a 3 day retreat to visit Fort Charlotte.")}
            className="group px-2 py-1 bg-gradient-to-br from-purple-50 to-violet-50 border border-purple-200 rounded hover:border-purple-400 hover:shadow-sm transition-all duration-200 text-center"
          >
            <div className="flex flex-col items-center space-y-0.5">
              <span className="text-sm">🏰</span>
              <p className="text-xs font-medium text-purple-800 leading-tight">
                I want to go on a 3 day retreat to visit Fort Charlotte.
              </p>
              <span className="text-xs text-purple-600">St. Vincent & the Grenadines</span>
            </div>
          </button>

          {/* Antigua - Nelson's Dockyard */}
          <button
            onClick={() => onPromptSelect("I want to plan a visit to Nelson's Dockyard with my family of 4.")}
            className="group px-2 py-1 bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-200 rounded hover:border-amber-400 hover:shadow-sm transition-all duration-200 text-center"
          >
            <div className="flex flex-col items-center space-y-0.5">
              <span className="text-sm">⚓</span>
              <p className="text-xs font-medium text-amber-800 leading-tight">
                I want to plan a visit to Nelson's Dockyard with my family of 4.
              </p>
              <span className="text-xs text-amber-600">Antigua</span>
            </div>
          </button>
        </div>

        {/* Heritage tagline */}
        <div className="text-center">
          <p className="text-xs text-gray-600 italic">
        
          </p>
        </div>
      </div>


    </div>
  );
};
export default EmptyState;
