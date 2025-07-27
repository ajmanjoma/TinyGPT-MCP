import React from 'react';
import { motion } from 'framer-motion';
import { Cloud, DollarSign, BookOpen, Search, Smile, Newspaper, CheckCircle, XCircle } from 'lucide-react';
import { ToolInfo } from '../services/apiService';

interface ToolGridProps {
  tools: ToolInfo[];
}

const toolIcons: Record<string, React.ReactNode> = {
  weather: <Cloud className="w-6 h-6" />,
  crypto: <DollarSign className="w-6 h-6" />,
  wiki: <BookOpen className="w-6 h-6" />,
  search: <Search className="w-6 h-6" />,
  joke: <Smile className="w-6 h-6" />,
  news: <Newspaper className="w-6 h-6" />,
};

const toolColors: Record<string, string> = {
  weather: 'from-blue-500 to-blue-600',
  crypto: 'from-yellow-500 to-yellow-600',
  wiki: 'from-green-500 to-green-600',
  search: 'from-purple-500 to-purple-600',
  joke: 'from-pink-500 to-pink-600',
  news: 'from-red-500 to-red-600',
};

export const ToolGrid: React.FC<ToolGridProps> = ({ tools }) => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Available Tools
      </h3>
      
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        {tools.map((tool, index) => (
          <motion.div
            key={tool.name}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            className={`relative p-4 rounded-lg bg-gradient-to-br ${
              toolColors[tool.name] || 'from-gray-500 to-gray-600'
            } text-white`}
          >
            {/* Status Indicator */}
            <div className="absolute top-2 right-2">
              {tool.enabled ? (
                <CheckCircle className="w-4 h-4 text-green-200" />
              ) : (
                <XCircle className="w-4 h-4 text-red-200" />
              )}
            </div>

            {/* Icon */}
            <div className="flex justify-center mb-2">
              {toolIcons[tool.name] || <Search className="w-6 h-6" />}
            </div>

            {/* Name */}
            <div className="text-center">
              <div className="text-sm font-medium capitalize">
                {tool.name}
              </div>
              <div className="text-xs opacity-75 mt-1">
                {tool.category}
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {tools.length === 0 && (
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          <Search className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No tools available</p>
        </div>
      )}
    </div>
  );
};