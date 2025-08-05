import { Palmtree, Globe, Heart } from "lucide-react";

const Navbar = () => {
  return (
    <header className="flex items-center justify-between px-[5%] py-4 bg-white border-b border-gray-200 shadow-sm">
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-green-500 rounded-full flex items-center justify-center">
          <Palmtree className="w-6 h-6 text-white" />
        </div>
        <div>
          <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent">
            TropicTrek
          </span>
          <p className="text-xs text-gray-500">Caribbean Travel Assistant</p>
        </div>
      </div>
      
      <div className="flex items-center space-x-4">
        <div className="hidden md:flex items-center space-x-6 text-sm text-gray-600">
          <div className="flex items-center space-x-1">
            <Globe className="w-4 h-4 text-blue-500" />
            <span>6 ECCU Countries</span>
          </div>
          <div className="flex items-center space-x-1">
            <Heart className="w-4 h-4 text-red-500" />
            <span>AI-Powered</span>
          </div>
        </div>
        
        <div className="w-8 h-8 bg-gradient-to-br from-orange-400 to-pink-400 rounded-full flex items-center justify-center">
          <span className="text-white text-sm font-semibold">🌴</span>
        </div>
      </div>
    </header>
  );
};
export default Navbar;
