export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  className?: string;
}

export interface Message {
  id: string;
  content: string;
  sender: "user" | "ai";
  timestamp: Date;
  pdfId?: string;
  pdfGenerated?: boolean;
}

export interface UserInputProps {
  onSend?: (message: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

export interface SuggestedPrompt {
  id: string;
  text: string;
  category: string;
}
