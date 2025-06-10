import { h } from 'preact';
import { useState } from 'preact/hooks';
import FileBrowser from './pages/FileBrowser.jsx';

// Simple router for future extensibility
export default function Router() {
  // For now, always render FileBrowser
  // You can add more routes/pages here later
  return <FileBrowser />;
}
