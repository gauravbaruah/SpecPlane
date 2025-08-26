/**
 * Markdown Generator Component
 * Generates well-formatted Markdown from parsed SpecPlane data
 */

const { Logger } = require('../utils/logger');

class MarkdownGenerator {
  constructor() {
    this.logger = new Logger();
    this.stats = {
      filesGenerated: 0,
      sectionsGenerated: 0,
      diagramsRendered: 0,
      referencesProcessed: 0
    };
  }

  /**
   * Generate complete markdown from SpecPlane data
   */
  async generateMarkdown(specData) {
    try {
      this.logger.debug('Generating markdown for specification');
      
      // Generate frontmatter for Docusaurus routing
      const frontmatter = this.generateFrontmatter(specData.meta);
      
      // Start with the main title (H1) using the ID
      const mainTitle = `# ${specData.meta?.id || 'untitled'}\n\n`;
      
      const sections = [];
      
      // Generate sections in specific order
      
      // 1. Meta section (first)
      if (specData.meta) {
        sections.push(this.generateMetaSection(specData.meta));
      }
      
      // 2. Diagrams section (including default relationships diagram)
      if (specData.diagrams && specData.diagrams.flowchart && specData.diagrams.flowchart.length > 0) {
        sections.push(this.generateDiagramsSection(specData.diagrams.flowchart));
      } else if (specData.diagrams && Array.isArray(specData.diagrams) && specData.diagrams.length > 0) {
        // Handle case where diagrams is directly an array
        sections.push(this.generateDiagramsSection(specData.diagrams));
      }
      
      // Always add a relationships diagram if not present
      if ((!specData.diagrams || (!specData.diagrams.flowchart && !Array.isArray(specData.diagrams))) || 
          (specData.diagrams.flowchart && specData.diagrams.flowchart.length === 0) ||
          (Array.isArray(specData.diagrams) && specData.diagrams.length === 0)) {
        sections.push(this.generateDefaultRelationshipsDiagram(specData));
      }
      
      // 3. Contracts section
      if (specData.contracts) {
        sections.push(this.generateContractsSection(specData.contracts));
      }
      
      // 4. Validation section
      if (specData.validation) {
        sections.push(this.generateValidationSection(specData.validation));
      }
      
      // 5. Other sections (relationships, dependencies, constraints, etc.)
      for (const [key, value] of Object.entries(specData)) {
        if (!['meta', 'diagrams', 'contracts', 'validation', 'refs'].includes(key) && 
            value && typeof value === 'object' && Object.keys(value).length > 0) {
          sections.push(this.generateGenericSection(key, value));
        }
      }
      
      // 6. References section
      if (specData.refs) {
        sections.push(this.generateReferencesSection(specData.refs));
      }
      
      // 7. Specs YAML section (at the end)
      sections.push(this.generateSpecsYamlSection(specData));
      
      // Add table of contents
      sections.push(this.generateTableOfContents(sections));
      
      // Combine all sections
      const markdown = sections.join('\n\n');
      
      // Add frontmatter and main title at the beginning
      const finalMarkdown = frontmatter + '\n\n' + mainTitle + markdown;
      
      this.stats.filesGenerated++;
      this.stats.sectionsGenerated += sections.length;
      
      this.logger.debug(`Markdown generated with ${sections.length} sections`);
      
      return finalMarkdown;
      
    } catch (error) {
      this.logger.error('Failed to generate markdown:', error);
      throw error;
    }
  }

  /**
   * Generate frontmatter for Docusaurus routing
   */
  generateFrontmatter(meta) {
    if (!meta) return '';
    
    // Manually construct frontmatter to avoid problematic YAML syntax
    const frontmatter = {
      id: meta.id || 'untitled',
      title: meta.purpose || 'Specification',
      sidebar_label: meta.id || meta.purpose || 'Specification',
      description: meta.purpose || 'SpecPlane specification',
      keywords: [...new Set([meta.type, meta.level, meta.domain].filter(Boolean))],
      hide_table_of_contents: false,
      toc_min_heading_level: 2,
      toc_max_heading_level: 3
    };
    
    // Manually construct YAML frontmatter to avoid js-yaml.dump() issues
    let yamlContent = '---\n';
    
    if (frontmatter.id) yamlContent += `id: ${frontmatter.id}\n`;
    if (frontmatter.title) yamlContent += `title: ${frontmatter.title}\n`;
    if (frontmatter.sidebar_label) yamlContent += `sidebar_label: ${frontmatter.sidebar_label}\n`;
    if (frontmatter.description) yamlContent += `description: ${frontmatter.description}\n`;
    if (frontmatter.keywords && frontmatter.keywords.length > 0) {
      yamlContent += `keywords:\n`;
      frontmatter.keywords.forEach(keyword => {
        yamlContent += `  - ${keyword}\n`;
      });
    }
    yamlContent += `hide_table_of_contents: ${frontmatter.hide_table_of_contents}\n`;
    yamlContent += `toc_min_heading_level: ${frontmatter.toc_min_heading_level}\n`;
    yamlContent += `toc_max_heading_level: ${frontmatter.toc_max_heading_level}\n`;
    yamlContent += '---';
    
    return yamlContent;
  }

