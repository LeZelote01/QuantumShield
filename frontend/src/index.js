import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Hide loading screen once React app is mounted
setTimeout(() => {
  if (window.hideLoadingScreen) {
    window.hideLoadingScreen();
  }
}, 1000);