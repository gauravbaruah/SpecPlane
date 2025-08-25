/**
 * Docusaurus Runner Component
 * Handles dependency checking, server management, and lunr plugin integration
 */

const { spawn } = require('child_process');
const fs = require('fs-extra');
const path = require('path');
const { Logger } = require('../utils/logger');

class DocusaurusRunner {
  constructor() {
    this.logger = new Logger();
    this.currentProcess = null;
    this.isRunning = false;
    this.currentPort = null;
  }

  /**
   * Check for required dependencies
   */
  async checkDependencies() {
    try {
      this.logger.info('Checking required dependencies...');
      
      const results = {
        node: await this.checkNodeVersion(),
        npm: await this.checkPackageManager('npm'),
        yarn: await this.checkPackageManager('yarn'),
        docusaurus: await this.checkDocusaurusCLI()
      };
      
      const missingDeps = Object.entries(results)
        .filter(([_, available]) => !available)
        .map(([dep, _]) => dep);
      
      if (missingDeps.length > 0) {
        this.logger.warn(`Missing dependencies: ${missingDeps.join(', ')}`);
        this.logger.info('Please run "npm install" in the .specplane directory to install Docusaurus dependencies');
      } else {
        this.logger.success('All required dependencies are available');
      }
      
      return {
        success: missingDeps.length === 0,
        results,
        missing: missingDeps
      };
      
    } catch (error) {
      this.logger.error('Failed to check dependencies:', error);
      throw error;
    }
  }

  /**
   * Check Node.js version
   */
  async checkNodeVersion() {
    try {
      const version = process.version;
      const majorVersion = parseInt(version.slice(1).split('.')[0]);
      
      if (majorVersion >= 18) {
        this.logger.debug(`Node.js version: ${version} ✓`);
        return true;
      } else {
        this.logger.warn(`Node.js version ${version} is below required version 18.0`);
        return false;
      }
    } catch (error) {
      this.logger.error('Failed to check Node.js version:', error);
      return false;
    }
  }

  /**
   * Check if package manager is available
   */
  async checkPackageManager(manager) {
    try {
      return new Promise((resolve) => {
        const process = spawn(manager, ['--version'], { stdio: 'ignore' });
        
        process.on('close', (code) => {
          if (code === 0) {
            this.logger.debug(`${manager} is available ✓`);
            resolve(true);
          } else {
            this.logger.warn(`${manager} is not available`);
            resolve(false);
          }
        });
        
        process.on('error', () => {
          this.logger.warn(`${manager} is not available`);
          resolve(false);
        });
      });
    } catch (error) {
      this.logger.error(`Failed to check ${manager}:`, error);
      return false;
    }
  }

  /**
   * Check if Docusaurus CLI is available
   */
  async checkDocusaurusCLI() {
    try {
      // Check if we're in a Docusaurus project directory with dependencies
      const packageJsonPath = path.join(process.cwd(), 'package.json');
      if (await fs.pathExists(packageJsonPath)) {
        const packageJson = await fs.readJson(packageJsonPath);
        if (packageJson.dependencies && packageJson.dependencies['@docusaurus/core']) {
          this.logger.debug('Docusaurus dependencies are available locally ✓');
          return true;
        }
      }
      
      // Check if we're in the parent directory and .specplane has dependencies
      const specplanePackageJsonPath = path.join(process.cwd(), '.specplane', 'package.json');
      if (await fs.pathExists(specplanePackageJsonPath)) {
        const packageJson = await fs.readJson(specplanePackageJsonPath);
        if (packageJson.dependencies && packageJson.dependencies['@docusaurus/core']) {
          this.logger.debug('Docusaurus dependencies are available in .specplane directory ✓');
          return true;
        }
      }
      
      // Fallback: try to run npx docusaurus --version
      return new Promise((resolve) => {
        const process = spawn('npx', ['docusaurus', '--version'], { stdio: 'ignore' });
        
        process.on('close', (code) => {
          if (code === 0) {
            this.logger.debug('Docusaurus CLI is available via npx ✓');
            resolve(true);
          } else {
            this.logger.warn('Docusaurus CLI is not available');
            resolve(false);
          }
        });
        
        process.on('error', () => {
          this.logger.warn('Docusaurus CLI is not available');
          resolve(false);
        });
      });
    } catch (error) {
      this.logger.error('Failed to check Docusaurus CLI:', error);
      return false;
    }
  }

