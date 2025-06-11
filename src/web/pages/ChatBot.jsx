import { h } from 'preact';
import { useState, useEffect, useRef } from 'preact/hooks';

// Firebase imports
import { initializeApp } from 'firebase/app';
import { getFirestore, collection, addDoc, serverTimestamp } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: "AIzaSyCdlY2aAh4vMeVpaDqaYTLGEio4xnr52bs",
  authDomain: "araqode-25038.firebaseapp.com",
  projectId: "araqode-25038",
  storageBucket: "araqode-25038.firebasestorage.app",
  messagingSenderId: "80695730852",
  appId: "1:80695730852:web:dc6669bb5b9c166d5cfc31"
};

const appId = typeof __app_id !== 'undefined' ? __app_id : 'default-app-id';

export default function ChatBot() {
  const [chatHistory, setChatHistory] = useState([]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [db, setDb] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [apiKey, setApiKey] = useState((typeof window !== 'undefined' && window.__gemini_api_key) ? window.__gemini_api_key : "");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    try {
      const firebaseApp = initializeApp(firebaseConfig);
      const firestoreDb = getFirestore(firebaseApp);
      setDb(firestoreDb);
      const newSessionId = crypto.randomUUID();
      setSessionId(newSessionId);
    } catch (error) {
      console.error("Failed to initialize Firebase or generate session ID:", error);
    }
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatHistory]);

  const sendMessageToGemini = async (message) => {
    setIsLoading(true);
    let chatHistoryForApi = [];
    chatHistoryForApi.push({ role: "user", parts: [{ text: message }] });
    const payload = { contents: chatHistoryForApi };
    try {
      const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`;
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const result = await response.json();
      if (result.candidates && result.candidates.length > 0 &&
          result.candidates[0].content && result.candidates[0].content.parts &&
          result.candidates[0].content.parts.length > 0) {
        const botResponse = result.candidates[0].content.parts[0].text;
        return botResponse;
      } else {
        return "I'm sorry, I couldn't generate a response.";
      }
    } catch (error) {
      return "There was an error connecting to the AI. Please try again.";
    } finally {
      setIsLoading(false);
    }
  };

  const saveInteractionToFirestore = async (userMsg, botMsg) => {
    if (!db || !sessionId) return;
    try {
      const chatSessionsRef = collection(db, `artifacts/${appId}/public/data/chatSessions`);
      await addDoc(chatSessionsRef, {
        sessionId: sessionId,
        timestamp: serverTimestamp(),
        userMessage: userMsg,
        botResponse: botMsg,
      });
    } catch (error) {
      // Ignore
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!userInput.trim()) return;
    const userMessage = userInput.trim();
    setChatHistory(prev => [...prev, { sender: 'user', message: userMessage }]);
    setUserInput('');
    const botResponse = await sendMessageToGemini(userMessage);
    setChatHistory(prev => [...prev, { sender: 'bot', message: botResponse }]);
    saveInteractionToFirestore(userMessage, botResponse);
  };

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #f0f4ff 0%, #e0e7ff 100%)', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 16, fontFamily: 'sans-serif', color: '#222' }}>
      <div style={{ width: '100%', maxWidth: 640, background: '#fff', borderRadius: 24, boxShadow: '0 4px 24px #0001', overflow: 'hidden', display: 'flex', flexDirection: 'column', height: '80vh' }}>
        <div style={{ background: 'linear-gradient(90deg, #2563eb 0%, #4f46e5 100%)', color: '#fff', padding: 16, textAlign: 'center', fontSize: 24, fontWeight: 700, borderTopLeftRadius: 24, borderTopRightRadius: 24, boxShadow: '0 2px 8px #0001' }}>
          Open Chatbot Prototype
        </div>
        {/* Debug: Show Gemini API Key if available */}
        <div style={{ background: '#fef3c7', color: '#92400e', padding: 8, fontSize: 12, textAlign: 'center', fontFamily: 'monospace', borderBottom: '1px solid #fde68a' }}>
          Gemini API Key: {apiKey ? (apiKey.length > 8 ? apiKey.slice(0, 4) + '...' + apiKey.slice(-4) : apiKey) : '(not set)'}
        </div>
        <div style={{ padding: 8, background: '#f3f4f6', borderBottom: '1px solid #eee', textAlign: 'center' }}>
          <input
            type="password"
            value={apiKey}
            onInput={e => setApiKey(e.target.value)}
            placeholder="Enter Gemini API Key"
            style={{
              padding: 10,
              borderRadius: 8,
              border: '2px solid #2563eb',
              width: 340,
              maxWidth: '95%',
              fontSize: 16,
              background: '#fff',
              color: '#222',
              outline: 'none',
              boxShadow: '0 2px 8px #2563eb22',
              margin: '0 auto',
              transition: 'border 0.2s, box-shadow 0.2s'
            }}
          />
        </div>
        <div style={{ flex: 1, padding: 24, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
          {chatHistory.length === 0 && (
            <div style={{ textAlign: 'center', color: '#888', fontStyle: 'italic', padding: 40 }}>
              Start a conversation! Your Session ID: <br /> <span style={{ fontWeight: 700, color: '#333', wordBreak: 'break-all' }}>{sessionId || 'Generating...'}</span>
            </div>
          )}
          {chatHistory.map((msg, index) => (
            <div key={index} style={{ display: 'flex', justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start' }}>
              <div style={{ maxWidth: '75%', padding: 12, borderRadius: 12, boxShadow: '0 1px 4px #0001', background: msg.sender === 'user' ? '#2563eb' : '#f3f4f6', color: msg.sender === 'user' ? '#fff' : '#222', borderBottomRightRadius: msg.sender === 'user' ? 0 : 12, borderBottomLeftRadius: msg.sender === 'user' ? 12 : 0 }}>
                <p style={{ whiteSpace: 'pre-wrap', margin: 0 }}>{msg.message}</p>
              </div>
            </div>
          ))}
          {isLoading && (
            <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
              <div style={{ maxWidth: '75%', padding: 12, borderRadius: 12, boxShadow: '0 1px 4px #0001', background: '#f3f4f6', color: '#222', borderBottomLeftRadius: 0 }}>
                <p style={{ animation: 'pulse 1.5s infinite' }}>Typing...</p>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
        <form onSubmit={handleSendMessage} style={{ padding: 16, background: '#f3f4f6', borderTop: '1px solid #e5e7eb', display: 'flex', alignItems: 'center', borderBottomLeftRadius: 24, borderBottomRightRadius: 24 }}>
          <input
            type="text"
            value={userInput}
            onInput={e => setUserInput(e.target.value)}
            placeholder="Type your message..."
            style={{ flex: 1, padding: 12, border: '1px solid #d1d5db', borderRadius: 8, outline: 'none', marginRight: 12 }}
            disabled={!sessionId}
          />
          <button
            type="submit"
            style={{ background: '#2563eb', color: '#fff', padding: 12, borderRadius: 8, border: 'none', fontWeight: 600, cursor: isLoading || !sessionId || !userInput.trim() ? 'not-allowed' : 'pointer', opacity: isLoading || !sessionId || !userInput.trim() ? 0.5 : 1 }}
            disabled={isLoading || !sessionId || !userInput.trim()}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
