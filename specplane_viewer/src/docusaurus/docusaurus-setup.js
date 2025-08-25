/**
 * Docusaurus Setup Component
 * Handles Docusaurus project initialization and configuration
 */

const fs = require('fs-extra');
const path = require('path');
const { Logger } = require('../utils/logger');

class DocusaurusSetup {
  constructor() {
    this.logger = new Logger();
    this.projectPath = null;
  }

  /**
   * Setup Docusaurus project for markdown files
   */
  async setupProject(markdownPath, options = {}) {
    try {
      this.logger.info('Setting up Docusaurus project...');
      
      // Determine project path (parent directory of markdown)
      this.projectPath = path.dirname(markdownPath);
      
      this.logger.info(`Project path: ${this.projectPath}`);
      
      // Check if project already exists
      const projectExists = await this.checkProjectExists();
      
      if (projectExists) {
        this.logger.info('Docusaurus project already exists, updating configuration...');
        await this.updateExistingProject(markdownPath, options);
      } else {
        this.logger.info('Creating new Docusaurus project...');
        await this.createNewProject(markdownPath, options);
      }
      
      // Install lunr plugin
      await this.installLunrPlugin();
      
      this.logger.success('Docusaurus project setup completed successfully!');
      
      return {
        success: true,
        projectPath: this.projectPath,
        markdownPath
      };
      
    } catch (error) {
      this.logger.error('Failed to setup Docusaurus project:', error);
      throw error;
    }
  }

  /**
   * Check if Docusaurus project already exists
   */
  async checkProjectExists() {
    const packageJsonPath = path.join(this.projectPath, 'package.json');
    const docusaurusConfigPath = path.join(this.projectPath, 'docusaurus.config.js');
    
    return await fs.pathExists(packageJsonPath) && await fs.pathExists(docusaurusConfigPath);
  }

  /**
   * Update existing Docusaurus project
   */
  async updateExistingProject(markdownPath, options) {
    try {
      // Update docusaurus.config.js
      await this.updateDocusaurusConfig(markdownPath, options);
      
      // Update package.json if needed
      await this.updatePackageJson();
      
    } catch (error) {
      this.logger.error('Failed to update existing project:', error);
      throw error;
    }
  }

  /**
   * Create new Docusaurus project
   */
  async createNewProject(markdownPath, options) {
    try {
      // Create package.json
      await this.createPackageJson();
      
      // Create docusaurus.config.js
      await this.createDocusaurusConfig(markdownPath, options);
      
      // Create sidebars.js
      await this.createSidebarsConfig();
      
      // Create basic CSS
      await this.createBasicCSS();
      
      // Create README
      await this.createREADME();
      
    } catch (error) {
      this.logger.error('Failed to create new project:', error);
      throw error;
    }
  }

  /**
   * Create package.json for Docusaurus project
   */
  async createPackageJson() {
    const packageJson = {
      name: "specplane-docs",
      version: "0.1.0",
      description: "SpecPlane Documentation Site",
      main: "docusaurus.config.js",
      scripts: {
        "docusaurus": "docusaurus",
        "start": "docusaurus start",
        "build": "docusaurus build",
        "swizzle": "docusaurus swizzle",
        "deploy": "docusaurus deploy",
        "clear": "docusaurus clear",
        "serve": "docusaurus serve",
        "write-translations": "docusaurus write-translations",
        "write-heading-ids": "docusaurus write-heading-ids",
        "typecheck": "tsc"
      },
      dependencies: {
        "@docusaurus/core": "^3.0.0",
        "@docusaurus/preset-classic": "^3.0.0",
        "docusaurus-lunr-search": "^3.6.1"
      },
      devDependencies: {
        "@docusaurus/module-type-aliases": "^3.0.0"
      },
      browserslist: {
        production: [
          ">0.5%",
          "not dead",
          "not op_mini all"
        ],
        development: [
          "last 1 chrome version",
          "last 1 firefox version",
          "last 1 safari version"
        ]
      },
      engines: {
        node: ">=18.0"
      }
    };
    
    const packageJsonPath = path.join(this.projectPath, 'package.json');
    await fs.writeJson(packageJsonPath, packageJson, { spaces: 2 });
    
    this.logger.info('Created package.json');
  }

  /**
   * Create docusaurus.config.js
   */
  async createDocusaurusConfig(markdownPath, options) {
    const { port = 3001 } = options;
    
    const config = `const config = {
  title: 'SpecPlane Documentation',
  tagline: 'Systematic framework for designing software components',
  favicon: 'img/favicon.ico',
  url: 'https://your-domain.com',
  baseUrl: '/',
  organizationName: 'specplane',
  projectName: 'specplane-docs',
  
  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',
  
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },
  
  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: require.resolve('./sidebars.js'),
          routeBasePath: '/',
          editUrl: 'https://github.com/specplane/specplane-docs/edit/main/',
          path: './docs', // Use standard Docusaurus docs folder
        },
        blog: false,
        pages: {
          path: './src/pages',
          routeBasePath: '/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
  
  plugins: [
    [
      'docusaurus-lunr-search',
      {
        indexBaseUrl: true,
        highlightTerms: true,
        maxSearchResults: 8,
        searchResultLength: 10,
        searchBarPosition: 'right',
        searchBarPosition: 'right',
        fields: {
          title: { boost: 200 },
          content: { boost: 2 },
          keywords: { boost: 100 }
        }
      },
    ],
  ],
  
  themeConfig: {
    navbar: {
      title: 'SpecPlane',
      logo: {
        alt: 'SpecPlane Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Specifications',
        },
        {
          href: 'https://github.com/specplane/specplane',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Getting Started',
              to: '/test.component',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/specplane/specplane',
            },
          ],
        },
      ],
      copyright: \`Copyright © \${new Date().getFullYear()} SpecPlane. Built with Docusaurus.\`,
    },
  },
};

module.exports = config;`;
    
    const configPath = path.join(this.projectPath, 'docusaurus.config.js');
    await fs.writeFile(configPath, config);
    
    this.logger.info('Created docusaurus.config.js');
  }

