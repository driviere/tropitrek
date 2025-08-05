import React from "react";
import { type ButtonProps } from "../lib/types";

const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  disabled = false,
  className = "",
}) => {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        px-4 py-2 
        bg-transparent 
        text-black 
        border border-gray-600 
        rounded-lg 
        hover:bg-gray-700 
        hover:text-white 
        disabled:opacity-50 
        disabled:cursor-not-allowed 
        disabled:hover:bg-transparent 
        disabled:hover:text-black
        transition-all 
        duration-200 
        ease-in-out
        focus:outline-none 
        focus:ring-2 
        focus:ring-gray-500 
        focus:ring-opacity-50
        ${className}
      `}
    >
      {children}
    </button>
  );
};

export default Button;
