import { h } from 'preact';
import { useState } from 'preact/hooks';
import FileBrowser from './pages/FileBrowser.jsx';
import ChatBot from './pages/ChatBot.jsx';

// Simple router for future extensibility
export default function Router() {
  const [route, setRoute] = useState('files');
  return (
    <div>
      <nav style={{ padding: 12, borderBottom: '1px solid #eee', marginBottom: 16 }}>
        <button onClick={() => setRoute('files')} style={{ marginRight: 8, fontWeight: route === 'files' ? 'bold' : 'normal' }}>File Browser</button>
        <button onClick={() => setRoute('chat')} style={{ fontWeight: route === 'chat' ? 'bold' : 'normal' }}>Chat Bot</button>
      </nav>
      {route === 'files' ? <FileBrowser /> : <ChatBot />}
    </div>
  );
}