  /**
   * Install lunr search plugin
   */
  async installLunrSearchPlugin() {
    try {
      this.logger.info('Installing lunr search plugin...');
      
      // Check if we're in a Docusaurus project directory
      const packageJsonPath = path.join(process.cwd(), 'package.json');
      if (!await fs.pathExists(packageJsonPath)) {
        this.logger.warn('Not in a Docusaurus project directory, skipping lunr installation');
        return { success: false, reason: 'Not in project directory' };
      }
      
      // Check if lunr search plugin is already installed
      const packageJson = await fs.readJson(packageJsonPath);
      if (packageJson.dependencies && packageJson.dependencies['docusaurus-lunr-search']) {
        this.logger.info('Lunr search plugin is already installed ✓');
        return { success: true, alreadyInstalled: true };
      }
      
      // Install the plugin
      this.logger.info('Installing docusaurus-lunr-search...');
      
      return new Promise((resolve) => {
        const installProcess = spawn('npm', ['install', 'docusaurus-lunr-search'], {
          stdio: 'pipe',
          cwd: process.cwd()
        });
        
        let output = '';
        installProcess.stdout.on('data', (data) => {
          output += data.toString();
        });
        
        installProcess.stderr.on('data', (data) => {
          output += data.toString();
        });
        
        installProcess.on('close', (code) => {
          if (code === 0) {
            this.logger.success('Lunr plugin installed successfully ✓');
            resolve({ success: true, alreadyInstalled: false });
          } else {
            this.logger.error('Failed to install lunr plugin');
            this.logger.debug('Install output:', output);
            resolve({ success: false, reason: 'Installation failed', output });
          }
        });
        
        installProcess.on('error', (error) => {
          this.logger.error('Failed to install lunr plugin:', error);
          resolve({ success: false, reason: 'Process error', error: error.message });
        });
      });
      
    } catch (error) {
      this.logger.error('Failed to install lunr plugin:', error);
      return { success: false, reason: 'Unexpected error', error: error.message };
    }
  }

  /**
   * Start Docusaurus development server
   */
  async startDevServer(options = {}) {
    try {
      const { port = 3001, open = false } = options;
      
      if (this.isRunning) {
        this.logger.warn('Docusaurus server is already running');
        return { success: false, reason: 'Already running' };
      }
      
      // Check dependencies first
      const depsCheck = await this.checkDependencies();
      if (!depsCheck.success) {
        this.logger.error('Cannot start server - missing dependencies');
        return { success: false, reason: 'Missing dependencies', missing: depsCheck.missing };
      }
      
      this.logger.info(`Starting Docusaurus development server on port ${port}...`);
      
      // Start the server
      const args = ['start', '--port', port.toString()];
      if (open) {
        args.push('--open');
      }
      
      // Determine the correct working directory for Docusaurus
      // If we're in the parent directory, use .specplane subdirectory
      let docusaurusCwd = process.cwd();
      const specplaneConfigPath = path.join(process.cwd(), '.specplane', 'docusaurus.config.js');
      if (await fs.pathExists(specplaneConfigPath)) {
        docusaurusCwd = path.join(process.cwd(), '.specplane');
        this.logger.debug(`Using Docusaurus working directory: ${docusaurusCwd}`);
      }
      
      this.currentProcess = spawn('npx', ['docusaurus', ...args], {
        stdio: 'pipe',
        cwd: docusaurusCwd
      });
      
      this.currentPort = port;
      
      // Handle process events
      this.currentProcess.stdout.on('data', (data) => {
        const output = data.toString();
        if (output.includes('Local:')) {
          this.isRunning = true;
          this.logger.success(`Docusaurus server started successfully on port ${port}`);
        }
        process.stdout.write(output);
      });
      
      this.currentProcess.stderr.on('data', (data) => {
        const output = data.toString();
        if (output.includes('Error:')) {
          this.logger.error('Docusaurus server error:', output);
        }
        process.stderr.write(output);
      });
      
      this.currentProcess.on('close', (code) => {
        this.isRunning = false;
        this.currentProcess = null;
        this.currentPort = null;
        
        if (code === 0) {
          this.logger.info('Docusaurus server stopped normally');
        } else {
          this.logger.warn(`Docusaurus server stopped with code ${code}`);
        }
      });
      
      this.currentProcess.on('error', (error) => {
        this.logger.error('Failed to start Docusaurus server:', error);
        this.isRunning = false;
        this.currentProcess = null;
        this.currentPort = null;
      });
      
      // Wait a bit for the server to start
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      return { success: this.isRunning, port };
      
    } catch (error) {
      this.logger.error('Failed to start development server:', error);
      return { success: false, reason: 'Start failed', error: error.message };
    }
  }

