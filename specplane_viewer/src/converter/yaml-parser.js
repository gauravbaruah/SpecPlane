/**
 * YAML Parser Component
 * Parses and validates SpecPlane YAML files against the schema
 */

const yaml = require('js-yaml');
const { Logger } = require('../utils/logger');

class YAMLParser {
  constructor() {
    this.logger = new Logger();
    this.stats = {
      filesParsed: 0,
      filesValidated: 0,
      parseErrors: 0,
      validationErrors: 0,
      warnings: 0
    };
  }

  /**
   * Parse YAML content and validate against SpecPlane schema
   */
  async parseAndValidate(yamlContent) {
    try {
      // Parse YAML content
      const parsedData = this.parseYAML(yamlContent);
      
      if (!parsedData.success) {
        return parsedData;
      }
      
      // Validate against SpecPlane schema
      const validationResult = this.validateSpec(parsedData.data);
      
      return {
        success: validationResult.success,
        data: parsedData.data,
        errors: validationResult.errors,
        warnings: validationResult.warnings
      };
      
    } catch (error) {
      this.logger.error('Parse and validate failed:', error);
      return {
        success: false,
        errors: [error.message],
        warnings: []
      };
    }
  }

  /**
   * Parse YAML content to JavaScript object
   */
  parseYAML(yamlContent) {
    try {
      const startTime = Date.now();
      
      // Parse YAML content
      const parsedData = yaml.load(yamlContent);
      
      const parseTime = Date.now() - startTime;
      
      this.stats.filesParsed++;
      
      this.logger.debug(`YAML parsed successfully in ${parseTime}ms`);
      
      return {
        success: true,
        data: parsedData,
        parseTime
      };
      
    } catch (error) {
      this.stats.parseErrors++;
      
      // Provide helpful error messages
      let errorMessage = 'YAML parsing failed';
      
      if (error.message.includes('end of the stream')) {
        errorMessage = 'YAML file appears to be empty or incomplete';
      } else if (error.message.includes('unexpected end')) {
        errorMessage = 'YAML file has unexpected end - check for missing quotes or brackets';
      } else if (error.message.includes('duplicate key')) {
        errorMessage = `YAML file has duplicate key: ${error.message.split('duplicate key ')[1]}`;
      } else if (error.message.includes('line')) {
        errorMessage = `YAML syntax error at line ${error.message.split('line ')[1]}`;
      } else {
        errorMessage = `YAML parsing error: ${error.message}`;
      }
      
      return {
        success: false,
        errors: [errorMessage],
        warnings: []
      };
    }
  }

  /**
   * Validate parsed data against SpecPlane schema
   */
  validateSpec(parsedData) {
    const errors = [];
    const warnings = [];
    
    try {
      // Basic structure validation
      if (!parsedData || typeof parsedData !== 'object') {
        errors.push('Specification must be a valid YAML object');
        return { success: false, errors, warnings };
      }
      
      // Check for required meta section
      if (!parsedData.meta) {
        errors.push('Missing required "meta" section');
      } else {
        const metaValidation = this.validateMetaSection(parsedData.meta);
        errors.push(...metaValidation.errors);
        warnings.push(...metaValidation.warnings);
      }
      
      // Check for required contracts section
      if (!parsedData.contracts) {
        warnings.push('Missing "contracts" section - consider adding behavioral contracts');
      }
      
      // Check for required validation section
      if (!parsedData.validation) {
        warnings.push('Missing "validation" section - consider adding acceptance criteria');
      }
      
      // Validate other sections if present
      if (parsedData.diagrams) {
        const diagramValidation = this.validateDiagramsSection(parsedData.diagrams);
        warnings.push(...diagramValidation.warnings);
      }
      
      if (parsedData.refs) {
        const refsValidation = this.validateRefsSection(parsedData.refs);
        warnings.push(...refsValidation.warnings);
      }
      
      this.stats.filesValidated++;
      
      if (errors.length > 0) {
        this.stats.validationErrors++;
      }
      
      if (warnings.length > 0) {
        this.stats.warnings += warnings.length;
      }
      
      return {
        success: errors.length === 0,
        errors,
        warnings
      };
      
    } catch (error) {
      this.logger.error('Validation failed:', error);
      return {
        success: false,
        errors: [`Validation error: ${error.message}`],
        warnings
      };
    }
  }

  /**
   * Validate meta section
   */
  validateMetaSection(meta) {
    const errors = [];
    const warnings = [];
    
    // Check required fields
    if (!meta.purpose) {
      errors.push('Meta section missing required "purpose" field');
    }
    
    if (!meta.type) {
      errors.push('Meta section missing required "type" field');
    }
    
    if (!meta.level) {
      errors.push('Meta section missing required "level" field');
    }
    
    // Check field values
    if (meta.type && !['component', 'container', 'system', 'widget', 'service', 'agent'].includes(meta.type)) {
      warnings.push(`Meta type "${meta.type}" is not a standard SpecPlane type`);
    }
    
    if (meta.level && !['system', 'container', 'component', 'code'].includes(meta.level)) {
      warnings.push(`Meta level "${meta.level}" is not a standard SpecPlane level`);
    }
    
    return { errors, warnings };
  }

  /**
   * Validate diagrams section
   */
  validateDiagramsSection(diagrams) {
    const warnings = [];
    
    if (!Array.isArray(diagrams)) {
      warnings.push('Diagrams section should be an array');
      return { warnings };
    }
    
    for (const diagram of diagrams) {
      if (!diagram.title) {
        warnings.push('Diagram missing required "title" field');
      }
      
      if (!diagram.mermaid) {
        warnings.push('Diagram missing required "mermaid" field');
      }
    }
    
    return { warnings };
  }

  /**
   * Validate refs section
   */
  validateRefsSection(refs) {
    const warnings = [];
    
    if (typeof refs !== 'object') {
      warnings.push('Refs section should be an object');
      return { warnings };
    }
    
    for (const [refId, ref] of Object.entries(refs)) {
      if (!ref.type) {
        warnings.push(`Ref "${refId}" missing required "type" field`);
      }
      
      if (!ref.title) {
        warnings.push(`Ref "${refId}" missing required "title" field`);
      }
    }
    
    return { warnings };
  }

  /**
   * Get validation statistics
   */
  getStats() {
    return { ...this.stats };
  }

  /**
   * Reset statistics
   */
  resetStats() {
    this.stats = {
      filesParsed: 0,
      filesValidated: 0,
      parseErrors: 0,
      validationErrors: 0,
      warnings: 0
    };
  }
}

module.exports = { YAMLParser };
