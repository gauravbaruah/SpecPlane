const fs = require('fs-extra');
const path = require('path');
const { spawn, execSync } = require('child_process');
const { Logger } = require('../utils/logger');

class DocusaurusHandler {
  constructor() {
    this.projectPath = null;
    this.docusaurusPath = null;
    this.serverProcess = null;
    this.serverPID = null;
    this.logger = new Logger();
  }

  /**
   * Setup Docusaurus project with user confirmation
   */
  async setupProject(projectPath, options = {}) {
    this.projectPath = path.resolve(projectPath);
    this.docusaurusPath = path.join(this.projectPath, 'specs_viewer'); // Docusaurus project will be created in specs_viewer subdirectory

    this.logger.info(`Setting up Docusaurus project at: ${this.docusaurusPath}`);

    // Check if Docusaurus project already exists
    if (await fs.pathExists(this.docusaurusPath)) {
      const { confirmDelete } = await this.confirmProjectDeletion();
      
      if (confirmDelete) {
        await this.backupExistingProject();
      } else {
        this.logger.info('Setup cancelled by user');
        return false;
      }
    }

    // Create new Docusaurus project
    await this.createDocusaurusProject();
    
    // Install dependencies
    await this.installDependencies();
    
    // Clean up default content
    await this.cleanupDefaultContent();
    
    // Create welcome intro page
    await this.createIntroPage();
    
    // Install and configure Lunr search
    await this.installLunrSearch();
    
    // Update configuration
    await this.updateConfiguration();

    this.logger.info('Docusaurus project setup completed successfully!');
    return true;
  }

  /**
   * Set project path for existing project (without setup)
   */
  setProjectPath(projectPath) {
    this.projectPath = path.resolve(projectPath);
    this.docusaurusPath = path.join(this.projectPath, 'specs_viewer');
    this.logger.info(`Project path set to: ${this.docusaurusPath}`);
  }

  /**
   * Confirm deletion of existing project
   */
  async confirmProjectDeletion() {
    // For CLI, we'll use a simple prompt
    // In a real implementation, you might want to use a proper CLI prompt library
    this.logger.warn('Docusaurus project already exists at this location.');
    this.logger.info('This will delete the existing project and create a fresh one.');
    this.logger.info('If you want to save the current version, it will be backed up with timestamp.');
    
    // For now, we'll proceed with backup (you can enhance this with actual user input)
    return { confirmDelete: true };
  }

  /**
   * Backup existing project with timestamp
   */
  async backupExistingProject() {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupPath = `${this.docusaurusPath}_bkp_${timestamp}`;
    
    this.logger.info(`Backing up existing project to: ${backupPath}`);
    
    // Create backup directory and move contents
    await fs.ensureDir(backupPath);
    await fs.copy(this.docusaurusPath, backupPath);
    await fs.remove(this.docusaurusPath);
    
    this.logger.info('Backup completed');
  }

  /**
   * Create new Docusaurus project
   */
  async createDocusaurusProject() {
    this.logger.info('Creating new Docusaurus project...');
    
    try {
      // Run create-docusaurus command with non-interactive options
      const result = execSync(
        'npx create-docusaurus@latest specs_viewer classic --typescript --skip-install',
        { 
          cwd: this.projectPath,
          stdio: 'pipe',
          encoding: 'utf8'
        }
      );
      
      this.logger.info('Docusaurus project created successfully');
      return true;
    } catch (error) {
      this.logger.error('Failed to create Docusaurus project:', error.message);
      throw new Error(`Failed to create Docusaurus project: ${error.message}`);
    }
  }

  /**
   * Clean up default content
   */
  async cleanupDefaultContent() {
    this.logger.info('Cleaning up default content...');
    
    try {
      // Remove default blog and docs content
      const blogPath = path.join(this.docusaurusPath, 'blog');
      const docsPath = path.join(this.docusaurusPath, 'docs');
      
      if (await fs.pathExists(blogPath)) {
        await fs.emptyDir(blogPath);
        this.logger.info('Cleaned blog directory');
      }
      
      if (await fs.pathExists(docsPath)) {
        await fs.emptyDir(docsPath);
        this.logger.info('Cleaned docs directory');
      }
    } catch (error) {
      this.logger.error('Failed to cleanup default content:', error.message);
      throw new Error(`Failed to cleanup default content: ${error.message}`);
    }
  }

