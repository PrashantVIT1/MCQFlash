function ModeSelector({ selectedOption, onOptionChange }) {
  return (
    <div className="grid grid-cols-2 gap-3 mb-6">
      {/* Fast OCR Option */}
      <button
        onClick={() => onOptionChange(1)}
        className={`
          p-4 rounded-xl border-2 transition-all duration-200
          ${selectedOption === 1
            ? 'border-indigo-600 bg-indigo-50'
            : 'border-gray-200 bg-white hover:border-gray-300'
          }
        `}
      >
        <div className="text-center">
          <p className="font-semibold text-gray-900 mb-1">Fast OCR</p>
          <p className="text-xs text-gray-600">Extract text → solve</p>
        </div>
      </button>

      {/* Direct Image Option */}
      <button
        onClick={() => onOptionChange(2)}
        className={`
          p-4 rounded-xl border-2 transition-all duration-200
          ${selectedOption === 2
            ? 'border-indigo-600 bg-indigo-50'
            : 'border-gray-200 bg-white hover:border-gray-300'
          }
        `}
      >
        <div className="text-center">
          <p className="font-semibold text-gray-900 mb-1">Direct Image</p>
          <p className="text-xs text-gray-600">Image → solve</p>
        </div>
      </button>
    </div>
  );
}

export default ModeSelector;
