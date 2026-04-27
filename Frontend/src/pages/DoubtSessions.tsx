import { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, Send, Plus } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { apiUrl } from '../utils/api';

interface Message {
  id: string;
  sender: 'user' | 'mentor';
  text: string;
  timestamp: string;
}

interface Session {
  id: string;
  title: string;
  last_message: string;
  timestamp: string;
  updated_at: string;
  messages: Message[];
}

const DoubtSessions = () => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSession, setActiveSession] = useState<Session | null>(null);
  const [inputText, setInputText] = useState('');
  const [loadingSessions, setLoadingSessions] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user, token } = useAuth();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    const loadSessions = async () => {
      setLoadingSessions(true);
      setError('');

      try {
        const query = user?.email ? `?user_email=${encodeURIComponent(user.email)}` : '';
        const response = await fetch(apiUrl(`/doubt-sessions${query}`), {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
        });
        const data = await response.json();

        if (!response.ok) {
          throw new Error(data?.error || 'Failed to load doubt sessions');
        }

        setSessions(data.sessions || []);
        setActiveSession(data.sessions?.[0] || null);
      } catch (err: any) {
        setError(err.message || 'Failed to load doubt sessions');
      } finally {
        setLoadingSessions(false);
      }
    };

    loadSessions();
  }, [user?.email]);

  useEffect(() => {
    if (activeSession) {
      scrollToBottom();
    }
  }, [activeSession?.messages]);

  const updateSessionState = (updatedSession: Session) => {
    setActiveSession(updatedSession);
    setSessions((currentSessions) =>
      currentSessions.map((session) => (session.id === updatedSession.id ? updatedSession : session))
    );
  };

  const handleSend = async () => {
    if (!inputText.trim() || !activeSession || sending) return;

    const question = inputText.trim();
    setInputText('');
    setError('');
    setSending(true);

    const newMessage: Message = {
      id: `${Date.now()}`,
      sender: 'user',
      text: question,
      timestamp: new Date().toISOString(),
    };

    updateSessionState({
      ...activeSession,
      messages: [...activeSession.messages, newMessage],
      last_message: question,
      updated_at: new Date().toISOString(),
    });

    try {
      const response = await fetch(apiUrl(`/doubt-sessions/${activeSession.id}/messages`), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ question }),
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data?.error || 'Failed to ask doubt');
      }

      updateSessionState(data.session);
    } catch (err: any) {
      setError(err.message || 'Failed to ask doubt');
    } finally {
      setSending(false);
    }
  };

  const handleNewSession = async () => {
    setError('');

    try {
      const response = await fetch(apiUrl('/doubt-sessions'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          title: 'New Doubt Session',
          user_email: user?.email,
        }),
      });
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data?.error || 'Failed to create session');
      }

      setSessions((currentSessions) => [data.session, ...currentSessions]);
      setActiveSession(data.session);
    } catch (err: any) {
      setError(err.message || 'Failed to create session');
    }
  };

  if (!activeSession) {
    return (
      <div className="max-w-7xl mx-auto h-[calc(100vh-8rem)]">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <h1 className="text-3xl font-bold text-[#1C1C1C] mb-2">Doubt Sessions</h1>
          <p className="text-gray-600">Get personalized help with your learning</p>
        </motion.div>
        <div className="flex items-center justify-center h-[calc(100%-5rem)]">
          <div className="text-center">
            {loadingSessions && <p className="mb-4 text-gray-600">Loading sessions...</p>}
            {error && <p className="mb-4 text-sm text-[#E63946]">{error}</p>}
            <button
              onClick={handleNewSession}
              className="px-6 py-3 bg-[#E63946] text-white rounded-xl hover:bg-[#d32f3b] transition-all duration-300 flex items-center justify-center gap-2 mb-4 font-semibold"
            >
              <Plus className="w-5 h-5" />
              Start a New Session
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto h-[calc(100vh-8rem)]">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <h1 className="text-3xl font-bold text-[#1C1C1C] mb-2">Doubt Sessions</h1>
        <p className="text-gray-600">Get personalized help with your learning</p>
      </motion.div>

      <div className="grid lg:grid-cols-4 gap-6 h-[calc(100%-5rem)]">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:col-span-1 bg-white rounded-2xl shadow-md p-4 overflow-y-auto"
        >
          <button
            onClick={handleNewSession}
            className="w-full py-3 bg-[#E63946] text-white rounded-xl hover:bg-[#d32f3b] transition-all duration-300 flex items-center justify-center gap-2 mb-4 font-semibold"
          >
            <Plus className="w-5 h-5" />
            New Session
          </button>

          <div className="space-y-2">
            {sessions.map((session) => (
              <button
                key={session.id}
                onClick={() => setActiveSession(session)}
                className={`w-full text-left p-4 rounded-xl transition-all duration-300 ${
                  activeSession.id === session.id
                    ? 'bg-[#E63946] bg-opacity-10 border-2 border-[#E63946]'
                    : 'bg-gray-50 hover:bg-gray-100'
                }`}
              >
                <h4 className="font-semibold text-[#1C1C1C] mb-1 truncate">
                  {session.title}
                </h4>
                <p className="text-sm text-gray-500 truncate">{session.last_message}</p>
              </button>
            ))}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:col-span-3 bg-white rounded-2xl shadow-md flex flex-col"
        >
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-[#E63946] bg-opacity-10 rounded-xl flex items-center justify-center">
                <MessageSquare className="w-6 h-6 text-[#E63946]" />
              </div>
              <div>
                <h3 className="font-bold text-[#1C1C1C]">{activeSession.title}</h3>
                <p className="text-sm text-gray-500">Active Session</p>
              </div>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {error && (
              <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}

            {activeSession.messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[70%] rounded-2xl px-4 py-3 ${
                    message.sender === 'user'
                      ? 'bg-[#E63946] text-white'
                      : 'bg-gray-100 text-[#1C1C1C]'
                  }`}
                >
                  <p className="text-sm leading-relaxed">{message.text}</p>
                  <p
                    className={`text-xs mt-2 ${
                      message.sender === 'user' ? 'text-white opacity-70' : 'text-gray-500'
                    }`}
                  >
                    {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </p>
                </div>
              </motion.div>
            ))}
            {sending && (
              <div className="flex justify-start">
                <div className="max-w-[70%] rounded-2xl bg-gray-100 px-4 py-3 text-sm text-gray-500">
                  Shikshak is thinking...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div className="p-6 border-t border-gray-200">
            <div className="flex gap-3">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                placeholder={sending ? 'Shikshak is thinking...' : 'Ask your doubt...'}
                disabled={sending}
                className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-[#E63946] focus:outline-none transition-all duration-300"
              />
              <button
                onClick={handleSend}
                disabled={sending || !inputText.trim()}
                className="px-6 py-3 bg-[#E63946] text-white rounded-xl hover:bg-[#d32f3b] transition-all duration-300 shadow-md hover:shadow-lg"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default DoubtSessions;
