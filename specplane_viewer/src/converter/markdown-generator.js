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
      
      // Generate sections based on YAML structure
      for (const [key, value] of Object.entries(specData)) {
        if (key === 'meta' && value) {
          sections.push(this.generateMetaSection(value));
        } else if (key === 'relationships' || key === 'dependencies') {
          if (value) {
            sections.push(this.generateRelationshipSection(key, value, specData.meta?.id));
          }
        } else if (key === 'diagrams' && Array.isArray(value) && value.length > 0) {
          sections.push(this.generateDiagramsSection(value));
        } else if (key === 'contracts' && value) {
          sections.push(this.generateContractsSection(value));
        } else if (key === 'validation' && value) {
          sections.push(this.generateValidationSection(value));
        } else if (key === 'refs' && value) {
          sections.push(this.generateReferencesSection(value));
        } else if (value && typeof value === 'object' && Object.keys(value).length > 0) {
          // Handle other top-level sections
          sections.push(this.generateGenericSection(key, value));
        }
      }
      
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
    
    const frontmatter = {
      id: meta.id || 'untitled',
      title: meta.purpose || 'Specification',
      sidebar_label: meta.id || meta.purpose || 'Specification',
      description: meta.purpose || 'SpecPlane specification',
      keywords: [...new Set([meta.type, meta.level, meta.domain].filter(Boolean))],
      hide_table_of_contents: false,
      toc_min_heading_level: 1,
      toc_max_heading_level: 3
    };
    
    // Convert to YAML frontmatter
    const yaml = require('js-yaml');
    return '---\n' + yaml.dump(frontmatter) + '---';
  }

  /**
   * Generate meta section
   */
  generateMetaSection(meta) {
    let markdown = '## Meta\n\n';
    
    if (meta.purpose) {
      markdown += `- **Purpose:** ${meta.purpose}`;
    }
    
    if (meta.type) {
      markdown += `\n- **Type:** ${meta.type}`;
    }
    
    if (meta.level) {
      markdown += `\n- **Level:** ${meta.level}`;
    }
    
    if (meta.domain) {
      markdown += `\n- **Domain:** ${meta.domain}`;
    }
    
    if (meta.status) {
      markdown += `\n- **Status:** ${meta.status}`;
    }
    
    if (meta.version) {
      markdown += `\n- **Version:** ${meta.version}`;
    }
    
    if (meta.id) {
      markdown += `\n- **ID:** ${meta.id}`;
    }
    
    if (meta.owner) {
      markdown += `\n- **Owner:** ${meta.owner}`;
    }
    
    if (meta.last_updated) {
      markdown += `\n- **Last Updated:** ${meta.last_updated}`;
    }
    
    return markdown.trim();
  }

  /**
   * Generate relationship section
   */
  generateRelationshipSection(key, value, componentId) {
    let markdown = `## ${this.capitalizeFirst(key)}\n\n`;
    
    // Create a simple graph showing relationships
    const relationships = [];
    
    if (value.depends_on) {
      relationships.push(...value.depends_on.map(dep => `  ${componentId || 'this'} --> ${dep}`));
    }
    
    if (value.used_by) {
      relationships.push(...value.used_by.map(user => `  ${user} --> ${componentId || 'this'}`));
    }
    
    if (value.integrates_with) {
      relationships.push(...value.integrates_with.map(integration => `  ${componentId || 'this'} -.-> ${integration}`));
    }
    
    if (relationships.length > 0) {
      markdown += '```mermaid\ngraph TD\n';
      markdown += relationships.join('\n');
      markdown += '\n```\n\n';
    } else {
      markdown += '*No relationships defined*\n\n';
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
        markdown += `- ${capability}\n`;
      }
      markdown += '\n';
    }
    
    if (contracts.apis && contracts.apis.length > 0) {
      markdown += '### APIs\n\n';
      for (const api of contracts.apis) {
        markdown += `- ${api}\n`;
      }
      markdown += '\n';
    }
    
    if (contracts.events && contracts.events.length > 0) {
      markdown += '### Events\n\n';
      for (const event of contracts.events) {
        // Handle events that might contain curly braces or special formatting
        let eventText = event;
        
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
        markdown += `- ${state}\n`;
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
        markdown += `- [ ] ${criteria}\n`;
      }
      markdown += '\n';
    }
    
    if (validation.edge_cases && validation.edge_cases.length > 0) {
      markdown += '### Edge Cases\n\n';
      for (const edgeCase of validation.edge_cases) {
        markdown += `- ${edgeCase}\n`;
      }
      markdown += '\n';
    }
    
    if (validation.assumptions && validation.assumptions.length > 0) {
      markdown += '### Assumptions\n\n';
      for (const assumption of validation.assumptions) {
        markdown += `- ${assumption}\n`;
      }
      markdown += '\n';
    }
    
    if (validation.open_questions && validation.open_questions.length > 0) {
      markdown += '### Open Questions\n\n';
      for (const question of validation.open_questions) {
        markdown += `- ${question}\n`;
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
          markdown += `- ${item}\n`;
        } else if (typeof item === 'object') {
          markdown += `- ${JSON.stringify(item)}\n`;
        }
      }
      markdown += '\n';
    } else if (typeof value === 'object' && value !== null) {
      // Handle object values
      for (const [subKey, subValue] of Object.entries(value)) {
        if (typeof subValue === 'string') {
          markdown += `### ${this.capitalizeFirst(subKey)}\n\n${subValue}\n\n`;
        } else if (Array.isArray(subValue)) {
          markdown += `### ${this.capitalizeFirst(subKey)}\n\n`;
          for (const item of subValue) {
            markdown += `- ${item}\n`;
          }
          markdown += '\n';
        } else if (typeof subValue === 'object' && subValue !== null) {
          markdown += `### ${this.capitalizeFirst(subKey)}\n\n`;
          for (const [k, v] of Object.entries(subValue)) {
            markdown += `- **${k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:** ${v}\n`;
          }
          markdown += '\n';
        }
      }
    } else if (typeof value === 'string') {
      // Handle string values
      markdown += `${value}\n\n`;
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
   * Generate references section
   */
  generateReferencesSection(refs) {
    let markdown = '## References\n\n';
    
    for (const [refId, ref] of Object.entries(refs)) {
      markdown += `### ${ref.title || refId}\n\n`;
      
      if (ref.type) {
        markdown += `**Type:** ${ref.type}\n\n`;
      }
      
      if (ref.url) {
        markdown += `**URL:** [${ref.url}](${ref.url})\n\n`;
      }
      
      if (ref.path) {
        markdown += `**Path:** ${ref.path}\n\n`;
      }
      
      if (ref.version) {
        markdown += `**Version:** ${ref.version}\n\n`;
      }
      
      if (ref.owner) {
        markdown += `**Owner:** ${ref.owner}\n\n`;
      }
      
      if (ref.tags && ref.tags.length > 0) {
        markdown += `**Tags:** ${ref.tags.join(', ')}\n\n`;
      }
      
      if (ref.notes) {
        markdown += `${ref.notes}\n\n`;
      }
      
      markdown += '---\n\n';
      this.stats.referencesProcessed++;
    }
    
    return markdown.trim();
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
