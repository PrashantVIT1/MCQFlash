import { ArrowRight } from 'lucide-react';

function NextQuestionButton({ onClick }) {
  return (
    <button
      onClick={onClick}
      className="w-full py-4 px-6 rounded-xl font-semibold text-lg bg-white border-2 border-indigo-600 text-indigo-600 hover:bg-indigo-50 active:bg-indigo-100 transition-all duration-200 flex items-center justify-center gap-2"
    >
      Next Question
      <ArrowRight size={20} />
    </button>
  );
}

export default NextQuestionButton;