  /**
   * Generate meta section
   */
  generateMetaSection(meta) {
    let markdown = '## Meta\n\n';
    
    if (meta.purpose) {
      markdown += `- **Purpose:** ${this.formatJSXSafeText(meta.purpose)}`;
    }
    
    if (meta.type) {
      markdown += `\n- **Type:** ${this.formatJSXSafeText(meta.type)}`;
    }
    
    if (meta.level) {
      markdown += `\n- **Level:** ${this.formatJSXSafeText(meta.level)}`;
    }
    
    if (meta.domain) {
      markdown += `\n- **Domain:** ${this.formatJSXSafeText(meta.domain)}`;
    }
    
    if (meta.status) {
      markdown += `\n- **Status:** ${this.formatJSXSafeText(meta.status)}`;
    }
    
    if (meta.version) {
      markdown += `\n- **Version:** ${this.formatJSXSafeText(meta.version)}`;
    }
    
    if (meta.id) {
      markdown += `\n- **ID:** ${this.formatJSXSafeText(meta.id)}`;
    }
    
    if (meta.owner) {
      markdown += `\n- **Owner:** ${this.formatJSXSafeText(meta.owner)}`;
    }
    
    if (meta.last_updated) {
      markdown += `\n- **Last Updated:** ${this.formatJSXSafeText(meta.last_updated)}`;
    }
    
    return markdown.trim();
  }

  /**
   * Generate default relationships diagram when none is provided
   */
  generateDefaultRelationshipsDiagram(specData) {
    let markdown = '## Relationships\n\n';
    
    // Create a simple graph showing relationships
    const relationships = [];
    const componentId = specData.meta?.id || 'this';
    
    if (specData.relationships) {
      if (specData.relationships.depends_on) {
        relationships.push(...specData.relationships.depends_on.map(dep => `  ${componentId} --> ${dep}`));
      }
      
      if (specData.relationships.used_by) {
        relationships.push(...specData.relationships.used_by.map(user => `  ${user} --> ${componentId}`));
      }
      
      if (specData.relationships.integrates_with) {
        relationships.push(...specData.relationships.integrates_with.map(integration => `  ${componentId} -.-> ${integration}`));
      }
    }
    
    if (specData.dependencies) {
      if (specData.dependencies.internal) {
        relationships.push(...specData.dependencies.internal.map(dep => `  ${componentId} --> ${dep}`));
      }
      
      if (specData.dependencies.external) {
        relationships.push(...specData.dependencies.external.map(dep => `  ${componentId} -.-> ${dep}`));
      }
    }
    
    if (relationships.length > 0) {
      markdown += '```mermaid\ngraph TD\n';
      markdown += relationships.join('\n');
      markdown += '\n```\n\n';
    } else {
      markdown += '*No relationships or dependencies defined*\n\n';
    }
    
    return markdown;
  }

  /**
   * Generate diagrams section
   */
  generateDiagramsSection(diagrams) {
    let markdown = '## Diagrams\n\n';
    
    for (const diagram of diagrams) {
      if (diagram.title) {
        markdown += `### ${diagram.title}\n\n`;
      }
      
      if (diagram.description) {
        markdown += `${diagram.description}\n\n`;
      }
      
      if (diagram.mermaid) {
        markdown += '```mermaid\n';
        markdown += diagram.mermaid;
        markdown += '\n```\n\n';
        this.stats.diagramsRendered++;
      }
    }
    
    return markdown.trim();
  }

