import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Brain, Sun, Moon, User, LogOut, Settings } from 'lucide-react';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';
import { AuthModal } from './AuthModal';

export const Header: React.FC = () => {
  const { isDark, toggleTheme } = useTheme();
  const { user, logout } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);

  return (
    <>
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {/* Logo */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center space-x-3"
            >
              <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-2 rounded-lg">
                <Brain className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  TinyGPT-MCP
                </h1>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  AI Assistant with Tool Calling
                </p>
              </div>
            </motion.div>

            {/* Actions */}
            <div className="flex items-center space-x-3">
              {/* Theme Toggle */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={toggleTheme}
                className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                {isDark ? (
                  <Sun className="w-5 h-5 text-yellow-500" />
                ) : (
                  <Moon className="w-5 h-5 text-blue-600" />
                )}
              </motion.button>

              {/* User Menu */}
              {user ? (
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600 dark:text-gray-300">
                    Welcome, {user.username}
                  </span>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={logout}
                    className="p-2 rounded-lg bg-red-100 dark:bg-red-900/20 hover:bg-red-200 dark:hover:bg-red-900/40 transition-colors text-red-600 dark:text-red-400"
                  >
                    <LogOut className="w-5 h-5" />
                  </motion.button>
                </div>
              ) : (
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setShowAuthModal(true)}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  <User className="w-4 h-4" />
                  <span>Login</span>
                </motion.button>
              )}
            </div>
          </div>
        </div>
      </header>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
      />
    </>
  );
};