  /**
   * Build production site
   */
  async buildProduction(options = {}) {
    try {
      this.logger.info('Building Docusaurus production site...');
      
      // Check dependencies first
      const depsCheck = await this.checkDependencies();
      if (!depsCheck.success) {
        this.logger.error('Cannot build - missing dependencies');
        return { success: false, reason: 'Missing dependencies', missing: depsCheck.missing };
      }
      
      // Determine the correct working directory for Docusaurus
      let docusaurusCwd = process.cwd();
      const specplaneConfigPath = path.join(process.cwd(), '.specplane', 'docusaurus.config.js');
      if (await fs.pathExists(specplaneConfigPath)) {
        docusaurusCwd = path.join(process.cwd(), '.specplane');
        this.logger.debug(`Using Docusaurus working directory for build: ${docusaurusCwd}`);
      }
      
      return new Promise((resolve) => {
        const buildProcess = spawn('npx', ['docusaurus', 'build'], {
          stdio: 'pipe',
          cwd: docusaurusCwd
        });
        
        let output = '';
        buildProcess.stdout.on('data', (data) => {
          output += data.toString();
          process.stdout.write(data);
        });
        
        buildProcess.stderr.on('data', (data) => {
          output += data.toString();
          process.stderr.write(data);
        });
        
        buildProcess.on('close', (code) => {
          if (code === 0) {
            this.logger.success('Production build completed successfully ✓');
            resolve({ success: true, output });
          } else {
            this.logger.error('Production build failed');
            resolve({ success: false, reason: 'Build failed', output });
          }
        });
        
        buildProcess.on('error', (error) => {
          this.logger.error('Build process error:', error);
          resolve({ success: false, reason: 'Process error', error: error.message });
        });
      });
      
    } catch (error) {
      this.logger.error('Failed to build production site:', error);
      return { success: false, reason: 'Build failed', error: error.message };
    }
  }

  /**
   * Stop the current server
   */
  async stopServer() {
    if (this.currentProcess && this.isRunning) {
      try {
        this.logger.info('Stopping Docusaurus server...');
        
        this.currentProcess.kill('SIGTERM');
        
        // Wait for graceful shutdown
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        if (this.currentProcess.exitCode === null) {
          this.logger.warn('Server did not stop gracefully, forcing...');
          this.currentProcess.kill('SIGKILL');
        }
        
        this.isRunning = false;
        this.currentProcess = null;
        this.currentPort = null;
        
        this.logger.info('Docusaurus server stopped');
        
      } catch (error) {
        this.logger.error('Failed to stop server:', error);
      }
    }
  }

  /**
   * Trigger rebuild (for file watching)
   */
  async triggerRebuild() {
    try {
      this.logger.info('Triggering Docusaurus rebuild...');
      
      if (!this.isRunning) {
        this.logger.warn('Cannot trigger rebuild - server not running');
        return { success: false, reason: 'Server not running' };
      }
      
      // For development mode, Docusaurus auto-rebuilds
      // We just need to wait for the file change to be processed
      this.logger.info('Waiting for Docusaurus to process changes...');
      
      return { success: true, message: 'Rebuild triggered' };
      
    } catch (error) {
      this.logger.error('Failed to trigger rebuild:', error);
      return { success: false, reason: 'Rebuild failed', error: error.message };
    }
  }

  /**
   * Get server status
   */
  getServerStatus() {
    return {
      isRunning: this.isRunning,
      port: this.currentPort,
      processId: this.currentProcess?.pid || null
    };
  }

  /**
   * Check if server is healthy
   */
  async checkServerHealth() {
    if (!this.isRunning || !this.currentPort) {
      return { healthy: false, reason: 'Server not running' };
    }
    
    try {
      // Simple health check - could be enhanced with actual HTTP request
      return { healthy: true, port: this.currentPort };
    } catch (error) {
      return { healthy: false, reason: 'Health check failed', error: error.message };
    }
  }
}

module.exports = { DocusaurusRunner };