  /**
   * Generate contracts section
   */
  generateContractsSection(contracts) {
    let markdown = '## Contracts\n\n';
    
    if (contracts.capabilities && contracts.capabilities.length > 0) {
      markdown += '### Capabilities\n\n';
      for (const capability of contracts.capabilities) {
        markdown += `- ${this.formatJSXSafeText(capability)}\n`;
      }
      markdown += '\n';
    }
    
    if (contracts.apis && contracts.apis.length > 0) {
      markdown += '### APIs\n\n';
      for (const api of contracts.apis) {
        markdown += `- ${this.formatJSXSafeText(api)}\n`;
      }
      markdown += '\n';
    }
    
    if (contracts.events && contracts.events.length > 0) {
      markdown += '### Events\n\n';
      for (const event of contracts.events) {
        // Handle events that might contain curly braces or special formatting
        let eventText = this.formatJSXSafeText(event);
        
        // If event contains curly braces, format it as code
        if (event.includes('{') && event.includes('}')) {
          eventText = `\`${event}\``;
        }
        
        markdown += `- ${eventText}\n`;
      }
      markdown += '\n';
    }
    
    if (contracts.states && contracts.states.length > 0) {
      markdown += '### States\n\n';
      for (const state of contracts.states) {
        markdown += `- ${this.formatJSXSafeText(state)}\n`;
      }
      markdown += '\n';
    }
    
    return markdown.trim();
  }

  /**
   * Generate validation section
   */
  generateValidationSection(validation) {
    let markdown = '## Validation\n\n';
    
    if (validation.acceptance_criteria && validation.acceptance_criteria.length > 0) {
      markdown += '### Acceptance Criteria\n\n';
      for (const criteria of validation.acceptance_criteria) {
        markdown += `- [ ] ${this.formatJSXSafeText(criteria)}\n`;
      }
      markdown += '\n';
    }
    
    if (validation.edge_cases && validation.edge_cases.length > 0) {
      markdown += '### Edge Cases\n\n';
      for (const edgeCase of validation.edge_cases) {
        markdown += `- ${this.formatJSXSafeText(edgeCase)}\n`;
      }
      markdown += '\n';
    }
    
    if (validation.assumptions && validation.assumptions.length > 0) {
      markdown += '### Assumptions\n\n';
      for (const assumption of validation.assumptions) {
        markdown += `- ${this.formatJSXSafeText(assumption)}\n`;
      }
      markdown += '\n';
    }
    
    if (validation.open_questions && validation.open_questions.length > 0) {
      markdown += '### Open Questions\n\n';
      for (const question of validation.open_questions) {
        markdown += `- ${this.formatJSXSafeText(question)}\n`;
      }
      markdown += '\n';
    }
    
    return markdown.trim();
  }

  /**
   * Generate generic section for any top-level YAML key
   */
  generateGenericSection(key, value) {
    let markdown = `## ${this.capitalizeFirst(key)}\n\n`;
    
    if (Array.isArray(value)) {
      // Handle array values
      for (const item of value) {
        if (typeof item === 'string') {
          markdown += `- ${this.formatJSXSafeText(item)}\n`;
        } else if (typeof item === 'object') {
          markdown += `- ${JSON.stringify(item)}\n`;
        }
      }
      markdown += '\n';
    } else if (typeof value === 'object' && value !== null) {
      // Handle object values
      for (const [subKey, subValue] of Object.entries(value)) {
        if (typeof subValue === 'string') {
          markdown += `### ${this.capitalizeFirst(subKey)}\n\n${this.formatJSXSafeText(subValue)}\n\n`;
        } else if (Array.isArray(subValue)) {
          markdown += `### ${this.capitalizeFirst(subKey)}\n\n`;
          for (const item of subValue) {
            markdown += `- ${this.formatJSXSafeText(item)}\n`;
          }
          markdown += '\n';
        } else if (typeof subValue === 'object' && subValue !== null) {
          markdown += `### ${this.capitalizeFirst(subKey)}\n\n`;
          for (const [k, v] of Object.entries(subValue)) {
            markdown += `- **${k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:** ${this.formatJSXSafeText(v)}\n`;
          }
          markdown += '\n';
        }
      }
    } else if (typeof value === 'string') {
      // Handle string values
      markdown += `${this.formatJSXSafeText(value)}\n\n`;
    }
    
    return markdown.trim();
  }

