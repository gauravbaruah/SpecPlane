/**
 * Logger utility for SpecPlane Viewer
 * Writes events to JSONL file and console output
 */

const fs = require('fs-extra');
const path = require('path');

class Logger {
  constructor() {
    this.logFile = path.join(process.cwd(), 'specplane-viewer.log');
    this.initializeLogFile();
  }

  /**
   * Initialize the log file
   */
  async initializeLogFile() {
    try {
      // Ensure log directory exists
      const logDir = path.dirname(this.logFile);
      await fs.ensureDir(logDir);
      
      // Create log file if it doesn't exist
      if (!await fs.pathExists(this.logFile)) {
        await fs.writeFile(this.logFile, '');
      }
    } catch (error) {
      console.error('Failed to initialize log file:', error.message);
    }
  }

  /**
   * Write log entry to JSONL file
   */
  async writeLog(level, message, data = {}) {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      level,
      message,
      ...data
    };

    try {
      const logLine = JSON.stringify(logEntry) + '\n';
      await fs.appendFile(this.logFile, logLine);
    } catch (error) {
      console.error('Failed to write to log file:', error.message);
    }
  }

  /**
   * Log info message
   */
  info(message, data = {}) {
    console.log(`[INFO] ${message}`);
    this.writeLog('info', message, data);
  }

  /**
   * Log warning message
   */
  warn(message, data = {}) {
    console.warn(`[WARN] ${message}`);
    this.writeLog('warn', message, data);
  }

  /**
   * Log error message
   */
  error(message, data = {}) {
    console.error(`[ERROR] ${message}`);
    this.writeLog('error', message, data);
  }

  /**
   * Log debug message
   */
  debug(message, data = {}) {
    if (process.env.DEBUG) {
      console.log(`[DEBUG] ${message}`);
      this.writeLog('debug', message, data);
    }
  }

  /**
   * Log success message
   */
  success(message, data = {}) {
    console.log(`✅ ${message}`);
    this.writeLog('success', message, data);
  }

  /**
   * Get log file path
   */
  getLogFilePath() {
    return this.logFile;
  }

  /**
   * Clear log file
   */
  async clearLog() {
    try {
      await fs.writeFile(this.logFile, '');
      this.info('Log file cleared');
    } catch (error) {
      console.error('Failed to clear log file:', error.message);
    }
  }
}

module.exports = { Logger };
