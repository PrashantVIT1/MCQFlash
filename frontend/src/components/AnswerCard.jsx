function AnswerCard({ answer }) {
  const modeLabel = answer.mode === 'ocr' ? 'Fast OCR' : 'Direct Image';

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Answer</h2>

      <div className="space-y-4">
        {/* Answer Display */}
        <div className="flex items-baseline gap-3">
          <span className="text-2xl md:text-3xl font-bold text-indigo-600">
            {answer.answer}
          </span>
        </div>

        {/* Mode */}
        <div className="pt-2">
          <p className="text-sm text-gray-500 mb-1">Mode</p>
          <p className="text-base font-semibold text-gray-900">{modeLabel}</p>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-100">
          <div>
            <p className="text-sm text-gray-500 mb-1">Confidence</p>
            <p className="text-lg font-semibold text-gray-900">
              {typeof answer.confidence === 'number'
                ? `${answer.confidence.toFixed(2)}%`
                : answer.confidence}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500 mb-1">Total latency</p>
            <p className="text-lg font-semibold text-gray-900">
              {answer.latency}
            </p>
          </div>
        </div>

        {/* Performance Breakdown */}
        {(answer.ocrTime || answer.decisionLatency) && (
          <div className="pt-4 border-t border-gray-100">
            <p className="text-xs text-gray-500 mb-2">Performance breakdown</p>
            <div className="grid grid-cols-2 gap-4">
              {answer.ocrTime && (
                <div>
                  <p className="text-xs text-gray-500 mb-1">OCR time</p>
                  <p className="text-sm font-medium text-gray-900">{answer.ocrTime}</p>
                </div>
              )}
              {answer.decisionLatency && (
                <div>
                  <p className="text-xs text-gray-500 mb-1">Decision latency</p>
                  <p className="text-sm font-medium text-gray-900">{answer.decisionLatency}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AnswerCard;