  /**
   * Capitalize first letter of a string
   */
  capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1).replace(/_/g, ' ');
  }

  /**
   * Format text to handle JSX characters by wrapping problematic lines in code blocks
   */
  formatJSXSafeText(text) {
    if (typeof text !== 'string') {
      return String(text);
    }
    
    // If text is already wrapped in backticks, return as-is
    if (text.startsWith('`') && text.endsWith('`')) {
      return text;
    }
    
    // Simple approach: if line contains problematic JSX characters, wrap the whole line
    if (text.includes('<') || text.includes('>') || text.includes('{') || text.includes('}')) {
      return `\`${text}\``;
    }
    
    return text;
  }

  /**
   * Generate references section
   */
  generateReferencesSection(refs) {
    let markdown = '## References\n\n';
    
    for (const [refId, ref] of Object.entries(refs)) {
      markdown += `### ${ref.title || refId}\n\n`;
      
      if (ref.type) {
        markdown += `**Type:** ${this.formatJSXSafeText(ref.type)}\n\n`;
      }
      
      if (ref.url) {
        markdown += `**URL:** [${ref.url}](${ref.url})\n\n`;
      }
      
      if (ref.path) {
        markdown += `**Path:** ${this.formatJSXSafeText(ref.path)}\n\n`;
      }
      
      if (ref.version) {
        markdown += `**Version:** ${this.formatJSXSafeText(ref.version)}\n\n`;
      }
      
      if (ref.owner) {
        markdown += `**Owner:** ${this.formatJSXSafeText(ref.owner)}\n\n`;
      }
      
      if (ref.tags && ref.tags.length > 0) {
        markdown += `**Tags:** ${ref.tags.join(', ')}\n\n`;
      }
      
      if (ref.notes) {
        markdown += `${this.formatJSXSafeText(ref.notes)}\n\n`;
      }
      
      markdown += '---\n\n';
      this.stats.referencesProcessed++;
    }
    
    return markdown.trim();
  }

  /**
   * Generate specs YAML section
   */
  generateSpecsYamlSection(specData) {
    let markdown = '## Specs YAML\n\n';
    markdown += '```yaml\n';
    
    try {
      const yaml = require('js-yaml');
      // Use safe options to avoid problematic YAML syntax
      markdown += yaml.dump(specData, { 
        indent: 2, 
        lineWidth: 120,
        noRefs: true,
        noCompatMode: true,
        sortKeys: true
      });
    } catch (error) {
      markdown += `# Error serializing YAML: ${error.message}\n`;
      // Fallback to JSON if YAML serialization fails
      markdown += JSON.stringify(specData, null, 2);
    }
    
    markdown += '```\n\n';
    return markdown;
  }

  /**
   * Generate table of contents
   */
  generateTableOfContents(sections) {
    let markdown = '# Table of Contents\n\n';
    
    // Extract headings from sections (up to level 3)
    const headings = [];
    
    for (const section of sections) {
      const lines = section.split('\n');
      for (const line of lines) {
        if (line.startsWith('# ')) {
          // H1 header - main section
          const title = line.substring(2);
          const anchor = this.generateAnchor(title);
          headings.push(`- [${title}](#${anchor})`);
        } else if (line.startsWith('## ')) {
          // H2 header - subsection
          const title = line.substring(3);
          const anchor = this.generateAnchor(title);
          headings.push(`  - [${title}](#${anchor})`);
        } else if (line.startsWith('### ')) {
          // H3 header - sub-subsection
          const title = line.substring(4);
          const anchor = this.generateAnchor(title);
          headings.push(`    - [${title}](#${anchor})`);
        }
      }
    }
    
    if (headings.length > 0) {
      markdown += headings.join('\n');
    } else {
      markdown += '*No headings found*';
    }
    
    return markdown;
  }

  /**
   * Generate anchor link from heading text
   */
  generateAnchor(text) {
    return text
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '') // Remove special characters except spaces and hyphens
      .replace(/\s+/g, '-') // Replace spaces with hyphens
      .replace(/-+/g, '-') // Replace multiple hyphens with single hyphen
      .replace(/^-|-$/g, ''); // Remove leading/trailing hyphens
  }

  /**
   * Get generation statistics
   */
  getStats() {
    return { ...this.stats };
  }

  /**
   * Reset statistics
   */
  resetStats() {
    this.stats = {
      filesGenerated: 0,
      sectionsGenerated: 0,
      diagramsRendered: 0,
      referencesProcessed: 0
    };
  }
}

module.exports = { MarkdownGenerator };