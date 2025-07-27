import React from 'react';
import { motion } from 'framer-motion';

interface ExamplePromptsProps {
  onExampleClick: (prompt: string) => void;
}

const examplePrompts = [
  "What's the weather in Paris and the price of Bitcoin?",
  "Tell me a joke and show Wikipedia info about artificial intelligence.",
  "Search who won the last football world cup and get crypto prices for ETH.",
  "Give me news on technology and a summary from Wikipedia about machine learning.",
  "What's the weather in Tokyo and tell me a programming joke?",
  "Search for recent AI developments and show me the price of Dogecoin.",
];

export const ExamplePrompts: React.FC<ExamplePromptsProps> = ({ onExampleClick }) => {
  return (
    <div>
      <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        Try these examples:
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
        {examplePrompts.map((prompt, index) => (
          <motion.button
            key={index}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => onExampleClick(prompt)}
            className="text-left p-3 text-sm text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors duration-200 border border-transparent hover:border-blue-200 dark:hover:border-blue-800"
          >
            "{prompt}"
          </motion.button>
        ))}
      </div>
    </div>
  );
};