
import React from 'react';

interface ResultImageProps {
  src: string;
}

export const ResultImage: React.FC<ResultImageProps> = ({ src }) => {
  return (
    <div className="bg-gray-800/50 p-2 rounded-xl shadow-2xl border border-gray-700">
      <img
        src={src}
        alt="Generated architectural render"
        className="w-full h-auto rounded-lg"
      />
    </div>
  );
};
