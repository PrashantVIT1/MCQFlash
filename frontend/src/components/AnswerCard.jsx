function AnswerCard({ answer }) {
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
            <p className="text-sm text-gray-500 mb-1">Response time</p>
            <p className="text-lg font-semibold text-gray-900">
              {answer.latency}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AnswerCard;
