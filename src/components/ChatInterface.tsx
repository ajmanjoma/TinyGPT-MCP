import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Send, Loader2, AlertCircle } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { apiService, ChatRequest, ChatResponse, SystemStatus, ToolInfo } from '../services/apiService';
import { StatusIndicator } from './StatusIndicator';
import { ToolGrid } from './ToolGrid';
import { ChatResponse as ChatResponseComponent } from './ChatResponse';
import { ExamplePrompts } from './ExamplePrompts';
import toast from 'react-hot-toast';

export const ChatInterface: React.FC = () => {
  const { user } = useAuth();
  const [prompt, setPrompt] = useState('');
  const [temperature, setTemperature] = useState(0.7);
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [tools, setTools] = useState<ToolInfo[]>([]);

  useEffect(() => {
    loadStatus();
    loadTools();
  }, []);

  const loadStatus = async () => {
    try {
      const statusData = await apiService.getStatus();
      setStatus(statusData);
    } catch (error) {
      console.error('Failed to load status:', error);
    }
  };

  const loadTools = async () => {
    try {
      const toolsData = await apiService.getTools();
      setTools(toolsData);
    } catch (error) {
      console.error('Failed to load tools:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() || !user) {
      if (!user) {
        toast.error('Please log in to use the assistant');
      }
      return;
    }

    setIsLoading(true);
    setResponse(null);

    try {
      const request: ChatRequest = {
        prompt: prompt.trim(),
        temperature,
        max_tokens: 500,
      };

      const chatResponse = await apiService.chat(request);
      setResponse(chatResponse);
      toast.success('Response generated successfully!');
    } catch (error: any) {
      console.error('Chat error:', error);
      toast.error(error.response?.data?.detail || 'Failed to generate response');
    } finally {
      setIsLoading(false);
    }
  };

  const handleExampleClick = (examplePrompt: string) => {
    setPrompt(examplePrompt);
  };

  if (!user) {
    return (
      <div className="text-center py-12">
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-4 rounded-full w-20 h-20 mx-auto mb-6">
          <AlertCircle className="w-12 h-12 text-white" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          Authentication Required
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Please log in to access the TinyGPT-MCP assistant and start chatting with AI.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Status and Tools */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <StatusIndicator status={status} />
        </div>
        <div className="lg:col-span-2">
          <ToolGrid tools={tools} />
        </div>
      </div>

      {/* Chat Interface */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700">
        {/* Input Section */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Your Message
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Ask me anything! Try: 'What's the weather in Paris and the price of Bitcoin?' or 'Tell me a joke and show Wikipedia info about AI.'"
                className="w-full p-4 border border-gray-300 dark:border-gray-600 rounded-lg resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 transition-all duration-200"
                rows={4}
                disabled={isLoading}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-2">
                  <label className="text-sm text-gray-600 dark:text-gray-300">
                    Temperature:
                  </label>
                  <input
                    type="range"
                    min="0.1"
                    max="1.0"
                    step="0.1"
                    value={temperature}
                    onChange={(e) => setTemperature(parseFloat(e.target.value))}
                    className="w-20"
                    disabled={isLoading}
                  />
                  <span className="text-sm text-gray-600 dark:text-gray-300 min-w-[2rem]">
                    {temperature}
                  </span>
                </div>
              </div>

              <motion.button
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                type="submit"
                disabled={isLoading || !prompt.trim()}
                className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-5 h-5" />
                    <span>Send</span>
                  </>
                )}
              </motion.button>
            </div>
          </form>
        </div>

        {/* Response Section */}
        {response && (
          <div className="p-6">
            <ChatResponseComponent response={response} />
          </div>
        )}

        {/* Example Prompts */}
        <div className="p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
          <ExamplePrompts onExampleClick={handleExampleClick} />
        </div>
      </div>
    </div>
  );
};