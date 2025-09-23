/**
 * Spec2MD Converter Container
 * Orchestrates YAML to Markdown conversion with proper structure and formatting
 */

const path = require('path');
const fs = require('fs-extra');
const { YAMLParser } = require('./yaml-parser');
const { MarkdownGenerator } = require('./markdown-generator');
const { Logger } = require('../utils/logger');

class Spec2MDConverter {
  constructor() {
    this.logger = new Logger();
    this.yamlParser = new YAMLParser();
    this.markdownGenerator = new MarkdownGenerator();
  }

  /**
   * Convert a single YAML file to Markdown
   */
  async convertFile(inputPath, outputPath) {
    try {
      this.logger.info(`Converting file: ${inputPath}`);
      
      // Parse YAML file
      const yamlContent = await fs.readFile(inputPath, 'utf8');
      const parsedData = await this.yamlParser.parseAndValidate(yamlContent);
      
      if (!parsedData.success) {
        throw new Error(`YAML parsing failed: ${parsedData.errors.join(', ')}`);
      }
      
      // Generate markdown
      const markdownContent = await this.markdownGenerator.generateMarkdown(parsedData.data, outputPath);
      
      // Ensure output directory exists
      const outputDir = path.dirname(outputPath);
      await fs.ensureDir(outputDir);
      
      // Write markdown file
      await fs.writeFile(outputPath, markdownContent, 'utf8');
      
      this.logger.success(`Successfully converted: ${inputPath} -> ${outputPath}`);
      
      return {
        success: true,
        inputPath,
        outputPath,
        warnings: parsedData.warnings || []
      };
      
    } catch (error) {
      this.logger.error(`Failed to convert file ${inputPath}:`, error);
      throw error;
    }
  }

  /**
   * Convert entire directory of YAML files to Markdown
   */
  async convertDirectory(inputDir, outputDir) {
    try {
      this.logger.info(`Converting directory: ${inputDir} -> ${outputDir}`);
      
      // Ensure output directory exists
      await fs.ensureDir(outputDir);
      
      // Find all YAML files recursively
      const yamlFiles = await this.findYamlFiles(inputDir);
      
      if (yamlFiles.length === 0) {
        this.logger.warn(`No YAML files found in: ${inputDir}`);
        return { success: true, filesProcessed: 0, warnings: [] };
      }
      
      this.logger.info(`Found ${yamlFiles.length} YAML files to convert`);
      
      const results = [];
      const allWarnings = [];
      
      // Process each file
      for (const yamlFile of yamlFiles) {
        try {
          // Calculate relative path to maintain directory structure
          const relativePath = path.relative(inputDir, yamlFile);
          const outputFile = path.join(outputDir, relativePath.replace(/\.(yaml|yml)$/, '.md'));
          
          const result = await this.convertFile(yamlFile, outputFile);
          results.push(result);
          
          if (result.warnings) {
            allWarnings.push(...result.warnings);
          }
          
        } catch (error) {
          this.logger.error(`Failed to convert ${yamlFile}:`, error);
          results.push({
            success: false,
            inputPath: yamlFile,
            error: error.message
          });
        }
      }
      
      const successCount = results.filter(r => r.success).length;
      const failureCount = results.length - successCount;
      
      // Generate sidebar configuration after conversion
      if (successCount > 0) {
        try {
          // Generate document IDs based on Docusaurus's automatic ID generation rules
          const convertedFiles = results
            .filter(r => r.success)
            .map(r => {
              // Get relative path from docs directory
              const relativePath = path.relative(outputDir, r.outputPath);
              // Docusaurus generates IDs based on file path: remove .md extension
              return relativePath.replace(/\.md$/, '').replace(/\\/g, '/');
            })
            .sort();
          
          const sidebarConfig = this.markdownGenerator.generateSidebarConfig(convertedFiles);
          const sidebarPath = path.join(path.dirname(outputDir), 'sidebars.ts');
          await fs.writeFile(sidebarPath, sidebarConfig, 'utf8');
          this.logger.info('Sidebar configuration updated');
        } catch (error) {
          this.logger.warn('Failed to update sidebar configuration:', error.message);
        }
      }
      
      this.logger.success(`Directory conversion completed: ${successCount} successful, ${failureCount} failed`);
      
      if (allWarnings.length > 0) {
        this.logger.warn(`Total warnings: ${allWarnings.length}`);
      }
      
      return {
        success: failureCount === 0,
        filesProcessed: results.length,
        successful: successCount,
        failed: failureCount,
        results,
        warnings: allWarnings
      };
      
    } catch (error) {
      this.logger.error(`Failed to convert directory ${inputDir}:`, error);
      throw error;
    }
  }

  /**
   * Find all YAML files in a directory recursively
   */
  async findYamlFiles(directory) {
    const yamlFiles = [];
    
    try {
      const items = await fs.readdir(directory);
      
      for (const item of items) {
        const itemPath = path.join(directory, item);
        const stat = await fs.stat(itemPath);
        
        if (stat.isDirectory()) {
          // Skip .specplane directory
          if (item !== '.specplane') {
            const subFiles = await this.findYamlFiles(itemPath);
            yamlFiles.push(...subFiles);
          }
        } else if (stat.isFile()) {
          const ext = path.extname(item).toLowerCase();
          if (ext === '.yaml' || ext === '.yml') {
            yamlFiles.push(itemPath);
          }
        }
      }
    } catch (error) {
      this.logger.error(`Error reading directory ${directory}:`, error);
    }
    
    return yamlFiles;
  }

  /**
   * Validate a YAML file without converting
   */
  async validateFile(filePath) {
    try {
      const yamlContent = await fs.readFile(filePath, 'utf8');
      return await this.yamlParser.parseAndValidate(yamlContent);
    } catch (error) {
      this.logger.error(`Failed to validate file ${filePath}:`, error);
      throw error;
    }
  }

  /**
   * Get conversion statistics
   */
  getStats() {
    return {
      yamlParser: this.yamlParser.getStats(),
      markdownGenerator: this.markdownGenerator.getStats()
    };
  }
}

module.exports = { Spec2MDConverter };
