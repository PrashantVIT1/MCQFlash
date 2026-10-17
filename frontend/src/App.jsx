import { useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import ImageUploadCard from './components/ImageUploadCard';
import SolveButton from './components/SolveButton';
import AnswerCard from './components/AnswerCard';
import NextQuestionButton from './components/NextQuestionButton';
import PerformanceCard from './components/PerformanceCard';
import ModeSelector from './components/ModeSelector';
import { compressImage } from './utils/imageCompression';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_BASE_URL) {
  throw new Error('VITE_API_BASE_URL is not configured');
}

function App() {
  const [image1, setImage1] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [answer, setAnswer] = useState(null);
  const [error, setError] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [selectedOption, setSelectedOption] = useState(2); // Default: Direct Image

  const handleNewSession = () => {
    setImage1(null);
    setAnswer(null);
    setError(null);
    setIsLoading(false);
  };

  const handleSolve = async () => {
    if (!image1) {
      setError('Add at least one image to solve the question.');
      return;
    }

    setError(null);
    setIsLoading(true);

    try {
      // Use image1 if available
      const imageToProcess = image1;
      const file = imageToProcess.file;

      if (!file) {
        throw new Error('No file data available');
      }

      // Compress image before sending
      const compressedBlob = await compressImage(file, 1280, 0.80);

      // Create FormData for multipart upload
      const formData = new FormData();
      formData.append('option', String(selectedOption));
      formData.append('image', compressedBlob, 'compressed.jpg');

      // Send to backend
      const response = await fetch(`${API_BASE_URL}/solve`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to process image');
      }

      const data = await response.json();

      // Parse response and set answer
      setAnswer({
        answer: data.message || 'Unknown',
        answerText: '', // Backend returns message directly
        confidence: parseFloat(data.confidence) || 0,
        latency: data.total_latency || '0ms',
        ocrTime: data.ocr_time || '0ms',
        decisionLatency: data.decision_latency || '0ms',
        mode: data.mode || 'unknown'
      });

    } catch (err) {
      console.error('Error solving MCQ:', err);
      setError(err.message || 'Failed to process the image. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleNextQuestion = () => {
    setImage1(null);
    setAnswer(null);
    setError(null);
    setIsLoading(false);
    // Preserve selectedOption (don't reset it)
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
        onNewSession={handleNewSession}
      />

      <main className="flex-1 flex flex-col overflow-hidden">
        <Header />

        <div className="flex-1 overflow-y-auto p-4 md:p-8">
          <div className="max-w-4xl mx-auto">
            {/* Performance Card */}
            <PerformanceCard />

            {/* Image Upload Area */}
            <div className="grid grid-cols-1 md:grid-cols-1 gap-4 md:gap-6 mb-6">
              <ImageUploadCard
                image={image1}
                onImageChange={setImage1}
                label="Image 1"
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-lg text-sm">
                {error}
              </div>
            )}

            {/* Mode Selector */}
            <ModeSelector
              selectedOption={selectedOption}
              onOptionChange={setSelectedOption}
            />

            {/* Solve Button */}
            <div className="mb-6">
              <SolveButton
                onClick={handleSolve}
                isLoading={isLoading}
                disabled={!image1}
              />
            </div>

            {/* Loading State */}
            {isLoading && (
              <div className="flex items-center justify-center py-12">
                <div className="text-center">
                  <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-gray-300 border-t-indigo-600 mb-4"></div>
                  <p className="text-gray-600">Analyzing question...</p>
                </div>
              </div>
            )}

            {/* Answer Card */}
            {answer && !isLoading && (
              <div className="mb-6">
                <AnswerCard answer={answer} />
                <div className="mt-6">
                  <NextQuestionButton onClick={handleNextQuestion} />
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
