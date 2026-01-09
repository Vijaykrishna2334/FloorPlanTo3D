
import React, { useState, useRef, ChangeEvent } from 'react';
import { UploadIcon } from './Icons';

interface ImageUploaderProps {
  id: string;
  title: string;
  onImageUpload: (file: File) => void;
  disabled?: boolean;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({ id, title, onImageUpload, disabled = false }) => {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result as string);
      };
      reader.readAsDataURL(file);
      onImageUpload(file);
    }
  };

  const handleUploaderClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="bg-gray-800/50 p-6 rounded-xl shadow-lg border border-gray-700">
      <h3 className="text-xl font-semibold text-center mb-4 text-gray-300">{title}</h3>
      <div
        onClick={disabled ? undefined : handleUploaderClick}
        className={`relative aspect-video w-full border-2 border-dashed border-gray-600 rounded-lg flex items-center justify-center transition-all duration-300 ${!disabled ? 'cursor-pointer hover:border-purple-500 hover:bg-gray-800' : 'cursor-not-allowed bg-gray-800'}`}
      >
        <input
          type="file"
          id={id}
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
          accept="image/*"
          disabled={disabled}
        />
        {previewUrl ? (
          <img src={previewUrl} alt="Preview" className="object-contain w-full h-full rounded-lg" />
        ) : (
          <div className="text-center text-gray-500">
            <UploadIcon className="w-12 h-12 mx-auto mb-2" />
            <p>Click to upload an image</p>
          </div>
        )}
      </div>
    </div>
  );
};
