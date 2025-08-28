import { Globe, Heart } from "lucide-react";

const Navbar = () => {
  return (
    <header className="flex items-center justify-between px-[5%] py-2 bg-white border-b border-gray-200 shadow-sm">
      <div className="flex items-center space-x-3">
        <div className="w-12 h-12 flex items-center justify-center">
          <img
            src="/TropiTrek logo.png"
            alt="Trekki"
            className="w-full h-full object-contain"
          />
        </div>
        {/* <div>
          <span className="text-lg font-bold bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent">
            Trekki
          </span>
          <p className="text-xs text-gray-500">Caribbean Travel Assistant</p>
        </div> */}

      </div>

      <div className="flex items-center space-x-4">
        <div className="hidden md:flex items-center space-x-6 text-sm text-gray-600">
          <div className="flex items-center space-x-1">
            <Globe className="w-4 h-4 text-blue-500" />
            <span>8 ECCU Countries</span>
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