  /**
   * Create welcome intro page
   */
  async createIntroPage() {
    this.logger.info('Creating welcome intro page...');
    
    try {
      const docsPath = path.join(this.docusaurusPath, 'docs');
      const introPath = path.join(docsPath, 'intro.md');
      
      const introContent = `---
id: intro
title: Welcome to SpecPlane Viewer
sidebar_label: Introduction
---

# Welcome to SpecPlane Viewer

SpecPlane Viewer is a powerful tool that converts SpecPlane YAML specifications to Markdown and serves them via Docusaurus for easy viewing, navigation, and collaboration.

## What is SpecPlane Viewer?

SpecPlane Viewer transforms your software architecture specifications into beautiful, searchable documentation. It automatically converts SpecPlane YAML files to structured Markdown with proper sections, diagrams, and cross-references.

## Getting Started

### 1. Setup Docusaurus Project
\`\`\`bash
./bin/specplane setup ./.specplane
\`\`\`

### 2. Convert Specifications
\`\`\`bash
# Convert specs in current directory
./bin/specplane convert

# Convert specs with custom input/output
./bin/specplane convert --input ./my_specs --output ./custom_output

# Convert specific directory
./bin/specplane convert ./specs
\`\`\`

### 3. Serve with Live Reloading
\`\`\`bash
# Start full workflow with file watching
./bin/specplane convert ./specs
./bin/specplane start

# Or use the combined command
./bin/specplane serve ./specs --watch
\`\`\`

## Features

- **🔄 YAML to Markdown Conversion**: Automatically converts SpecPlane specifications
- **👀 Live Reloading**: Watches for changes and updates in real-time
- **🔍 Search**: Integrated Lunr search functionality
- **🧭 Navigation**: Automatic sidebar generation and cross-references
- **📊 Diagrams**: Mermaid diagram support for visual relationships
- **🔗 References**: Clickable cross-references between components

## Project Information

- **GitHub**: [SpecPlane Project](https://github.com/gauravbaruah/SpecPlane)
- **Maintainer**: Contact the maintainer for support and contributions
- **License**: See the project repository for licensing details

---

*Made with [Docusaurus](https://github.com/facebook/docusaurus) - A modern static website generator*
`;
      
      await fs.writeFile(introPath, introContent);
      this.logger.info('Welcome intro page created successfully');
      
    } catch (error) {
      this.logger.error('Failed to create intro page:', error.message);
      throw new Error(`Failed to create intro page: ${error.message}`);
    }
  }

  /**
   * Install Docusaurus dependencies
   */
  async installDependencies() {
    this.logger.info('Installing Docusaurus dependencies...');
    
    try {
      const result = execSync(
        'npm install',
        { 
          cwd: this.docusaurusPath,
          stdio: 'pipe',
          encoding: 'utf8'
        }
      );
      
      this.logger.info('Dependencies installed successfully');
      return true;
    } catch (error) {
      this.logger.error('Failed to install dependencies:', error.message);
      throw new Error(`Failed to install dependencies: ${error.message}`);
    }
  }

  /**
   * Install Lunr search plugin
   */
  async installLunrSearch() {
    this.logger.info('Installing Lunr search plugin...');
    
    try {
      const result = execSync(
        'npm install docusaurus-lunr-search',
        { 
          cwd: this.docusaurusPath,
          stdio: 'pipe',
          encoding: 'utf8'
        }
      );
      
      this.logger.info('Lunr search plugin installed successfully');
      return true;
    } catch (error) {
      this.logger.error('Failed to install Lunr search plugin:', error.message);
      throw new Error(`Failed to install Lunr search plugin: ${error.message}`);
    }
  }

