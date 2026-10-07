function PerformanceCard() {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm mb-6">
      <h2 className="text-sm font-semibold text-gray-900 mb-4 tracking-wide uppercase">
        PERFORMANCE
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 mb-4">
        {/* Primary Metric */}
        <div className="min-w-0">
          <div className="text-3xl md:text-4xl font-bold text-indigo-600 mb-1 whitespace-nowrap">
            &lt;2 sec
          </div>
          <p className="text-sm text-gray-600 leading-tight">
            Target end-to-end latency
          </p>
        </div>

        {/* Secondary Metric */}
        <div className="min-w-0">
          <div className="text-2xl md:text-3xl font-semibold text-gray-800 mb-1 whitespace-nowrap">
            ~38 ms
          </div>
          <p className="text-sm text-gray-600 leading-tight">
            Median decision latency
          </p>
        </div>

        {/* AWS Metric */}
        <div className="min-w-0">
          <div className="text-2xl md:text-3xl font-semibold mb-1">
            <span className="text-[#FF9900]">AWS</span>
          </div>
          <p className="text-sm text-gray-600 leading-tight">
            Low-latency deployment
          </p>
        </div>
      </div>

      {/* Supporting Note */}
      <p className="text-xs text-gray-500 leading-relaxed">
        Currently running on a low-processing-power free-tier environment, so current latency may be higher.
      </p>
    </div>
  );
}

export default PerformanceCard;
