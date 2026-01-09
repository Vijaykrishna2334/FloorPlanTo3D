
import React from 'react';
import { BuildingIcon } from './Icons';

export const Header: React.FC = () => {
  return (
    <header className="py-8 px-4 text-center border-b border-gray-700/50">
      <div className="inline-flex items-center mb-4">
        <BuildingIcon className="w-12 h-12 text-purple-400" />
        <h1 className="ml-4 text-4xl md:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-500">
          AI Architectural Visualizer
        </h1>
      </div>
      <p className="max-w-2xl mx-auto text-lg text-gray-400">
        Transform 2D floor plans into stunning, 3D furnished renders. Just upload your plan and a style reference to let Gemini work its magic.
      </p>
    </header>
  );
};
