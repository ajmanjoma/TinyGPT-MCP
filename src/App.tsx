import React from 'react';
import { Toaster } from 'react-hot-toast';
import { ChatInterface } from './components/ChatInterface';
import { Header } from './components/Header';
import { ThemeProvider } from './contexts/ThemeContext';
import { AuthProvider } from './contexts/AuthContext';

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
          <Header />
          <main className="container mx-auto px-4 py-8 max-w-6xl">
            <ChatInterface />
          </main>
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              className: 'dark:bg-gray-800 dark:text-white',
            }}
          />
        </div>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
