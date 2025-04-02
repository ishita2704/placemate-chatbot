import React from 'react';
import { BackgroundPaths } from "@/components/ui/background-paths";
import { useNavigate } from 'react-router-dom';
import { Facebook, Instagram, Twitter } from 'lucide-react';
import {ButtonColorful} from "@/components/ui/button-colorful";
import { RainbowButton } from "@/components/ui/rainbow-button";
import bot from "../assets/bot.jpg"  // adjust the path as needed

const Navbar = () => {
    const navigate=useNavigate() ;
    return (
      <nav className="fixed w-full z-50 bg-black/80 backdrop-blur-sm border-b border-gray-800">
        <div className="container mx-auto px-4 py-3 flex justify-between items-center">
          <div className="text-white">
           <img src={bot} alt="placemate logo" width={170} height={150}/>
          </div>

          <div>
            {/* <RainbowButton onClick={() => navigate("/Placemate-Chatbot")}>
              Discover Placemate →
            </RainbowButton>{" "} */}
            <ButtonColorful
              onClick={() => navigate("/Placemate-Chatbot")}
              label="Get Started"
            />
          </div>
        </div>
      </nav>
    );
  };


  const Footer = () => {
    return (
      <footer className="bg-black border-t border-gray-800 text-gray-400">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center md:items-start">
            <div className="mb-6 md:mb-0 text-center md:text-left">
              <h3 className="text-white font-semibold text-lg mb-2">Placemate</h3>
              <p className="text-sm max-w-xs">
              Your Ultimate Guide to JEC Placement
              
              </p>
            </div>
            
            
            
            <div className="flex space-x-4">
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
              <Instagram />
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
              <Twitter />
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
              <Facebook />
              </a>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-6 pt-6 text-sm text-center">
            &copy; {new Date().getFullYear()} Placemate. All rights reserved.
          </div>
        </div>
      </footer>
    );
  };
const Home = () => {
  return (
    <div className="bg-black min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-grow pt-3">
        <BackgroundPaths title="Placemate" />
      </main>
      <Footer />
    </div>
  );
};

export default Home;