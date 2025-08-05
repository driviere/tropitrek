import { MapPin, Palmtree, Camera, Calendar } from "lucide-react";

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
  const suggestedPrompts: SuggestedPrompt[] = [
    {
      id: "1",
      text: "I want to plan a 4-day adventure trip to St. Lucia",
      category: "Adventure Travel",
      icon: <Palmtree className="w-4 h-4 text-green-600" />
    },
    {
      id: "2",
      text: "Create a romantic getaway itinerary for Grenada",
      category: "Romantic Travel",
      icon: <MapPin className="w-4 h-4 text-blue-600" />
    },
    {
      id: "3",
      text: "Show me the best attractions in Dominica with photos",
      category: "Sightseeing",
      icon: <Camera className="w-4 h-4 text-purple-600" />
    },
    {
      id: "4",
      text: "Plan a budget-friendly trip to Antigua & Barbuda",
      category: "Budget Travel",
      icon: <Calendar className="w-4 h-4 text-orange-600" />
    },
    {
      id: "5",
      text: "I'm interested in cultural experiences in St. Kitts & Nevis",
      category: "Cultural Tourism",
      icon: <MapPin className="w-4 h-4 text-red-600" />
    },
    {
      id: "6",
      text: "What are the best beaches in St. Vincent & the Grenadines?",
      category: "Beach Tourism",
      icon: <Palmtree className="w-4 h-4 text-cyan-600" />
    },
  ];

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 animate-fadeIn bg-gradient-to-br from-blue-50 via-white to-green-50">
      <div className="text-center mb-8">
        <div className="flex items-center justify-center mb-4">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-green-500 rounded-full flex items-center justify-center">
            <Palmtree className="w-8 h-8 text-white" />
          </div>
        </div>
        <h2 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent mb-2">
          Welcome to TropicTrek! 🌴
        </h2>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Your AI-powered Caribbean travel assistant for the Eastern Caribbean Currency Union (ECCU) countries.
          Let me help you plan the perfect island adventure!
        </p>
        <div className="mt-4 text-sm text-gray-500">
          <span className="inline-flex items-center space-x-2">
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

      <div className="mt-8 text-center">
        <p className="text-sm text-gray-500">
          💡 Try asking me about destinations, activities, or say "Create an itinerary" to get a personalized PDF!
        </p>
      </div>
    </div>
  );
};
export default EmptyState;