  /**
   * Create sidebars.js configuration
   */
  async createSidebarsConfig() {
    const sidebars = `const sidebars = {
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Specifications',
      items: [
        'test',
        // Add more items as needed
      ],
    },
  ],
};

module.exports = sidebars;`;
    
    const sidebarsPath = path.join(this.projectPath, 'sidebars.js');
    await fs.writeFile(sidebarsPath, sidebars);
    
    this.logger.info('Created sidebars.js');
  }

  /**
   * Create basic CSS file
   */
  async createBasicCSS() {
    const cssDir = path.join(this.projectPath, 'src', 'css');
    await fs.ensureDir(cssDir);
    
    const css = `/**
 * Custom CSS for SpecPlane Documentation
 */

:root {
  --ifm-color-primary: #2e8555;
  --ifm-color-primary-dark: #29784c;
  --ifm-color-primary-darker: #277148;
  --ifm-color-primary-darkest: #205d3b;
  --ifm-color-primary-light: #33925d;
  --ifm-color-primary-lighter: #359962;
  --ifm-color-primary-lightest: #3cad6e;
  --ifm-code-font-size: 95%;
  --docusaurus-highlighted-code-line-bg: rgba(0, 0, 0, 0.1);
}

[data-theme='dark'] {
  --ifm-color-primary: #25c2a0;
  --ifm-color-primary-dark: #21af90;
  --ifm-color-primary-darker: #1fa588;
  --ifm-color-primary-darkest: #1a8870;
  --ifm-color-primary-light: #29d5b0;
  --ifm-color-primary-lighter: #32d8b4;
  --ifm-color-primary-lightest: #4fddbf;
  --docusaurus-highlighted-code-line-bg: rgba(0, 0, 0, 0.3);
}

/* Custom styles for SpecPlane */
.specplane-meta {
  background: var(--ifm-color-emphasis-100);
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem 0;
}

.specplane-relationships {
  border: 1px solid var(--ifm-color-emphasis-300);
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem 0;
}

.specplane-validation {
  background: var(--ifm-color-warning-lightest);
  border-left: 4px solid var(--ifm-color-warning);
  padding: 1rem;
  margin: 1rem 0;
}`;
    
    const cssPath = path.join(cssDir, 'custom.css');
    await fs.writeFile(cssPath, css);
    
    this.logger.info('Created custom CSS');
  }

  /**
   * Create README file
   */
  async createREADME() {
    const readme = `# SpecPlane Documentation

This is a Docusaurus-powered documentation site for SpecPlane specifications.

## Development

\`\`\`bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
\`\`\`

## Structure

- \`docs/\` - Contains the markdown files (auto-generated from .specplane/markdown/)
- \`src/\` - Custom React components and CSS
- \`static/\` - Static assets like images and logos

## Features

- **Lunr Search**: Full-text search across all specifications
- **Responsive Design**: Works on desktop and mobile devices
- **Dark Mode**: Automatic theme switching
- **Mermaid Diagrams**: Renders diagrams from markdown

## Customization

Edit \`docusaurus.config.js\` to customize the site configuration.
Edit \`sidebars.js\` to customize the navigation structure.`;
    
    const readmePath = path.join(this.projectPath, 'README.md');
    await fs.writeFile(readmePath, readme);
    
    this.logger.info('Created README.md');
  }

  /**
   * Update existing docusaurus.config.js
   */
  async updateDocusaurusConfig(markdownPath, options) {
    // For now, just recreate the config
    // In the future, this could parse and update existing config
    await this.createDocusaurusConfig(markdownPath, options);
  }

  /**
   * Update existing package.json
   */
  async updatePackageJson() {
    // For now, just recreate the package.json
    // In the future, this could update existing dependencies
    await this.createPackageJson();
  }

  /**
   * Install lunr plugin
   */
  async installLunrPlugin() {
    try {
      this.logger.info('Installing lunr search plugin...');
      
      // This would typically run npm install
      // For now, we'll just log that it should be installed
      this.logger.info('Please run "npm install" in the project directory to install dependencies');
      
    } catch (error) {
      this.logger.error('Failed to install lunr plugin:', error);
      throw error;
    }
  }

  /**
   * Get project information
   */
  getProjectInfo() {
    return {
      projectPath: this.projectPath,
      hasProject: this.projectPath !== null
    };
  }
}

module.exports = { DocusaurusSetup };
