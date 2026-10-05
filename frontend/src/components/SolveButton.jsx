function SolveButton({ onClick, isLoading, disabled }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled || isLoading}
      className={`
        w-full py-4 px-6 rounded-xl font-semibold text-lg
        transition-all duration-200
        ${disabled
          ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
          : isLoading
            ? 'bg-indigo-500 text-white cursor-wait'
            : 'bg-indigo-600 text-white hover:bg-indigo-700 active:bg-indigo-800 hover:shadow-lg'
        }
      `}
    >
      {isLoading ? 'Solving...' : 'Solve MCQ'}
    </button>
  );
}

export default SolveButton;
