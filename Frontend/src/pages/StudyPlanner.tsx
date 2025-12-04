import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles } from 'lucide-react';

const StudyPlanner = () => {
  const [subjects, setSubjects] = useState('');
  const [difficulty, setDifficulty] = useState('medium');
  const [deadline, setDeadline] = useState('');
  const [schedule, setSchedule] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setSchedule(null);
    setError(null);

    try {
      const response = await fetch('http://localhost:5000/generate-study-plan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ subjects, difficulty, deadline }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setSchedule(data);

    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.");
      console.error("Failed to generate study plan:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-[#1C1C1C] mb-6">AI Study Planner</h1>
      
      <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Create Your Study Plan</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Subjects (comma separated)
            </label>
            <input
              type="text"
              value={subjects}
              onChange={(e) => setSubjects(e.target.value)}
              placeholder="e.g., Mathematics, Physics, Chemistry"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#E63946] focus:border-[#E63946] transition"
              required
              disabled={loading}
            />
          </div>
          
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Difficulty Level
              </label>
              <select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#E63946] focus:border-[#E63946] transition"
                disabled={loading}
              >
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Deadline
              </label>
              <input
                type="date"
                value={deadline}
                onChange={(e) => setDeadline(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#E63946] focus:border-[#E63946] transition"
                required
                disabled={loading}
              />
            </div>
          </div>
          
          <button
            type="submit"
            disabled={loading || !subjects || !deadline}
            className="w-full bg-[#E63946] text-white py-3 px-4 rounded-lg hover:bg-[#d32f3f] transition-colors duration-300 font-semibold flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                  className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                Generate Study Plan
              </>
            )}
          </button>
        </form>
      </div>
      
      <AnimatePresence>
        {loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="text-center p-6"
          >
             <p className="text-gray-600">AI is crafting your personalized plan...</p>
          </motion.div>
        )}

        {error && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg relative"
            role="alert"
          >
            <strong className="font-bold">Error: </strong>
            <span className="block sm:inline">{error}</span>
          </motion.div>
        )}

        {schedule && (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-xl shadow-lg p-6"
          >
            <h2 className="text-2xl font-bold text-[#1C1C1C] mb-4">Your Personalized Study Plan</h2>
            <div className="mb-4 grid md:grid-cols-3 gap-2 text-sm">
              <p><span className="font-semibold text-gray-600">Subjects:</span> {schedule.subjects.join(', ')}</p>
              <p><span className="font-semibold text-gray-600">Difficulty:</span> <span className="capitalize">{schedule.difficulty}</span></p>
              <p><span className="font-semibold text-gray-600">Deadline:</span> {schedule.deadline}</p>
            </div>
            
            <div className="space-y-4">
              {schedule.plan.map((day: any, index: number) => (
                <motion.div 
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="border border-gray-200 rounded-lg p-4 bg-gray-50"
                >
                  <h3 className="font-semibold text-lg text-[#E63946] mb-2">{day.day}</h3>
                  <ul className="space-y-2 list-disc list-inside">
                    {day.tasks.map((task: string, taskIndex: number) => (
                      <li key={taskIndex} className="text-gray-700">{task}</li>
                    ))}
                  </ul>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default StudyPlanner;