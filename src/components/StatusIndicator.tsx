import React from 'react';
import { motion } from 'framer-motion';
import { Activity, Users, Zap, AlertTriangle } from 'lucide-react';
import { SystemStatus } from '../services/apiService';

interface StatusIndicatorProps {
  status: SystemStatus | null;
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({ status }) => {
  if (!status) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-3">
          <div className="w-3 h-3 rounded-full bg-gray-400 animate-pulse" />
          <span className="text-gray-600 dark:text-gray-300">Loading status...</span>
        </div>
      </div>
    );
  }

  const isHealthy = status.status === 'healthy';
  const statusColor = isHealthy ? 'bg-green-500' : 'bg-red-500';
  const statusText = isHealthy ? 'System Online' : 'System Issues';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700"
    >
      <div className="space-y-4">
        {/* Main Status */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <motion.div
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              className={`w-3 h-3 rounded-full ${statusColor}`}
            />
            <span className="font-medium text-gray-900 dark:text-white">
              {statusText}
            </span>
          </div>
          <span className="text-sm text-gray-500 dark:text-gray-400">
            v{status.version}
          </span>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center space-x-2">
            <Activity className="w-4 h-4 text-blue-500" />
            <div>
              <div className="text-sm font-medium text-gray-900 dark:text-white">
                {status.tools_available}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Tools
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Users className="w-4 h-4 text-green-500" />
            <div>
              <div className="text-sm font-medium text-gray-900 dark:text-white">
                {status.active_users}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Active
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <Zap className="w-4 h-4 text-yellow-500" />
            <div>
              <div className="text-sm font-medium text-gray-900 dark:text-white">
                {status.requests_today}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Today
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {status.model_loaded ? (
              <div className="w-4 h-4 bg-green-500 rounded-full" />
            ) : (
              <AlertTriangle className="w-4 h-4 text-red-500" />
            )}
            <div>
              <div className="text-sm font-medium text-gray-900 dark:text-white">
                {status.model_loaded ? 'Ready' : 'Error'}
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400">
                Model
              </div>
            </div>
          </div>
        </div>

        {/* Uptime */}
        <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
          <div className="text-xs text-gray-500 dark:text-gray-400">
            Uptime: {Math.floor(status.uptime / 3600)}h {Math.floor((status.uptime % 3600) / 60)}m
          </div>
        </div>
      </div>
    </motion.div>
  );
};