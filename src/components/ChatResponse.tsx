import React from 'react';
import { motion } from 'framer-motion';
import { Brain, Wrench, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { ChatResponse as ChatResponseType } from '../services/apiService';

interface ChatResponseProps {
  response: ChatResponseType;
}

export const ChatResponse: React.FC<ChatResponseProps> = ({ response }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-6"
    >
      {/* Thought Process */}
      {response.thought && (
        <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
          <div className="flex items-center space-x-2 mb-3">
            <Brain className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            <h3 className="font-semibold text-blue-900 dark:text-blue-100">
              Thought Process
            </h3>
          </div>
          <p className="text-blue-800 dark:text-blue-200">
            {response.thought}
          </p>
        </div>
      )}

      {/* Tool Calls */}
      {response.tool_calls.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <Wrench className="w-5 h-5 text-green-600 dark:text-green-400" />
            <h3 className="font-semibold text-gray-900 dark:text-white">
              Tool Executions ({response.tool_calls.length})
            </h3>
          </div>
          
          <div className="grid gap-3">
            {response.tool_calls.map((toolCall, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`p-4 rounded-lg border ${
                  toolCall.success
                    ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
                    : 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-lg">
                      {getToolEmoji(toolCall.tool)}
                    </span>
                    <span className="font-medium text-gray-900 dark:text-white capitalize">
                      {toolCall.tool}
                    </span>
                    {toolCall.success ? (
                      <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400" />
                    ) : (
                      <AlertCircle className="w-4 h-4 text-red-600 dark:text-red-400" />
                    )}
                  </div>
                  <div className="flex items-center space-x-1 text-xs text-gray-500 dark:text-gray-400">
                    <Clock className="w-3 h-3" />
                    <span>{toolCall.execution_time.toFixed(2)}s</span>
                  </div>
                </div>

                {/* Parameters */}
                {Object.keys(toolCall.params).length > 0 && (
                  <div className="mb-2">
                    <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Parameters:
                    </div>
                    <div className="text-sm bg-gray-100 dark:bg-gray-700 p-2 rounded">
                      {Object.entries(toolCall.params).map(([key, value]) => (
                        <div key={key}>
                          <strong>{key}:</strong> {String(value)}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Result */}
                <div>
                  <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Result:
                  </div>
                  <div className="text-sm bg-gray-100 dark:bg-gray-700 p-2 rounded">
                    {formatToolResult(toolCall.result)}
                  </div>
                </div>

                {/* Error */}
                {toolCall.error && (
                  <div className="mt-2">
                    <div className="text-sm font-medium text-red-700 dark:text-red-300 mb-1">
                      Error:
                    </div>
                    <div className="text-sm text-red-600 dark:text-red-400">
                      {toolCall.error}
                    </div>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Final Answer */}
      <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4 border border-purple-200 dark:border-purple-800">
        <div className="flex items-center space-x-2 mb-3">
          <CheckCircle className="w-5 h-5 text-purple-600 dark:text-purple-400" />
          <h3 className="font-semibold text-purple-900 dark:text-purple-100">
            Final Answer
          </h3>
        </div>
        <div className="text-purple-800 dark:text-purple-200 whitespace-pre-wrap">
          {response.final_answer}
        </div>
      </div>

      {/* Metadata */}
      <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-4">
          <span>Model: {response.model_info.name}</span>
          <span>Tokens: {response.tokens_used}</span>
        </div>
        <span>Processing: {response.processing_time.toFixed(2)}s</span>
      </div>
    </motion.div>
  );
};

function getToolEmoji(toolName: string): string {
  const emojiMap: Record<string, string> = {
    weather: '🌦️',
    crypto: '🪙',
    wiki: '📚',
    search: '🔍',
    joke: '🤣',
    news: '📰',
  };
  return emojiMap[toolName] || '🔧';
}

function formatToolResult(result: any): string {
  if (typeof result === 'object') {
    return JSON.stringify(result, null, 2);
  }
  return String(result);
}