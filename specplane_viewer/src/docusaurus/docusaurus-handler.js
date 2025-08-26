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
      
      // Create redirect index page
      await this.createRedirectIndexPage();
      
      // Install and configure Lunr search
      await this.installLunrSearch();
      
      // Install Mermaid theme
      await this.installMermaidTheme();
      
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
          encoding: 'utf8',
          env: { ...process.env, PATH: process.env.PATH }
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
      
      // Remove default pages content
      const pagesPath = path.join(this.docusaurusPath, 'src', 'pages');
      if (await fs.pathExists(pagesPath)) {
        await fs.emptyDir(pagesPath);
        this.logger.info('Cleaned pages directory');
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
./bin/specplane_viewer setup ./.specplane
\`\`\`

### 2. Convert Specifications
\`\`\`bash
# Convert specs in current directory
./bin/specplane_viewer convert

# Convert specs with custom input/output
./bin/specplane_viewer convert --input ./my_specs --output ./custom_output

# Convert specific directory
./bin/specplane_viewer convert ./specs
\`\`\`

### 3. Serve with Live Reloading
\`\`\`bash
# Start full workflow with file watching
./bin/specplane_viewer convert ./specs
./bin/specplane_viewer start

# Or use the combined command
./bin/specplane_viewer serve ./specs --watch
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
   * Create redirect index page
   */
  async createRedirectIndexPage() {
    this.logger.info('Creating redirect index page...');
    
    try {
      const pagesPath = path.join(this.docusaurusPath, 'src', 'pages');
      await fs.ensureDir(pagesPath);
      
      const indexPath = path.join(pagesPath, 'index.tsx');
      
      const indexContent = `import React from 'react';
import {Redirect} from '@docusaurus/router';

export default function Home(): JSX.Element {
  return <Redirect to="/intro" />;
}`;
      
      await fs.writeFile(indexPath, indexContent);
      this.logger.info('Redirect index page created successfully');
      
    } catch (error) {
      this.logger.error('Failed to create redirect index page:', error.message);
      throw new Error(`Failed to create redirect index page: ${error.message}`);
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
   * Install Mermaid theme
   */
  async installMermaidTheme() {
    this.logger.info('Installing Mermaid theme...');
    
    try {
      const result = execSync(
        'npm install @docusaurus/theme-mermaid',
        { 
          cwd: this.docusaurusPath,
          stdio: 'pipe',
          encoding: 'utf8'
        }
      );
      
      this.logger.info('Mermaid theme installed successfully');
      return true;
    } catch (error) {
      this.logger.error('Failed to install Mermaid theme:', error.message);
      throw new Error(`Failed to install Mermaid theme: ${error.message}`);
    }
  }

  /**
   * Update Docusaurus configuration
   */
  async updateConfiguration() {
    this.logger.info('Updating Docusaurus configuration...');
    
    try {
      const configPath = path.join(this.docusaurusPath, 'docusaurus.config.ts');
      
      // Create a clean, properly structured config object
      const config = {
        title: 'SpecPlane Viewer',
        tagline: 'Convert SpecPlane YAML to beautiful documentation',
        favicon: 'img/favicon.ico',
        
        // Future flags
        future: {
          v4: true, // Improve compatibility with the upcoming Docusaurus v4
        },
        
        // Site configuration
        url: 'https://your-docusaurus-site.example.com',
        baseUrl: '/',
        
        // GitHub pages deployment config
        organizationName: 'gauravbaruah',
        projectName: 'SpecPlane',
        
        // Link handling
        onBrokenLinks: 'throw',
        onBrokenMarkdownLinks: 'warn',
        
        // Internationalization
        i18n: {
          defaultLocale: 'en',
          locales: ['en'],
        },
        
        // Plugins
        plugins: [
          require.resolve('docusaurus-lunr-search'),
        ],
        
        // Mermaid support
        themes: ['@docusaurus/theme-mermaid'],
        
        // Markdown configuration for Mermaid
        markdown: {
          mermaid: true,
        },
        
        // Presets
        presets: [
          [
            'classic',
            {
              docs: {
                routeBasePath: '/', // Make docs the home page
                sidebarPath: './sidebars.ts',
                editUrl: 'https://github.com/gauravbaruah/SpecPlane/tree/main/',
              },
              theme: {
                customCss: './src/css/custom.css',
              },
            },
          ],
        ],
        
        // Theme configuration
        themeConfig: {
          image: 'img/docusaurus-social-card.jpg',
          navbar: {
            title: 'SpecPlane Viewer',
            logo: {
              alt: 'SpecPlane Viewer Logo',
              src: 'img/logo.svg',
            },
            items: [
              {
                type: 'docSidebar',
                sidebarId: 'tutorialSidebar',
                position: 'left',
                label: 'Specs',
              },
              // Search bar
              {
                type: 'search',
                position: 'right',
              },
            ],
          },
          footer: {
            style: 'dark',
            links: [
              {
                title: 'Specs',
                items: [
                  {
                    label: 'Introduction',
                    to: '/intro',
                  },
                ],
              },
              {
                title: 'Project',
                items: [
                  {
                    label: 'GitHub',
                    href: 'https://github.com/gauravbaruah/SpecPlane',
                  },
                  {
                    label: 'Issues',
                    href: 'https://github.com/gauravbaruah/SpecPlane/issues',
                  },
                ],
              },
            ],
            copyright: `Copyright © ${new Date().getFullYear()} SpecPlane Project. Made with [Docusaurus](https://github.com/facebook/docusaurus).`,
          },
          // Mermaid configuration
          mermaid: {
            theme: { light: 'default', dark: 'dark' },
            options: {
              maxTextSize: 50000,
              securityLevel: 'loose',
            },
          },
          
          // prism: {
          //   theme: prismThemes.github,
          //   darkTheme: prismThemes.dracula,
          // },
        },
      };
      
      // Convert to TypeScript config format
      const configContent = `import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = ${JSON.stringify(config, null, 2).replace(/"([^"]+)":/g, '$1:')};

export default config;`;
      
      // Write the clean config
      await fs.writeFile(configPath, configContent);
      this.logger.info('Configuration updated successfully');
      
    } catch (error) {
      this.logger.error('Failed to update configuration:', error.message);
      throw new Error(`Failed to update configuration: ${error.message}`);
    }
  }

  /**
   * Build Docusaurus project for production
   */
  async buildProject() {
    this.logger.info('Building Docusaurus project for production...');
    
    try {
      const { execSync } = require('child_process');
      
      // Build the project
      execSync('npm run build', { 
        cwd: this.docusaurusPath,
        stdio: 'inherit',
        env: { ...process.env, PATH: process.env.PATH }
      });
      
      this.logger.info('Docusaurus project built successfully');
      return true;
      
    } catch (error) {
      this.logger.error('Failed to build Docusaurus project:', error.message);
      throw new Error(`Build failed: ${error.message}`);
    }
  }

  /**
   * Start Docusaurus server (builds first for search functionality)
   */
  async startDevServer(port = 3001) {
    // Check if server is already running by checking PID file
    if (await this.isServerRunning()) {
      this.logger.warn('Docusaurus server is already running');
      return false;
    }

    this.logger.info(`Starting Docusaurus server on port ${port}...`);
    
    try {
      // Build the project first to generate search index
      await this.buildProject();
      
      this.logger.info(`Starting Docusaurus server on port ${port}...`);
      
      // Start the server process (serve the built version)
      this.serverProcess = spawn('npx', ['docusaurus', 'serve', '--port', port.toString()], {
        cwd: this.docusaurusPath,
        stdio: ['pipe', 'pipe', 'pipe'],
        detached: false
      });

      // Store the PID
      this.serverPID = this.serverProcess.pid;
      
      // Write PID to file for cross-process tracking
      await this.writePIDFile(this.serverPID, port);
      
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
        this.cleanupPIDFile();
        throw new Error(`Docusaurus server error: ${error.message}`);
      });

      // Wait for the server to start or fail
      await new Promise((resolve, reject) => {
        let resolved = false;
        
        this.serverProcess.on('exit', (code, signal) => {
          if (!resolved) {
            resolved = true;
            this.cleanupPIDFile();
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
      
      this.logger.info(`Docusaurus server started successfully on port ${port}`);
      this.logger.info(`Server PID: ${this.serverPID}`);
      
      return true;
    } catch (error) {
      this.logger.error('Failed to start Docusaurus server:', error.message);
      // Clean up on failure
      this.cleanupPIDFile();
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
    // Check if server is running (including cross-process check)
    if (!(await this.isServerRunning())) {
      this.logger.warn('No Docusaurus server is currently running');
      return false;
    }

    // Get PID from file if we don't have local reference
    let pidToKill = this.serverPID;
    if (!pidToKill) {
      const pidData = await this.readPIDFile();
      if (pidData) {
        pidToKill = pidData.pid;
      }
    }

    // If still no PID, try to detect from running processes
    if (!pidToKill) {
      try {
        const { execSync } = require('child_process');
        const result = execSync('ps aux | grep "docusaurus start" | grep -v grep', { encoding: 'utf8' });
        if (result.trim()) {
          const lines = result.trim().split('\n');
          for (const line of lines) {
            const match = line.match(/^\S+\s+(\d+)/);
            if (match) {
              const detectedPid = parseInt(match[1]);
              // Check if this process is actually running
              try {
                process.kill(detectedPid, 0);
                pidToKill = detectedPid;
                break;
              } catch (error) {
                // Process doesn't exist, continue checking
              }
            }
          }
        }
      } catch (error) {
        this.logger.debug('Failed to detect processes via ps command');
      }
    }

    if (!pidToKill) {
      this.logger.warn('No Docusaurus server PID found');
      return false;
    }

    this.logger.info(`Stopping Docusaurus server (PID: ${pidToKill})...`);
    
    try {
      // Kill the process by PID
      process.kill(pidToKill, 'SIGTERM');
      
      // Wait a bit for graceful shutdown
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Check if process is still running and force kill if needed
      try {
        process.kill(pidToKill, 0); // Check if process exists
        process.kill(pidToKill, 'SIGKILL'); // Force kill
        await new Promise(resolve => setTimeout(resolve, 1000));
      } catch (error) {
        // Process already terminated
      }
      
      // Clean up
      this.serverProcess = null;
      this.serverPID = null;
      await this.cleanupPIDFile();
      
      this.logger.info('Docusaurus server stopped successfully');
      return true;
    } catch (error) {
      this.logger.error('Failed to stop Docusaurus server:', error.message);
      throw new Error(`Failed to stop Docusaurus server: ${error.message}`);
    }
  }

  /**
   * Get PID file path
   */
  getPIDFilePath() {
    return path.join(this.projectPath, '.docusaurus.pid');
  }

  /**
   * Write PID to file for cross-process tracking
   */
  async writePIDFile(pid, port) {
    try {
      const pidData = {
        pid: pid,
        port: port,
        startTime: new Date().toISOString(),
        projectPath: this.projectPath
      };
      await fs.writeFile(this.getPIDFilePath(), JSON.stringify(pidData, null, 2));
    } catch (error) {
      this.logger.warn('Failed to write PID file:', error.message);
    }
  }

  /**
   * Read PID from file
   */
  async readPIDFile() {
    try {
      const pidPath = this.getPIDFilePath();
      if (await fs.pathExists(pidPath)) {
        const pidData = JSON.parse(await fs.readFile(pidPath, 'utf8'));
        return pidData;
      }
    } catch (error) {
      this.logger.debug('Failed to read PID file:', error.message);
    }
    return null;
  }

  /**
   * Clean up PID file
   */
  async cleanupPIDFile() {
    try {
      const pidPath = this.getPIDFilePath();
      if (await fs.pathExists(pidPath)) {
        await fs.remove(pidPath);
      }
    } catch (error) {
      this.logger.debug('Failed to cleanup PID file:', error.message);
    }
  }

  /**
   * Check if server is running by checking PID file and process
   */
  async isServerRunning() {
    // First check if we have a local process reference
    if (this.serverProcess !== null && this.serverPID !== null) {
      return true;
    }
    
    // Check PID file for cross-process detection
    const pidData = await this.readPIDFile();
    if (pidData) {
      // Check if the process is actually running
      try {
        // Use a simple process check - if kill(0) succeeds, process exists
        process.kill(pidData.pid, 0);
        return true;
      } catch (error) {
        // Process doesn't exist, clean up stale PID file
        await this.cleanupPIDFile();
        return false;
      }
    }
    
    // If no PID file, try to detect Docusaurus processes by scanning
    // This is a fallback for when processes were started manually
    try {
      const { execSync } = require('child_process');
      const result = execSync('ps aux | grep "docusaurus start" | grep -v grep', { encoding: 'utf8' });
      if (result.trim()) {
        // Extract PID from ps output
        const lines = result.trim().split('\n');
        for (const line of lines) {
          const match = line.match(/^\S+\s+(\d+)/);
          if (match) {
            const pid = parseInt(match[1]);
            // Check if this process is actually running
            try {
              process.kill(pid, 0);
              // Found a running Docusaurus process
              this.logger.debug(`Found running Docusaurus process: ${pid}`);
              return true;
            } catch (error) {
              // Process doesn't exist, continue checking
            }
          }
        }
      }
    } catch (error) {
      // ps command failed or no processes found
      this.logger.debug('No Docusaurus processes found via ps command');
    }
    
    return false;
  }

  /**
   * Get server status
   */
  async getServerStatus() {
    // Check if server is running (including cross-process check)
    const isRunning = await this.isServerRunning();
    
    if (!isRunning) {
      return { running: false, pid: null, port: null };
    }
    
    // Get PID and port from file if we don't have local reference
    let pid = this.serverPID;
    let port = null;
    
    if (!pid) {
      const pidData = await this.readPIDFile();
      if (pidData) {
        pid = pidData.pid;
        port = pidData.port;
      }
    }
    
    // If still no PID, try to detect from running processes
    if (!pid) {
      try {
        const { execSync } = require('child_process');
        const result = execSync('ps aux | grep "docusaurus start" | grep -v grep', { encoding: 'utf8' });
        if (result.trim()) {
          const lines = result.trim().split('\n');
          for (const line of lines) {
            const match = line.match(/^\S+\s+(\d+)/);
            if (match) {
              const detectedPid = parseInt(match[1]);
              // Check if this process is actually running
              try {
                process.kill(detectedPid, 0);
                pid = detectedPid;
                // Try to extract port from the command line
                const portMatch = line.match(/--port\s+(\d+)/);
                if (portMatch) {
                  port = parseInt(portMatch[1]);
                }
                break;
              } catch (error) {
                // Process doesn't exist, continue checking
              }
            }
          }
        }
      } catch (error) {
        this.logger.debug('Failed to detect processes via ps command');
      }
    }
    
    return {
      running: true,
      pid: pid,
      port: port
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