  /**
   * Update Docusaurus configuration
   */
  async updateConfiguration() {
    this.logger.info('Updating Docusaurus configuration...');
    
    try {
      const configPath = path.join(this.docusaurusPath, 'docusaurus.config.ts');
      
      // Read existing config
      let configContent = await fs.readFile(configPath, 'utf8');
      
      // Add Lunr search plugin configuration
      if (!configContent.includes('docusaurus-lunr-search')) {
        // Check if plugins array exists
        if (configContent.includes('plugins:')) {
          // Find the plugins array and add our plugin
          const pluginRegex = /(plugins:\s*\[)([\s\S]*?)(\])/;
          const match = configContent.match(pluginRegex);
          
          if (match) {
            const newPlugin = `\n        'docusaurus-lunr-search',`;
            configContent = configContent.replace(
              pluginRegex,
              `$1${newPlugin}$2$3`
            );
          }
        } else {
          // Add plugins array before presets
          const presetsRegex = /(presets:\s*\[)/;
          const match = configContent.match(presetsRegex);
          
          if (match) {
            const pluginsArray = `\n  plugins: [\n    'docusaurus-lunr-search',\n  ],\n\n  `;
            configContent = configContent.replace(presetsRegex, pluginsArray + '$1');
          }
        }
      }
      
      // Update site metadata
      configContent = configContent.replace(
        /title:\s*['"]My Site['"]/,
        "title: 'SpecPlane Viewer'"
      );
      
      configContent = configContent.replace(
        /tagline:\s*['"]Dinosaurs are cool['"]/,
        "tagline: 'Convert SpecPlane YAML to beautiful documentation'"
      );
      
      // Add routeBasePath to docs config
      if (!configContent.includes('routeBasePath')) {
        configContent = configContent.replace(
          /(docs:\s*\{)/,
          '$1\n          routeBasePath: \'/\', // Make docs the home page'
        );
      }
      
      // Write updated config
      await fs.writeFile(configPath, configContent);
      this.logger.info('Configuration updated successfully');
      
    } catch (error) {
      this.logger.error('Failed to update configuration:', error.message);
      throw new Error(`Failed to update configuration: ${error.message}`);
    }
  }

  /**
   * Start Docusaurus development server
   */
  async startDevServer(port = 3001) {
    if (this.serverProcess) {
      this.logger.warn('Docusaurus server is already running');
      return false;
    }

    this.logger.info(`Starting Docusaurus development server on port ${port}...`);
    
    try {
      // Start the server process
      this.serverProcess = spawn('npx', ['docusaurus', 'start', '--port', port.toString()], {
        cwd: this.docusaurusPath,
        stdio: ['pipe', 'pipe', 'pipe'],
        detached: false
      });

      // Store the PID
      this.serverPID = this.serverProcess.pid;
      
      // Collect output for debugging
      let stdout = '';
      let stderr = '';
      
      this.serverProcess.stdout.on('data', (data) => {
        stdout += data.toString();
        this.logger.debug(`Docusaurus stdout: ${data.toString().trim()}`);
      });
      
      this.serverProcess.stderr.on('data', (data) => {
        stderr += data.toString();
        this.logger.debug(`Docusaurus stderr: ${data.toString().trim()}`);
      });
      
      // Handle process events
      this.serverProcess.on('error', (error) => {
        this.logger.error('Docusaurus server error:', error.message);
        throw new Error(`Docusaurus server error: ${error.message}`);
      });

      // Wait for the server to start or fail
      await new Promise((resolve, reject) => {
        let resolved = false;
        
        this.serverProcess.on('exit', (code, signal) => {
          if (!resolved) {
            resolved = true;
            if (code === 0) {
              this.logger.info(`Docusaurus server exited normally with code ${code}`);
            } else {
              reject(new Error(`Docusaurus server failed to start (exit code: ${code}).\nStdout: ${stdout}\nStderr: ${stderr}`));
            }
            this.serverProcess = null;
            this.serverPID = null;
          }
        });
        
        // Check if server is running after a delay
        setTimeout(() => {
          if (!resolved && this.serverProcess && this.serverProcess.exitCode === null) {
            resolved = true;
            resolve();
          }
        }, 5000);
      });
      
      this.logger.info(`Docusaurus development server started successfully on port ${port}`);
      this.logger.info(`Server PID: ${this.serverPID}`);
      
      return true;
    } catch (error) {
      this.logger.error('Failed to start Docusaurus server:', error.message);
      // Clean up on failure
      if (this.serverProcess) {
        this.serverProcess = null;
        this.serverPID = null;
      }
      throw error;
    }
  }

  /**
   * Stop Docusaurus development server
   */
  async stopDevServer() {
    if (!this.serverProcess || !this.serverPID) {
      this.logger.warn('No Docusaurus server is currently running');
      return false;
    }

    this.logger.info(`Stopping Docusaurus server (PID: ${this.serverPID})...`);
    
    try {
      // Kill the process
      this.serverProcess.kill('SIGTERM');
      
      // Wait for graceful shutdown
      await new Promise(resolve => {
        this.serverProcess.on('exit', resolve);
        setTimeout(resolve, 5000); // Force kill after 5 seconds
      });
      
      // Force kill if still running
      if (this.serverProcess.exitCode === null) {
        this.serverProcess.kill('SIGKILL');
      }
      
      this.serverProcess = null;
      this.serverPID = null;
      
      this.logger.info('Docusaurus server stopped successfully');
      return true;
    } catch (error) {
      this.logger.error('Failed to stop Docusaurus server:', error.message);
      throw new Error(`Failed to stop Docusaurus server: ${error.message}`);
    }
  }

  /**
   * Check if server is running
   */
  isServerRunning() {
    return this.serverProcess !== null && this.serverPID !== null;
  }

  /**
   * Get server status
   */
  getServerStatus() {
    if (!this.serverProcess) {
      return { running: false, pid: null };
    }
    
    return {
      running: true,
      pid: this.serverPID,
      exitCode: this.serverProcess.exitCode
    };
  }

  /**
   * Clean up resources
   */
  async cleanup() {
    if (this.serverProcess) {
      await this.stopDevServer();
    }
  }

  /**
   * Get the docs directory path
   */
  getDocsPath() {
    return path.join(this.docusaurusPath, 'docs');
  }

  /**
   * Get the project root path
   */
  getProjectPath() {
    return this.projectPath;
  }
}

module.exports = { DocusaurusHandler };
