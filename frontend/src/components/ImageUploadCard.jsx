import { Plus, X } from 'lucide-react';
import { useRef } from 'react';

function ImageUploadCard({ image, onImageChange, label }) {
  const fileInputRef = useRef(null);

  const handleCardClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
      const imageUrl = URL.createObjectURL(file);
      // Store both URL and file object
      onImageChange({ url: imageUrl, file: file });
    }
  };

  const handleRemove = (e) => {
    e.stopPropagation();
    onImageChange(null);
  };

  return (
    <div
      onClick={handleCardClick}
      className={`
        relative border-2 border-dashed rounded-xl p-6 md:p-8
        flex flex-col items-center justify-center
        cursor-pointer transition-all duration-200
        ${image
          ? 'border-gray-300 bg-white hover:border-gray-400'
          : 'border-gray-300 bg-white hover:border-indigo-400 hover:bg-indigo-50/50'
        }
        min-h-[200px] md:min-h-[280px]
      `}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        onChange={handleFileChange}
        className="hidden"
        aria-label={`Upload ${label}`}
      />

      {image ? (
        <>
          {/* Image Preview */}
          <img
            src={image.url || image}
            alt={label}
            className="w-full h-full object-contain max-h-[200px] md:max-h-[280px]"
          />

          {/* Remove Button */}
          <button
            onClick={handleRemove}
            className="absolute top-3 right-3 p-2 bg-white rounded-full shadow-md border border-gray-200 hover:bg-gray-50 transition-colors"
            aria-label="Remove image"
          >
            <X size={18} className="text-gray-600" />
          </button>
        </>
      ) : (
        <>
          {/* Empty State */}
          <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center mb-4">
            <Plus size={32} className="text-gray-400" />
          </div>
          <p className="text-gray-700 font-medium mb-1">Add Image</p>
          <p className="text-gray-500 text-sm text-center">
            Capture or upload MCQ
          </p>
        </>
      )}
    </div>
  );
}

export default ImageUploadCard;
