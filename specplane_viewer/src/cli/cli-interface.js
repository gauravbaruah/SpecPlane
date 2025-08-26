/**
 * CLI Interface Container
 * Orchestrates the file watching, conversion, and Docusaurus setup workflow
 */

const path = require('path');
const fs = require('fs-extra');
const { FileWatcher } = require('../file-watcher/file-watcher');
const { DocusaurusHandler } = require('../docusaurus/docusaurus-handler');
const { Spec2MDConverter } = require('../converter/spec2md-converter');
const { Logger } = require('../utils/logger');

class CLIInterface {
  constructor() {
    this.logger = new Logger();
    this.fileWatcher = new FileWatcher();
    this.docusaurusHandler = new DocusaurusHandler();
    this.converter = new Spec2MDConverter();
    
    this.isWatching = false;
    this.currentProcess = null;
  }

  /**
   * Main serve command - convert specs and serve via Docusaurus
   */
  async serve(specsDirectory, options = {}) {
    const { port = 3001, watch = false, open = false } = options;
    
    try {
      this.logger.info('Starting SpecPlane Viewer...');
      
      // Resolve absolute paths
      const specsPath = path.resolve(specsDirectory);
      const outputPath = path.join(path.dirname(specsPath), '.specplane', 'specs_viewer', 'docs');
      
      // Check if specs directory exists
      if (!await fs.pathExists(specsPath)) {
        throw new Error(`Specs directory not found: ${specsPath}`);
      }
      
      this.logger.info(`Specs directory: ${specsPath}`);
      this.logger.info(`Output directory: ${outputPath}`);
      
      // Setup Docusaurus project first
      const projectPath = path.dirname(outputPath);
      await this.docusaurusHandler.setupProject(projectPath, { port });
      
      // Convert existing specs to the docs folder
      const docsPath = this.docusaurusHandler.getDocsPath();
      await this.converter.convertDirectory(specsPath, docsPath);
      
      if (watch) {
        // Start watching for changes
        await this.startWatching(specsPath, outputPath);
      }
      
      // Start Docusaurus development server
      await this.docusaurusHandler.startDevServer(port);
      
    } catch (error) {
      this.logger.error('Serve command failed:', error);
      throw error;
    }
  }

  /**
   * Convert command - just convert specs to markdown
   */
  async convert(specsDirectory, options = {}) {
    const { output = './.specplane/specs_viewer/docs' } = options;
    
    try {
      this.logger.info('Converting SpecPlane specs to Markdown...');
      
      const specsPath = path.resolve(specsDirectory);
      const outputPath = path.resolve(output);
      
      if (!await fs.pathExists(specsPath)) {
        throw new Error(`Specs directory not found: ${specsPath}`);
      }
      
      await this.converter.convertDirectory(specsPath, outputPath);
      this.logger.info('Conversion completed successfully!');
      
    } catch (error) {
      this.logger.error('Convert command failed:', error);
      throw error;
    }
  }

  /**
   * Setup command - setup Docusaurus project
   */
  async setup(projectDirectory, options = {}) {
    try {
      this.logger.info('Setting up Docusaurus project...');
      
      const projectPath = path.resolve(projectDirectory);
      
      // Create the directory if it doesn't exist
      if (!await fs.pathExists(projectPath)) {
        this.logger.info(`Creating project directory: ${projectPath}`);
        await fs.ensureDir(projectPath);
      }
      
      await this.docusaurusHandler.setupProject(projectPath, options);
      
      this.logger.info('Docusaurus project setup completed successfully!');
      
    } catch (error) {
      this.logger.error('Setup command failed:', error);
      throw error;
    }
  }

  /**
   * Start watching for file changes
   */
  async startWatching(specsPath, outputPath) {
    this.isWatching = true;
    
    this.logger.info('Starting file watcher...');
    
    this.fileWatcher.watchDirectory(specsPath, async (filePath, changeType) => {
      if (this.isWatching) {
        this.logger.info(`File ${changeType}: ${filePath}`);
        
        try {
          // Convert the changed file to the docs folder
          const docsPath = this.docusaurusHandler.getDocsPath();
          await this.converter.convertFile(filePath, docsPath);
          
          // Docusaurus will auto-reload since we're watching the docs folder
          this.logger.info('Markdown updated, Docusaurus will auto-reload');
          
        } catch (error) {
          this.logger.error(`Error processing file change: ${error.message}`);
        }
      }
    });
    
    this.logger.info('File watcher started successfully');
  }

  /**
   * Stop watching for file changes
   */
  async stopWatching() {
    if (this.isWatching) {
      this.isWatching = false;
      await this.fileWatcher.stopWatching();
      this.logger.info('File watcher stopped');
    }
  }

  /**
   * Start Docusaurus server
   */
  async startServer(options = {}) {
    const { port = 3001 } = options;
    
    try {
      this.logger.info('Starting Docusaurus server...');
      
      // Check if project exists
      const projectPath = './.specplane';
      if (!await fs.pathExists(projectPath)) {
        throw new Error('Docusaurus project not found. Please run "setup" first.');
      }
      
      // Set the project path for the handler
      this.docusaurusHandler.setProjectPath(projectPath);
      
      // Start the server
      await this.docusaurusHandler.startDevServer(port);
      
    } catch (error) {
      this.logger.error('Start server failed:', error);
      throw error;
    }
  }

  /**
   * Stop Docusaurus server
   */
  async stopServer() {
    try {
      this.logger.info('Stopping Docusaurus server...');
      
      if (await this.docusaurusHandler.isServerRunning()) {
        await this.docusaurusHandler.stopDevServer();
        this.logger.info('Server stopped successfully');
      } else {
        this.logger.info('No server is currently running');
      }
      
    } catch (error) {
      this.logger.error('Stop server failed:', error);
      throw error;
    }
  }

  /**
   * Check server status
   */
  async serverStatus() {
    try {
      const status = await this.docusaurusHandler.getServerStatus();
      
      if (status.running) {
        this.logger.info(`Server is running (PID: ${status.pid}, Port: ${status.port})`);
      } else {
        this.logger.info('Server is not running');
      }
      
      return status;
      
    } catch (error) {
      this.logger.error('Status check failed:', error);
      throw error;
    }
  }

  /**
   * Cleanup resources
   */
  async cleanup() {
    await this.stopWatching();
    
    // Stop Docusaurus server if running
    if (await this.docusaurusHandler.isServerRunning()) {
      await this.docusaurusHandler.stopDevServer();
    }
    
    this.logger.info('Cleanup completed');
  }
}

module.exports = { CLIInterface };
