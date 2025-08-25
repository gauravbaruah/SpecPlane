/**
 * File Watcher Component
 * Monitors specified directories for YAML file changes and triggers conversions
 */

const chokidar = require('chokidar');
const path = require('path');
const { Logger } = require('../utils/logger');

class FileWatcher {
  constructor() {
    this.logger = new Logger();
    this.watcher = null;
    this.isWatching = false;
    this.watchedPaths = new Set();
  }

  /**
   * Watch directory for file changes
   */
  async watchDirectory(directoryPath, callback) {
    if (this.isWatching) {
      this.logger.warn('Already watching a directory, stopping previous watcher');
      await this.stopWatching();
    }

    try {
      this.logger.info(`Starting file watcher for: ${directoryPath}`);
      
      // Configure watcher with appropriate options
      this.watcher = chokidar.watch(directoryPath, {
        ignored: [
          /(^|[\/\\])\../, // Ignore hidden files
          /\.specplane/, // Ignore .specplane directory
          /node_modules/, // Ignore node_modules
          /\.git/, // Ignore git directory
          /\.DS_Store/, // Ignore macOS system files
          /\.tmp$/, // Ignore temporary files
          /\.swp$/, // Ignore vim swap files
        ],
        persistent: true,
        ignoreInitial: true,
        awaitWriteFinish: {
          stabilityThreshold: 2000, // Wait 2 seconds for file to stabilize
          pollInterval: 100
        }
      });

      // Set up event handlers
      this.watcher
        .on('add', (filePath) => this.handleFileChange(filePath, 'added', callback))
        .on('change', (filePath) => this.handleFileChange(filePath, 'modified', callback))
        .on('unlink', (filePath) => this.handleFileChange(filePath, 'removed', callback))
        .on('error', (error) => this.handleError(error))
        .on('ready', () => this.handleReady());

      this.isWatching = true;
      this.watchedPaths.add(directoryPath);
      
      this.logger.success(`File watcher started successfully for: ${directoryPath}`);
      
    } catch (error) {
      this.logger.error('Failed to start file watcher:', error);
      throw error;
    }
  }

  /**
   * Handle file change events
   */
  handleFileChange(filePath, changeType, callback) {
    // Only process YAML files
    if (this.isYamlFile(filePath)) {
      this.logger.info(`YAML file ${changeType}: ${filePath}`);
      
      // Call the callback with file information
      if (typeof callback === 'function') {
        try {
          callback(filePath, changeType);
        } catch (error) {
          this.logger.error(`Error in file change callback: ${error.message}`);
        }
      }
    } else {
      this.logger.debug(`Non-YAML file ${changeType}: ${filePath}`);
    }
  }

  /**
   * Handle watcher ready event
   */
  handleReady() {
    this.logger.info('File watcher is ready and monitoring for changes');
  }

  /**
   * Handle watcher errors
   */
  handleError(error) {
    this.logger.error('File watcher error:', error);
  }

  /**
   * Check if file is a YAML file
   */
  isYamlFile(filePath) {
    const ext = path.extname(filePath).toLowerCase();
    return ext === '.yaml' || ext === '.yml';
  }

  /**
   * Stop watching for file changes
   */
  async stopWatching() {
    if (this.watcher && this.isWatching) {
      try {
        await this.watcher.close();
        this.watcher = null;
        this.isWatching = false;
        this.watchedPaths.clear();
        
        this.logger.info('File watcher stopped successfully');
      } catch (error) {
        this.logger.error('Error stopping file watcher:', error);
      }
    }
  }

  /**
   * Get current watching status
   */
  isWatching() {
    return this.isWatching;
  }

  /**
   * Get list of watched paths
   */
  getWatchedPaths() {
    return Array.from(this.watchedPaths);
  }

  /**
   * Add additional directory to watch
   */
  addDirectory(directoryPath) {
    if (this.watcher && this.isWatching) {
      this.watcher.add(directoryPath);
      this.watchedPaths.add(directoryPath);
      this.logger.info(`Added directory to watch: ${directoryPath}`);
    }
  }

  /**
   * Remove directory from watching
   */
  removeDirectory(directoryPath) {
    if (this.watcher && this.isWatching) {
      this.watcher.unwatch(directoryPath);
      this.watchedPaths.delete(directoryPath);
      this.logger.info(`Removed directory from watch: ${directoryPath}`);
    }
  }
}

module.exports = { FileWatcher };
