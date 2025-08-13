import { Send } from "lucide-react";
import { useState } from "react";
import Button from "./Button";

const UserInput: React.FC<{
  onSendMessage: (message: string) => void;
  disabled: boolean;
  value: string;
  onChange: (value: string) => void;
}> = ({ onSendMessage, disabled, value, onChange }) => {
  const [charCount, setCharCount] = useState(0);
  const maxChars = 1000;

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;
    if (newValue.length <= maxChars) {
      onChange(newValue);
      setCharCount(newValue.length);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (value.trim() && !disabled) {
        onSendMessage(value.trim());
      }
    }
  };

  const handleSend = () => {
    if (value.trim() && !disabled) {
      onSendMessage(value.trim());
    }
  };

  return (
    <div className="p-4 bg-white border-t border-gray-200 shadow-lg">
      <div className="relative max-w-4xl mx-auto">
        <textarea
          value={value}
          onChange={handleInputChange}
          onKeyPress={handleKeyPress}
          placeholder="Write a message here..."
          disabled={disabled}
          className="w-full p-4 pr-24 border border-gray-300 rounded-xl resize-none bg-white text-gray-900 placeholder-gray-500 transition-all duration-200"
          rows={3}
        />

        <div className="absolute bottom-3 right-3 flex items-center space-x-3">
          <span
            className={`text-xs ${
              charCount > maxChars * 0.9 ? "text-red-500" : "text-gray-400"
            }`}
          >
            {charCount}/{maxChars}
          </span>

          <Button
            onClick={handleSend}
            disabled={!value.trim() || disabled}
            className="flex items-center space-x-2"
          >
            <Send className="w-4 h-4" />
            <span>Send</span>
          </Button>
        </div>
      </div>
    </div>
  );
};

export default UserInput;
