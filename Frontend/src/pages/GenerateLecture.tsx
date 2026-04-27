import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Download, Video, FileText, HelpCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { apiUrl } from '../utils/api';

interface GeneratedAssets {
  slides_path: string;
  voice_path: string;
  slides_url?: string;
  voice_url?: string;
  video_path: string | null;
  video_local_path?: string | null;
  slide_images: string[];
  quiz: QuizQuestion[];
}

interface QuizQuestion {
  question: string;
  options: string[];
  correct: number;
}

const isAbsoluteUrl = (value: string) => /^https?:\/\//i.test(value);

const filenameFromPath = (path: string) => path.split(/[\\/]/).pop() || path;

const mediaSrc = (path: string | null | undefined) => {
  if (!path) return '';
  if (isAbsoluteUrl(path)) return path;
  return apiUrl(`/media/${filenameFromPath(path)}`);
};

const GenerateLecture = () => {
  const [topic, setTopic] = useState('');
  const [audience, setAudience] = useState('High School');
  const [duration, setDuration] = useState('5 min');
  const [theme, setTheme] = useState('Minimalist');
  const [generating, setGenerating] = useState(false);
  const [generated, setGenerated] = useState(false);
  const [progress, setProgress] = useState(0);
  const [generatedAssets, setGeneratedAssets] = useState<GeneratedAssets | null>(null);
  const [error, setError] = useState('');
  const { user, token } = useAuth();

  const handleGenerate = async () => {
    setGenerating(true);
    setGenerated(false);
    setProgress(0);
    setGeneratedAssets(null);
    setError('');

    const progressTimer = window.setInterval(() => {
      setProgress(current => Math.min(current + 8, 90));
    }, 1200);

    try {
      const response = await fetch(apiUrl('/generate'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ prompt: topic, theme: theme, user_email: user?.email }),
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(data?.error || `Request failed with status ${response.status}`);
      }

      if (!data || !Array.isArray(data.slide_images) || !data.slides_path) {
        throw new Error(data?.error || 'Backend returned an unexpected response.');
      }

      console.log('API Response:', data);
      setGeneratedAssets(data);
      setProgress(100);
      setGenerated(true);

    } catch (error: any) {
      console.error('Error generating lecture:', error);
      setError(error.message || 'Failed to generate lecture assets.');
    } finally {
      window.clearInterval(progressTimer);
      setGenerating(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-bold text-[#1C1C1C] mb-2">Generate Lecture</h1>
        <p className="text-gray-600">Transform your ideas into complete educational materials</p>
      </motion.div>

      <AnimatePresence mode="wait">
        {!generating && !generated && (
          <motion.div
            key="form"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="bg-white rounded-2xl p-8 shadow-lg"
          >
            <div className="space-y-6">
              {error && (
                <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                  {error}
                </div>
              )}

              <div>
                <label className="block text-sm font-semibold text-[#1C1C1C] mb-2">
                  Topic
                </label>
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="Explain the water cycle for middle school students"
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-[#E63946] focus:outline-none transition-all duration-300"
                />
              </div>

              <div className="grid md:grid-cols-3 gap-6">
                <div>
                  <label className="block text-sm font-semibold text-[#1C1C1C] mb-2">
                    Target Audience
                  </label>
                  <select
                    value={audience}
                    onChange={(e) => setAudience(e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-[#E63946] focus:outline-none transition-all duration-300"
                  >
                    <option>Primary</option>
                    <option>High School</option>
                    <option>College</option>
                    <option>Corporate</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-[#1C1C1C] mb-2">
                    Duration
                  </label>
                  <select
                    value={duration}
                    onChange={(e) => setDuration(e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-[#E63946] focus:outline-none transition-all duration-300"
                  >
                    <option>2 min</option>
                    <option>5 min</option>
                    <option>10 min</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-[#1C1C1C] mb-2">
                    Visual Theme
                  </label>
                  <select
                    value={theme}
                    onChange={(e) => setTheme(e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-[#E63946] focus:outline-none transition-all duration-300"
                  >
                    <option>Minimalist</option>
                    <option>Chalkboard</option>
                    <option>Corporate</option>
                  </select>
                </div>
              </div>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={handleGenerate}
                disabled={!topic}
                className="w-full py-4 bg-gradient-to-r from-[#E63946] to-[#d32f3b] text-white rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <Sparkles className="w-5 h-5" />
                Generate Assets
              </motion.button>
            </div>
          </motion.div>
        )}

        {generating && (
          <motion.div
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="bg-white rounded-2xl p-12 shadow-lg text-center"
          >
            <div className="max-w-md mx-auto">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                className="w-20 h-20 mx-auto mb-6 bg-gradient-to-r from-[#E63946] to-[#d32f3b] rounded-full flex items-center justify-center"
              >
                <Sparkles className="w-10 h-10 text-white" />
              </motion.div>

              <h2 className="text-2xl font-bold text-[#1C1C1C] mb-4">
                Creating Your Lecture...
              </h2>

              <div className="w-full bg-gray-200 rounded-full h-3 mb-6">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  className="h-full bg-gradient-to-r from-[#E63946] to-[#d32f3b] rounded-full"
                  transition={{ duration: 0.3 }}
                />
              </div>

              <div className="space-y-2 text-sm text-gray-600">
                <p className={progress >= 25 ? 'text-[#E63946] font-semibold' : ''}>
                  ✓ Generating Slides
                </p>
                <p className={progress >= 50 ? 'text-[#E63946] font-semibold' : ''}>
                  {progress >= 50 ? '✓' : '○'} Adding Voiceover
                </p>
                <p className={progress >= 75 ? 'text-[#E63946] font-semibold' : ''}>
                  {progress >= 75 ? '✓' : '○'} Creating Quiz
                </p>
                <p className={progress === 100 ? 'text-[#E63946] font-semibold' : ''}>
                  {progress === 100 ? '✓' : '○'} Done!
                </p>
              </div>
            </div>
          </motion.div>
        )}

        {generated && generatedAssets && (
          <motion.div
            key="output"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-6"
          >
            <div className="grid md:grid-cols-2 gap-6">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 }}
                className="bg-white rounded-2xl p-6 shadow-lg"
              >
                <div className="flex items-center gap-3 mb-4">
                  <FileText className="w-6 h-6 text-[#E63946]" />
                  <h3 className="text-xl font-bold text-[#1C1C1C]">Slides</h3>
                </div>
                <div className="grid grid-cols-2 gap-3 mb-4">
                  {generatedAssets.slide_images.map((image: string, index: number) => (
                    <img
                      key={index}
                      src={mediaSrc(image)}
                      alt={`Slide ${index + 1}`}
                      className="w-full h-auto rounded-lg shadow-md"
                    />
                  ))}
                </div>
                <button
                  onClick={() => {
                    const slidesTarget = generatedAssets.slides_url || generatedAssets.slides_path;
                    if (isAbsoluteUrl(slidesTarget)) {
                      window.open(slidesTarget, '_blank');
                    } else {
                      const filename = filenameFromPath(slidesTarget);
                      window.open(apiUrl(`/download/${filename}`), '_blank');
                    }
                  }}
                  className="w-full py-2 bg-[#E63946] text-white rounded-xl hover:bg-[#d32f3b] transition-all duration-300 flex items-center justify-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  Download Slides (.PDF)
                </button>
              </motion.div>

              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
                className="bg-white rounded-2xl p-6 shadow-lg"
              >
                <div className="flex items-center gap-3 mb-4">
                  <Video className="w-6 h-6 text-[#E63946]" />
                  <h3 className="text-xl font-bold text-[#1C1C1C]">Video</h3>
                </div>
                <div className="aspect-video bg-gradient-to-br from-gray-800 to-gray-900 rounded-lg mb-4 flex items-center justify-center">
                  {generatedAssets.video_path ? (
                    <video controls src={mediaSrc(generatedAssets.video_path)} className="w-full h-full rounded-lg"></video>
                  ) : (
                    <p className="px-4 text-center text-sm text-white">
                      Video generation did not return a playable file. Slides are still available.
                    </p>
                  )}
                </div>
                <button
                  onClick={() => window.open(mediaSrc(generatedAssets.video_path), '_blank')}
                  disabled={!generatedAssets.video_path}
                  className="w-full py-2 bg-[#E63946] text-white rounded-xl hover:bg-[#d32f3b] transition-all duration-300 flex items-center justify-center gap-2"
                >
                  <Download className="w-4 h-4" />
                  Download Video (.MP4)
                </button>
              </motion.div>
            </div>

            {generatedAssets.quiz.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="bg-white rounded-2xl p-6 shadow-lg"
              >
                <div className="flex items-center gap-3 mb-5">
                  <HelpCircle className="w-6 h-6 text-[#E63946]" />
                  <h3 className="text-xl font-bold text-[#1C1C1C]">Quiz</h3>
                </div>

                <div className="space-y-4">
                  {generatedAssets.quiz.map((question, questionIndex) => (
                    <div key={questionIndex} className="rounded-xl border border-gray-200 bg-gray-50 p-4">
                      <p className="mb-3 font-semibold text-[#1C1C1C]">
                        {questionIndex + 1}. {question.question}
                      </p>
                      <div className="grid gap-2 md:grid-cols-2">
                        {question.options.map((option, optionIndex) => (
                          <div
                            key={optionIndex}
                            className={`rounded-lg px-3 py-2 text-sm ${
                              optionIndex === question.correct
                                ? 'border border-green-200 bg-green-50 text-green-800'
                                : 'border border-gray-200 bg-white text-gray-700'
                            }`}
                          >
                            {option}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}


            <button
              onClick={() => {
                setGenerated(false);
                setTopic('');
              }}
              className="w-full py-3 bg-gray-200 text-[#1C1C1C] rounded-xl hover:bg-gray-300 transition-all duration-300 font-semibold"
            >
              Generate New Lecture
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default GenerateLecture;
