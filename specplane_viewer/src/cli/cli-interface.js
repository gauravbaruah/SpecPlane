/**
 * CLI Interface Container
 * Orchestrates the file watching, conversion, and Docusaurus setup workflow
 */

const path = require('path');
const fs = require('fs-extra');
const { FileWatcher } = require('../file-watcher/file-watcher');
const { DocusaurusSetup } = require('../docusaurus/docusaurus-setup');
const { DocusaurusRunner } = require('../docusaurus/docusaurus-runner');
const { Spec2MDConverter } = require('../converter/spec2md-converter');
const { Logger } = require('../utils/logger');

class CLIInterface {
  constructor() {
    this.logger = new Logger();
    this.fileWatcher = new FileWatcher();
    this.docusaurusSetup = new DocusaurusSetup();
    this.docusaurusRunner = new DocusaurusRunner();
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
      const outputPath = path.join(path.dirname(specsPath), '.specplane', 'markdown');
      
      // Check if specs directory exists
      if (!await fs.pathExists(specsPath)) {
        throw new Error(`Specs directory not found: ${specsPath}`);
      }
      
      this.logger.info(`Specs directory: ${specsPath}`);
      this.logger.info(`Output directory: ${outputPath}`);
      
      // Convert existing specs first
      await this.converter.convertDirectory(specsPath, outputPath);
      
      // Setup Docusaurus project
      await this.docusaurusSetup.setupProject(outputPath, { port });
      
      // Install lunr search plugin
      await this.docusaurusRunner.installLunrSearchPlugin();
      
      if (watch) {
        // Start watching for changes
        await this.startWatching(specsPath, outputPath);
      }
      
      // Start Docusaurus development server
      await this.docusaurusRunner.startDevServer({ port, open });
      
    } catch (error) {
      this.logger.error('Serve command failed:', error);
      throw error;
    }
  }

  /**
   * Convert command - just convert specs to markdown
   */
  async convert(specsDirectory, options = {}) {
    const { output = './.specplane/markdown' } = options;
    
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
   * Setup command - setup Docusaurus for existing markdown
   */
  async setup(markdownDirectory, options = {}) {
    try {
      this.logger.info('Setting up Docusaurus project...');
      
      const markdownPath = path.resolve(markdownDirectory);
      
      if (!await fs.pathExists(markdownPath)) {
        throw new Error(`Markdown directory not found: ${markdownPath}`);
      }
      
      await this.docusaurusSetup.setupProject(markdownPath, options);
      await this.docusaurusRunner.installLunrSearchPlugin();
      
      this.logger.info('Docusaurus setup completed successfully!');
      
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
          // Convert the changed file
          await this.converter.convertFile(filePath, outputPath);
          
          // Trigger Docusaurus rebuild
          await this.docusaurusRunner.triggerRebuild();
          
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
   * Cleanup resources
   */
  async cleanup() {
    await this.stopWatching();
    
    if (this.currentProcess) {
      this.currentProcess.kill();
    }
    
    this.logger.info('Cleanup completed');
  }
}

module.exports = { CLIInterface };
