import { Plus, FileText, Menu, X } from 'lucide-react';

function Sidebar({ isOpen, onToggle, onNewSession }) {
  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={onToggle}
        className="md:hidden fixed top-4 left-4 z-50 p-2 bg-white rounded-lg shadow-md border border-gray-200"
        aria-label="Toggle menu"
      >
        {isOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/50 z-40"
          onClick={onToggle}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed md:static inset-y-0 left-0 z-40
          w-64 bg-white border-r border-gray-200
          transform transition-transform duration-300 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}
      >
        <div className="flex flex-col h-full p-6">
          {/* Logo */}
          <div className="mb-8">
            <h1 className="text-2xl font-semibold text-gray-900">MCQFlash</h1>
            <p className="text-sm text-gray-500 mt-1">Snap. Solve. Instantly.</p>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-2">
            <button
              onClick={onNewSession}
              className="w-full flex items-center gap-3 px-4 py-3 text-left text-gray-700 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <Plus size={20} />
              <span className="font-medium">New Session</span>
            </button>

            <button
              className="w-full flex items-center gap-3 px-4 py-3 text-left text-gray-500 hover:bg-gray-50 rounded-lg transition-colors cursor-not-allowed opacity-60"
              disabled
            >
              <FileText size={20} />
              <span className="font-medium">References</span>
              <span className="ml-auto text-xs bg-gray-200 text-gray-600 px-2 py-0.5 rounded-full">
                Coming soon
              </span>
            </button>
          </nav>

          {/* Footer placeholder */}
          <div className="pt-6 border-t border-gray-200">
            <p className="text-xs text-gray-400">MCQFlash v1.0</p>
          </div>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;
